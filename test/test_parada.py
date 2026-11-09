import pytest
from datetime import datetime
from parada import Parada
from solicitud import Solicitud
from viaje import Viaje
from comprobante import Comprobante
from excepciones import EstadoInvalidoError, DatoInvalidoError

HORA_PREV = datetime(2026, 10, 11, 9, 30)
HORA_REAL = datetime(2026, 10, 11, 10, 5)

@pytest.fixture(autouse = True)
def resetearId():
    Parada.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("parada.Validaciones")
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    mock.validar_instancia.side_effect = lambda valor, **kwargs: valor
    mock.validar_fecha.side_effect = lambda valor, **kwargs: valor
    mock.validar_en.side_effect = lambda valor, **kwargs: valor
    return mock

# Viaje en curso donde la parada es la actual (las operaciones de la parada lo exigen)
@pytest.fixture
def viaje(mocker):
    mock = mocker.Mock(spec = Viaje)
    mock.es_parada_actual.return_value = True
    return mock

@pytest.fixture
def solicitud(mocker, viaje):
    mock = mocker.Mock(spec = Solicitud)
    mock.getter_comprobante.return_value = None
    mock.getter_destino.return_value = "Destino 1"
    mock.getter_viaje.return_value = viaje
    return mock

@pytest.fixture
def mock_comprobante(mocker):
    mock = mocker.patch("parada.Comprobante")
    mock.return_value = mock
    return mock

@pytest.fixture
def parada(solicitud, mock_validaciones):
    return Parada(1, solicitud, HORA_PREV, None)

# Funcionamiento normal
def test_parada_ok(parada, solicitud):
    assert parada.getter_orden() == 1
    assert parada.getter_solicitud() is solicitud
    assert parada.getter_hora_prev() == HORA_PREV
    assert parada.getter_hora_real() is None
    assert parada.getter_estado() == "PENDIENTE"
    assert parada.getter_comprobante() is None
    # id
    assert parada.getter_id() == 1
    parada2 = Parada(2, solicitud, HORA_PREV, None)
    assert parada2.getter_id() == 2
def test_parada_horaRealNone(parada):
    assert parada.getter_hora_real() is None
# Getters
def test_parada_getters(parada, solicitud):
    assert parada.getter_estado() == "PENDIENTE"
    assert parada.getter_solicitud() is solicitud
    assert parada.getter_orden() == 1
    assert parada.getter_hora_prev() == HORA_PREV
    assert parada.getter_hora_real() is None
    assert parada.getter_comprobante() is None
    assert parada.getter_id() == 1
# Metodos mágicos
def test_parada_metodosMagicos(parada):
    assert str(parada) == "Parada 1 [PENDIENTE] -> Destino 1 a las 09:30"
    assert repr(parada) == "<Parada 1 PENDIENTE>"
    parada.restaurar_estado("ENTREGADA")
    parada.setter_hora_real(HORA_REAL)
    assert str(parada) == "Parada 1 [ENTREGADA] -> Destino 1 a las 10:05 (REAL)"
    assert repr(parada) == "<Parada 1 ENTREGADA>"
# Validaciones
def test_parada_validaciones(mock_validaciones, solicitud):
    Parada(3, solicitud, HORA_PREV, HORA_REAL)
    mock_validaciones.validar_numero.assert_called_once_with(3, entero = True, nombre = "orden de la parada")
    mock_validaciones.validar_instancia.assert_called_once_with(solicitud, clase = Solicitud, nombre = "solicitud")
    assert mock_validaciones.validar_fecha.call_count == 2
    mock_validaciones.validar_fecha.assert_any_call(HORA_PREV, nombre = "hora_prev")
    mock_validaciones.validar_fecha.assert_any_call(HORA_REAL, vacio = True, nombre = "hora_real")
# Errores en __init__
def test_parada_ordenNoNumero_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_numero.side_effect = TypeError("El orden debe ser numero")
    with pytest.raises(TypeError, match = "El orden debe ser numero"):
        Parada("uno", solicitud, HORA_PREV, None)
    assert Parada.curr_id == 0
def test_parada_ordenNoEntero_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("El orden debe ser entero")
    with pytest.raises(DatoInvalidoError, match = "El orden debe ser entero"):
        Parada(1.5, solicitud, HORA_PREV, None)
    assert Parada.curr_id == 0
def test_parada_ordenNegativo_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("El orden no puede ser negativo")
    with pytest.raises(DatoInvalidoError, match = "El orden no puede ser negativo"):
        Parada(-1, solicitud, HORA_PREV, None)
    assert Parada.curr_id == 0
def test_parada_solicitudInvalida_sePropaga(mock_validaciones):
    mock_validaciones.validar_instancia.side_effect = TypeError("La solicitud no es Solicitud")
    with pytest.raises(TypeError, match = "La solicitud no es Solicitud"):
        Parada(1, "solicitud", HORA_PREV, None)
    assert Parada.curr_id == 0
def test_parada_horaPrevInvalida_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_fecha.side_effect = TypeError("La fecha debe ser datetime")
    with pytest.raises(TypeError, match = "La fecha debe ser datetime"):
        Parada(1, solicitud, "9AM", None)
    assert Parada.curr_id == 0
def test_parada_horaRealInvalida_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_fecha.side_effect = [HORA_PREV, TypeError("La fecha debe ser datetime")]
    with pytest.raises(TypeError, match = "La fecha debe ser datetime"):
        Parada(1, solicitud, HORA_PREV, "10AM")
    assert Parada.curr_id == 0

# Generar_comprobante
def test_parada_generarComprobante_ok(parada, solicitud, viaje, mock_comprobante):
    resultado = parada.generar_comprobante("Juan", HORA_REAL, 100)
    viaje.es_parada_actual.assert_called_once_with(parada)
    mock_comprobante.assert_called_once_with(solicitud, HORA_REAL, "Juan", 100)
    assert resultado is mock_comprobante
    assert parada.getter_comprobante() is mock_comprobante
    solicitud.setter_comprobante.assert_called_once_with(mock_comprobante)
    assert parada.getter_hora_real() == HORA_REAL
    assert parada.getter_estado() == "ENTREGADA"
def test_parada_generarComprobante_sinViaje(parada, solicitud, mock_comprobante):
    solicitud.getter_viaje.return_value = None
    with pytest.raises(EstadoInvalidoError, match = "la parada no es la actual de un viaje en curso"):
        parada.generar_comprobante("Juan", HORA_REAL, 100)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()
    assert parada.getter_estado() == "PENDIENTE"
    assert parada.getter_hora_real() is None
def test_parada_generarComprobante_noEsLaParadaActual(parada, solicitud, viaje, mock_comprobante):
    viaje.es_parada_actual.return_value = False
    with pytest.raises(EstadoInvalidoError, match = "la parada no es la actual de un viaje en curso"):
        parada.generar_comprobante("Juan", HORA_REAL, 100)
    viaje.es_parada_actual.assert_called_once_with(parada)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()
    assert parada.getter_estado() == "PENDIENTE"
    assert parada.getter_comprobante() is None
def test_parada_generarComprobanteDuplicado(parada, solicitud, mock_comprobante, mocker):
    solicitud.getter_comprobante.return_value = mocker.Mock(spec = Comprobante)
    with pytest.raises(EstadoInvalidoError):
        parada.generar_comprobante("Manuel", HORA_REAL, 100)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()
    assert parada.getter_estado() == "PENDIENTE"
    assert parada.getter_hora_real() is None
    assert parada.getter_comprobante() is None
def test_parada_generarComprobante_yaEntregada(parada, solicitud, mock_comprobante):
    parada.restaurar_estado("ENTREGADA")
    with pytest.raises(EstadoInvalidoError):
        parada.generar_comprobante("Massimo", HORA_REAL, 100)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()
def test_parada_generarComprobante_yaFallida(parada, solicitud, mock_comprobante):
    parada.restaurar_estado("FALLIDA")
    with pytest.raises(EstadoInvalidoError):
        parada.generar_comprobante("Uriel", HORA_REAL, 100)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()

# Setter estado
def test_parada_setterEstado_ok(parada, mock_validaciones):
    parada.setter_estado("FALLIDA")
    assert parada.getter_estado() == "FALLIDA"
    mock_validaciones.validar_en.assert_called_once_with("FALLIDA", opciones = "FALLIDA, ENTREGADA", nombre = "estado")
# Setter estado errores
def test_parada_estadoInvalido_sePropaga(parada, mock_validaciones):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("Estado inválido")
    with pytest.raises(DatoInvalidoError, match = "Estado inválido"):
        parada.setter_estado("REORDENADA")
    assert parada.getter_estado() == "PENDIENTE"
def test_parada_correccionEstadoError(parada):
    # Entregada a fallida
    parada.restaurar_estado("ENTREGADA")
    with pytest.raises(EstadoInvalidoError):
        parada.setter_estado("FALLIDA")
    assert parada.getter_estado() == "ENTREGADA"
    # Fallida a entregada
    parada.restaurar_estado("FALLIDA")
    with pytest.raises(EstadoInvalidoError):
        parada.setter_estado("ENTREGADA")
    assert parada.getter_estado() == "FALLIDA"
def test_parada_setterEstado_fueraDeTurno(parada, viaje):
    viaje.es_parada_actual.return_value = False
    with pytest.raises(EstadoInvalidoError, match = "la parada no es la actual de un viaje en curso"):
        parada.setter_estado("FALLIDA")
    assert parada.getter_estado() == "PENDIENTE"
    viaje.es_parada_actual.return_value = True
    parada.setter_estado("FALLIDA")
    assert parada.getter_estado() == "FALLIDA"
def test_parada_entregadaSinComprobante(parada):
    with pytest.raises(EstadoInvalidoError):
        parada.setter_estado("ENTREGADA")
    assert parada.getter_estado() == "PENDIENTE"
# Setter hora real
def test_setterHoraReal_ok(parada, mock_validaciones):
    parada.restaurar_estado("FALLIDA")
    parada.setter_hora_real(HORA_REAL)
    assert parada.getter_hora_real() == HORA_REAL
    mock_validaciones.validar_fecha.assert_called_with(HORA_REAL, nombre = "hora_real")
# Errores setter hora real
def test_parada_setterHoraRealInvalida_sePropaga(parada, mock_validaciones):
    parada.restaurar_estado("ENTREGADA")
    mock_validaciones.validar_fecha.side_effect = TypeError("La hora real debe ser datetime")
    with pytest.raises(TypeError, match = "La hora real debe ser datetime"):
        parada.setter_hora_real("10AM")
    assert parada.getter_hora_real() is None
def test_parada_setterHoraReal_fueraDeTurno(parada, solicitud, viaje):
    parada.restaurar_estado("FALLIDA")
    viaje.es_parada_actual.return_value = False
    with pytest.raises(EstadoInvalidoError, match = "la parada no es la actual de un viaje en curso"):
        parada.setter_hora_real(HORA_REAL)
    assert parada.getter_hora_real() is None
    solicitud.getter_viaje.return_value = None
    with pytest.raises(EstadoInvalidoError, match = "la parada no es la actual de un viaje en curso"):
        parada.setter_hora_real(HORA_REAL)
    assert parada.getter_hora_real() is None
def test_parada_setterHoraReal_enParadaPendiente(parada):
    with pytest.raises(EstadoInvalidoError):
        parada.setter_hora_real(HORA_REAL)
    assert parada.getter_hora_real() is None

# Setter id
def test_parada_setterId(parada):
    parada.setter_id(7)
    assert parada.getter_id() == 7
# Setter comprobante (no necesita un viaje)
def test_parada_setterComprobante(parada, solicitud, mocker):
    solicitud.getter_viaje.return_value = None
    comprobante = mocker.Mock(spec = Comprobante)
    parada.setter_comprobante(comprobante)
    assert parada.getter_comprobante() is comprobante
    assert parada.getter_estado() == "PENDIENTE"
    solicitud.setter_comprobante.assert_not_called()
# Restaurar estado (no necesita un viaje en curso)
def test_parada_restaurarEstado_ok(parada, solicitud, mock_validaciones):
    solicitud.getter_viaje.return_value = None
    parada.restaurar_estado("ENTREGADA")
    assert parada.getter_estado() == "ENTREGADA"
    mock_validaciones.validar_en.assert_called_once_with("ENTREGADA", opciones = "FALLIDA, ENTREGADA", nombre = "estado")
    parada.restaurar_estado("FALLIDA")
    assert parada.getter_estado() == "FALLIDA"
    solicitud.getter_viaje.assert_not_called()
# Restaurar estado inválido se propaga
def test_parada_restaurarEstado_invalido_sePropaga(parada, mock_validaciones):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("Estado inválido")
    with pytest.raises(DatoInvalidoError, match = "Estado inválido"):
        parada.restaurar_estado("REORDENADA")
    assert parada.getter_estado() == "PENDIENTE"

# Deserializar
def test_parada_deserializar_ok(mock_validaciones, solicitud, mocker):
    solicitud.getter_id.return_value = 5
    comprobante = mocker.Mock(spec = Comprobante)
    comprobante.getter_id.return_value = 8
    contexto = {Solicitud: [solicitud], Comprobante: [comprobante]}
    archivo = [["id", "orden", "id_solicitud", "hora_prev", "hora_real", "estado", "id_comprobante", "Parada"],
               ["3", "1", "5", "2026-10-11 09:30:00", "2026-10-11 10:05:00", "ENTREGADA", "8"],
               [],
               ["4", "2", "5", "2026-10-11 10:30:00", "2026-10-11 10:45:00", "FALLIDA", ""],
               ["6", "3", "5", "2026-10-11 11:30:00", "", "PENDIENTE", ""]]
    paradas = Parada.deserializar(archivo, contexto)
    assert len(paradas) == 3
    entregada, fallida, pendiente = paradas
    assert entregada.getter_id() == 3
    assert entregada.getter_orden() == 1
    assert entregada.getter_solicitud() is solicitud
    assert entregada.getter_hora_prev() == datetime(2026, 10, 11, 9, 30)
    assert entregada.getter_hora_real() == datetime(2026, 10, 11, 10, 5)
    assert entregada.getter_estado() == "ENTREGADA"
    assert entregada.getter_comprobante() is comprobante
    assert fallida.getter_id() == 4
    assert fallida.getter_estado() == "FALLIDA"
    assert fallida.getter_hora_real() == datetime(2026, 10, 11, 10, 45)
    assert fallida.getter_comprobante() is None
    assert pendiente.getter_id() == 6
    assert pendiente.getter_estado() == "PENDIENTE"
    assert pendiente.getter_hora_real() is None
    assert pendiente.getter_comprobante() is None
    # No necesita un viaje: no consulta el viaje de la solicitud
    solicitud.getter_viaje.assert_not_called()
    # El próximo id continúa desde el mayor
    assert Parada.curr_id == 6
def test_parada_deserializar_soloEncabezado(mock_validaciones):
    archivo = [["id", "orden", "id_solicitud", "hora_prev", "hora_real", "estado", "id_comprobante", "Parada"]]
    assert Parada.deserializar(archivo, {Solicitud: [], Comprobante: []}) == []
    assert Parada.curr_id == 0


# Serializar
def test_parada_serializar(parada, solicitud, mocker):
    solicitud.getter_id.return_value = 5
    # Pendiente: sin hora real ni comprobante
    assert parada.serializar() == [1, 1, 5, HORA_PREV, "", "PENDIENTE", ""]
    # Entregada: con hora real y comprobante
    comprobante = mocker.Mock(spec = Comprobante)
    comprobante.getter_id.return_value = 8
    parada.restaurar_estado("ENTREGADA")
    parada.setter_comprobante(comprobante)
    parada.setter_hora_real(HORA_REAL)
    assert parada.serializar() == [1, 1, 5, HORA_PREV, HORA_REAL, "ENTREGADA", 8]
def test_parada_serializar_fallida(parada, solicitud):
    solicitud.getter_id.return_value = 5
    parada.restaurar_estado("FALLIDA")
    parada.setter_hora_real(HORA_REAL)
    assert parada.serializar() == [1, 1, 5, HORA_PREV, HORA_REAL, "FALLIDA", ""]
# Lo serializado se puede volver a cargar
def test_parada_serializar_deserializar(parada, solicitud, mocker):
    solicitud.getter_id.return_value = 5
    comprobante = mocker.Mock(spec = Comprobante)
    comprobante.getter_id.return_value = 8
    parada.restaurar_estado("ENTREGADA")
    parada.setter_comprobante(comprobante)
    parada.setter_hora_real(HORA_REAL)
    fila = list(map(str, parada.serializar()))
    archivo = [["id", "orden", "id_solicitud", "hora_prev", "hora_real", "estado", "id_comprobante", "Parada"], fila]
    copia = Parada.deserializar(archivo, {Solicitud: [solicitud], Comprobante: [comprobante]})[0]
    assert copia.getter_id() == parada.getter_id()
    assert copia.getter_orden() == parada.getter_orden()
    assert copia.getter_solicitud() is solicitud
    assert copia.getter_hora_prev() == HORA_PREV
    assert copia.getter_hora_real() == HORA_REAL
    assert copia.getter_estado() == "ENTREGADA"
    assert copia.getter_comprobante() is comprobante
