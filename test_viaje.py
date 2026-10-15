# ACTUALIZAR LOS TESTS DE ORDENAR_SOLICITUDES, COSTO_TOTAL Y DISTANCIA_TOTAL

import pytest
from datetime import datetime
import re
from viaje import Viaje
from solicitud import Solicitud
from articulo import Articulo
from parada import Parada
from cola import Cola
from pila import Pila
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
def articulo(mocker):
    return mocker.Mock(spec = Articulo)

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
def comprobante(mocker):
    return mocker.Mock(spec = Comprobante)

@pytest.fixture
def incidente(mocker):
    return mocker.Mock(spec = Incidente)

@pytest.fixture
def mock_solicitud_clase(mocker, solicitud_a):
    mock = mocker.patch("viaje.Solicitud")
    mock.return_value = solicitud_a
    return mock

@pytest.fixture
def mock_parada(mocker):
    mock = mocker.patch("viaje.Parada")
    def crear_parada_falsa(**kwargs):
        parada = mocker.Mock(spec = Parada)
        parada.getter_orden.return_value = kwargs["orden"]
        parada.getter_solicitud.return_value = kwargs["solicitud"]
        parada.getter_hora_prev.return_value = kwargs["hora_prev"]
        return parada
    mock.side_effect = crear_parada_falsa
    return mock

@pytest.fixture
def mock_incidente(mocker, incidente):
    mock = mocker.patch("viaje.Incidente")
    mock.return_value = incidente
    return mock

# Por defecto las políticas sugieren el orden de carga: A, B
@pytest.fixture
def mock_vecinos(mocker, solicitud_a, solicitud_b):
    mock = mocker.patch("viaje.Vecinos")
    mock.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    return mock

@pytest.fixture
def mock_ventanas(mocker, solicitud_a, solicitud_b):
    mock = mocker.patch("viaje.VentanasTiempo")
    mock.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    return mock

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
    return mocker.patch.object(Viaje, "_validar_estado", autospec = True)

@pytest.fixture
def mock_validar_recorrido(mocker):
    return mocker.patch.object(Viaje, "validar_recorrido", autospec = True, return_value = True)

# Fixtures para probar cada método sin depender de los demás: el estado se arma a mano y los colaboradores propios se mockean
@pytest.fixture
def viaje_cargado(viaje, solicitud_a, solicitud_b):
    viaje.solicitudes = [solicitud_a, solicitud_b]
    viaje.historial_solicitudes.apilar(solicitud_a)
    viaje.historial_solicitudes.apilar(solicitud_b)
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

# Clase Cola mockeada: lo que instancia iniciar_viaje es cola_paradas
@pytest.fixture
def mock_cola_clase(mocker, cola_paradas):
    mock = mocker.patch("viaje.Cola")
    mock.return_value = cola_paradas
    return mock

@pytest.fixture
def viaje_con_paradas(viaje, cola_paradas):
    viaje.estado = "EN_CURSO"
    viaje.paradas = cola_paradas
    return viaje

@pytest.fixture
def mock_agregar_solicitud(mocker):
    return mocker.patch.object(Viaje, "agregar_solicitud", autospec = True)

@pytest.fixture
def mock_distancia_total(mocker):
    return mocker.patch.object(Viaje, "distancia_total", autospec = True, return_value = 50)

@pytest.fixture
def mock_ordenar_solicitudes(mocker, solicitud_a, solicitud_b):
    return mocker.patch.object(Viaje, "ordenar_solicitudes", autospec = True, return_value = [solicitud_a, solicitud_b])

@pytest.fixture
def mock_finalizar_viaje(mocker):
    return mocker.patch.object(Viaje, "finalizar_viaje", autospec = True)

@pytest.fixture
def viaje_en_curso(viaje_con_solicitudes, mock_parada, mock_vecinos):
    viaje_con_solicitudes.iniciar_viaje()
    return viaje_con_solicitudes


# ---------- __init__ ----------
# Funcionamiento normal
def test_viaje_ok(viaje, transporte, matriz):
    assert viaje.transporte is transporte
    assert viaje.deposito == "Deposito"
    assert viaje.horario == HORARIO
    assert viaje.matriz is matriz
    assert viaje.estado == "PLANIFICADO"
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0
    assert viaje.solicitudes == []
    assert viaje.incidentes == []
    assert viaje.paradas.esVacia()
    assert isinstance(viaje.paradas, Cola)
    assert viaje.paradas_resueltas == []
    assert viaje.historial_solicitudes.esVacia()
    assert isinstance(viaje.historial_solicitudes, Pila)
    # id
    assert viaje.id == 1
    viaje2 = Viaje(transporte, "Deposito", HORARIO, matriz)
    assert viaje2.id == 2
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
def test_viaje_getters(viaje, transporte):
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
    viaje_en_curso.registrar_entrega(hora(9, 30), "Receptor", 100)
    paradas = viaje_en_curso.getter_paradas()
    assert list(map(lambda p: p.getter_solicitud(), paradas)) == [solicitud_a, solicitud_b]
    pendientes = viaje_en_curso.paradas_pendientes()
    assert list(map(lambda p: p.getter_solicitud(), pendientes)) == [solicitud_b]
    assert pendientes[0] is paradas[1]

def test_viaje_getters_conIncidente(viaje_en_curso, mock_incidente, incidente, solicitud_a, solicitud_b):
    assert viaje_en_curso.registrar_incidente("AUSENTE", hora(9, 30), "No había nadie") is incidente
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
    assert viaje.agregar_solicitud(solicitud_a) is None
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
    assert viaje.getter_peso() == 500 == viaje.transporte.getter_peso_max()
    assert viaje.getter_volumen() == 8 == viaje.transporte.getter_volumen()
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


# ---------- crear_solicitud ----------
# Funcionamiento normal
def test_crearSolicitud_ok(viaje, mock_validar_estado, mock_solicitud_clase, mock_agregar_solicitud, solicitud_a, articulo, mocker):
    articulo2 = mocker.Mock(spec = Articulo)
    resultado = viaje.crear_solicitud("Destino A", hora(9), hora(12), articulo, articulo2)
    assert isinstance(resultado, Solicitud)
    assert resultado is solicitud_a
    mock_validar_estado.assert_called_once_with(viaje, "crear_solicitud", "PLANIFICADO")
    mock_solicitud_clase.assert_called_once_with("Destino A", hora(9), hora(12), articulo, articulo2)
    mock_agregar_solicitud.assert_called_once_with(viaje, solicitud_a)
# Errores se propagan
def test_crearSolicitud_estadoInvalido_sePropaga(viaje, mock_validar_estado, mock_solicitud_clase, mock_agregar_solicitud, articulo):
    viaje.estado = "FINALIZADO"
    mock_validar_estado.side_effect = EstadoInvalidoError("crear_solicitud", "FINALIZADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede crear_solicitud porque el estado es FINALIZADO"):
        viaje.crear_solicitud("Destino A", hora(9), hora(12), articulo)
    mock_solicitud_clase.assert_not_called()
    mock_agregar_solicitud.assert_not_called()
def test_crearSolicitud_solicitudInvalida_sePropaga(viaje, mock_validar_estado, mock_solicitud_clase, mock_agregar_solicitud, articulo):
    mock_solicitud_clase.side_effect = DatoInvalidoError("El destino no debe estar vacío")
    with pytest.raises(DatoInvalidoError, match = "El destino no debe estar vacío"):
        viaje.crear_solicitud("   ", hora(9), hora(12), articulo)
    mock_agregar_solicitud.assert_not_called()
def test_crearSolicitud_agregarRechaza_sePropaga(viaje, mock_validar_estado, mock_solicitud_clase, mock_agregar_solicitud, articulo):
    mock_agregar_solicitud.side_effect = ExcesoPesoError(500, 600)
    with pytest.raises(ExcesoPesoError, match = "Capacidad excedida: El peso 600 supera el peso máximo del transporte 500"):
        viaje.crear_solicitud("Destino A", hora(9), hora(12), articulo)


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
    assert viaje_cargado.historial_solicitudes.ver_tope() == solicitud_b
    assert viaje_cargado.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje_cargado.getter_peso() == 350
    assert viaje_cargado.getter_volumen() == 6
    solicitud_b.setter_viaje.assert_not_called()
# historial vacio se propaga
def test_deshacerUltimaSolicitud_sinSolicitudes(viaje, mock_validar_estado, mocker):
    mock_historial = mocker.Mock(spec = Pila)
    mock_historial.esVacia.return_value = True
    viaje.historial_solicitudes = mock_historial
    with pytest.raises(ViajeVacioError, match = "No hay solicitudes para deshacer"):
        viaje.deshacer_ultima_solicitud()
    mock_historial.desapilar.assert_not_called()
    assert viaje.getter_peso() == 0
    assert viaje.getter_volumen() == 0


# ---------- validar_recorrido ----------
# Funcionamiento normal
def test_validarRecorrido_ok(viaje, matriz, solicitud_a, solicitud_b, mock_agregar_solicitud, mocker):
    assert viaje.validar_recorrido([]) is True
    matriz.obtener_distancia.assert_not_called()
    viaje.solicitudes = [solicitud_a]
    matriz.obtener_distancia.side_effect = [15, 10]
    # Llega 9:30 a Destino A. Sale 9:40 y llega 10:00 a Destino B
    solicitud_a.getter_ventana_fin.return_value = hora(9, 30)
    solicitud_b.getter_ventana_fin.return_value = hora(10)
    assert viaje.validar_recorrido([solicitud_a, solicitud_b]) is True
    assert matriz.obtener_distancia.call_args_list == [mocker.call("Deposito", "Destino A"), mocker.call("Destino A", "Destino B")]
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


# ---------- distancia_total ----------
def test_distanciaTotal_ok(viaje_cargado, solicitud_a, solicitud_b, matriz, mocker):
    matriz.obtener_distancia.side_effect = [15, 10, 25]
    assert viaje_cargado.distancia_total() == 50
    matriz.obtener_distancia.assert_any_call("Deposito", "Destino A")
    matriz.obtener_distancia.assert_any_call("Destino A", "Destino B")
    matriz.obtener_distancia.assert_any_call("Destino B", "Deposito")
    assert matriz.obtener_distancia.call_count == 3
def test_distanciaTotal_viajeVacio(viaje, matriz):
    matriz.obtener_distancia.return_value = 0
    assert viaje.distancia_total() == 0
    matriz.obtener_distancia.assert_called_once_with("Deposito", "Deposito")
def test_distanciaTotal_tramoFaltante_sePropaga(viaje_cargado, matriz):
    matriz.obtener_distancia.side_effect = [15, 10, RutaIncompletaError("Destino B", "Deposito")]
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Destino B a Deposito"):
        viaje_cargado.distancia_total()


# A futuro: Costo total y el cálculo de impacto ambiental (delegado en transporte)
# ---------- costo_total e impacto_ambiental ----------
def test_costoTotal_ok(viaje_cargado, mock_distancia_total, transporte):
    # 50 km * $2 / km + 2 paradas * $5 / parada = $110
    assert viaje_cargado.costo_total() == 110
    transporte.getter_costo_km.assert_called_once_with()
    transporte.getter_costo_parada.assert_called_once_with()
    mock_distancia_total.assert_called_once_with(viaje_cargado)
def test_costoTotal_viajeVacio(viaje, mock_distancia_total, transporte):
    mock_distancia_total.return_value = 0
    assert viaje.costo_total() == 0
def test_impactoAmbiental_delegaEnElTransporte(viaje_cargado, transporte, mock_distancia_total):
    transporte.calcular_impacto_ambiental.return_value = 13.5
    assert viaje_cargado.impacto_ambiental() == 13.5
    transporte.calcular_impacto_ambiental.assert_called_once_with(50, 350)


# ---------- setter_estado ----------
# Funcionamiento normal
def test_viaje_setterEstado_ok(viaje, mock_validaciones):
    assert viaje.getter_estado() == "PLANIFICADO"
    viaje.setter_estado("EN_CURSO")
    assert viaje.getter_estado() == "EN_CURSO"
    mock_validaciones.validar_en.assert_called_with("EN_CURSO", opciones = "PLANIFICADO, EN_CURSO, FINALIZADO", nombre = "estado del viaje")
    viaje.setter_estado("FINALIZADO")
    assert viaje.getter_estado() == "FINALIZADO"
    mock_validaciones.validar_en.assert_called_with("FINALIZADO", opciones = "PLANIFICADO, EN_CURSO, FINALIZADO", nombre = "estado del viaje")
# Estado inválido
def test_viaje_setterEstado_invalido_sePropaga(viaje, mock_validaciones):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("El estado del viaje debe ser uno de")
    with pytest.raises(DatoInvalidoError, match = "El estado del viaje debe ser uno de"):
        viaje.setter_estado("MODIFICADO")
    assert viaje.getter_estado() == "PLANIFICADO"
# Transicion ilegal
def test_viaje_setterEstado_transicionIlegal(viaje, mock_validaciones):
    # PLANIFICADO --> FINALIZADO ERROR
    assert viaje.getter_estado() == "PLANIFICADO"
    with pytest.raises(TransicionIlegalError, match = "PLANIFICADO -> EN_CURSO -> FINALIZADO"):
        viaje.setter_estado("FINALIZADO")
    assert viaje.getter_estado() == "PLANIFICADO"
    # EN_CURSO --> PLANIFICADO ERROR
    viaje.estado = "EN_CURSO"
    with pytest.raises(TransicionIlegalError):
        viaje.setter_estado("PLANIFICADO")
    assert viaje.getter_estado() == "EN_CURSO"
    # FINALIZADO --> PLANIFICADO O EN_CURSO ERROR 
    viaje.estado = "FINALIZADO"
    with pytest.raises(TransicionIlegalError):
        viaje.setter_estado("PLANIFICADO")
    with pytest.raises(TransicionIlegalError):
        viaje.setter_estado("EN_CURSO")
    assert viaje.getter_estado() == "FINALIZADO"
    assert mock_validaciones.validar_en.call_count == 4


# ---------- ordenar_solicitudes ----------
# Funcionamiento normal
def test_ordenarSolicitudes_vecinos_ok(viaje_cargado, mock_vecinos, mock_ventanas, mock_validar_recorrido, matriz, solicitud_a, solicitud_b):
    # Vecinos funciona y orden válido
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    mock_validar_recorrido.return_value = True
    assert viaje_cargado.ordenar_solicitudes() == [solicitud_b, solicitud_a]
    mock_vecinos.sugerir_orden.assert_called_once_with("Deposito", [solicitud_a, solicitud_b], matriz)
    mock_validar_recorrido.assert_called_once_with(viaje_cargado, [solicitud_b, solicitud_a])
    mock_ventanas.sugerir_orden.assert_not_called()
    assert viaje_cargado.getter_solicitudes() == [solicitud_a, solicitud_b]
    assert viaje_cargado.getter_estado() == "PLANIFICADO"
def test_ordenarSolicitudes_ventanas_ok(viaje_cargado, mock_vecinos, mock_ventanas, mock_validar_recorrido, matriz, solicitud_a, solicitud_b):
    # Vecinos funciona, orden no valido, y ventanas funciona con orden válido
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    mock_validar_recorrido.side_effect = [VentanaIncumplidaError("Destino A", "10:30", "10:20"), True]
    assert viaje_cargado.ordenar_solicitudes() == [solicitud_a, solicitud_b]
    mock_vecinos.sugerir_orden.assert_called_with("Deposito", [solicitud_a, solicitud_b], matriz)
    assert mock_validar_recorrido.call_count == 2
    mock_validar_recorrido.assert_any_call(viaje_cargado, [solicitud_b, solicitud_a])
    mock_validar_recorrido.assert_any_call(viaje_cargado, [solicitud_a, solicitud_b])
    mock_ventanas.sugerir_orden.assert_called_once_with("Deposito", [solicitud_a, solicitud_b], matriz)
def test_ordenarSolicitudes_vecinosNo_ventana_ok(viaje_cargado, mock_vecinos, mock_ventanas, mock_validar_recorrido, matriz, solicitud_a, solicitud_b):
    # Vecinos no funciona, y ventanas funciona con orden válido
    mock_vecinos.sugerir_orden.side_effect = RutaIncompletaError("Destino B", "Destino A")
    mock_ventanas.sugerir_orden.return_value = [solicitud_a, solicitud_b]
    mock_validar_recorrido.return_value = True
    assert viaje_cargado.ordenar_solicitudes() == [solicitud_a, solicitud_b]
    mock_vecinos.sugerir_orden.assert_called_with("Deposito", [solicitud_a, solicitud_b], matriz)
    assert mock_validar_recorrido.call_count == 1
    mock_validar_recorrido.assert_called_once_with(viaje_cargado, [solicitud_a, solicitud_b])
    mock_ventanas.sugerir_orden.assert_called_once_with("Deposito", [solicitud_a, solicitud_b], matriz)
# Ninguna
def test_ordenarSolicitudes_vecinosYVentanaFallan(viaje_cargado, mock_vecinos, mock_ventanas, mock_validar_recorrido, solicitud_a, solicitud_b):
    mock_vecinos.sugerir_orden.side_effect = RutaIncompletaError("Deposito", "Destino B")
    mock_ventanas.sugerir_orden.side_effect = RutaIncompletaError("Deposito", "Destino B")
    assert viaje_cargado.ordenar_solicitudes() == [solicitud_a, solicitud_b]
    mock_validar_recorrido.assert_not_called()
# Ambos recorridos inválidos
def test_ordenarSolicitudes_validarRecorridoFalla(viaje_cargado, mock_vecinos, mock_ventanas, mock_validar_recorrido, solicitud_a, solicitud_b):
    mock_vecinos.sugerir_orden.return_value = [solicitud_b, solicitud_a]
    mock_ventanas.sugerir_orden.return_value = [solicitud_b, solicitud_a]
    mock_validar_recorrido.side_effect = VentanaIncumplidaError("Destino A", hora(11), hora(10, 45))
    assert viaje_cargado.ordenar_solicitudes() == [solicitud_a, solicitud_b]
    assert mock_validar_recorrido.call_count == 2


# ---------- iniciar_viaje ----------
# Funcionamiento normal
def test_iniciarViaje_ok(viaje_cargado, matriz, mocker, mock_validar_estado, mock_ordenar_solicitudes, mock_parada, mock_cola_clase, cola_paradas, solicitud_a, solicitud_b, transporte):
    matriz.obtener_distancia.side_effect = [15, 10]
    viaje_cargado.iniciar_viaje()
    mock_validar_estado.assert_called_once_with(viaje_cargado, "iniciar_viaje", "PLANIFICADO")
    mock_ordenar_solicitudes.assert_called_once_with(viaje_cargado)
    mock_cola_clase.assert_called_once_with()
    assert viaje_cargado.paradas_resueltas == []
    # solicitud a
    solicitud_a.getter_destino.assert_called_once()
    matriz.obtener_distancia.assert_any_call == ("Deposito", "Destino A")
    assert transporte.getter_velocidad.call_count == 2
    solicitud_a.getter_ventana_inicio.assert_called_once()
    mock_parada.assert_any_call(orden = 1, solicitud = solicitud_a, hora_prev = hora(9, 30), hora_real = None)
    # solicitud b
    solicitud_b.getter_destino.assert_called_once()
    matriz.obtener_distancia.assert_any_call == ("Destino A", "Destino B")
    assert solicitud_b.getter_ventana_inicio.call_count == 2
    mock_parada.assert_any_call(orden = 2, solicitud = solicitud_b, hora_prev = hora(10, 30), hora_real = None)
    assert viaje_cargado.paradas is cola_paradas
    assert mock_parada.call_count == 2
    assert viaje_cargado.getter_estado() == "EN_CURSO"
    paradas_encoladas = map(lambda l: l.args[0], cola_paradas.encolar.call_args_list)
    assert list(map(lambda p: p.getter_solicitud(), paradas_encoladas)) == [solicitud_a, solicitud_b]
# Usa el orden de ordenar_solicitudes
def test_iniciarViaje_ordenInverso(viaje_cargado, matriz, mocker, mock_validar_estado, mock_ordenar_solicitudes, mock_parada, mock_cola_clase, cola_paradas, solicitud_a, solicitud_b):
    mock_ordenar_solicitudes.return_value = [solicitud_b, solicitud_a]
    matriz.obtener_distancia.side_effect = [25, 10]
    viaje_cargado.iniciar_viaje()
    assert viaje_cargado.getter_solicitudes() == [solicitud_b, solicitud_a]
    mock_parada.assert_any_call(orden = 1, solicitud = solicitud_b, hora_prev = hora(10, 30), hora_real = None)
    mock_parada.assert_any_call(orden = 2, solicitud = solicitud_a, hora_prev = hora(11), hora_real = None)
# Estado inválido se propaga
def test_iniciarViaje_estadoInvalido_sePropaga(viaje_cargado, mock_validar_estado, mock_ordenar_solicitudes, mock_parada, mock_cola_clase):
    mock_validar_estado.side_effect = EstadoInvalidoError("iniciar_viaje", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede iniciar_viaje porque el estado es EN_CURSO"):
        viaje_cargado.iniciar_viaje()
    assert viaje_cargado.getter_estado() == "PLANIFICADO"
    mock_ordenar_solicitudes.assert_not_called()
    mock_parada.assert_not_called()
    mock_cola_clase.assert_not_called()
# ViajeVacio error
def test_iniciarViaje_viajeVacio(viaje, mock_validar_estado, mock_ordenar_solicitudes, mock_parada, mock_cola_clase):
    with pytest.raises(ViajeVacioError, match = "Viaje Vacio: El viaje aún no tiene solicitudes"):
        viaje.iniciar_viaje()
    assert viaje.getter_estado() == "PLANIFICADO"
    mock_ordenar_solicitudes.assert_not_called()
    mock_parada.assert_not_called()
    mock_cola_clase.assert_not_called()
# Éste error no debería suceder nunca. Pero si cambiamos el proyecto, para que no se vayan validando las solicitudes cuando se agregan, y se valida solo al inicio el viaje, entonces en ese caso ésto es útil
def test_iniciarViaje_tramoFaltante_sePropaga(viaje_cargado, matriz, mock_validar_estado, mock_ordenar_solicitudes, mock_parada, mock_cola_clase):
    matriz.obtener_distancia.side_effect = RutaIncompletaError("Deposito", "Destino A")
    with pytest.raises(RutaIncompletaError):
        viaje_cargado.iniciar_viaje()
    assert viaje_cargado.getter_estado() == "PLANIFICADO"
    mock_parada.assert_not_called()


# ---------- _validar_estado ----------
# Funcionamiento normal
def test_validarEstado_estadoCorrecto_noLanza(viaje):
    assert viaje.estado == "PLANIFICADO"
    assert viaje._validar_estado("iniciar_viaje", "PLANIFICADO") is None
    viaje.estado = "EN_CURSO"
    assert viaje._validar_estado("registrar_entrega", "EN_CURSO") is None
    viaje.estado = "FINALIZADO"
    assert viaje._validar_estado("mostrar detalles", "FINALIZADO") is None
# EstadoInvalido
def test_validarEstado_estadoInvalido(viaje):
    # Desde planificado
    assert viaje.estado == "PLANIFICADO"
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es PLANIFICADO"):
        viaje._validar_estado("registrar_entrega", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede mostrar_detalles porque el estado es PLANIFICADO"):
        viaje._validar_estado("mostrar_detalles", "FINALIZADO")
    assert viaje.estado == "PLANIFICADO"
    # Desde en_curso
    viaje.estado = "EN_CURSO"
    with pytest.raises(EstadoInvalidoError, match = "No se puede iniciar_viaje porque el estado es EN_CURSO"):
        viaje._validar_estado("iniciar_viaje", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede mostrar_detalles porque el estado es EN_CURSO"):
        viaje._validar_estado("mostrar_detalles", "FINALIZADO")
    # Desde finalizado
    viaje.estado = "FINALIZADO"
    with pytest.raises(EstadoInvalidoError, match = "No se puede iniciar_viaje porque el estado es FINALIZADO"):
        viaje._validar_estado("iniciar_viaje", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es FINALIZADO"):
        viaje._validar_estado("registrar_entrega", "EN_CURSO")


# ---------- registrar_entrega ----------
# Funcionamiento normal
def test_registrarEntrega_ok(viaje_con_paradas, cola_paradas, parada_1, comprobante, mock_validar_estado, mock_validaciones, mock_finalizar_viaje):
    parada_1.generar_comprobante.return_value = comprobante
    resultado = viaje_con_paradas.registrar_entrega(hora(9, 35), "Juan", 100)
    assert resultado is comprobante
    mock_validar_estado.assert_called_once_with(viaje_con_paradas, "registrar_entrega", "EN_CURSO")
    mock_validaciones.validar_ventana.assert_called_once_with(HORARIO, hora(9, 35), nombre_inicio = "fecha de salida del viaje", nombre_fin = "fecha de entrega")
    assert cola_paradas.esVacia.call_count == 2
    cola_paradas.frente.assert_called_once_with()
    parada_1.generar_comprobante.assert_called_once_with("Juan", hora(9, 35), 100)
    cola_paradas.desencolar.assert_called_once_with()
    assert viaje_con_paradas.paradas_resueltas == [parada_1]
    mock_finalizar_viaje.assert_not_called()
def test_registrarEntrega_conParadaPrevia(mocker, viaje_con_paradas, parada_1, parada_2, mock_validar_estado, mock_validaciones, cola_paradas, mock_finalizar_viaje):
    comprobante2 = mocker.Mock(spec = Comprobante)
    cola_paradas.frente.side_effect = [parada_1, parada_2]
    cola_paradas.desencolar.side_effect = [parada_1, parada_2]
    cola_paradas.esVacia.side_effect = [False, False, False, True]
    parada_1.generar_comprobante.return_value = comprobante
    parada_2.generar_comprobante.return_value = comprobante2
    assert viaje_con_paradas.registrar_entrega(hora(9, 35), "Massimo", 120) is comprobante
    parada_1.getter_hora_real.return_value = hora(9, 35)
    assert viaje_con_paradas.registrar_entrega(hora(10, 40), "Uriel", 120) is comprobante2
    parada_1.generar_comprobante.assert_called_once_with("Massimo", hora(9, 35), 120)
    parada_2.generar_comprobante.assert_called_once_with("Uriel", hora(10, 40), 120)
    mock_validaciones.validar_ventana.assert_any_call(hora(9, 35), hora(10, 40), nombre_inicio = "fecha de la parada previa", nombre_fin = "fecha de entrega")
    assert viaje_con_paradas.paradas_resueltas == [parada_1, parada_2]
    mock_finalizar_viaje.assert_called_once_with(viaje_con_paradas)
# Estado inválido se propaga
def test_registrarEntrega_estadoInvalido_sePropaga(viaje_con_paradas, cola_paradas, parada_1, mock_validar_estado, mock_validaciones):
    viaje_con_paradas.estado = "PLANIFICADO"
    mock_validar_estado.side_effect = EstadoInvalidoError("registrar_entrega", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_entrega porque el estado es PLANIFICADO"):
        viaje_con_paradas.registrar_entrega(hora(10), "Juan", 100)
    mock_validaciones.validar_ventana.assert_not_called()
    parada_1.generar_comprobante.assert_not_called()
    cola_paradas.desencolar.assert_not_called()
# Ventana inválida
def test_registrarEntrega_ventanaInvalida_sePropaga(viaje_con_paradas, cola_paradas, parada_1, parada_2, mock_validar_estado, mock_validaciones):
    viaje_con_paradas.paradas_resueltas.append(parada_2)
    parada_2.getter_hora_real.return_value = HORARIO
    mock_validaciones.validar_ventana.side_effect = VentanaInvalidaError(HORARIO, hora(8), "fecha de la parada previa", "fecha de entrega")
    with pytest.raises(VentanaInvalidaError, match = re.escape("La fecha de la parada previa (2026-10-11 09:00:00) debe ser anterior a la fecha de entrega (2026-10-11 08:00:00)")):
        viaje_con_paradas.registrar_entrega(hora(8), "Manuel", 100)
    mock_validaciones.validar_ventana.assert_called_once_with(HORARIO, hora(8), nombre_inicio = "fecha de la parada previa", nombre_fin = "fecha de entrega")
    parada_1.generar_comprobante.assert_not_called()
    cola_paradas.desencolar.assert_not_called()
# sin paradas pendientes
def test_registrarEntrega_sinParadasPendientes(viaje_con_paradas, cola_paradas, mock_validar_estado, mock_validaciones):
    cola_paradas.esVacia.return_value = True
    with pytest.raises(SinParadasPendientesError, match = "Sin paradas pendientes: No se puede registrar_entrega"):
        viaje_con_paradas.registrar_entrega(hora(10), "Massimo", 100)
    cola_paradas.frente.assert_not_called()
    cola_paradas.desencolar.assert_not_called()
    assert viaje_con_paradas.paradas_resueltas == []
# comprobanteInvalido se propaga
def test_registrarEntrega_comprobanteInvalido_sePropaga(viaje_con_paradas, cola_paradas, parada_1, mock_validar_estado, mock_finalizar_viaje, mock_validaciones):
    parada_1.generar_comprobante.side_effect = DatoInvalidoError("El receptor no debe estar vacío")
    with pytest.raises(DatoInvalidoError, match = "El receptor no debe estar vacío"):
        viaje_con_paradas.registrar_entrega(hora(9, 35), "   ", 1500)
    cola_paradas.desencolar.assert_not_called()
    assert viaje_con_paradas.paradas_resueltas == []
    mock_finalizar_viaje.assert_not_called()


# ---------- registrar_incidente ----------
# Funcionamiento normal
def test_registrarIncidente_ok(viaje_con_paradas, cola_paradas, parada_1, mock_validar_estado, mock_validaciones, mock_incidente, incidente, solicitud_a, mock_finalizar_viaje):
    resultado = viaje_con_paradas.registrar_incidente("DAÑO", hora(9, 40), "Pinchazo", rueda = "delantera", costo = 500)
    assert resultado is incidente
    mock_validar_estado.assert_called_once_with(viaje_con_paradas, "registrar_incidente", "EN_CURSO")
    mock_validaciones.validar_ventana.assert_called_once_with(HORARIO, hora(9, 40), nombre_inicio = "fecha de salida del viaje", nombre_fin = "fecha del incidente")
    mock_incidente.assert_called_once_with("DAÑO", hora(9, 40), "Pinchazo", solicitud_a, rueda = "delantera", costo = 500)
    assert viaje_con_paradas.getter_incidentes() == [incidente]
    parada_1.setter_estado.assert_called_once_with("FALLIDA")
    parada_1.setter_hora_real.assert_called_once_with(hora(9, 40))
    parada_1.generar_comprobante.assert_not_called()
    assert cola_paradas.esVacia.call_count == 2
    cola_paradas.desencolar.assert_called_once_with()
    assert viaje_con_paradas.paradas_resueltas == [parada_1]
    mock_finalizar_viaje.assert_not_called()
# con parada previa
def test_registrarIncidente_conParadaPrevia(viaje_con_paradas, parada_1, mocker, mock_validar_estado, mock_validaciones, mock_incidente, mock_finalizar_viaje):
    parada_previa = mocker.Mock(spec = Parada)
    parada_previa.getter_hora_real.return_value = hora(9, 40)
    viaje_con_paradas.paradas_resueltas.append(parada_previa)
    viaje_con_paradas.registrar_incidente("DAÑO", hora(10, 45), "Caja rota")
    mock_validaciones.validar_ventana.assert_called_once_with(hora(9, 40), hora(10, 45), nombre_inicio = "fecha de la parada previa", nombre_fin = "fecha del incidente")
    assert viaje_con_paradas.paradas_resueltas == [parada_previa, parada_1]
def test_registrarIncidente_finalizarViaje(viaje_con_paradas, cola_paradas, mock_validar_estado, mock_incidente, mock_finalizar_viaje, mock_validaciones, parada_1):
    cola_paradas.esVacia.side_effect = [False, True]
    viaje_con_paradas.registrar_incidente("AUSENTE", hora(9, 40), "No había nadie")
    mock_finalizar_viaje.assert_called_once_with(viaje_con_paradas)
# Estado inválido error se propaga
def test_registrarIncidente_estadoInvalido_sePropaga(viaje_con_paradas, cola_paradas, mock_validar_estado, mock_validaciones, mock_incidente):
    viaje_con_paradas.estado = "PLANIFICADO"
    mock_validar_estado.side_effect = EstadoInvalidoError("registrar_incidente", "PLANIFICADO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede registrar_incidente porque el estado es PLANIFICADO"):
        viaje_con_paradas.registrar_incidente("DAÑO", hora(10), "Pinchazo")
    mock_validaciones.validar_ventana.assert_not_called()
    mock_incidente.assert_not_called()
    assert viaje_con_paradas.getter_incidentes() == []
    cola_paradas.desencolar.assert_not_called()
# Ventana inválida error se propaga
def test_registrarIncidente_anteriorALaSalida_sePropaga(viaje_con_paradas, cola_paradas, mock_validar_estado, mock_validaciones, mock_incidente):
    mock_validaciones.validar_ventana.side_effect = VentanaInvalidaError(HORARIO, hora(8), "fecha de salida del viaje", "fecha del incidente")
    with pytest.raises(VentanaInvalidaError, match = re.escape("La fecha de salida del viaje (2026-10-11 09:00:00) debe ser anterior a la fecha del incidente (2026-10-11 08:00:00)")):
        viaje_con_paradas.registrar_incidente("DAÑO", hora(8), "Pinchazo")
    mock_validaciones.validar_ventana.assert_called_once_with(HORARIO, hora(8), nombre_inicio = "fecha de salida del viaje", nombre_fin = "fecha del incidente")
    mock_incidente.assert_not_called()
    assert viaje_con_paradas.getter_incidentes() == []
    cola_paradas.desencolar.assert_not_called()
# Sin paradas pendientes
def test_registrarIncidente_sinParadasPendientes(viaje_con_paradas, cola_paradas, mock_validar_estado, mock_incidente, mock_validaciones):
    cola_paradas.esVacia.return_value = True
    with pytest.raises(SinParadasPendientesError, match = "Sin paradas pendientes: No se puede registrar_incidente"):
        viaje_con_paradas.registrar_incidente("DAÑO", hora(10), "Pinchazo")
    mock_incidente.assert_not_called()
    assert viaje_con_paradas.getter_incidentes() == []
    cola_paradas.frente.assert_not_called()
    cola_paradas.desencolar.assert_not_called()
# Incidente inválido se propaga
def test_registrarIncidente_incidenteInvalido_sePropaga(viaje_con_paradas, cola_paradas, parada_1, mock_validar_estado, mock_validaciones, mock_incidente, mock_finalizar_viaje):
    mock_incidente.side_effect = DatoInvalidoError("El tipo debe ser uno de: DAÑO, AUSENTE, RETRASO")
    with pytest.raises(DatoInvalidoError, match = "El tipo debe ser uno de: DAÑO, AUSENTE, RETRASO"):
        viaje_con_paradas.registrar_incidente("CHOQUE", hora(9, 40), "Pinchazo")
    parada_1.setter_estado.assert_not_called()
    parada_1.setter_hora_real.assert_not_called()
    cola_paradas.desencolar.assert_not_called()
    assert viaje_con_paradas.getter_incidentes() == []
    assert viaje_con_paradas.paradas_resueltas == []
    mock_finalizar_viaje.assert_not_called()


# ---------- finalizar_viaje ----------
# Funcionamiento normal
def test_finalizarViaje_ok(viaje_con_paradas, cola_paradas, mock_validar_estado):
    cola_paradas.esVacia.return_value = True
    assert viaje_con_paradas.finalizar_viaje() is None
    mock_validar_estado.assert_called_once_with(viaje_con_paradas, "finalizar_viaje", "EN_CURSO")
    cola_paradas.esVacia.assert_called_once()
    assert viaje_con_paradas.getter_estado() == "FINALIZADO"
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