import pytest
from datetime import datetime
from menu import Menu, MenuAdmin, MenuSolic
from sistema import Sistema
from excepciones import DatoInvalidoError

@pytest.fixture
def mock_sistema(mocker):
    sistema = mocker.Mock(spec = Sistema)
    sistema.ROL_ADMINISTRADOR = Sistema.ROL_ADMINISTRADOR
    sistema.ROL_SOLICITANTE = Sistema.ROL_SOLICITANTE
    sistema.ROL_OTRO = Sistema.ROL_OTRO
    return sistema

@pytest.fixture
def menu(mock_sistema):
    return Menu(mock_sistema)

@pytest.fixture
def menu_admin(mock_sistema):
    return MenuAdmin(mock_sistema)

@pytest.fixture
def menu_solic(mock_sistema):
    return MenuSolic(mock_sistema)

@pytest.fixture
def mock_input(mocker):
    return mocker.patch("builtins.input")

# Funcionamiento normal
def test_menu_ok(menu, mock_sistema):
    assert menu.getter_sistema() is mock_sistema
    assert issubclass(MenuAdmin, Menu)
    assert issubclass(MenuSolic, Menu)

# pedir_texto
def test_pedirTexto_recortaEspacios(menu, mock_input):
    mock_input.side_effect = ["  hola  "]
    assert menu.pedir_texto("Texto: ") == "hola"

# Vacío: vuelve a pedir
def test_pedirTexto_vacioReintenta(menu, mock_input):
    mock_input.side_effect = ["", "   ", "ok"]
    assert menu.pedir_texto("Texto: ") == "ok"
    assert mock_input.call_count == 3

# pedir_entero / pedir_numero
def test_pedirEntero_ok(menu, mock_input):
    mock_input.side_effect = [" 42 "]
    assert menu.pedir_entero("N: ") == 42

# Un decimal no es un entero
def test_pedirEntero_invalidoReintenta(menu, mock_input):
    mock_input.side_effect = ["abc", "3.5", "7"]
    assert menu.pedir_entero("N: ") == 7
    assert mock_input.call_count == 3

def test_pedirNumero_ok(menu, mock_input):
    mock_input.side_effect = ["3.5"]
    assert menu.pedir_numero("N: ") == 3.5

def test_pedirNumero_invalidoReintenta(menu, mock_input):
    mock_input.side_effect = ["x", "2"]
    assert menu.pedir_numero("N: ") == 2.0
    assert mock_input.call_count == 2

# pedir_fecha_hora
def test_pedirFechaHora_ok(menu, mock_input):
    mock_input.side_effect = ["09/10/2026 14:30"]
    assert menu.pedir_fecha_hora("Hora") == datetime(2026, 10, 9, 14, 30)

def test_pedirFechaHora_invalidaReintenta(menu, mock_input):
    mock_input.side_effect = ["2026-10-09 14:30", "32/13/2026 10:00", "09/10/2026 14:30"]
    assert menu.pedir_fecha_hora("Hora") == datetime(2026, 10, 9, 14, 30)
    assert mock_input.call_count == 3

# pedir_si_no: solo "s" es sí
def test_pedirSiNo(menu, mock_input):
    mock_input.side_effect = ["S", "n", ""]
    assert menu.pedir_si_no("Seguir?") is True
    assert menu.pedir_si_no("Seguir?") is False
    assert menu.pedir_si_no("Seguir?") is False

# pedir_lugar: valida con el sistema, no con la matriz
def test_pedirLugar_conocido(menu, mock_sistema, mocker):
    mocker.patch.object(menu, "pedir_texto", return_value = "Palermo")
    mock_sistema.es_lugar_conocido.return_value = True
    assert menu.pedir_lugar("Lugar: ") == "Palermo"
    mock_sistema.es_lugar_conocido.assert_called_once_with("Palermo")

def test_pedirLugar_desconocidoReintenta(menu, mock_sistema, mocker, capsys):
    mocker.patch.object(menu, "pedir_texto", side_effect = ["Marte", "Palermo"])
    mock_sistema.es_lugar_conocido.side_effect = [False, True]
    mock_sistema.lugares_conocidos.return_value = ["Palermo"]
    assert menu.pedir_lugar("Lugar: ") == "Palermo"
    assert "'Marte' no es un lugar de la matriz" in capsys.readouterr().out

# pedir_persona
def test_pedirPersona(menu, mocker):
    mocker.patch.object(menu, "pedir_texto", return_value = "Ana")
    mocker.patch.object(menu, "pedir_entero", side_effect = [12345678, 1122334455])
    assert menu.pedir_persona() == ("Ana", 12345678, 1122334455)

# pedir_articulos: una tupla por artículo, sin crear objetos
def test_pedirArticulos_varios(menu, mocker):
    mocker.patch.object(menu, "pedir_texto", side_effect = ["Caja", "Sobre"])
    mocker.patch.object(menu, "pedir_numero", side_effect = [2.0, 1.0, 0.5, 0.1])
    mocker.patch.object(menu, "pedir_si_no", side_effect = [True, False])
    assert menu.pedir_articulos() == [("Caja", 2.0, 1.0), ("Sobre", 0.5, 0.1)]

# Cada llamada empieza con una lista nueva
def test_pedirArticulos_listaNueva(menu, mocker):
    mocker.patch.object(menu, "pedir_texto", return_value = "Caja")
    mocker.patch.object(menu, "pedir_numero", return_value = 1.0)
    mocker.patch.object(menu, "pedir_si_no", return_value = False)
    menu.pedir_articulos()
    assert menu.pedir_articulos() == [("Caja", 1.0, 1.0)]

# elegir_viaje
def test_elegirViaje_ok(menu, mock_sistema, mocker, capsys):
    mock_sistema.opciones_viajes.return_value = ["0) Viaje A", "2) Viaje C"]
    mocker.patch.object(menu, "pedir_entero", return_value = 2)
    assert menu.elegir_viaje("PLANIFICADO") == 2
    mock_sistema.opciones_viajes.assert_called_once_with("PLANIFICADO")
    salida = capsys.readouterr().out
    assert "0) Viaje A" in salida
    assert "2) Viaje C" in salida

# Si el sistema no tiene viajes, el error se propaga y no se pide número
def test_elegirViaje_sinViajes(menu, mock_sistema, mocker):
    mock_sistema.opciones_viajes.side_effect = DatoInvalidoError("Todavia no hay ningun viaje creado.")
    mock_pedir = mocker.patch.object(menu, "pedir_entero")
    with pytest.raises(DatoInvalidoError, match = "ningun viaje"):
        menu.elegir_viaje()
    mock_pedir.assert_not_called()

# correr_menu
def test_correrMenu_ejecutaYSale(menu, mock_input, mocker):
    accion = mocker.Mock()
    salida = mocker.Mock()
    mock_input.side_effect = ["1", "2"]
    menu.correr_menu("MENU", {"1": accion, "2": salida}, "2")
    accion.assert_called_once_with()
    salida.assert_called_once_with()

# Opción inexistente: pide de nuevo sin ejecutar nada
def test_correrMenu_opcionInvalida(menu, mock_input, mocker):
    salida = mocker.Mock()
    mock_input.side_effect = ["9", "x", "1"]
    menu.correr_menu("MENU", {"1": salida}, "1")
    salida.assert_called_once_with()

# Una excepción se muestra y el menú sigue
def test_correrMenu_excepcionNoCorta(menu, mock_input, mocker, capsys):
    falla = mocker.Mock(side_effect = DatoInvalidoError("algo salió mal"))
    salida = mocker.Mock()
    mock_input.side_effect = ["1", "2"]
    menu.correr_menu("MENU", {"1": falla, "2": salida}, "2")
    assert "algo salió mal" in capsys.readouterr().out
    salida.assert_called_once_with()

# Si la opción de salida falla, no se sale
def test_correrMenu_salidaFallidaNoSale(menu, mock_input, mocker):
    salida = mocker.Mock(side_effect = [DatoInvalidoError("no se pudo guardar"), None])
    mock_input.side_effect = ["2", "2"]
    menu.correr_menu("MENU", {"2": salida}, "2")
    assert salida.call_count == 2

# Opciones compartidas: solo muestran lo que devuelve el sistema
def test_verViajes(menu, mock_sistema, capsys):
    mock_sistema.ver_viajes.return_value = ["Viaje 1", "Viaje 2"]
    menu.ver_viajes()
    salida = capsys.readouterr().out
    assert "Viaje 1" in salida
    assert "Viaje 2" in salida

def test_cerrarSesion(menu, mock_sistema):
    menu.cerrar_sesion()
    mock_sistema.cerrar_sesion.assert_called_once_with()

# iniciar_sesion
def test_iniciarSesion_admin(menu, mock_sistema, mocker):
    mock_menu_admin = mocker.patch("menu.MenuAdmin")
    mock_menu_solic = mocker.patch("menu.MenuSolic")
    mocker.patch.object(menu, "pedir_entero", return_value = 123)
    mock_sistema.iniciar_sesion.return_value = Sistema.ROL_ADMINISTRADOR
    menu.iniciar_sesion()
    mock_sistema.iniciar_sesion.assert_called_once_with(123)
    mock_menu_admin.assert_called_once_with(mock_sistema)
    mock_menu_admin.return_value.ejecutar.assert_called_once_with()
    mock_menu_solic.assert_not_called()

def test_iniciarSesion_solicitante(menu, mock_sistema, mocker):
    mock_menu_admin = mocker.patch("menu.MenuAdmin")
    mock_menu_solic = mocker.patch("menu.MenuSolic")
    mocker.patch.object(menu, "pedir_entero", return_value = 123)
    mock_sistema.iniciar_sesion.return_value = Sistema.ROL_SOLICITANTE
    menu.iniciar_sesion()
    mock_menu_solic.return_value.ejecutar.assert_called_once_with()
    mock_menu_admin.assert_not_called()

# Otro rol: no abre ningún menú
def test_iniciarSesion_otroRol(menu, mock_sistema, mocker, capsys):
    mock_menu_admin = mocker.patch("menu.MenuAdmin")
    mock_menu_solic = mocker.patch("menu.MenuSolic")
    mocker.patch.object(menu, "pedir_entero", return_value = 123)
    mock_sistema.iniciar_sesion.return_value = Sistema.ROL_OTRO
    menu.iniciar_sesion()
    mock_menu_admin.assert_not_called()
    mock_menu_solic.assert_not_called()
    assert "NO TIENES ACCESO" in capsys.readouterr().out

# DNI inexistente: vuelve a pedir hasta que exista
def test_iniciarSesion_dniIncorrectoReintenta(menu, mock_sistema, mocker):
    mock_menu_admin = mocker.patch("menu.MenuAdmin")
    mocker.patch.object(menu, "pedir_entero", side_effect = [1, 2, 3])
    mock_sistema.iniciar_sesion.side_effect = [None, None, Sistema.ROL_ADMINISTRADOR]
    menu.iniciar_sesion()
    assert mock_sistema.iniciar_sesion.call_count == 3
    mock_menu_admin.return_value.ejecutar.assert_called_once_with()

# crear personas
def test_crearAdministrador(menu, mock_sistema, mocker, capsys):
    mocker.patch.object(menu, "pedir_persona", return_value = ("Ana", 12345678, 1122334455))
    mock_sistema.crear_administrador.return_value = "ADMINISTRADOR CREADO: Ana"
    menu.crear_administrador()
    mock_sistema.crear_administrador.assert_called_once_with("Ana", 12345678, 1122334455)
    mock_sistema.crear_solicitante.assert_not_called()
    assert "ADMINISTRADOR CREADO: Ana" in capsys.readouterr().out

def test_crearSolicitante(menu, mock_sistema, mocker):
    mocker.patch.object(menu, "pedir_persona", return_value = ("Ana", 12345678, 1122334455))
    mock_sistema.crear_solicitante.return_value = "SOLICITANTE CREADO: Ana"
    menu.crear_solicitante()
    mock_sistema.crear_solicitante.assert_called_once_with("Ana", 12345678, 1122334455)
    mock_sistema.crear_administrador.assert_not_called()

# Si el sistema rechaza los datos, el error se propaga (lo muestra correr_menu)
def test_crearSolicitante_datosInvalidos(menu, mock_sistema, mocker):
    mocker.patch.object(menu, "pedir_persona", return_value = ("Ana", 1, 1))
    mock_sistema.crear_solicitante.side_effect = DatoInvalidoError("DNI inválido")
    with pytest.raises(DatoInvalidoError, match = "DNI inválido"):
        menu.crear_solicitante()

def test_salir(menu, mock_sistema):
    menu.salir()
    mock_sistema.salir.assert_called_once_with()

# ejecutar: 5 opciones, salir es la 5
def test_ejecutar_inicio(menu, mocker):
    mock_correr = mocker.patch.object(menu, "correr_menu")
    menu.ejecutar()
    mensaje, opciones, salida = mock_correr.call_args.args
    assert mensaje == Menu.MENSAJE_MENU_INICIO
    assert sorted(opciones) == ["1", "2", "3", "4", "5"]
    assert salida == "5"
    assert opciones[salida] == menu.salir

# MenuAdmin
def test_registrarTransporte(menu_admin, mock_sistema, mocker, capsys):
    mock_sistema.tipos_transporte.return_value = ["Furgoneta", "Motocicleta"]
    mocker.patch.object(menu_admin, "pedir_entero", return_value = 1)
    mock_sistema.registrar_transporte.return_value = "TRANSPORTE REGISTRADO"
    menu_admin.registrar_transporte()
    salida = capsys.readouterr().out
    assert "0) Furgoneta" in salida
    assert "1) Motocicleta" in salida
    mock_sistema.registrar_transporte.assert_called_once_with(1)

# Los datos se pasan al sistema en el orden correcto
def test_crearViaje(menu_admin, mock_sistema, mocker):
    horario = datetime(2026, 10, 9, 8, 0)
    mock_sistema.opciones_transportes.return_value = ["0) Furgoneta"]
    mocker.patch.object(menu_admin, "pedir_entero", return_value = 0)
    mocker.patch.object(menu_admin, "pedir_lugar", return_value = "Deposito")
    mocker.patch.object(menu_admin, "pedir_fecha_hora", return_value = horario)
    menu_admin.crear_viaje()
    mock_sistema.crear_viaje.assert_called_once_with(0, "Deposito", horario)

# Sin transportes: no se pide nada más
def test_crearViaje_sinTransportes(menu_admin, mock_sistema, mocker):
    mock_sistema.opciones_transportes.side_effect = DatoInvalidoError("Todavia no hay ningun transporte registrado.")
    mock_lugar = mocker.patch.object(menu_admin, "pedir_lugar")
    with pytest.raises(DatoInvalidoError):
        menu_admin.crear_viaje()
    mock_lugar.assert_not_called()
    mock_sistema.crear_viaje.assert_not_called()

# Cada operación pide el viaje en el estado que corresponde
def test_iniciarViaje_pideViajePlanificado(menu_admin, mock_sistema, mocker):
    mock_elegir = mocker.patch.object(menu_admin, "elegir_viaje", return_value = 3)
    mock_sistema.iniciar_viaje.return_value = ["VIAJE INICIADO"]
    menu_admin.iniciar_viaje()
    mock_elegir.assert_called_once_with("PLANIFICADO")
    mock_sistema.iniciar_viaje.assert_called_once_with(3)

def test_verDetalleViaje_cualquierEstado(menu_admin, mock_sistema, mocker):
    mock_elegir = mocker.patch.object(menu_admin, "elegir_viaje", return_value = 1)
    mock_sistema.detalle_viaje.return_value = ["Detalle"]
    menu_admin.ver_detalle_viaje()
    mock_elegir.assert_called_once_with()
    mock_sistema.detalle_viaje.assert_called_once_with(1)

def test_registrarEntrega(menu_admin, mock_sistema, mocker):
    hora = datetime(2026, 10, 9, 10, 0)
    mock_elegir = mocker.patch.object(menu_admin, "elegir_viaje", return_value = 2)
    mocker.patch.object(menu_admin, "pedir_fecha_hora", return_value = hora)
    mocker.patch.object(menu_admin, "pedir_texto", return_value = "Juan")
    mocker.patch.object(menu_admin, "pedir_numero", return_value = 150.0)
    menu_admin.registrar_entrega()
    mock_elegir.assert_called_once_with("EN_CURSO")
    mock_sistema.registrar_entrega.assert_called_once_with(2, hora, "Juan", 150.0)

def test_registrarIncidente(menu_admin, mock_sistema, mocker, capsys):
    fecha = datetime(2026, 10, 9, 10, 0)
    mock_sistema.tipos_incidente.return_value = ["DAÑO", "AUSENTE"]
    mock_sistema.descripciones_alcance.return_value = ["Falla la entrega"]
    mock_elegir = mocker.patch.object(menu_admin, "elegir_viaje", return_value = 2)
    mocker.patch.object(menu_admin, "pedir_entero", side_effect = [1, 0])
    mocker.patch.object(menu_admin, "pedir_fecha_hora", return_value = fecha)
    mocker.patch.object(menu_admin, "pedir_texto", return_value = "No estaba")
    menu_admin.registrar_incidente()
    mock_elegir.assert_called_once_with("EN_CURSO")
    mock_sistema.registrar_incidente.assert_called_once_with(2, 1, fecha, "No estaba", 0)
    salida = capsys.readouterr().out
    assert "1) AUSENTE" in salida
    assert "0) Falla la entrega" in salida

# agregar_distancias
def test_agregarDistancias_sinVuelta(menu_admin, mock_sistema, mocker):
    mocker.patch.object(menu_admin, "pedir_texto", side_effect = ["A", "B"])
    mocker.patch.object(menu_admin, "pedir_numero", return_value = 5.0)
    mocker.patch.object(menu_admin, "pedir_si_no", side_effect = [False, False])
    menu_admin.agregar_distancias()
    mock_sistema.agregar_distancia.assert_called_once_with("A", "B", 5.0)

# Con vuelta: origen y destino se invierten y se pide otra distancia
def test_agregarDistancias_conVuelta(menu_admin, mock_sistema, mocker):
    mocker.patch.object(menu_admin, "pedir_texto", side_effect = ["A", "B"])
    mocker.patch.object(menu_admin, "pedir_numero", side_effect = [5.0, 7.0])
    mocker.patch.object(menu_admin, "pedir_si_no", side_effect = [True, False])
    menu_admin.agregar_distancias()
    assert mock_sistema.agregar_distancia.call_args_list == [mocker.call("A", "B", 5.0), mocker.call("B", "A", 7.0)]

# Otro tramo: vuelve a empezar
def test_agregarDistancias_otroTramo(menu_admin, mock_sistema, mocker):
    mocker.patch.object(menu_admin, "pedir_texto", side_effect = ["A", "B", "C", "D"])
    mocker.patch.object(menu_admin, "pedir_numero", side_effect = [1.0, 2.0])
    mocker.patch.object(menu_admin, "pedir_si_no", side_effect = [False, True, False, False])
    menu_admin.agregar_distancias()
    assert mock_sistema.agregar_distancia.call_args_list == [mocker.call("A", "B", 1.0), mocker.call("C", "D", 2.0)]

# deshacer_ultima_solicitud
def test_deshacer_noReasigna(menu_admin, mock_sistema, mocker):
    mocker.patch.object(menu_admin, "elegir_viaje", return_value = 0)
    mocker.patch.object(menu_admin, "pedir_si_no", return_value = False)
    menu_admin.deshacer_ultima_solicitud()
    mock_sistema.deshacer_ultima_solicitud.assert_called_once_with(0)
    mock_sistema.descartar_solicitud_deshecha.assert_called_once_with()
    mock_sistema.reasignar_solicitud_deshecha.assert_not_called()

def test_deshacer_reasigna(menu_admin, mock_sistema, mocker):
    mock_elegir = mocker.patch.object(menu_admin, "elegir_viaje", side_effect = [0, 4])
    mocker.patch.object(menu_admin, "pedir_si_no", return_value = True)
    menu_admin.deshacer_ultima_solicitud()
    mock_sistema.deshacer_ultima_solicitud.assert_called_once_with(0)
    mock_sistema.reasignar_solicitud_deshecha.assert_called_once_with(4)
    mock_sistema.descartar_solicitud_deshecha.assert_not_called()
    assert mock_elegir.call_count == 2

def test_asignarSolicitudPendiente(menu_admin, mock_sistema, mocker):
    mock_sistema.opciones_pendientes.return_value = ["0) Solicitud"]
    mocker.patch.object(menu_admin, "pedir_entero", return_value = 0)
    mock_elegir = mocker.patch.object(menu_admin, "elegir_viaje", return_value = 3)
    menu_admin.asignar_solicitud_pendiente()
    mock_elegir.assert_called_once_with("PLANIFICADO")
    mock_sistema.asignar_solicitud_pendiente.assert_called_once_with(0, 3)

def test_buscarPersona(menu_admin, mock_sistema, mocker, capsys):
    mocker.patch.object(menu_admin, "pedir_entero", return_value = 12345678)
    mock_sistema.buscar_persona.return_value = ["PERSONA ENCONTRADA: Ana", "Saltos: 2"]
    menu_admin.buscar_persona()
    mock_sistema.buscar_persona.assert_called_once_with(12345678)
    assert "PERSONA ENCONTRADA: Ana" in capsys.readouterr().out

# ejecutar: 14 opciones, cerrar sesión es la 14
def test_ejecutar_admin(menu_admin, mock_sistema, mocker):
    mock_correr = mocker.patch.object(menu_admin, "correr_menu")
    menu_admin.ejecutar()
    mensaje, opciones, salida = mock_correr.call_args.args
    assert mensaje == MenuAdmin.MENSAJE_MENU
    assert sorted(opciones, key = int) == list(map(str, range(1, 15)))
    assert salida == "14"
    assert opciones["14"] == menu_admin.cerrar_sesion

# MenuSolic
def test_crearSolicitud(menu_solic, mock_sistema, mocker):
    inicio = datetime(2026, 10, 9, 9, 0)
    fin = datetime(2026, 10, 9, 12, 0)
    articulos = [("Caja", 2.0, 1.0)]
    mock_elegir = mocker.patch.object(menu_solic, "elegir_viaje", return_value = 1)
    mock_sistema.alcanzables_desde_viaje.return_value = ("Deposito", ["Palermo"])
    mocker.patch.object(menu_solic, "pedir_lugar", return_value = "Palermo")
    mocker.patch.object(menu_solic, "pedir_fecha_hora", side_effect = [inicio, fin])
    mocker.patch.object(menu_solic, "pedir_articulos", return_value = articulos)
    menu_solic.crear_solicitud()
    mock_elegir.assert_called_once_with("PLANIFICADO")
    mock_sistema.crear_solicitud.assert_called_once_with(1, "Palermo", inicio, fin, articulos)

# Sin tramos desde el último lugar: no se piden más datos
def test_crearSolicitud_sinAlcanzables(menu_solic, mock_sistema, mocker):
    mocker.patch.object(menu_solic, "elegir_viaje", return_value = 1)
    mock_sistema.alcanzables_desde_viaje.side_effect = DatoInvalidoError("Todavia no hay ninguna distancia")
    mock_lugar = mocker.patch.object(menu_solic, "pedir_lugar")
    with pytest.raises(DatoInvalidoError):
        menu_solic.crear_solicitud()
    mock_lugar.assert_not_called()
    mock_sistema.crear_solicitud.assert_not_called()

# ejecutar: 4 opciones, cerrar sesión es la 4
def test_ejecutar_solic(menu_solic, mocker):
    mock_correr = mocker.patch.object(menu_solic, "correr_menu")
    menu_solic.ejecutar()
    mensaje, opciones, salida = mock_correr.call_args.args
    assert mensaje == MenuSolic.MENSAJE_MENU
    assert sorted(opciones) == ["1", "2", "3", "4"]
    assert salida == "4"
    assert opciones["4"] == menu_solic.cerrar_sesion
