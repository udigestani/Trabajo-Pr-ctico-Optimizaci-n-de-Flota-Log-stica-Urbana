import pytest
import re
from datetime import datetime
from persona import Persona, Administrador
from viaje import Viaje
from transporte import Transporte
from matrizdistancia import MatrizDistancia
from transporte import Furgoneta
from solicitud import Solicitud
from parada import Parada
from comprobante import Comprobante
from incidente import Incidente
from excepciones import (DatoInvalidoError, DNIInvalidoError, EstadoInvalidoError, ViajeVacioError, SinParadasPendientesError,
                         VentanaIncumplidaError, VentanaInvalidaError, RutaIncompletaError)


@pytest.fixture(autouse=True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

@pytest.fixture
def admin():
    return Administrador("Juan", 12345678, 1122334455)

@pytest.fixture
def mock_transporte(mocker):
    return mocker.Mock(spec = Transporte)

@pytest.fixture
def mock_matriz(mocker):
    return mocker.Mock(spec = MatrizDistancia)

@pytest.fixture
def horario():
    return datetime(2026, 10, 9, 8, 0)

# Funcionamiento normal
def test_admin_ok(admin):
    assert admin.getter_nombre() == "Juan"
    assert admin.getter_dni() == 12345678
    assert admin.getter_telefono() == 1122334455
    assert isinstance(admin, Administrador)
    assert isinstance(admin, Persona)
    assert issubclass(Administrador, Persona)
    arbol = Persona.getter_dnis_registrados()
    assert arbol.buscar(arbol.getter_raiz(), 12345678) is admin
    assert str(admin) == "Administrador de nombre Juan y DNI: 12345678"
    assert repr(admin) == "<Persona Juan - 12345678>"

# DNIInvalidoError si el DNI ya está registrado
def test_admin_dniRepetido(admin):
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Administrador("Uriel", 12345678, 1155556666)

# # Datos invalidos
# def test_admin_datosInvalidos():
#     with pytest.raises(DatoInvalidoError, match = "El nombre no debe estar vacío"):
#         Administrador("      ", 12345678, 1122334455)
#     with pytest.raises(DatoInvalidoError, match = "El DNI 123 debe ser un número entero positivo de 7 o 8 dígitos"):
#         Administrador("Ana", 123, 1122334455)
#     with pytest.raises(DatoInvalidoError, match = "El teléfono 112233 debe ser un número entero positivo de 10 dígitos"):
#         Administrador("Ana", 12345678, 112233)
# VA PARA PERSONA

def test_crearViaje_ok(admin, mock_transporte, mock_matriz, horario):
    viaje = admin.crear_viaje(mock_transporte, "Deposito", horario, mock_matriz)
    assert isinstance(viaje, Viaje)
    assert viaje.getter_transporte() is mock_transporte
    assert viaje.getter_deposito() == "Deposito"
    assert viaje.getter_horario() == horario
    assert viaje.getter_matriz() is mock_matriz
    assert viaje.getter_estado() == "PLANIFICADO"
    assert viaje.getter_solicitudes() == viaje.getter_incidentes() == viaje.getter_paradas() == []
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0

def test_crearViaje_dosViajes(admin, mock_transporte, mock_matriz, horario):
    viaje1 = admin.crear_viaje(mock_transporte, "Deposito", horario, mock_matriz)
    viaje2 = admin.crear_viaje(mock_transporte, "Deposito", horario, mock_matriz)
    assert viaje1 is not viaje2
    assert viaje1.getter_id() != viaje2.getter_id()

def test_crearViaje_datosInvalidos(admin, mock_transporte, mock_matriz, horario):
    # transporte invalido
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Transporte"):
        admin.crear_viaje("camion", "Deposito", horario, mock_matriz)
    # deposito invalido
    with pytest.raises(DatoInvalidoError, match = "El depósito no debe estar vacío"):
        admin.crear_viaje(mock_transporte, "      ", horario, mock_matriz)
    # horario invalido
    with pytest.raises(TypeError, match = "debe ser un objeto datetime"):
        admin.crear_viaje(mock_transporte, "Deposito", "8:00", mock_matriz)
    # matriz invalida
    matriz = {("Deposito", "D1"): 10}
    with pytest.raises(TypeError, match = "debe ser un objeto de clase MatrizDistancia"):
        admin.crear_viaje(mock_transporte, "Deposito", horario, matriz)


def hora(horas, minutos = 0):
    return datetime(2026, 10, 11, horas, minutos)

HORARIO = hora(9)

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("persona.Validaciones")
    mock.validar_instancia.side_effect = lambda valor, **kwargs: valor
    mock.validar_en.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def mock_viaje(mocker):
    return mocker.Mock(spec = Viaje)

@pytest.fixture
def solicitud_a(mocker):
    return mocker.Mock(spec = Solicitud)

@pytest.fixture
def solicitud_b(mocker):
    return mocker.Mock(spec = Solicitud)

@pytest.fixture
def solicitud_c(mocker):
    return mocker.Mock(spec = Solicitud)

@pytest.fixture
def parada_1(mocker, solicitud_a):
    mock = mocker.Mock(spec = Parada)
    mock.getter_solicitud.return_value = solicitud_a
    return mock

@pytest.fixture
def parada_2(mocker):
    return mocker.Mock(spec = Parada)

@pytest.fixture
def comprobante(mocker):
    return mocker.Mock(spec = Comprobante)

@pytest.fixture
def incidente(mocker):
    return mocker.Mock(spec = Incidente)

# Por defecto las políticas sugieren el orden de carga: A, B
@pytest.fixture
def mock_vecinos(mocker, solicitud_a, solicitud_b):
    mock = mocker.patch("persona.Vecinos")
    mock.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    return mock

@pytest.fixture
def mock_ventanas(mocker, solicitud_a, solicitud_b):
    mock = mocker.patch("persona.VentanasTiempo")
    mock.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    return mock

@pytest.fixture
def mock_parada_clase(mocker, parada_1, parada_2):
    mock = mocker.patch("persona.Parada")
    mock.side_effect = [parada_1, parada_2]
    return mock

@pytest.fixture
def mock_incidente_clase(mocker, incidente):
    mock = mocker.patch("persona.Incidente")
    mock.return_value = incidente
    return mock

@pytest.fixture
def mock_ordenar_solicitudes(mocker, solicitud_a, solicitud_b):
    return mocker.patch.object(Administrador, "ordenar_solicitudes", return_value = [solicitud_a, solicitud_b])

# Viaje con tres solicitudes cargadas: A, B, C
@pytest.fixture
def viaje_a_ordenar(mock_viaje, mock_matriz, solicitud_a, solicitud_b, solicitud_c):
    mock_viaje.getter_solicitudes.return_value = [solicitud_a, solicitud_b, solicitud_c]
    mock_viaje.getter_deposito.return_value = "Deposito"
    mock_viaje.getter_matriz.return_value = mock_matriz
    return mock_viaje

# Viaje en curso: la parada actual es parada_1
@pytest.fixture
def viaje_en_curso(mock_viaje, parada_1):
    mock_viaje.parada_actual.return_value = parada_1
    return mock_viaje


# ---------- ordenar_solicitudes ----------
# Funcionamiento normal
def test_ordenarSolicitudes_ok(viaje_a_ordenar, mock_vecinos, mock_ventanas, mock_matriz, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    # Gana solicitudes
    viaje_a_ordenar.costo_total.side_effect = [100, 150, 200]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_a, solicitud_b, solicitud_c]
    mock_vecinos.sugerir_orden.assert_called_once_with("Deposito", [solicitud_a, solicitud_b, solicitud_c], mock_matriz)
    mock_ventanas.sugerir_orden.assert_called_once_with("Deposito", [solicitud_a, solicitud_b, solicitud_c], mock_matriz)
    assert viaje_a_ordenar.validar_recorrido.call_count == 3
    viaje_a_ordenar.validar_recorrido.assert_any_call([solicitud_a, solicitud_b, solicitud_c])
    viaje_a_ordenar.validar_recorrido.assert_any_call((solicitud_b, solicitud_c, solicitud_a))
    viaje_a_ordenar.validar_recorrido.assert_any_call((solicitud_c, solicitud_a, solicitud_b))
    assert viaje_a_ordenar.costo_total.call_count == 3
    # Gana vecinos
    viaje_a_ordenar.costo_total.side_effect = [150, 100, 200]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_b, solicitud_c, solicitud_a]
    # Gana ventanas
    viaje_a_ordenar.costo_total.side_effect = [150, 200, 100]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_c, solicitud_a, solicitud_b]

def test_ordenarSolicitudes_noModificaElViaje(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.costo_total.side_effect = [150, 100, 200]
    Administrador.ordenar_solicitudes(viaje_a_ordenar)
    viaje_a_ordenar.comenzar.assert_not_called()
    viaje_a_ordenar.agregar_incidente.assert_not_called()

def test_ordenarSolicitudes_empate(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.costo_total.return_value = 100
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_a, solicitud_b, solicitud_c]

def test_ordenarSolicitudes_vecinosVentanaIncumplida(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.validar_recorrido.side_effect = [True, VentanaIncumplidaError("Destino A", hora(10, 30), hora(10, 20)), True]
    viaje_a_ordenar.costo_total.side_effect = [100, 90]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_c, solicitud_a, solicitud_b]
    assert viaje_a_ordenar.validar_recorrido.call_count == 3
    assert viaje_a_ordenar.costo_total.call_count == 2

def test_ordenarSolicitudes_ventanasVentanaIncumplida(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.validar_recorrido.side_effect = [True, True, VentanaIncumplidaError("Destino A", hora(10, 30), hora(10, 20))]
    viaje_a_ordenar.costo_total.side_effect = [100, 90]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_b, solicitud_c, solicitud_a]
    assert viaje_a_ordenar.validar_recorrido.call_count == 3
    assert viaje_a_ordenar.costo_total.call_count == 2

def test_ordenarSolicitudes_vecinosRutaIncompleta(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.side_effect = RutaIncompletaError("Destino B", "Destino A")
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.costo_total.side_effect = [100, 90]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_c, solicitud_a, solicitud_b]
    assert viaje_a_ordenar.validar_recorrido.call_count == 2
    viaje_a_ordenar.validar_recorrido.assert_any_call([solicitud_a, solicitud_b, solicitud_c])
    viaje_a_ordenar.validar_recorrido.assert_any_call((solicitud_c, solicitud_a, solicitud_b))

def test_ordenarSolicitudes_ventanasRutaIncompleta(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.side_effect = RutaIncompletaError("Destino B", "Destino A")
    viaje_a_ordenar.costo_total.side_effect = [100, 90]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_b, solicitud_c, solicitud_a]

def test_ordenarSolicitudes_vecinosYVentanaFallan(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.side_effect = RutaIncompletaError("Deposito", "Destino B")
    mock_ventanas.sugerir_orden.side_effect = RutaIncompletaError("Deposito", "Destino B")
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_a, solicitud_b, solicitud_c]
    viaje_a_ordenar.validar_recorrido.assert_called_once_with([solicitud_a, solicitud_b, solicitud_c])

def test_ordenarSolicitudes_validarRecorridoFalla_sePropaga(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.validar_recorrido.side_effect = VentanaIncumplidaError("Destino A", hora(10, 30), hora(10, 20))
    with pytest.raises(VentanaIncumplidaError):
        Administrador.ordenar_solicitudes(viaje_a_ordenar)
    assert viaje_a_ordenar.validar_recorrido.call_count == 3

def test_ordenarSolicitudes_ordenActualRutaIncompleta_ganaPolitica(viaje_a_ordenar, mock_vecinos, mock_ventanas, solicitud_a, solicitud_b, solicitud_c):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_c, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_c, solicitud_a, solicitud_b]
    viaje_a_ordenar.costo_total.side_effect = [RutaIncompletaError("Deposito", "Destino A"), 90, 110]
    assert Administrador.ordenar_solicitudes(viaje_a_ordenar) == [solicitud_b, solicitud_c, solicitud_a]

def test_ordenarSolicitudes_ordenActualRutaIncompleta_politicasFallan_sePropaga(viaje_a_ordenar, mock_vecinos, mock_ventanas):
    viaje_a_ordenar.costo_total.side_effect = RutaIncompletaError("Deposito", "Destino A")
    mock_vecinos.sugerir_orden.side_effect = RutaIncompletaError("Deposito", "Destino B")
    mock_ventanas.sugerir_orden.side_effect = RutaIncompletaError("Deposito", "Destino B")
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Deposito a Destino A"):
        Administrador.ordenar_solicitudes(viaje_a_ordenar)

def test_ordenarSolicitudes_ordenActualRutaIncompleta_recorridosInvalidos_sePropaga(viaje_a_ordenar, mock_vecinos, mock_ventanas):
    viaje_a_ordenar.costo_total.side_effect = RutaIncompletaError("Deposito", "Destino A")
    viaje_a_ordenar.validar_recorrido.side_effect = [True, VentanaIncumplidaError("Destino A", hora(11), hora(10, 45)), VentanaIncumplidaError("Destino A", hora(11), hora(10, 45))]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Deposito a Destino A"):
        Administrador.ordenar_solicitudes(viaje_a_ordenar)
    assert viaje_a_ordenar.validar_recorrido.call_count == 3


# ---------- iniciar_viaje ----------
# Funcionamiento normal
def test_iniciarViaje_ok(mock_viaje, mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase, parada_1, parada_2, solicitud_a, solicitud_b):
    mock_viaje.getter_solicitudes.return_value = [solicitud_a, solicitud_b]
    mock_viaje.calcular_horarios.return_value = [hora(9, 30), hora(10, 30)]
    assert Administrador.iniciar_viaje(mock_viaje) is None
    mock_validaciones.validar_instancia.assert_called_once_with(mock_viaje, clase = Viaje, nombre = "viaje")
    mock_viaje.validar_estado.assert_called_once_with("iniciar_viaje", "PLANIFICADO")
    mock_ordenar_solicitudes.assert_called_once_with(mock_viaje)
    mock_viaje.calcular_horarios.assert_called_once_with([solicitud_a, solicitud_b])
    assert mock_parada_clase.call_count == 2
    mock_parada_clase.assert_any_call(orden = 1, solicitud = solicitud_a, hora_prev = hora(9, 30), hora_real = None)
    mock_parada_clase.assert_any_call(orden = 2, solicitud = solicitud_b, hora_prev = hora(10, 30), hora_real = None)
    mock_viaje.comenzar.assert_called_once_with([solicitud_a, solicitud_b], [parada_1, parada_2])
# Usa el orden de ordenar_solicitudes
def test_iniciarViaje_ordenInverso(mock_viaje, mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase, parada_1, parada_2, solicitud_a, solicitud_b):
    mock_viaje.getter_solicitudes.return_value = [solicitud_a, solicitud_b]
    mock_ordenar_solicitudes.return_value = [solicitud_b, solicitud_a]
    mock_viaje.calcular_horarios.return_value = [hora(10, 30), hora(11)]
    Administrador.iniciar_viaje(mock_viaje)
    mock_viaje.calcular_horarios.assert_called_once_with([solicitud_b, solicitud_a])
    mock_parada_clase.assert_any_call(orden = 1, solicitud = solicitud_b, hora_prev = hora(10, 30), hora_real = None)
    mock_parada_clase.assert_any_call(orden = 2, solicitud = solicitud_a, hora_prev = hora(11), hora_real = None)
    mock_viaje.comenzar.assert_called_once_with([solicitud_b, solicitud_a], [parada_1, parada_2])
# No es un Viaje
def test_iniciarViaje_noEsViaje_sePropaga(mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase):
    mock_validaciones.validar_instancia.side_effect = TypeError("El viaje debe ser un objeto de clase Viaje")
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        Administrador.iniciar_viaje("viaje")
    mock_ordenar_solicitudes.assert_not_called()
    mock_parada_clase.assert_not_called()
# Estado inválido se propaga
def test_iniciarViaje_estadoInvalido_sePropaga(mock_viaje, mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase):
    mock_viaje.validar_estado.side_effect = EstadoInvalidoError("iniciar_viaje", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede iniciar_viaje porque el estado es EN_CURSO"):
        Administrador.iniciar_viaje(mock_viaje)
    mock_ordenar_solicitudes.assert_not_called()
    mock_parada_clase.assert_not_called()
    mock_viaje.comenzar.assert_not_called()
# ViajeVacio error
def test_iniciarViaje_viajeVacio(mock_viaje, mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase):
    mock_viaje.getter_solicitudes.return_value = []
    with pytest.raises(ViajeVacioError, match = "Viaje Vacio: El viaje aún no tiene solicitudes"):
        Administrador.iniciar_viaje(mock_viaje)
    mock_ordenar_solicitudes.assert_not_called()
    mock_parada_clase.assert_not_called()
    mock_viaje.comenzar.assert_not_called()
# Ningún orden es factible: el error de ordenar_solicitudes se propaga y el viaje no comienza
def test_iniciarViaje_ordenInviable_sePropaga(mock_viaje, mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase, solicitud_a, solicitud_b):
    mock_viaje.getter_solicitudes.return_value = [solicitud_a, solicitud_b]
    mock_ordenar_solicitudes.side_effect = VentanaIncumplidaError("Destino A", hora(10, 30), hora(10, 20))
    with pytest.raises(VentanaIncumplidaError):
        Administrador.iniciar_viaje(mock_viaje)
    mock_viaje.calcular_horarios.assert_not_called()
    mock_parada_clase.assert_not_called()
    mock_viaje.comenzar.assert_not_called()
# Éste error no debería suceder nunca. Pero si cambiamos el proyecto, para que no se vayan validando las solicitudes cuando se agregan, y se valida solo al inicio el viaje, entonces en ese caso ésto es útil
def test_iniciarViaje_tramoFaltante_sePropaga(mock_viaje, mock_validaciones, mock_ordenar_solicitudes, mock_parada_clase, solicitud_a, solicitud_b):
    mock_viaje.getter_solicitudes.return_value = [solicitud_a, solicitud_b]
    mock_viaje.calcular_horarios.side_effect = RutaIncompletaError("Deposito", "Destino A")
    with pytest.raises(RutaIncompletaError):
        Administrador.iniciar_viaje(mock_viaje)
    mock_parada_clase.assert_not_called()
    mock_viaje.comenzar.assert_not_called()


# ---------- registrar_entrega ----------
# Funcionamiento normal
def test_registrarEntrega_ok(viaje_en_curso, mock_validaciones, parada_1, comprobante):
    parada_1.generar_comprobante.return_value = comprobante
    resultado = Administrador.registrar_entrega(viaje_en_curso, hora(9, 35), "Juan", 100)
    assert resultado is comprobante
    mock_validaciones.validar_instancia.assert_called_once_with(viaje_en_curso, clase = Viaje, nombre = "viaje")
    viaje_en_curso.parada_actual.assert_called_once_with("registrar_entrega")
    viaje_en_curso.validar_hora_resolucion.assert_called_once_with(hora(9, 35), "fecha de entrega")
    parada_1.generar_comprobante.assert_called_once_with("Juan", hora(9, 35), 100)
    viaje_en_curso.cerrar_parada_actual.assert_called_once_with()
# No es un Viaje
def test_registrarEntrega_noEsViaje_sePropaga(viaje_en_curso, mock_validaciones, parada_1):
    mock_validaciones.validar_instancia.side_effect = TypeError("El viaje debe ser un objeto de clase Viaje")
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        Administrador.registrar_entrega("viaje", hora(9, 35), "Juan", 100)
    viaje_en_curso.parada_actual.assert_not_called()
    parada_1.generar_comprobante.assert_not_called()
# Estado inválido se propaga
def test_registrarEntrega_estadoInvalido_sePropaga(viaje_en_curso, mock_validaciones, parada_1):
    viaje_en_curso.parada_actual.side_effect = EstadoInvalidoError("registrar_entrega", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es PLANIFICADO"):
        Administrador.registrar_entrega(viaje_en_curso, hora(10), "Juan", 100)
    viaje_en_curso.validar_hora_resolucion.assert_not_called()
    parada_1.generar_comprobante.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# sin paradas pendientes
def test_registrarEntrega_sinParadasPendientes(viaje_en_curso, mock_validaciones, parada_1):
    viaje_en_curso.parada_actual.side_effect = SinParadasPendientesError("registrar_entrega")
    with pytest.raises(SinParadasPendientesError, match = "Sin paradas pendientes: No se puede registrar_entrega"):
        Administrador.registrar_entrega(viaje_en_curso, hora(10), "Massimo", 100)
    parada_1.generar_comprobante.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# Ventana inválida
def test_registrarEntrega_ventanaInvalida_sePropaga(viaje_en_curso, mock_validaciones, parada_1):
    viaje_en_curso.validar_hora_resolucion.side_effect = VentanaInvalidaError(HORARIO, hora(8), "fecha de la parada previa", "fecha de entrega")
    with pytest.raises(VentanaInvalidaError, match = re.escape("La fecha de la parada previa (2026-10-11 09:00:00) debe ser anterior a la fecha de entrega (2026-10-11 08:00:00)")):
        Administrador.registrar_entrega(viaje_en_curso, hora(8), "Manuel", 100)
    viaje_en_curso.validar_hora_resolucion.assert_called_once_with(hora(8), "fecha de entrega")
    parada_1.generar_comprobante.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# comprobanteInvalido se propaga
def test_registrarEntrega_comprobanteInvalido_sePropaga(viaje_en_curso, mock_validaciones, parada_1):
    parada_1.generar_comprobante.side_effect = DatoInvalidoError("El receptor no debe estar vacío")
    with pytest.raises(DatoInvalidoError, match = "El receptor no debe estar vacío"):
        Administrador.registrar_entrega(viaje_en_curso, hora(9, 35), "   ", 1500)
    viaje_en_curso.cerrar_parada_actual.assert_not_called()


# ---------- registrar_incidente ----------
# Funcionamiento normal (alcance por defecto: FALLA)
def test_registrarIncidente_ok(viaje_en_curso, mock_validaciones, mock_incidente_clase, incidente, parada_1, solicitud_a):
    resultado = Administrador.registrar_incidente(viaje_en_curso, "DAÑO", hora(9, 40), "Pinchazo", rueda = "delantera", costo = 500)
    assert resultado is incidente
    mock_validaciones.validar_instancia.assert_called_once_with(viaje_en_curso, clase = Viaje, nombre = "viaje")
    viaje_en_curso.parada_actual.assert_called_once_with("registrar_incidente")
    mock_validaciones.validar_en.assert_called_once_with("FALLA", opciones = ("FALLA", "SOLICITUD", "TRANSPORTE"), nombre = "alcance del incidente")
    viaje_en_curso.validar_hora_resolucion.assert_called_once_with(hora(9, 40), "fecha del incidente")
    mock_incidente_clase.assert_called_once_with("DAÑO", hora(9, 40), "Pinchazo", solicitud_a, rueda = "delantera", costo = 500)
    viaje_en_curso.agregar_incidente.assert_called_once_with(incidente)
    parada_1.setter_estado.assert_called_once_with("FALLIDA")
    parada_1.setter_hora_real.assert_called_once_with(hora(9, 40))
    parada_1.generar_comprobante.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_called_once_with()
# alcance FALLA explícito se comporta igual que sin pasar alcance
def test_registrarIncidente_alcanceFalla(viaje_en_curso, mock_validaciones, mock_incidente_clase, incidente, parada_1, solicitud_a):
    resultado = Administrador.registrar_incidente(viaje_en_curso, "AUSENTE", hora(9, 40), "No había nadie", alcance = "FALLA")
    assert resultado is incidente
    mock_validaciones.validar_en.assert_called_once_with("FALLA", opciones = ("FALLA", "SOLICITUD", "TRANSPORTE"), nombre = "alcance del incidente")
    mock_incidente_clase.assert_called_once_with("AUSENTE", hora(9, 40), "No había nadie", solicitud_a)
    parada_1.setter_estado.assert_called_once_with("FALLIDA")
    parada_1.setter_hora_real.assert_called_once_with(hora(9, 40))
    viaje_en_curso.cerrar_parada_actual.assert_called_once_with()
# alcance SOLICITUD: el afectado es la solicitud y la parada sigue pendiente
def test_registrarIncidente_alcanceSolicitud(viaje_en_curso, mock_validaciones, mock_incidente_clase, incidente, parada_1, solicitud_a):
    resultado = Administrador.registrar_incidente(viaje_en_curso, "DAÑO", hora(9, 40), "Caja rota", alcance = "SOLICITUD")
    assert resultado is incidente
    mock_incidente_clase.assert_called_once_with("DAÑO", hora(9, 40), "Caja rota", solicitud_a)
    viaje_en_curso.agregar_incidente.assert_called_once_with(incidente)
    parada_1.setter_estado.assert_not_called()
    parada_1.setter_hora_real.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# alcance TRANSPORTE: el afectado es el transporte del viaje y no se modifican las paradas
def test_registrarIncidente_alcanceTransporte(viaje_en_curso, mock_validaciones, mock_incidente_clase, incidente, parada_1, mock_transporte):
    viaje_en_curso.getter_transporte.return_value = mock_transporte
    resultado = Administrador.registrar_incidente(viaje_en_curso, "RETRASO", hora(9, 40), "Pinchazo", alcance = "TRANSPORTE")
    assert resultado is incidente
    mock_incidente_clase.assert_called_once_with("RETRASO", hora(9, 40), "Pinchazo", mock_transporte)
    viaje_en_curso.agregar_incidente.assert_called_once_with(incidente)
    parada_1.getter_solicitud.assert_not_called()
    parada_1.setter_estado.assert_not_called()
    parada_1.setter_hora_real.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# No es un Viaje
def test_registrarIncidente_noEsViaje_sePropaga(viaje_en_curso, mock_validaciones, mock_incidente_clase):
    mock_validaciones.validar_instancia.side_effect = TypeError("El viaje debe ser un objeto de clase Viaje")
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        Administrador.registrar_incidente("viaje", "DAÑO", hora(10), "Pinchazo")
    viaje_en_curso.parada_actual.assert_not_called()
    mock_incidente_clase.assert_not_called()
# Estado inválido error se propaga
def test_registrarIncidente_estadoInvalido_sePropaga(viaje_en_curso, mock_validaciones, mock_incidente_clase):
    viaje_en_curso.parada_actual.side_effect = EstadoInvalidoError("registrar_incidente", "PLANIFICADO")
    for alcance in ("FALLA", "SOLICITUD", "TRANSPORTE"):
        with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_incidente porque el estado es PLANIFICADO"):
            Administrador.registrar_incidente(viaje_en_curso, "DAÑO", hora(10), "Pinchazo", alcance = alcance)
    mock_validaciones.validar_en.assert_not_called()
    viaje_en_curso.validar_hora_resolucion.assert_not_called()
    mock_incidente_clase.assert_not_called()
    viaje_en_curso.agregar_incidente.assert_not_called()
# Sin paradas pendientes
def test_registrarIncidente_sinParadasPendientes(viaje_en_curso, mock_validaciones, mock_incidente_clase):
    viaje_en_curso.parada_actual.side_effect = SinParadasPendientesError("registrar_incidente")
    with pytest.raises(SinParadasPendientesError, match = "Sin paradas pendientes: No se puede registrar_incidente"):
        Administrador.registrar_incidente(viaje_en_curso, "DAÑO", hora(10), "Pinchazo")
    mock_incidente_clase.assert_not_called()
    viaje_en_curso.agregar_incidente.assert_not_called()
# Alcance inválido
def test_registrarIncidente_alcanceInvalido_sePropaga(viaje_en_curso, mock_validaciones, mock_incidente_clase, parada_1):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("El alcance del incidente CHOQUE debe ser uno de: FALLA, SOLICITUD, TRANSPORTE")
    with pytest.raises(DatoInvalidoError, match = "El alcance del incidente CHOQUE debe ser uno de: FALLA, SOLICITUD, TRANSPORTE"):
        Administrador.registrar_incidente(viaje_en_curso, "DAÑO", hora(9, 40), "Pinchazo", alcance = "CHOQUE")
    viaje_en_curso.validar_hora_resolucion.assert_not_called()
    mock_incidente_clase.assert_not_called()
    viaje_en_curso.agregar_incidente.assert_not_called()
    parada_1.setter_estado.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# Ventana inválida error se propaga
def test_registrarIncidente_anteriorALaSalida_sePropaga(viaje_en_curso, mock_validaciones, mock_incidente_clase, parada_1):
    viaje_en_curso.validar_hora_resolucion.side_effect = VentanaInvalidaError(HORARIO, hora(8), "fecha de salida del viaje", "fecha del incidente")
    for alcance in ("FALLA", "SOLICITUD", "TRANSPORTE"):
        with pytest.raises(VentanaInvalidaError, match = re.escape("La fecha de salida del viaje (2026-10-11 09:00:00) debe ser anterior a la fecha del incidente (2026-10-11 08:00:00)")):
            Administrador.registrar_incidente(viaje_en_curso, "DAÑO", hora(8), "Pinchazo", alcance = alcance)
    mock_incidente_clase.assert_not_called()
    viaje_en_curso.agregar_incidente.assert_not_called()
    parada_1.setter_estado.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()
# Incidente inválido se propaga
def test_registrarIncidente_incidenteInvalido_sePropaga(viaje_en_curso, mock_validaciones, mock_incidente_clase, parada_1):
    mock_incidente_clase.side_effect = DatoInvalidoError("El tipo debe ser uno de: DAÑO, AUSENTE, RETRASO")
    with pytest.raises(DatoInvalidoError, match = "El tipo debe ser uno de: DAÑO, AUSENTE, RETRASO"):
        Administrador.registrar_incidente(viaje_en_curso, "CHOQUE", hora(9, 40), "Pinchazo")
    viaje_en_curso.agregar_incidente.assert_not_called()
    parada_1.setter_estado.assert_not_called()
    parada_1.setter_hora_real.assert_not_called()
    viaje_en_curso.cerrar_parada_actual.assert_not_called()


# ---------- crear_transporte ----------
# Funcionamiento normal
def test_crearTransporte_ok(mocker):
    clase = mocker.Mock()
    assert Administrador.crear_transporte(clase) is clase.return_value
    clase.assert_called_once_with()
def test_crearTransporte_furgoneta():
    transporte = Administrador.crear_transporte(Furgoneta)
    assert isinstance(transporte, Furgoneta)
# El error de la clase se propaga
def test_crearTransporte_errorSePropaga(mocker):
    clase = mocker.Mock(side_effect = DatoInvalidoError("peso_max inválido"))
    with pytest.raises(DatoInvalidoError, match = "peso_max inválido"):
        Administrador.crear_transporte(clase)


# ---------- agregar_distancia ----------
# Funcionamiento normal
def test_agregarDistancia_ok(mock_matriz):
    assert Administrador.agregar_distancia(mock_matriz, "Deposito", "Destino 1", 5) is None
    mock_matriz.agregar_distancia.assert_called_once_with("Deposito", "Destino 1", 5)
# Distancia inválida se propaga
def test_agregarDistancia_distanciaInvalida_sePropaga(mock_matriz):
    mock_matriz.agregar_distancia.side_effect = DatoInvalidoError("La distancia no puede ser negativa")
    with pytest.raises(DatoInvalidoError, match = "La distancia no puede ser negativa"):
        Administrador.agregar_distancia(mock_matriz, "Deposito", "Destino 1", -1)


# ---------- asignar_solicitud ----------
# Funcionamiento normal
def test_asignarSolicitud_ok(mock_viaje, mock_validaciones, solicitud_a):
    assert Administrador.asignar_solicitud(mock_viaje, solicitud_a) is None
    mock_validaciones.validar_instancia.assert_called_once_with(mock_viaje, clase = Viaje, nombre = "viaje")
    mock_viaje.agregar_solicitud.assert_called_once_with(solicitud_a)
# No es un Viaje
def test_asignarSolicitud_noEsViaje_sePropaga(mock_viaje, mock_validaciones, solicitud_a):
    mock_validaciones.validar_instancia.side_effect = TypeError("El viaje debe ser un objeto de clase Viaje")
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        Administrador.asignar_solicitud("viaje", solicitud_a)
    mock_viaje.agregar_solicitud.assert_not_called()
# El viaje rechaza la solicitud
def test_asignarSolicitud_viajeRechaza_sePropaga(mock_viaje, mock_validaciones, solicitud_a):
    mock_viaje.agregar_solicitud.side_effect = VentanaIncumplidaError("Destino A", hora(11), hora(10))
    with pytest.raises(VentanaIncumplidaError):
        Administrador.asignar_solicitud(mock_viaje, solicitud_a)


# ---------- deshacer_ultima_solicitud ----------
# Funcionamiento normal
def test_deshacerUltimaSolicitud_ok(mock_viaje, mock_validaciones, solicitud_a):
    mock_viaje.deshacer_ultima_solicitud.return_value = solicitud_a
    assert Administrador.deshacer_ultima_solicitud(mock_viaje) is solicitud_a
    mock_validaciones.validar_instancia.assert_called_once_with(mock_viaje, clase = Viaje, nombre = "viaje")
    mock_viaje.deshacer_ultima_solicitud.assert_called_once_with()
# No es un Viaje
def test_deshacerUltimaSolicitud_noEsViaje_sePropaga(mock_viaje, mock_validaciones):
    mock_validaciones.validar_instancia.side_effect = TypeError("El viaje debe ser un objeto de clase Viaje")
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        Administrador.deshacer_ultima_solicitud("viaje")
    mock_viaje.deshacer_ultima_solicitud.assert_not_called()
# Viaje sin solicitudes
def test_deshacerUltimaSolicitud_sinSolicitudes_sePropaga(mock_viaje, mock_validaciones):
    mock_viaje.deshacer_ultima_solicitud.side_effect = ViajeVacioError("Viaje Vacio: No hay solicitudes para deshacer")
    with pytest.raises(ViajeVacioError, match = "No hay solicitudes para deshacer"):
        Administrador.deshacer_ultima_solicitud(mock_viaje)


# ---------- serializar ----------
def test_admin_serializar(admin):
    assert admin.serializar() == ["Administrador", "Juan", 12345678, 1122334455]
