import pytest
from datetime import datetime
from sistema import Sistema
from persona import Persona, Administrador, Solicitante
from transporte import Transporte, Furgoneta, Motocicleta, Camion
from matrizdistancia import MatrizDistancia
from solicitud import Solicitud
from viaje import Viaje
from comprobante import Comprobante
from incidente import Incidente
from parada import Parada
from articulo import Articulo
from excepciones import DatoInvalidoError, FlotaError, EstadoInvalidoError

@pytest.fixture
def contexto(mocker):
    return {Articulo: [], MatrizDistancia: mocker.Mock(spec = MatrizDistancia), Persona: [], Transporte: [], Solicitud: [], Comprobante: [], Incidente: [], Parada: [], Viaje: []}

@pytest.fixture
def sistema(mocker, contexto):
    mocker.patch.object(Sistema, "leer_todos", return_value = contexto)
    return Sistema()

@pytest.fixture
def admin(mocker, sistema):
    usuario = mocker.Mock(spec = Administrador)
    sistema.setter_usuario(usuario)
    return usuario

@pytest.fixture
def solicitante(mocker, sistema):
    usuario = mocker.Mock(spec = Solicitante)
    sistema.setter_usuario(usuario)
    return usuario

def crear_viaje_mock(mocker, contexto, *estados):
    viaje = mocker.Mock(spec = Viaje)
    viaje.getter_estado.side_effect = list(estados)
    contexto[Viaje].append(viaje)
    return viaje

# Funcionamiento normal
def test_sistema_ok(sistema, contexto):
    assert sistema.getter_contexto() is contexto
    assert sistema.getter_usuario() is None
    assert sistema.getter_solicitud_deshecha() is None

# iniciar_sesion
def test_iniciarSesion_administrador(sistema, mocker):
    persona = mocker.Mock(spec = Administrador)
    arbol = mocker.Mock()
    arbol.buscar.return_value = persona
    mocker.patch.object(Persona, "getter_dnis_registrados", return_value = arbol)
    assert sistema.iniciar_sesion(123) == Sistema.ROL_ADMINISTRADOR
    arbol.buscar.assert_called_once_with(arbol.getter_raiz.return_value, 123)
    assert sistema.getter_usuario() is persona

def test_iniciarSesion_solicitante(sistema, mocker):
    persona = mocker.Mock(spec = Solicitante)
    arbol = mocker.Mock()
    arbol.buscar.return_value = persona
    mocker.patch.object(Persona, "getter_dnis_registrados", return_value = arbol)
    assert sistema.iniciar_sesion(123) == Sistema.ROL_SOLICITANTE
    assert sistema.getter_usuario() is persona

# Persona que no es ni admin ni solicitante
def test_iniciarSesion_otroRol(sistema, mocker):
    persona = mocker.Mock(spec = Persona)
    arbol = mocker.Mock()
    arbol.buscar.return_value = persona
    mocker.patch.object(Persona, "getter_dnis_registrados", return_value = arbol)
    assert sistema.iniciar_sesion(123) == Sistema.ROL_OTRO

# DNI inexistente: devuelve None y no cambia el usuario
def test_iniciarSesion_dniInexistente(sistema, mocker):
    arbol = mocker.Mock()
    arbol.buscar.return_value = None
    mocker.patch.object(Persona, "getter_dnis_registrados", return_value = arbol)
    assert sistema.iniciar_sesion(999) is None
    assert sistema.getter_usuario() is None

# crear personas
def test_crearSolicitante_ok(sistema, contexto, mocker):
    mock_clase = mocker.patch("sistema.Solicitante")
    resultado = sistema.crear_solicitante("Ana", 12345678, 1122334455)
    mock_clase.assert_called_once_with("Ana", 12345678, 1122334455)
    assert contexto[Persona] == [mock_clase.return_value]
    assert "SOLICITANTE CREADO" in resultado

# Si el constructor falla, no se agrega a la lista
def test_crearSolicitante_invalido(sistema, contexto, mocker):
    mocker.patch("sistema.Solicitante", side_effect = DatoInvalidoError("DNI inválido"))
    with pytest.raises(DatoInvalidoError, match = "DNI inválido"):
        sistema.crear_solicitante("Ana", 1, 1)
    assert contexto[Persona] == []

def test_crearAdministrador_ok(sistema, contexto, mocker):
    mock_clase = mocker.patch("sistema.Administrador")
    resultado = sistema.crear_administrador("Ana", 12345678, 1122334455)
    assert contexto[Persona] == [mock_clase.return_value]
    assert "ADMINISTRADOR CREADO" in resultado

# Cerrar sesión guarda y olvida al usuario
def test_cerrarSesion(sistema, admin, mocker):
    mock_guardar = mocker.patch.object(sistema, "guardar_todos")
    sistema.cerrar_sesion()
    mock_guardar.assert_called_once_with()
    assert sistema.getter_usuario() is None

def test_salir_guarda(sistema, mocker):
    mock_guardar = mocker.patch.object(sistema, "guardar_todos")
    sistema.salir()
    mock_guardar.assert_called_once_with()

# elegir_de: índice inválido
def test_elegirDe_ok(sistema):
    assert sistema.elegir_de(["a", "b"], 1) == "b"

def test_elegirDe_fueraDeRango(sistema):
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.elegir_de(["a", "b"], 2)

# Un índice negativo no debe tomar el último elemento
def test_elegirDe_negativo(sistema):
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.elegir_de(["a", "b"], -1)

def test_elegirDe_noEntero(sistema):
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.elegir_de(["a", "b"], "1")

# obtener_viaje
def test_obtenerViaje_estadoCorrecto(sistema, contexto, mocker):
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    assert sistema.obtener_viaje(0, "PLANIFICADO") is viaje

def test_obtenerViaje_estadoIncorrecto(sistema, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    with pytest.raises(DatoInvalidoError, match = "PLANIFICADO"):
        sistema.obtener_viaje(0, "PLANIFICADO")

# opciones_viajes
def test_opcionesViajes_sinViajes(sistema):
    with pytest.raises(DatoInvalidoError, match = "ningun viaje"):
        sistema.opciones_viajes()

# El número que se muestra es el índice en la lista completa, no en la filtrada
def test_opcionesViajes_filtraPorEstadoConservandoIndice(sistema, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "FINALIZADO")
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    opciones = sistema.opciones_viajes("PLANIFICADO")
    assert len(opciones) == 1
    assert opciones[0].startswith("1) ")

def test_opcionesViajes_ningunoEnEseEstado(sistema, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "FINALIZADO")
    with pytest.raises(DatoInvalidoError, match = "EN_CURSO"):
        sistema.opciones_viajes("EN_CURSO")

# Sin estado: lista todos
def test_opcionesViajes_sinFiltro(sistema, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "FINALIZADO")
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    assert len(sistema.opciones_viajes()) == 2

# ver_impacto_ambiental
def test_verImpactoAmbiental_suma(sistema, contexto, mocker):
    viaje1 = crear_viaje_mock(mocker, contexto)
    viaje2 = crear_viaje_mock(mocker, contexto)
    viaje1.impacto_ambiental.return_value = 10.0
    viaje2.impacto_ambiental.return_value = 5.5
    lineas = sistema.ver_impacto_ambiental()
    assert len(lineas) == 3
    assert "15.50" in lineas[-1]

# Un viaje que no se puede calcular no corta el resto ni suma
def test_verImpactoAmbiental_unViajeFalla(sistema, contexto, mocker):
    viaje1 = crear_viaje_mock(mocker, contexto)
    viaje2 = crear_viaje_mock(mocker, contexto)
    viaje1.impacto_ambiental.side_effect = FlotaError("sin ruta")
    viaje2.impacto_ambiental.return_value = 4.0
    lineas = sistema.ver_impacto_ambiental()
    assert "no se pudo calcular (sin ruta)" in lineas[0]
    assert "4.00" in lineas[-1]

# lugares
def test_lugaresConocidos_ordenados(sistema, contexto):
    contexto[MatrizDistancia].getter_lugares.return_value = {"Palermo", "Centro", "Deposito"}
    assert sistema.lugares_conocidos() == ["Centro", "Deposito", "Palermo"]

def test_lugaresConocidos_matrizVacia(sistema, contexto):
    contexto[MatrizDistancia].getter_lugares.return_value = set()
    with pytest.raises(DatoInvalidoError, match = "matriz está vacía"):
        sistema.lugares_conocidos()

def test_esLugarConocido_delega(sistema, contexto):
    contexto[MatrizDistancia].lugar_conocido.return_value = True
    assert sistema.es_lugar_conocido("Palermo") is True
    contexto[MatrizDistancia].lugar_conocido.assert_called_once_with("Palermo")

# transportes
def test_opcionesTransportes_vacio(sistema):
    with pytest.raises(DatoInvalidoError, match = "ningun transporte"):
        sistema.opciones_transportes()

def test_registrarTransporte_usaLaClaseElegida(sistema, admin, contexto):
    resultado = sistema.registrar_transporte(2)
    admin.crear_transporte.assert_called_once_with(Camion)
    assert contexto[Transporte] == [admin.crear_transporte.return_value]
    assert "TRANSPORTE REGISTRADO" in resultado

def test_registrarTransporte_ordenDeOpciones(sistema, admin):
    sistema.registrar_transporte(0)
    sistema.registrar_transporte(1)
    assert admin.crear_transporte.call_args_list[0].args == (Furgoneta,)
    assert admin.crear_transporte.call_args_list[1].args == (Motocicleta,)

def test_registrarTransporte_opcionInvalida(sistema, admin, contexto):
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.registrar_transporte(3)
    admin.crear_transporte.assert_not_called()
    assert contexto[Transporte] == []

# crear_viaje
def test_crearViaje_ok(sistema, admin, contexto, mocker):
    transporte = mocker.Mock(spec = Transporte)
    contexto[Transporte].append(transporte)
    matriz = contexto[MatrizDistancia]
    matriz.getter_lugares.return_value = {"Deposito"}
    matriz.lugar_conocido.return_value = True
    horario = datetime(2026, 10, 9, 8, 0)
    resultado = sistema.crear_viaje(0, "Deposito", horario)
    admin.crear_viaje.assert_called_once_with(transporte, "Deposito", horario, matriz)
    assert contexto[Viaje] == [admin.crear_viaje.return_value]
    assert "VIAJE CREADO" in resultado

# Depósito que no está en la matriz: no se crea
def test_crearViaje_depositoDesconocido(sistema, admin, contexto, mocker):
    contexto[Transporte].append(mocker.Mock(spec = Transporte))
    contexto[MatrizDistancia].getter_lugares.return_value = {"Deposito"}
    contexto[MatrizDistancia].lugar_conocido.return_value = False
    with pytest.raises(DatoInvalidoError, match = "no es un lugar de la matriz"):
        sistema.crear_viaje(0, "Marte", datetime(2026, 10, 9, 8, 0))
    admin.crear_viaje.assert_not_called()
    assert contexto[Viaje] == []

def test_crearViaje_transporteInvalido(sistema, admin, contexto):
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.crear_viaje(0, "Deposito", datetime(2026, 10, 9, 8, 0))
    admin.crear_viaje.assert_not_called()

def test_crearViaje_matrizVacia(sistema, admin, contexto, mocker):
    contexto[Transporte].append(mocker.Mock(spec = Transporte))
    contexto[MatrizDistancia].getter_lugares.return_value = set()
    with pytest.raises(DatoInvalidoError, match = "matriz está vacía"):
        sistema.crear_viaje(0, "Deposito", datetime(2026, 10, 9, 8, 0))
    admin.crear_viaje.assert_not_called()

# detalle_viaje
def test_detalleViaje_sinParadas(sistema, contexto, mocker):
    viaje = crear_viaje_mock(mocker, contexto)
    viaje.getter_solicitudes.return_value = [mocker.Mock(spec = Solicitud)]
    viaje.getter_paradas.return_value = []
    viaje.distancia_total.return_value = 12.0
    viaje.costo_total.return_value = 300.0
    lineas = sistema.detalle_viaje(0)
    assert "Paradas:" not in lineas
    assert "Distancia total (con regreso al deposito): 12.0 km" in lineas
    assert "Costo total: $300.0" in lineas

def test_detalleViaje_conParadas(sistema, contexto, mocker):
    viaje = crear_viaje_mock(mocker, contexto)
    viaje.getter_solicitudes.return_value = []
    viaje.getter_paradas.return_value = [mocker.Mock(spec = Parada)]
    assert "Paradas:" in sistema.detalle_viaje(0)

# iniciar_viaje
def test_iniciarViaje_agregaParadas(sistema, admin, contexto, mocker):
    parada1 = mocker.Mock(spec = Parada)
    parada2 = mocker.Mock(spec = Parada)
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO", "EN_CURSO")
    viaje.getter_paradas.return_value = [parada1, parada2]
    lineas = sistema.iniciar_viaje(0)
    admin.iniciar_viaje.assert_called_once_with(viaje)
    assert contexto[Parada] == [parada1, parada2]
    assert "EN_CURSO" in lineas[0]

# Si no se puede iniciar, no se agregan paradas
def test_iniciarViaje_fallaNoAgregaParadas(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    admin.iniciar_viaje.side_effect = FlotaError("no hay orden factible")
    with pytest.raises(FlotaError, match = "no hay orden factible"):
        sistema.iniciar_viaje(0)
    assert contexto[Parada] == []

# El viaje tiene que estar planificado
def test_iniciarViaje_estadoIncorrecto(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    with pytest.raises(DatoInvalidoError):
        sistema.iniciar_viaje(0)
    admin.iniciar_viaje.assert_not_called()

# registrar_entrega
def test_registrarEntrega_ok(sistema, admin, contexto, mocker):
    hora = datetime(2026, 10, 9, 10, 0)
    viaje = crear_viaje_mock(mocker, contexto, "EN_CURSO", "EN_CURSO")
    resultado = sistema.registrar_entrega(0, hora, "Juan", 150.0)
    admin.registrar_entrega.assert_called_once_with(viaje, hora, "Juan", 150.0)
    assert contexto[Comprobante] == [admin.registrar_entrega.return_value]
    assert "FINALIZADO" not in resultado

# Al entregar la última parada avisa que el viaje finalizó
def test_registrarEntrega_avisaFinalizado(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO", "FINALIZADO")
    resultado = sistema.registrar_entrega(0, datetime(2026, 10, 9, 10, 0), "Juan", 150.0)
    assert "VIAJE FINALIZADO" in resultado

# Si el administrador rechaza la entrega, no se guarda el comprobante
def test_registrarEntrega_falla(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    admin.registrar_entrega.side_effect = EstadoInvalidoError("registrar_entrega", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError):
        sistema.registrar_entrega(0, datetime(2026, 10, 9, 10, 0), "Juan", 150.0)
    assert contexto[Comprobante] == []

def test_registrarEntrega_viajeNoEnCurso(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    with pytest.raises(DatoInvalidoError):
        sistema.registrar_entrega(0, datetime(2026, 10, 9, 10, 0), "Juan", 150.0)
    admin.registrar_entrega.assert_not_called()

# registrar_incidente: traduce los números a tipo y alcance
def test_registrarIncidente_traduceOpciones(sistema, admin, contexto, mocker):
    fecha = datetime(2026, 10, 9, 10, 0)
    viaje = crear_viaje_mock(mocker, contexto, "EN_CURSO", "EN_CURSO")
    sistema.registrar_incidente(0, 1, fecha, "No estaba", 2)
    admin.registrar_incidente.assert_called_once_with(viaje, "AUSENTE", fecha, "No estaba", "TRANSPORTE")
    assert contexto[Incidente] == [admin.registrar_incidente.return_value]

def test_registrarIncidente_tipoInvalido(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.registrar_incidente(0, 5, datetime(2026, 10, 9, 10, 0), "x", 0)
    admin.registrar_incidente.assert_not_called()
    assert contexto[Incidente] == []

def test_registrarIncidente_alcanceInvalido(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.registrar_incidente(0, 0, datetime(2026, 10, 9, 10, 0), "x", -1)
    admin.registrar_incidente.assert_not_called()

# Las opciones que se muestran tienen la misma cantidad que las que se aceptan
def test_opcionesIncidente_coherentes(sistema):
    assert len(sistema.tipos_incidente()) == len(Sistema.TIPOS_INCIDENTE)
    assert len(sistema.descripciones_alcance()) == len(Sistema.ALCANCES_INCIDENTE)

# ver_matriz
def test_verMatriz(sistema, contexto):
    contexto[MatrizDistancia].getter_distancias.return_value = {("A", "B"): 5.0, ("B", "A"): 7.0}
    assert sistema.ver_matriz() == ["A -> B: 5.0km", "B -> A: 7.0km"]

def test_agregarDistancia_delega(sistema, admin, contexto):
    sistema.agregar_distancia("A", "B", 5.0)
    admin.agregar_distancia.assert_called_once_with(contexto[MatrizDistancia], "A", "B", 5.0)

# deshacer / reasignar
def test_deshacer_guardaLaSolicitud(sistema, admin, contexto, mocker):
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    resultado = sistema.deshacer_ultima_solicitud(0)
    admin.deshacer_ultima_solicitud.assert_called_once_with(viaje)
    assert sistema.getter_solicitud_deshecha() is admin.deshacer_ultima_solicitud.return_value
    assert "Solicitud sacada" in resultado

# Si no se puede deshacer, no queda ninguna solicitud guardada
def test_deshacer_falla(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    admin.deshacer_ultima_solicitud.side_effect = FlotaError("no hay solicitudes")
    with pytest.raises(FlotaError):
        sistema.deshacer_ultima_solicitud(0)
    assert sistema.getter_solicitud_deshecha() is None

def test_reasignar_ok(sistema, admin, contexto, mocker):
    solicitud = mocker.Mock(spec = Solicitud)
    sistema.setter_solicitud_deshecha(solicitud)
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    resultado = sistema.reasignar_solicitud_deshecha(0)
    admin.asignar_solicitud.assert_called_once_with(viaje, solicitud)
    assert sistema.getter_solicitud_deshecha() is None
    assert "Solicitud agregada al viaje" in resultado

def test_reasignar_sinSolicitudDeshecha(sistema, admin, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    with pytest.raises(DatoInvalidoError, match = "No hay ninguna solicitud"):
        sistema.reasignar_solicitud_deshecha(0)
    admin.asignar_solicitud.assert_not_called()

# Si el viaje nuevo la rechaza, no se lanza el error: se avisa y queda pendiente
def test_reasignar_viajeRechaza(sistema, admin, contexto, mocker):
    sistema.setter_solicitud_deshecha(mocker.Mock(spec = Solicitud))
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    admin.asignar_solicitud.side_effect = FlotaError("capacidad excedida")
    resultado = sistema.reasignar_solicitud_deshecha(0)
    assert "capacidad excedida" in resultado
    assert "pendiente de asignación" in resultado
    assert sistema.getter_solicitud_deshecha() is None

def test_descartarSolicitudDeshecha(sistema, mocker):
    sistema.setter_solicitud_deshecha(mocker.Mock(spec = Solicitud))
    assert "pendiente de asignación" in sistema.descartar_solicitud_deshecha()
    assert sistema.getter_solicitud_deshecha() is None

# solicitudes pendientes
def test_opcionesPendientes_soloPendientes(sistema, contexto, mocker):
    asignada = mocker.Mock(spec = Solicitud)
    asignada.esta_pendiente.return_value = False
    pendiente = mocker.Mock(spec = Solicitud)
    pendiente.esta_pendiente.return_value = True
    contexto[Solicitud].extend([asignada, pendiente])
    opciones = sistema.opciones_pendientes()
    assert len(opciones) == 1
    assert opciones[0].startswith("0) ")

def test_opcionesPendientes_ninguna(sistema, contexto, mocker):
    asignada = mocker.Mock(spec = Solicitud)
    asignada.esta_pendiente.return_value = False
    contexto[Solicitud].append(asignada)
    with pytest.raises(DatoInvalidoError, match = "No hay solicitudes pendientes"):
        sistema.opciones_pendientes()

# El índice se refiere a la lista de pendientes, no a todas las solicitudes
def test_asignarSolicitudPendiente_indiceSobrePendientes(sistema, admin, contexto, mocker):
    asignada = mocker.Mock(spec = Solicitud)
    asignada.esta_pendiente.return_value = False
    pendiente1 = mocker.Mock(spec = Solicitud)
    pendiente1.esta_pendiente.return_value = True
    pendiente2 = mocker.Mock(spec = Solicitud)
    pendiente2.esta_pendiente.return_value = True
    contexto[Solicitud].extend([asignada, pendiente1, pendiente2])
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    sistema.asignar_solicitud_pendiente(1, 0)
    admin.asignar_solicitud.assert_called_once_with(viaje, pendiente2)

def test_asignarSolicitudPendiente_indiceInvalido(sistema, admin, contexto, mocker):
    pendiente = mocker.Mock(spec = Solicitud)
    pendiente.esta_pendiente.return_value = True
    contexto[Solicitud].append(pendiente)
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    with pytest.raises(DatoInvalidoError, match = "Numero invalido"):
        sistema.asignar_solicitud_pendiente(1, 0)
    admin.asignar_solicitud.assert_not_called()

# buscar_persona
def test_buscarPersona_encontrada(sistema, mocker):
    persona = mocker.Mock(spec = Persona)
    persona.getter_telefono.return_value = 1122334455
    mocker.patch.object(Persona, "buscar_persona", return_value = (persona, 3))
    lineas = sistema.buscar_persona(12345678)
    assert any(map(lambda l: "PERSONA ENCONTRADA" in l, lineas))
    assert any(map(lambda l: "1122334455" in l, lineas))
    assert any(map(lambda l: l.endswith("3"), lineas))

def test_buscarPersona_noEncontrada(sistema, mocker):
    mocker.patch.object(Persona, "buscar_persona", return_value = (None, 4))
    lineas = sistema.buscar_persona(99999999)
    assert "99999999" in lineas[0]
    assert lineas[1].endswith("4")

# alcanzables_desde_viaje
def test_alcanzablesDesdeViaje_ok(sistema, contexto, mocker):
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    viaje.ultimo_lugar.return_value = "Deposito"
    contexto[MatrizDistancia].alcanzables.return_value = ["Palermo"]
    assert sistema.alcanzables_desde_viaje(0) == ("Deposito", ["Palermo"])
    contexto[MatrizDistancia].alcanzables.assert_called_once_with("Deposito")

def test_alcanzablesDesdeViaje_ninguno(sistema, contexto, mocker):
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    viaje.ultimo_lugar.return_value = "Deposito"
    contexto[MatrizDistancia].alcanzables.return_value = []
    with pytest.raises(DatoInvalidoError, match = "Todavia no hay ninguna distancia cargada desde 'Deposito'"):
        sistema.alcanzables_desde_viaje(0)

# crear_solicitud
def test_crearSolicitud_ok(sistema, solicitante, contexto, mocker):
    inicio = datetime(2026, 10, 9, 9, 0)
    fin = datetime(2026, 10, 9, 12, 0)
    mock_articulo = mocker.patch("sistema.Articulo")
    articulo1 = mocker.Mock(spec = Articulo)
    articulo2 = mocker.Mock(spec = Articulo)
    mock_articulo.side_effect = [articulo1, articulo2]
    contexto[mock_articulo] = []
    viaje = crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    resultado = sistema.crear_solicitud(0, "Palermo", inicio, fin, [("Caja", 2.0, 1.0), ("Sobre", 0.5, 0.1)])
    assert mock_articulo.call_args_list == [mocker.call("Caja", 2.0, 1.0), mocker.call("Sobre", 0.5, 0.1)]
    solicitante.crear_solicitud.assert_called_once_with(viaje, "Palermo", inicio, fin, articulo1, articulo2)
    assert contexto[Solicitud] == [solicitante.crear_solicitud.return_value]
    assert contexto[mock_articulo] == [articulo1, articulo2]
    assert "Solicitud agregada" in resultado

# Si el solicitante no puede crearla, ni la solicitud ni los artículos quedan en el contexto
def test_crearSolicitud_falla(sistema, solicitante, contexto, mocker):
    mock_articulo = mocker.patch("sistema.Articulo")
    contexto[mock_articulo] = []
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    solicitante.crear_solicitud.side_effect = FlotaError("peso excedido")
    with pytest.raises(FlotaError, match = "peso excedido"):
        sistema.crear_solicitud(0, "Palermo", datetime(2026, 10, 9, 9, 0), datetime(2026, 10, 9, 12, 0), [("Caja", 2.0, 1.0)])
    assert contexto[Solicitud] == []
    assert contexto[mock_articulo] == []

# Un artículo inválido corta antes de tocar el viaje
def test_crearSolicitud_articuloInvalido(sistema, solicitante, contexto, mocker):
    mocker.patch("sistema.Articulo", side_effect = DatoInvalidoError("peso inválido"))
    crear_viaje_mock(mocker, contexto, "PLANIFICADO")
    with pytest.raises(DatoInvalidoError, match = "peso inválido"):
        sistema.crear_solicitud(0, "Palermo", datetime(2026, 10, 9, 9, 0), datetime(2026, 10, 9, 12, 0), [("Caja", -1.0, 1.0)])
    solicitante.crear_solicitud.assert_not_called()

def test_crearSolicitud_viajeNoPlanificado(sistema, solicitante, contexto, mocker):
    crear_viaje_mock(mocker, contexto, "EN_CURSO")
    with pytest.raises(DatoInvalidoError):
        sistema.crear_solicitud(0, "Palermo", datetime(2026, 10, 9, 9, 0), datetime(2026, 10, 9, 12, 0), [("Caja", 2.0, 1.0)])
    solicitante.crear_solicitud.assert_not_called()
