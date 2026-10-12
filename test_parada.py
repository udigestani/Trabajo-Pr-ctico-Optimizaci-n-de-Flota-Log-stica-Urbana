import pytest
from datetime import datetime
from parada import Parada
from solicitud import Solicitud
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

@pytest.fixture
def solicitud(mocker):
    mock = mocker.Mock(spec = Solicitud)
    mock.getter_comprobante.return_value = None
    mock.getter_destino.return_value = "Destino 1"
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
    assert parada.orden == 1
    assert parada.solicitud is solicitud
    assert parada.hora_prev == HORA_PREV
    assert parada.hora_real is None
    assert parada.estado == "PENDIENTE"
    assert parada.comprobante is None
    # id
    assert parada.id == 1
    parada2 = Parada(2, solicitud, HORA_PREV, None)
    assert parada2.id == 2
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
    parada.hora_real = HORA_REAL
    parada.estado = "ENTREGADA"
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
def test_parada_generarComprobante_ok(parada, solicitud, mock_comprobante):
    resultado = parada.generar_comprobante("Juan", HORA_REAL, 100)
    mock_comprobante.assert_called_once_with(solicitud, HORA_REAL, "Juan", 100)
    assert resultado is mock_comprobante
    assert parada.getter_comprobante() is mock_comprobante
    solicitud.setter_comprobante.assert_called_once_with(mock_comprobante)
    assert parada.getter_hora_real() == HORA_REAL
    assert parada.getter_estado() == "ENTREGADA"
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
    parada.estado = "ENTREGADA"
    with pytest.raises(EstadoInvalidoError):
        parada.generar_comprobante("Massimo", HORA_REAL, 100)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()
def test_parada_generarComprobante_yaFallida(parada, solicitud, mock_comprobante):
    parada.estado = "FALLIDA"
    with pytest.raises(EstadoInvalidoError):
        parada.generar_comprobante("Uriel", HORA_REAL, 100)
    mock_comprobante.assert_not_called()
    solicitud.setter_comprobante.assert_not_called()

# Setter estado
def test_parada_setterEstado_ok(parada, mock_validaciones):
    parada.setter_estado("FALLIDA")
    assert parada.estado == "FALLIDA"
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
    parada.estado = "ENTREGADA"
    with pytest.raises(EstadoInvalidoError):
        parada.setter_estado("FALLIDA")
    assert parada.getter_estado() == "ENTREGADA"
    # Fallida a entregada
    parada.estado = "FALLIDA"
    with pytest.raises(EstadoInvalidoError):
        parada.setter_estado("ENTREGADA")
    assert parada.getter_estado() == "FALLIDA"
def test_parada_entregadaSinComprobante(parada):
    with pytest.raises(EstadoInvalidoError):
        parada.setter_estado("ENTREGADA")
    assert parada.getter_estado() == "PENDIENTE"
# Setter hora real
def test_setterHoraReal_ok(parada, mock_validaciones):
    parada.estado = "FALLIDA"
    parada.setter_hora_real(HORA_REAL)
    assert parada.getter_hora_real() == HORA_REAL
    mock_validaciones.validar_fecha.assert_called_with(HORA_REAL, nombre = "hora_real")
# Errores setter hora real
def test_parada_setterHoraRealInvalida_sePropaga(parada, mock_validaciones):
    parada.estado = "ENTREGADA"
    mock_validaciones.validar_fecha.side_effect = TypeError("La hora real debe ser datetime")
    with pytest.raises(TypeError, match = "La hora real debe ser datetime"):
        parada.setter_hora_real("10AM")
    assert parada.getter_hora_real() is None
def test_parada_setterHoraReal_enParadaPendiente(parada):
    with pytest.raises(EstadoInvalidoError):
        parada.setter_hora_real(HORA_REAL)
    assert parada.getter_hora_real() is None
