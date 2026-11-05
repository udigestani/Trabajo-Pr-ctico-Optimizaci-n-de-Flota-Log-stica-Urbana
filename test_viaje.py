import pytest
from datetime import datetime
import re
from viaje import Viaje
from solicitud import Solicitud
from parada import Parada
from cola import Cola
from itertools import chain
from comprobante import Comprobante
from incidente import Incidente
from transporte import Transporte
from matrizdistancia import MatrizDistancia
from excepciones import (DatoInvalidoError, ExcesoPesoError, ExcesoVolumenError, VentanaIncumplidaError, RutaIncompletaError,
                         EstadoInvalidoError, ViajeVacioError, SinParadasPendientesError, ViajeIncompletoError,
                         SolicitudDuplicadaError, TransicionIlegalError, VentanaInvalidaError)

def hora(horas, minutos = 0):
    return datetime(2026, 10, 11, horas, minutos)

HORARIO = hora(9)
# Km dirigidos entre ubicaciones (la matriz real se reemplaza por un mock que lee este dict)
DISTANCIAS = {("Deposito", "Deposito"): 0,
              ("Deposito", "Destino A"): 15, ("Destino A", "Deposito"): 15,
              ("Deposito", "Destino B"): 25, ("Destino B", "Deposito"): 25,
              ("Destino A", "Destino B"): 10, ("Destino B", "Destino A"): 10}

def distancia_falsa(origen, destino):
    if (origen, destino) not in DISTANCIAS:
        raise RutaIncompletaError(origen, destino)
    return DISTANCIAS[(origen, destino)]

@pytest.fixture(autouse = True)
def resetearId():
    Viaje.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("viaje.Validaciones")
    mock.validar_instancia.side_effect = lambda valor, **kwargs: valor
    mock.validar_str.side_effect = lambda valor, **kwargs: valor
    mock.validar_fecha.side_effect = lambda valor, **kwargs: valor
    mock.validar_en.side_effect = lambda valor, **kwargs: valor
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def transporte(mocker):
    mock = mocker.Mock(spec = Transporte)
    mock.getter_peso_max.return_value = 500
    mock.getter_volumen.return_value = 8
    mock.getter_velocidad.return_value = 30
    mock.getter_costo_km.return_value = 2
    mock.getter_costo_parada.return_value = 5
    mock.getter_tipo.return_value = "Furgoneta"
    return mock

@pytest.fixture
def matriz(mocker):
    mock = mocker.Mock(spec = MatrizDistancia)
    mock.obtener_distancia.side_effect = distancia_falsa
    return mock

@pytest.fixture
def solicitud_a(mocker):
    mock = mocker.Mock(spec = Solicitud)
    mock.getter_id.return_value = 1
    mock.getter_destino.return_value = "Destino A"
    mock.getter_ventana_inicio.return_value = hora(9)
    mock.getter_ventana_fin.return_value = hora(12)
    mock.getter_peso.return_value = 150
    mock.getter_volumen.return_value = 3
    mock.esta_asignada.return_value = False
    mock.esta_entregada.return_value = False
    return mock

@pytest.fixture
def solicitud_b(mocker):
    mock = mocker.Mock(spec = Solicitud)
    mock.getter_id.return_value = 2
    mock.getter_destino.return_value = "Destino B"
    mock.getter_ventana_inicio.return_value = hora(10, 30)
    mock.getter_ventana_fin.return_value = hora(13)
    mock.getter_peso.return_value = 200
    mock.getter_volumen.return_value = 3
    mock.esta_asignada.return_value = False
    mock.esta_entregada.return_value = False
    return mock

@pytest.fixture
def solicitud_c(mocker):
    mock = mocker.Mock(spec = Solicitud)
    mock.getter_id.return_value = 3
    mock.getter_destino.return_value = "Destino C"
    mock.getter_ventana_inicio.return_value = hora(9, 30)
    mock.getter_ventana_fin.return_value = hora(10, 15)
    mock.getter_peso.return_value = 100
    mock.getter_volumen.return_value = 2
    mock.esta_asignada.return_value = False
    mock.esta_entregada.return_value = False
    return mock

@pytest.fixture
def incidente(mocker):
    return mocker.Mock(spec = Incidente)

@pytest.fixture
def viaje(mock_validaciones, transporte, matriz):
    return Viaje(transporte, "Deposito", HORARIO, matriz)

@pytest.fixture
def viaje_falso_igual(mocker):
    mock = mocker.MagicMock(spec = Viaje)
    mock.getter_id.return_value = 1
    mock.__hash__.return_value = hash(mock.getter_id())
    return mock

# A: 150 kg, 3 m³ - ventana 9:00 a 12:00. B: 200 kg, 3 m³ - ventana 10:30 a 13:00 (llega antes y espera)
@pytest.fixture
def viaje_con_solicitudes(viaje, solicitud_a, solicitud_b):
    viaje.agregar_solicitud(solicitud_a)
    viaje.agregar_solicitud(solicitud_b)
    return viaje

@pytest.fixture
def mock_validar_estado(mocker):
    return mocker.patch.object(Viaje, "validar_estado", autospec = True)

@pytest.fixture
def mock_validar_recorrido(mocker):
    return mocker.patch.object(Viaje, "validar_recorrido", autospec = True, return_value = True)

# Fixtures para probar cada método sin depender de los demás: el estado se arma a mano y los colaboradores propios se mockean
@pytest.fixture
def viaje_cargado(viaje, solicitud_a, solicitud_b):
    viaje.setter_solicitudes([solicitud_a, solicitud_b])
    viaje.setter_historial_solicitudes([solicitud_a, solicitud_b])
    return viaje

@pytest.fixture
def parada_1(mocker, solicitud_a):
    mock = mocker.Mock(spec = Parada)
    mock.getter_orden.return_value = 1
    mock.getter_solicitud.return_value = solicitud_a
    return mock

@pytest.fixture
def parada_2(mocker, solicitud_b):
    mock = mocker.Mock(spec = Parada)
    mock.getter_orden.return_value = 2
    mock.getter_solicitud.return_value = solicitud_b
    return mock

# Cola mockeada: el frente es parada_1 y por defecto quedan paradas pendientes (esVacia() -> False)
@pytest.fixture
def cola_paradas(mocker, parada_1):
    mock = mocker.MagicMock(spec = Cola)
    mock.esVacia.return_value = False
    mock.frente.return_value = parada_1
    mock.desencolar.return_value = parada_1
    return mock

# La cola del viaje es la cola mockeada (el viaje la crea al setear las paradas)
@pytest.fixture
def viaje_con_paradas(viaje, cola_paradas, mocker):
    mocker.patch("viaje.Cola", return_value = cola_paradas)
    viaje.setter_paradas([])
    viaje.setter_estado("EN_CURSO")
    return viaje

@pytest.fixture
def mock_agregar_solicitud(mocker):
    return mocker.patch.object(Viaje, "agregar_solicitud", autospec = True)

@pytest.fixture
def mock_distancia_total(mocker):
    return mocker.patch.object(Viaje, "distancia_total", autospec = True, return_value = 50)

@pytest.fixture
def viaje_en_curso(viaje_con_solicitudes, solicitud_a, solicitud_b, parada_1, parada_2):
    viaje_con_solicitudes.comenzar([solicitud_a, solicitud_b], [parada_1, parada_2])
    return viaje_con_solicitudes


# ---------- __init__ ----------
# Funcionamiento normal
def test_viaje_ok(viaje, transporte, matriz):
    assert viaje.getter_transporte() is transporte
    assert viaje.getter_deposito() == "Deposito"
    assert viaje.getter_horario() == HORARIO
    assert viaje.getter_matriz() is matriz
    assert viaje.getter_estado() == "PLANIFICADO"
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
    assert viaje.getter_solicitudes() == []
    assert viaje.getter_incidentes() == []
    assert viaje.paradas_pendientes() == []
    assert viaje.getter_paradas() == []
    # Historial vacío: no hay nada para deshacer
    with pytest.raises(ViajeVacioError):
        viaje.deshacer_ultima_solicitud()
    # id
    assert viaje.getter_id() == 1
    viaje2 = Viaje(transporte, "Deposito", HORARIO, matriz)
    assert viaje2.getter_id() == 2
# Validaciones
def test_viaje_validaciones(mock_validaciones, transporte, matriz):
    Viaje(transporte, "Deposito", HORARIO, matriz)
    mock_validaciones.validar_instancia.assert_any_call(transporte, clase = Transporte, nombre = "transporte")
    mock_validaciones.validar_str.assert_called_once_with("Deposito", nombre = "depósito")
    mock_validaciones.validar_fecha.assert_called_once_with(HORARIO, nombre = "horario de salida del viaje")
    mock_validaciones.validar_instancia.assert_any_call(matriz, clase = MatrizDistancia, nombre = "matriz")
    mock_validaciones.validar_en.assert_not_called()
# Errores en __init__. Propagación
def test_viaje_transporteInvalido_sePropaga(mock_validaciones, matriz):
    mock_validaciones.validar_instancia.side_effect = TypeError("El transporte debe ser un objeto de clase Transporte")
    with pytest.raises(TypeError, match = "El transporte debe ser un objeto de clase Transporte"):
        Viaje("Furgoneta", "Deposito", HORARIO, matriz)
    assert Viaje.curr_id == 0
def test_viaje_depositoInvalido_sePropaga(mock_validaciones, transporte, matriz):
    mock_validaciones.validar_str.side_effect = DatoInvalidoError("El depósito no debe estar vacío")
    with pytest.raises(DatoInvalidoError, match = "El depósito no debe estar vacío"):
        Viaje(transporte, "", HORARIO, matriz)
    assert Viaje.curr_id == 0
    mock_validaciones.validar_str.side_effect = TypeError("El depósito debe ser una cadena str")
    with pytest.raises(TypeError, match = "El depósito debe ser una cadena str"):
        Viaje(transporte, 123, HORARIO, matriz)
    assert Viaje.curr_id == 0
def test_viaje_horarioInvalido_sePropaga(mock_validaciones, transporte, matriz):
    mock_validaciones.validar_fecha.side_effect = TypeError("El horario debe ser un objeto datetime")
    with pytest.raises(TypeError, match = "El horario debe ser un objeto datetime"):
        Viaje(transporte, "Deposito", "9AM", matriz)
    assert Viaje.curr_id == 0
def test_viaje_matrizInvalida_sePropaga(mock_validaciones, transporte):
    mock_validaciones.validar_instancia.side_effect = [transporte, TypeError("La matriz debe ser un objeto de clase MatrizDistancia")]
    with pytest.raises(TypeError, match = "La matriz debe ser un objeto de clase MatrizDistancia"):
        Viaje(transporte, "Deposito", HORARIO, "Matriz")
    assert Viaje.curr_id == 0


# ---------- Getters ----------
def test_viaje_getters(viaje, transporte, matriz):
    assert viaje.getter_estado() == "PLANIFICADO"
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
    assert viaje.getter_peso_max() == 500
    transporte.getter_peso_max.assert_called_once()
    assert viaje.getter_volumen_max() == 8
    transporte.getter_volumen.assert_called_once()
    assert viaje.getter_solicitudes() == []
    assert viaje.getter_id() == 1
    assert viaje.getter_transporte() is transporte
    assert viaje.getter_deposito() == "Deposito"
    assert viaje.getter_horario() == HORARIO
    assert viaje.getter_matriz() is matriz
    assert viaje.getter_incidentes() == []
    assert viaje.getter_paradas() == []

def test_viaje_getters_devuelvenCopias(viaje_en_curso, solicitud_a, solicitud_b):
    viaje_en_curso.getter_solicitudes().clear()
    assert viaje_en_curso.getter_solicitudes() == [solicitud_a, solicitud_b]
    viaje_en_curso.getter_paradas().clear()
    assert len(viaje_en_curso.getter_paradas()) == 2
    viaje_en_curso.getter_incidentes().append("Incidente")
    assert viaje_en_curso.getter_incidentes() == []

def test_viaje_getters_conSolicitudes(viaje_con_solicitudes, solicitud_a, solicitud_b):
    assert viaje_con_solicitudes.getter_estado() == "PLANIFICADO"
    assert viaje_con_solicitudes.getter_peso() == 350
    assert viaje_con_solicitudes.getter_volumen() == 6
    assert viaje_con_solicitudes.getter_solicitudes() == [solicitud_a, solicitud_b]

def test_viaje_getters_viajeEnCurso(viaje_en_curso, solicitud_a, solicitud_b):
    assert viaje_en_curso.getter_estado() == "EN_CURSO"
    paradas = viaje_en_curso.getter_paradas()
    assert list(map(lambda p: p.getter_solicitud(), paradas)) == [solicitud_a, solicitud_b]
    assert list(map(lambda p: p.getter_orden(), paradas)) == [1, 2]
    assert viaje_en_curso.paradas_pendientes() == paradas

def test_viaje_getters_conParadaResuelta(viaje_en_curso, solicitud_a, solicitud_b):
    viaje_en_curso.cerrar_parada_actual()
    paradas = viaje_en_curso.getter_paradas()
    assert list(map(lambda p: p.getter_solicitud(), paradas)) == [solicitud_a, solicitud_b]
    pendientes = viaje_en_curso.paradas_pendientes()
    assert list(map(lambda p: p.getter_solicitud(), pendientes)) == [solicitud_b]
    assert pendientes[0] is paradas[1]

def test_viaje_getters_conIncidente(viaje_en_curso, incidente, solicitud_a, solicitud_b):
    viaje_en_curso.agregar_incidente(incidente)
    viaje_en_curso.cerrar_parada_actual()
    assert viaje_en_curso.getter_incidentes() == [incidente]
    paradas = viaje_en_curso.getter_paradas()
    assert list(map(lambda p: p.getter_solicitud(), paradas)) == [solicitud_a, solicitud_b]
    pendientes = viaje_en_curso.paradas_pendientes()
    assert list(map(lambda p: p.getter_solicitud(), pendientes)) == [solicitud_b]
    viaje_en_curso.getter_incidentes().clear()
    viaje_en_curso.paradas_pendientes().clear()
    assert viaje_en_curso.getter_incidentes() == [incidente]
    assert viaje_en_curso.paradas_pendientes() == pendientes


# ---------- Métodos mágicos ----------
def test_viaje_metodosMagicos(viaje, transporte, matriz, viaje_falso_igual):
    assert str(viaje) == "Viaje 1 [PLANIFICADO] - Furgoneta saliendo de Deposito a las 2026-10-11 09:00"
    assert repr(viaje) == "<Viaje 1 PLANIFICADO paradas=0>"
    # eq
    viaje2 = Viaje(transporte, "Deposito", HORARIO, matriz)
    assert viaje == viaje
    assert viaje == viaje_falso_igual
    assert viaje not in {viaje2, "Viaje 1", transporte}
    # hash - por si necesitamos set o dicc
    assert hash(viaje) == hash(viaje.getter_id())
    assert hash(viaje) != hash(viaje2)
    viajes = {viaje, viaje2, viaje, viaje_falso_igual}
    assert len(viajes) == 2
    dicc = {viaje: 100}
    assert dicc[viaje] == 100


# ---------- agregar_solicitud ----------
# Sn los errores ver que el peso y el volumen no se actualizan
# exc
def test_agregarSolicitud_ok(viaje, solicitud_a, solicitud_b, mock_validaciones, mock_validar_estado, mock_validar_recorrido):
    viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == [solicitud_a]
    assert viaje.getter_peso() == 150
    assert viaje.getter_volumen() == 3
    mock_validar_estado.assert_called_once_with(viaje, "agregar_solicitud", "PLANIFICADO")
    mock_validar_recorrido.assert_called_once_with(viaje, [solicitud_a])
    mock_validaciones.validar_instancia.assert_any_call(solicitud_a, clase = Solicitud, nombre = "solicitud")
    assert solicitud_a.getter_peso.call_count == 2
    assert solicitud_a.getter_volumen.call_count == 2
    solicitud_a.setter_viaje.assert_called_once_with(viaje)
    # varias solicitudes
    viaje.agregar_solicitud(solicitud_b)
    assert viaje.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje.getter_peso() == 350
    assert viaje.getter_volumen() == 6
    assert solicitud_a.getter_peso.call_count == 4
    assert solicitud_a.getter_volumen.call_count == 4
    solicitud_b.setter_viaje.assert_called_once_with(viaje)
    mock_validar_estado.assert_any_call(viaje, "agregar_solicitud", "PLANIFICADO")
    mock_validar_recorrido.assert_any_call(viaje, [solicitud_a, solicitud_b])
# solicitud no es Solicitud
def test_agregarSolicitud_noEsSolicitud_sePropaga(viaje, mock_validaciones):
    mock_validaciones.validar_instancia.side_effect = TypeError("La solicitud debe ser un objeto de clase Solicitud")
    with pytest.raises(TypeError, match = "La solicitud debe ser un objeto de clase Solicitud"):
        viaje.agregar_solicitud("Solicitud 1")
    assert viaje.getter_solicitudes() == []
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
# Estado inválido se propaga
def test_agregarSolicitud_estadoInvalido_sePropaga(viaje_en_curso, solicitud_a, solicitud_b, mock_validar_estado):
    mock_validar_estado.side_effect = EstadoInvalidoError("agregar_solicitud", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede agregar_solicitud porque el estado es EN_CURSO"):
        viaje_en_curso.agregar_solicitud(solicitud_a)
    assert viaje_en_curso.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje_en_curso.getter_peso() == 350
# solicitud duplicada
def test_agregarSolicitud_duplicada(viaje_con_solicitudes, solicitud_a, solicitud_b, mock_validar_estado):
    with pytest.raises(SolicitudDuplicadaError, match = "Solicitud duplicada"):
        viaje_con_solicitudes.agregar_solicitud(solicitud_a)
    assert viaje_con_solicitudes.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje_con_solicitudes.getter_peso() == 350
    solicitud_a.setter_viaje.assert_called_once_with(viaje_con_solicitudes)
# solicitud asignada a otro viaje
def test_agregarSolicitud_yaAsignada(viaje, solicitud_a, mock_validar_estado):
    solicitud_a.esta_asignada.return_value = True
    with pytest.raises(SolicitudDuplicadaError, match = "Solicitud duplicada"):
        viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == []
    solicitud_a.setter_viaje.assert_not_called()
# solicitud entregada
def test_agregarSolicitud_yaEntregada(viaje, solicitud_a, mock_validar_estado):
    solicitud_a.esta_entregada.return_value = True
    with pytest.raises(SolicitudDuplicadaError, match = "Solicitud duplicada"):
        viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == []
    solicitud_a.setter_viaje.assert_not_called()
# destino es el deposito
def test_agregarSolicitud_destinoEsElDeposito(viaje, solicitud_a, mock_validar_estado):
    solicitud_a.getter_destino.return_value = "Deposito"
    with pytest.raises(DatoInvalidoError, match = "no puede ser el depósito"):
        viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == []
    solicitud_a.setter_viaje.assert_not_called()
# máximo de peso y volumen permitido
def test_agregarSolicitud_maximaCapacidadPermitida(viaje, solicitud_a, solicitud_b, mock_validar_estado, mock_validar_recorrido):
    solicitud_a.getter_peso.return_value = 300
    solicitud_a.getter_volumen.return_value = 5
    solicitud_b.getter_peso.return_value = 200
    solicitud_b.getter_volumen.return_value = 3
    viaje.agregar_solicitud(solicitud_a)
    viaje.agregar_solicitud(solicitud_b)
    assert viaje.getter_peso() == 500 == viaje.getter_transporte().getter_peso_max()
    assert viaje.getter_volumen() == 8 == viaje.getter_transporte().getter_volumen()
# exceso de peso
def test_agregarSolicitud_excesoPeso(viaje, solicitud_a, mock_validar_estado):
    solicitud_a.getter_peso.return_value = 501
    with pytest.raises(ExcesoPesoError):
        viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == []
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
    solicitud_a.setter_viaje.assert_not_called()
# exceso de volumen
def test_agregarSolicitud_excesoVolumen(viaje, solicitud_a, mock_validar_estado):
    solicitud_a.getter_volumen.return_value = 9
    with pytest.raises(ExcesoVolumenError, match = "Capacidad excedida: El volumen 9 supera el volumen máximo del transporte 8"):
        viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == []
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
    solicitud_a.setter_viaje.assert_not_called()
# destino sin tramo de regreso al deposito
def test_agregarSolicitud_sinTramoDeRegreso_sePropaga(viaje, matriz, solicitud_a, mock_validar_estado):
    matriz.obtener_distancia.side_effect = [15, RutaIncompletaError("Destino A", "Deposito")]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino A a Deposito"):
        viaje.agregar_solicitud(solicitud_a)
    assert viaje.getter_solicitudes() == []
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
    solicitud_a.setter_viaje.assert_not_called()
# Recorrido inválido se propaga
def test_agregarSolicitud_recorridoInvalido_sePropaga(viaje, solicitud_a, solicitud_b, mock_validar_estado, mock_validar_recorrido):
    mock_validar_recorrido.side_effect = [True, VentanaIncumplidaError("Destino A", hora(11), hora(10))]
    viaje.agregar_solicitud(solicitud_a)
    with pytest.raises(VentanaIncumplidaError):
        viaje.agregar_solicitud(solicitud_b)
    assert viaje.getter_solicitudes() == [solicitud_a]
    assert viaje.getter_peso() == 150
    assert viaje.getter_volumen() == 3
    solicitud_b.setter_viaje.assert_not_called()


# ---------- deshacer_ultima_solicitud ----------
# Funcionamiento normal
def test_deshacerUltimaSolicitud_ok(viaje_cargado, solicitud_a, solicitud_b, mock_validar_estado):
    # Pila --> Saca la última
    assert viaje_cargado.deshacer_ultima_solicitud() is solicitud_b
    mock_validar_estado.assert_called_once_with(viaje_cargado, "deshacer_ultima_solicitud", "PLANIFICADO")
    assert viaje_cargado.getter_solicitudes() == [solicitud_a]
    assert viaje_cargado.getter_peso() == 150
    assert viaje_cargado.getter_volumen() == 3
    solicitud_b.setter_viaje.assert_called_once_with(None)
    solicitud_a.assert_not_called()
    # Desapila la anterior
    assert viaje_cargado.deshacer_ultima_solicitud() is solicitud_a
    assert viaje_cargado.getter_solicitudes() == []
    assert viaje_cargado.getter_peso() == 0
    assert viaje_cargado.getter_volumen() == 0
    solicitud_a.setter_viaje.assert_called_once_with(None)
# estadoInvalido se propaga
def test_deshacerUltimaSolicitud_estadoInvalido_sePropaga(viaje_cargado, solicitud_a, solicitud_b, mock_validar_estado):
    mock_validar_estado.side_effect = EstadoInvalidoError("deshacer_ultima_solicitud", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "No se puede deshacer_ultima_solicitud porque el estado es EN_CURSO"):
        viaje_cargado.deshacer_ultima_solicitud()
    assert viaje_cargado.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje_cargado.getter_peso() == 350
    assert viaje_cargado.getter_volumen() == 6
    solicitud_b.setter_viaje.assert_not_called()
    # El historial no cambió: la última solicitud sigue siendo la primera en deshacerse
    mock_validar_estado.side_effect = None
    assert viaje_cargado.deshacer_ultima_solicitud() is solicitud_b
# historial vacio se propaga
def test_deshacerUltimaSolicitud_sinSolicitudes(viaje, mock_validar_estado):
    with pytest.raises(ViajeVacioError, match = "No hay solicitudes para deshacer"):
        viaje.deshacer_ultima_solicitud()
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0


# ---------- validar_recorrido ----------
# Funcionamiento normal
def test_validarRecorrido_ok(viaje, matriz, solicitud_a, solicitud_b, mock_agregar_solicitud, mocker):
    assert viaje.validar_recorrido([]) is True
    matriz.obtener_distancia.assert_called_once_with("Deposito", "Deposito")
    viaje.setter_solicitudes([solicitud_a])
    matriz.obtener_distancia.side_effect = [15, 10, 5]
    # Llega 9:30 a Destino A. Sale 9:40 y llega 10:00 a Destino B
    solicitud_a.getter_ventana_fin.return_value = hora(9, 30)
    solicitud_b.getter_ventana_fin.return_value = hora(10)
    assert viaje.validar_recorrido([solicitud_a, solicitud_b]) is True
    assert matriz.obtener_distancia.call_args_list == [mocker.call("Deposito", "Deposito"), mocker.call("Deposito", "Destino A"), mocker.call("Destino A", "Destino B"), mocker.call("Destino B", "Deposito")]
    assert viaje.getter_solicitudes() == [solicitud_a]
    assert viaje.getter_peso() == 150
# Un transporte rápido llega pero uno lento no cumple los horarios
def test_validarRecorrido_transporteRapidoYLento(viaje, matriz, transporte, solicitud_a):
    solicitud_a.getter_ventana_fin.return_value = hora(9, 29)
    transporte.getter_velocidad.return_value = 60
    matriz.obtener_distancia.return_value = 15
    assert viaje.validar_recorrido([solicitud_a]) is True
    transporte.getter_velocidad.return_value = 30
    with pytest.raises(VentanaIncumplidaError, match = "Ventana incumplida: Se llegará a Destino A a las 2026-10-11 09:30:00 superando el límite 2026-10-11 09:29:00"):
        viaje.validar_recorrido([solicitud_a])
# Error ventana incumplida
def test_validarRecorrido_esperaInicioVentana_yVentanaIncumplida(viaje, matriz, solicitud_a, solicitud_b):
    matriz.obtener_distancia.side_effect = [15, 10]
    solicitud_a.getter_ventana_inicio.return_value = hora(10)
    solicitud_b.getter_ventana_inicio.return_value = hora(9)
    solicitud_b.getter_ventana_fin.return_value = hora(10, 29)
    # Llega 9:30 (A), espera 10:00 --> 10:10 sale, llega 10:30 (B)
    with pytest.raises(VentanaIncumplidaError, match = "Ventana incumplida: Se llegará a Destino B a las 2026-10-11 10:30:00 superando el límite 2026-10-11 10:29:00"):
        viaje.validar_recorrido([solicitud_a, solicitud_b])
# Error ruta incompleta se propaga
def test_validarRecorrido_tramoFaltante_sePropaga(viaje, matriz, solicitud_a, solicitud_b):
    matriz.obtener_distancia.side_effect = [15, RutaIncompletaError("Destino A", "Destino B")]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino A a Destino B"):
        viaje.validar_recorrido([solicitud_a, solicitud_b])
    assert matriz.obtener_distancia.call_count == 2
    # Falta el tramo de regreso al deposito
    matriz.obtener_distancia.side_effect = [15, 10, RutaIncompletaError("Destino B", "Deposito")]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino B a Deposito"):
        viaje.validar_recorrido([solicitud_a, solicitud_b])


# ---------- calcular_horarios ----------
# Funcionamiento normal
def test_calcularHorarios_ok(viaje, solicitud_a, solicitud_b):
    # Sale 9:00 y llega 9:30 a A. Sale 9:40 y llega 10:00 a B
    solicitud_b.getter_ventana_inicio.return_value = hora(9)
    assert viaje.calcular_horarios([solicitud_a, solicitud_b]) == [hora(9, 30), hora(10)]
    assert viaje.calcular_horarios([solicitud_b]) == [hora(9, 50)]
# Llega antes de que abra la ventana y espera
def test_calcularHorarios_esperaInicioVentana(viaje, solicitud_a, solicitud_b):
    # Llega 9:30 a A. Sale 9:40 y llega 10:00 a B, pero la ventana de B abre 10:30
    assert viaje.calcular_horarios([solicitud_a, solicitud_b]) == [hora(9, 30), hora(10, 30)]
# Ventana incumplida. Llegar justo al fin es válido
def test_calcularHorarios_ventanaIncumplida(viaje, solicitud_a):
    solicitud_a.getter_ventana_fin.return_value = hora(9, 30)
    assert viaje.calcular_horarios([solicitud_a]) == [hora(9, 30)]
    solicitud_a.getter_ventana_fin.return_value = hora(9, 29)
    with pytest.raises(VentanaIncumplidaError, match = "Ventana incumplida: Se llegará a Destino A a las 2026-10-11 09:30:00 superando el límite 2026-10-11 09:29:00"):
        viaje.calcular_horarios([solicitud_a])
# Recorrido vacío
def test_calcularHorarios_recorridoVacio(viaje, matriz):
    assert viaje.calcular_horarios([]) == []
    matriz.obtener_distancia.assert_not_called()
# Error ruta incompleta se propaga
def test_calcularHorarios_tramoFaltante_sePropaga(viaje, matriz, solicitud_a, solicitud_b):
    matriz.obtener_distancia.side_effect = [15, RutaIncompletaError("Destino A", "Destino B")]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino A a Destino B"):
        viaje.calcular_horarios([solicitud_a, solicitud_b])


# ---------- distancia_total ----------
def test_distanciaTotal_ok(viaje_cargado, solicitud_a, solicitud_b, matriz, mocker):
    matriz.obtener_distancia.side_effect = [15, 10, 25]
    assert viaje_cargado.distancia_total("Deposito", [solicitud_a, solicitud_b]) == 50
    matriz.obtener_distancia.assert_any_call("Deposito", "Destino A")
    matriz.obtener_distancia.assert_any_call("Destino A", "Destino B")
    matriz.obtener_distancia.assert_any_call("Destino B", "Deposito")
    assert matriz.obtener_distancia.call_count == 3
    # Sin argumentos parte del deposito con las solicitudes del viaje
    matriz.obtener_distancia.side_effect = [15, 10, 25]
    assert viaje_cargado.distancia_total() == 50
def test_distanciaTotal_viajeVacio(viaje, matriz):
    matriz.obtener_distancia.return_value = 0
    assert viaje.distancia_total("Deposito", viaje.getter_solicitudes()) == 0
    matriz.obtener_distancia.assert_called_once_with("Deposito", "Deposito")
def test_distanciaTotal_tramoFaltante_sePropaga(viaje_cargado, matriz, solicitud_a, solicitud_b):
    matriz.obtener_distancia.side_effect = [15, 10, RutaIncompletaError("Destino B", "Deposito")]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino B a Deposito"):
        viaje_cargado.distancia_total("Deposito", [solicitud_a, solicitud_b])
def test_distanciaTotal_otroOrden(viaje_cargado, solicitud_a, solicitud_b, matriz, mocker):
    matriz.obtener_distancia.return_value = 15
    assert viaje_cargado.distancia_total("Deposito", [solicitud_a]) == 30
    solicitud_b.getter_destino.assert_not_called()
    assert matriz.obtener_distancia.call_args_list == [mocker.call("Deposito", "Destino A"), mocker.call("Destino A", "Deposito")]
    matriz.obtener_distancia.return_value = 25
    assert viaje_cargado.distancia_total("Deposito", [solicitud_b]) == 50
    assert viaje_cargado.getter_solicitudes() == [solicitud_a, solicitud_b]
def test_distanciaTotal_ordenVacio(viaje_cargado, matriz):
    assert viaje_cargado.distancia_total("Deposito", []) == 0
    matriz.obtener_distancia.assert_called_once_with("Deposito", "Deposito")


# ---------- ultimo_lugar ----------
def test_ultimoLugar_viajeVacio(viaje):
    assert viaje.ultimo_lugar() == "Deposito"
def test_ultimoLugar_conSolicitudes(viaje_con_solicitudes):
    assert viaje_con_solicitudes.ultimo_lugar() == "Destino B"
    viaje_con_solicitudes.deshacer_ultima_solicitud()
    assert viaje_con_solicitudes.ultimo_lugar() == "Destino A"


# A futuro: Costo total y el cálculo de impacto ambiental (delegado en transporte)
# ---------- costo_total e impacto_ambiental ----------
def test_costoTotal_ok(viaje_cargado, mock_distancia_total, transporte, solicitud_a, solicitud_b):
    # 50 km * $2 / km + 2 paradas * $5 / parada = $110
    assert viaje_cargado.costo_total() == 110
    transporte.getter_costo_km.assert_called_once_with()
    transporte.getter_costo_parada.assert_called_once_with()
    mock_distancia_total.assert_called_once_with(viaje_cargado, "Deposito", [solicitud_a, solicitud_b])
def test_costoTotal_viajeVacio(viaje, mock_distancia_total, transporte):
    mock_distancia_total.return_value = 0
    assert viaje.costo_total() == 0
    mock_distancia_total.assert_called_once_with(viaje, "Deposito", [])
def test_costoTotal_otroOrden(viaje_cargado, mock_distancia_total, transporte, solicitud_a, solicitud_b):
    mock_distancia_total.return_value = 30
    # 30 km * $2 / km + 1 parada * $5 / parada = $65
    assert viaje_cargado.costo_total([solicitud_a]) == 65
    mock_distancia_total.assert_called_once_with(viaje_cargado, "Deposito", [solicitud_a])
    assert viaje_cargado.getter_solicitudes() == [solicitud_a, solicitud_b]
def test_costoTotal_ordenVacio(viaje_cargado, mock_distancia_total):
    mock_distancia_total.return_value = 0
    assert viaje_cargado.costo_total([]) == 0
    mock_distancia_total.assert_called_once_with(viaje_cargado, "Deposito", [])
def test_costoTotal_tramoFaltante_sePropaga(viaje_cargado, mock_distancia_total):
    mock_distancia_total.side_effect = RutaIncompletaError("Destino B", "Deposito")
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino B a Deposito"):
        viaje_cargado.costo_total()
def test_impactoAmbiental_delegaEnElTransporte(viaje_cargado, transporte, mock_distancia_total):
    transporte.calcular_impacto_ambiental.return_value = 13.5
    assert viaje_cargado.impacto_ambiental() == 13.5
    transporte.calcular_impacto_ambiental.assert_called_once_with(50, 350)


# ---------- validar_estado ----------
# Funcionamiento normal
def test_validarEstado_estadoCorrecto_noLanza(viaje):
    assert viaje.getter_estado() == "PLANIFICADO"
    assert viaje.validar_estado("iniciar_viaje", "PLANIFICADO") is None
    viaje.setter_estado("EN_CURSO")
    assert viaje.validar_estado("registrar_entrega", "EN_CURSO") is None
    viaje.setter_estado("FINALIZADO")
    assert viaje.validar_estado("mostrar detalles", "FINALIZADO") is None
# EstadoInvalido
def test_validarEstado_estadoInvalido(viaje):
    # Desde planificado
    assert viaje.getter_estado() == "PLANIFICADO"
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es PLANIFICADO"):
        viaje.validar_estado("registrar_entrega", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede mostrar_detalles porque el estado es PLANIFICADO"):
        viaje.validar_estado("mostrar_detalles", "FINALIZADO")
    assert viaje.getter_estado() == "PLANIFICADO"
    # Desde en_curso
    viaje.setter_estado("EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "No se puede iniciar_viaje porque el estado es EN_CURSO"):
        viaje.validar_estado("iniciar_viaje", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede mostrar_detalles porque el estado es EN_CURSO"):
        viaje.validar_estado("mostrar_detalles", "FINALIZADO")
    # Desde finalizado
    viaje.setter_estado("FINALIZADO")
    with pytest.raises(EstadoInvalidoError, match = "No se puede iniciar_viaje porque el estado es FINALIZADO"):
        viaje.validar_estado("iniciar_viaje", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es FINALIZADO"):
        viaje.validar_estado("registrar_entrega", "EN_CURSO")


# ---------- finalizar_viaje ----------
# Funcionamiento normal
def test_finalizarViaje_ok(viaje_con_paradas, cola_paradas, mock_validar_estado, capsys):
    cola_paradas.esVacia.return_value = True
    assert viaje_con_paradas.finalizar_viaje() is None
    mock_validar_estado.assert_called_once_with(viaje_con_paradas, "finalizar_viaje", "EN_CURSO")
    cola_paradas.esVacia.assert_called_once()
    assert viaje_con_paradas.getter_estado() == "FINALIZADO"
    assert capsys.readouterr().out == ""   # El dominio no imprime
# Quedan paradas pendientes
def test_finalizarViaje_conParadasPendientes(viaje_con_paradas, cola_paradas, mock_validar_estado):
    cola_paradas.esVacia.return_value = False
    cola_paradas.get_longitud.return_value = 2
    with pytest.raises(ViajeIncompletoError, match = "Viaje incompleto: No se puede finalizar porque quedan 2 paradas pendientes"):
        viaje_con_paradas.finalizar_viaje()
    assert viaje_con_paradas.getter_estado() == "EN_CURSO"
# Estado inválido se propaga
def test_finalizarViaje_estadoInvalido_sePropaga(viaje, mock_validar_estado):
    mock_validar_estado.side_effect = EstadoInvalidoError("finalizar_viaje", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede finalizar_viaje porque el estado es PLANIFICADO"):
        viaje.finalizar_viaje()
    assert viaje.getter_estado() == "PLANIFICADO"


# ---------- es_parada_actual ----------
# Funcionamiento normal
def test_esParadaActual_ok(viaje_en_curso, parada_1, parada_2):
    assert viaje_en_curso.es_parada_actual(parada_1)
    # No es el frente de la cola
    assert not viaje_en_curso.es_parada_actual(parada_2)
    viaje_en_curso.cerrar_parada_actual()
    assert not viaje_en_curso.es_parada_actual(parada_1)
    assert viaje_en_curso.es_parada_actual(parada_2)
# Viaje planificado, aunque la parada esté en la cola
def test_esParadaActual_viajePlanificado(viaje, parada_1):
    viaje.setter_paradas([parada_1])
    assert viaje.getter_estado() == "PLANIFICADO"
    assert not viaje.es_parada_actual(parada_1)
# Viaje finalizado (cola vacía)
def test_esParadaActual_viajeFinalizado(viaje_en_curso, parada_1, parada_2):
    viaje_en_curso.cerrar_parada_actual()
    viaje_en_curso.cerrar_parada_actual()
    assert viaje_en_curso.getter_estado() == "FINALIZADO"
    assert not viaje_en_curso.es_parada_actual(parada_1)
    assert not viaje_en_curso.es_parada_actual(parada_2)


# ---------- serializar ----------
def test_serializar_ok(viaje_en_curso, transporte, parada_1, parada_2, incidente):
    transporte.getter_id.return_value = 4
    parada_1.getter_id.return_value = 10
    parada_2.getter_id.return_value = 11
    incidente.getter_id.return_value = 7
    viaje_en_curso.agregar_incidente(incidente)
    viaje_en_curso.cerrar_parada_actual()
    assert viaje_en_curso.serializar() == [1, 4, "Deposito", HORARIO, "EN_CURSO", "1,2", "7", "11", "10", "1,2"]
    transporte.getter_id.assert_called_once()
def test_serializar_viajeVacio(viaje, transporte):
    transporte.getter_id.return_value = 4
    assert viaje.serializar() == [1, 4, "Deposito", HORARIO, "PLANIFICADO", "", "", "", "", ""]


# ---------- comenzar ----------
# Funcionamiento normal
def test_comenzar_ok(viaje_con_solicitudes, solicitud_a, solicitud_b, parada_1, parada_2, mock_validar_estado):
    viaje_con_solicitudes.setter_paradas_resueltas([parada_2])
    viaje_con_solicitudes.comenzar([solicitud_b, solicitud_a], [parada_1, parada_2])
    mock_validar_estado.assert_called_once_with(viaje_con_solicitudes, "iniciar_viaje", "PLANIFICADO")
    assert viaje_con_solicitudes.getter_estado() == "EN_CURSO"
    assert viaje_con_solicitudes.getter_solicitudes() == [solicitud_b, solicitud_a]
    assert viaje_con_solicitudes.paradas_pendientes() == [parada_1, parada_2]
    assert viaje_con_solicitudes.getter_paradas() == [parada_1, parada_2]    # Se vacían las paradas resueltas
    assert viaje_con_solicitudes.es_parada_actual(parada_1)
# Estado inválido se propaga
def test_comenzar_estadoInvalido_sePropaga(viaje_con_solicitudes, solicitud_a, solicitud_b, parada_1, mock_validar_estado):
    mock_validar_estado.side_effect = EstadoInvalidoError("iniciar_viaje", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede iniciar_viaje porque el estado es EN_CURSO"):
        viaje_con_solicitudes.comenzar([solicitud_b], [parada_1])
    assert viaje_con_solicitudes.getter_estado() == "PLANIFICADO"
    assert viaje_con_solicitudes.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje_con_solicitudes.getter_paradas() == []


# ---------- parada_actual ----------
# Funcionamiento normal
def test_paradaActual_ok(viaje_en_curso, parada_1, parada_2):
    assert viaje_en_curso.parada_actual("registrar_entrega") is parada_1
    # No saca la parada de la cola
    assert viaje_en_curso.parada_actual("registrar_entrega") is parada_1
    assert viaje_en_curso.paradas_pendientes() == [parada_1, parada_2]
# Estado inválido
def test_paradaActual_estadoInvalido(viaje):
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es PLANIFICADO"):
        viaje.parada_actual("registrar_entrega")
# Sin paradas pendientes
def test_paradaActual_sinParadasPendientes(viaje):
    viaje.setter_estado("EN_CURSO")
    with pytest.raises(SinParadasPendientesError, match = "Sin paradas pendientes: No se puede registrar_incidente"):
        viaje.parada_actual("registrar_incidente")


# ---------- validar_hora_resolucion ----------
# Funcionamiento normal
def test_validarHoraResolucion_sinParadasResueltas(viaje, mock_validaciones):
    assert viaje.validar_hora_resolucion(hora(9, 35), "fecha de entrega") is None
    mock_validaciones.validar_ventana.assert_called_once_with(HORARIO, hora(9, 35), nombre_inicio = "fecha de salida del viaje", nombre_fin = "fecha de entrega")
def test_validarHoraResolucion_conParadaPrevia(viaje_en_curso, mock_validaciones, parada_1):
    parada_1.getter_hora_real.return_value = hora(9, 35)
    viaje_en_curso.cerrar_parada_actual()
    assert viaje_en_curso.validar_hora_resolucion(hora(10, 40), "fecha del incidente") is None
    mock_validaciones.validar_ventana.assert_called_once_with(hora(9, 35), hora(10, 40), nombre_inicio = "fecha de la parada previa", nombre_fin = "fecha del incidente")
# Ventana inválida se propaga
def test_validarHoraResolucion_anteriorALaSalida_sePropaga(viaje, mock_validaciones):
    mock_validaciones.validar_ventana.side_effect = VentanaInvalidaError(HORARIO, hora(8), "fecha de salida del viaje", "fecha de entrega")
    with pytest.raises(VentanaInvalidaError, match = re.escape("La fecha de salida del viaje (2026-10-11 09:00:00) debe ser anterior a la fecha de entrega (2026-10-11 08:00:00)")):
        viaje.validar_hora_resolucion(hora(8), "fecha de entrega")
def test_validarHoraResolucion_anteriorALaParadaPrevia_sePropaga(viaje_en_curso, mock_validaciones, parada_1):
    parada_1.getter_hora_real.return_value = hora(9, 35)
    viaje_en_curso.cerrar_parada_actual()
    mock_validaciones.validar_ventana.side_effect = VentanaInvalidaError(hora(9, 35), hora(9, 20), "fecha de la parada previa", "fecha del incidente")
    with pytest.raises(VentanaInvalidaError, match = re.escape("La fecha de la parada previa (2026-10-11 09:35:00) debe ser anterior a la fecha del incidente (2026-10-11 09:20:00)")):
        viaje_en_curso.validar_hora_resolucion(hora(9, 20), "fecha del incidente")


# ---------- cerrar_parada_actual ----------
# Quedan paradas pendientes
def test_cerrarParadaActual_ok(viaje_en_curso, parada_1, parada_2):
    assert viaje_en_curso.cerrar_parada_actual() is None
    assert viaje_en_curso.getter_estado() == "EN_CURSO"
    assert viaje_en_curso.paradas_pendientes() == [parada_2]
    assert viaje_en_curso.getter_paradas() == [parada_1, parada_2]
# Última parada: el viaje finaliza
def test_cerrarParadaActual_ultimaParada_finalizaElViaje(viaje_en_curso, parada_1, parada_2):
    viaje_en_curso.cerrar_parada_actual()
    viaje_en_curso.cerrar_parada_actual()
    assert viaje_en_curso.getter_estado() == "FINALIZADO"
    assert viaje_en_curso.paradas_pendientes() == []
    assert viaje_en_curso.getter_paradas() == [parada_1, parada_2]


# ---------- Setters ----------
def test_viaje_setterId(viaje):
    viaje.setter_id(7)
    assert viaje.getter_id() == 7
def test_viaje_setterEstado_ok(viaje, mock_validaciones):
    for estado in ("EN_CURSO", "FINALIZADO", "PLANIFICADO"):
        viaje.setter_estado(estado)
        assert viaje.getter_estado() == estado
        mock_validaciones.validar_en.assert_any_call(estado, opciones = ("PLANIFICADO", "EN_CURSO", "FINALIZADO"), nombre = "estado")
# Estado inválido se propaga
def test_viaje_setterEstado_invalido_sePropaga(viaje, mock_validaciones):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("El estado CANCELADO debe ser uno de: PLANIFICADO, EN_CURSO, FINALIZADO")
    with pytest.raises(DatoInvalidoError, match = "El estado CANCELADO debe ser uno de"):
        viaje.setter_estado("CANCELADO")
    assert viaje.getter_estado() == "PLANIFICADO"
# Los setters de listas guardan una copia
def test_viaje_setters_guardanUnaCopia(viaje, solicitud_a, solicitud_b, incidente, parada_1):
    solicitudes = [solicitud_a, solicitud_b]
    viaje.setter_solicitudes(solicitudes)
    solicitudes.clear()
    assert viaje.getter_solicitudes() == [solicitud_a, solicitud_b]
    incidentes = [incidente]
    viaje.setter_incidentes(incidentes)
    incidentes.clear()
    assert viaje.getter_incidentes() == [incidente]
    resueltas = [parada_1]
    viaje.setter_paradas_resueltas(resueltas)
    resueltas.clear()
    assert viaje.getter_paradas() == [parada_1]
# La cola respeta el orden y reemplaza a la anterior
def test_viaje_setterParadas_respetaElOrden(viaje, parada_1, parada_2):
    viaje.setter_paradas([parada_1, parada_2])
    assert viaje.paradas_pendientes() == [parada_1, parada_2]
    viaje.setter_paradas([parada_2])
    assert viaje.paradas_pendientes() == [parada_2]
    viaje.setter_paradas([])
    assert viaje.paradas_pendientes() == []
# La pila: la última solicitud recibida es la primera en deshacerse
def test_viaje_setterHistorialSolicitudes_ultimaEnSalirPrimero(viaje, solicitud_a, solicitud_b):
    viaje.setter_solicitudes([solicitud_a, solicitud_b])
    viaje.setter_historial_solicitudes([solicitud_a, solicitud_b])
    assert viaje.deshacer_ultima_solicitud() is solicitud_b
    assert viaje.deshacer_ultima_solicitud() is solicitud_a
    assert viaje.getter_solicitudes() == []


# ---------- deserializar ----------
ENCABEZADO = ["id", "id_transporte", "deposito", "horario", "estado", "solicitudes", "incidentes", "paradas", "paradas_resueltas", "historial_solicitudes", "Viaje"]
@pytest.fixture
def contexto(matriz, transporte, solicitud_a, solicitud_b, incidente, parada_1, parada_2):
    transporte.getter_id.return_value = 4
    incidente.getter_id.return_value = 7
    parada_1.getter_id.return_value = 10
    parada_2.getter_id.return_value = 11
    return {MatrizDistancia: matriz, Transporte: [transporte], Solicitud: [solicitud_a, solicitud_b],
            Incidente: [incidente], Parada: [parada_1, parada_2]}
# Viaje en curso: con una parada resuelta y otra pendiente
def test_viaje_deserializar_enCurso(mock_validaciones, contexto, matriz, transporte, solicitud_a, solicitud_b, incidente, parada_1, parada_2):
    archivo = [ENCABEZADO, ["3", "4", "Deposito", "2026-10-11 09:00:00", "EN_CURSO", "1,2", "7", "11", "10", "1,2"]]
    viajes = Viaje.deserializar(archivo, contexto)
    assert len(viajes) == 1
    viaje = viajes[0]
    assert viaje.getter_id() == 3
    assert viaje.getter_transporte() is transporte
    assert viaje.getter_deposito() == "Deposito"
    assert viaje.getter_horario() == HORARIO
    assert viaje.getter_matriz() is matriz
    assert viaje.getter_estado() == "EN_CURSO"
    assert viaje.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje.getter_incidentes() == [incidente]
    assert viaje.paradas_pendientes() == [parada_2]
    assert viaje.getter_paradas() == [parada_1, parada_2]
    assert viaje.es_parada_actual(parada_2)
    # Las solicitudes quedan asociadas al viaje
    solicitud_a.setter_viaje.assert_called_once_with(viaje)
    solicitud_b.setter_viaje.assert_called_once_with(viaje)
    # El próximo id continúa desde el mayor
    assert Viaje.curr_id == 3
# Viaje planificado: el historial permite deshacer en orden inverso
def test_viaje_deserializar_planificado(mock_validaciones, contexto, solicitud_a, solicitud_b):
    archivo = [ENCABEZADO, ["1", "4", "Deposito", "2026-10-11 09:00:00", "PLANIFICADO", "1,2", "", "", "", "1,2"]]
    viaje = Viaje.deserializar(archivo, contexto)[0]
    assert viaje.getter_estado() == "PLANIFICADO"
    assert viaje.getter_incidentes() == []
    assert viaje.getter_paradas() == []
    assert viaje.deshacer_ultima_solicitud() is solicitud_b
    assert viaje.deshacer_ultima_solicitud() is solicitud_a
    assert viaje.getter_solicitudes() == []
# Varios viajes y filas vacías
def test_viaje_deserializar_variosViajes(mock_validaciones, contexto, solicitud_a, solicitud_b):
    archivo = [ENCABEZADO,
               ["1", "4", "Deposito", "2026-10-11 09:00:00", "PLANIFICADO", "1", "", "", "", "1"],
               [],
               ["2", "4", "Deposito", "2026-10-12 08:00:00", "PLANIFICADO", "", "", "", "", ""]]
    viajes = Viaje.deserializar(archivo, contexto)
    assert list(map(lambda v: v.getter_id(), viajes)) == [1, 2]
    assert viajes[0].getter_solicitudes() == [solicitud_a]
    assert viajes[1].getter_solicitudes() == []
    assert viajes[1].getter_horario() == datetime(2026, 10, 12, 8, 0)
    assert Viaje.curr_id == 2
# Sin filas
def test_viaje_deserializar_soloEncabezado(mock_validaciones, contexto):
    assert Viaje.deserializar([ENCABEZADO], contexto) == []
    assert Viaje.curr_id == 0
# Los incidentes y las paradas son opcionales en el contexto (todavía no se cargaron)
def test_viaje_deserializar_sinIncidentesNiParadas(mock_validaciones, matriz, transporte, solicitud_a):
    transporte.getter_id.return_value = 4
    contexto = {MatrizDistancia: matriz, Transporte: [transporte], Solicitud: [solicitud_a]}
    archivo = [ENCABEZADO, ["1", "4", "Deposito", "2026-10-11 09:00:00", "PLANIFICADO", "1", "", "", "", "1"]]
    assert len(Viaje.deserializar(archivo, contexto)) == 1
# Transporte inexistente
def test_viaje_deserializar_transporteInexistente(mock_validaciones, contexto):
    with pytest.raises(KeyError):
        Viaje.deserializar([ENCABEZADO, ["1", "99", "Deposito", "2026-10-11 09:00:00", "PLANIFICADO", "", "", "", "", ""]], contexto)
# Lo serializado se puede volver a cargar
def test_viaje_serializar_deserializar(viaje_con_solicitudes, contexto, transporte, solicitud_a, solicitud_b):
    fila = list(map(str, viaje_con_solicitudes.serializar()))
    copia = Viaje.deserializar([ENCABEZADO, fila], contexto)[0]
    assert copia.getter_id() == viaje_con_solicitudes.getter_id()
    assert copia.getter_transporte() is transporte
    assert copia.getter_deposito() == viaje_con_solicitudes.getter_deposito()
    assert copia.getter_horario() == viaje_con_solicitudes.getter_horario()
    assert copia.getter_estado() == viaje_con_solicitudes.getter_estado()
    assert copia.getter_solicitudes() == [solicitud_a, solicitud_b]
    # El historial conserva el orden
    assert copia.deshacer_ultima_solicitud() is solicitud_b
