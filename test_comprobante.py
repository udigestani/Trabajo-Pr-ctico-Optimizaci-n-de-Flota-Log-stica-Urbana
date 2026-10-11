import pytest
from datetime import datetime
from comprobante import Comprobante
from solicitud import Solicitud
from excepciones import DatoInvalidoError

HORARIO = datetime(2026, 10, 11, 12, 0)

@pytest.fixture(autouse = True)
def resetearId():
    Comprobante.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("comprobante.Validaciones")
    mock.validar_instancia.side_effect = lambda valor, **kwargs: valor
    mock.validar_str.side_effect = lambda valor, nombre = "valor": valor
    mock.validar_fecha.side_effect = lambda fecha, nombre = "fecha": fecha
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def solicitud(mocker):
    mock = mocker.Mock(spec = Solicitud)
    mock.getter_id.return_value = 200
    return mock

@pytest.fixture
def comprobante(solicitud, mock_validaciones):
    return Comprobante(solicitud, HORARIO, "Uriel", 100)

# Funcionamiento normal
def test_comprobante_ok(comprobante, solicitud):
    assert comprobante.solicitud is solicitud
    assert comprobante.receptor == "Uriel"
    assert comprobante.fecha_hora == HORARIO
    assert comprobante.monto == 100
    # id
    assert comprobante.id == 1
    comprobante2 = Comprobante(solicitud, HORARIO, "Juan", 50)
    assert comprobante2.id == 2
def test_comprobante_montoCero(mock_validaciones, solicitud):
    comprobante = Comprobante(solicitud, HORARIO, "Massimo", 0)
    assert comprobante.monto == 0
# Getters
def test_comprobante_getters(comprobante, solicitud):
    assert comprobante.getter_id() == 1
    assert comprobante.getter_solicitud() is solicitud
    assert comprobante.getter_receptor() == "Uriel"
    assert comprobante.getter_fecha_hora() == HORARIO
    assert comprobante.getter_monto() == 100
# Metodos mágicos
def test_comprobantes_metodosMagicos(comprobante):
    assert str(comprobante) == "Comprobante 1 | Solicitud 200 | Recibió: Uriel el 2026-10-11 12:00 | Monto: $100"
# Validaciones
def test_comprobante_validaciones(mock_validaciones, solicitud):
    comprobante = Comprobante(solicitud, HORARIO, "Juan", 100)
    mock_validaciones.validar_instancia.assert_called_once_with(solicitud, clase = Solicitud, nombre = "solicitud")
    mock_validaciones.validar_str.assert_called_once_with("Juan", nombre = "receptor")
    mock_validaciones.validar_fecha.assert_called_once_with(HORARIO, nombre = "fecha y hora del comprobante")
    mock_validaciones.validar_numero.assert_called_once_with(100, cero = True, nombre = "monto")
#Validar solicitud
def test_comprobante_validarSolicitud(mock_validaciones, solicitud):
    assert Comprobante.validar_solicitud(solicitud) is solicitud
    mock_validaciones.validar_instancia.assert_called_once_with(solicitud, clase = Solicitud, nombre = "solicitud")
# Errores en __init__
def test_comprobante_solicitudInvalida_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_instancia.side_effect = TypeError("La solicitud no es Solicitud")
    with pytest.raises(TypeError, match = "La solicitud no es Solicitud"):
        Comprobante("solicitud", HORARIO, "Manuel", 100)
    assert Comprobante.curr_id == 0
def test_comprobante_receptorVacio_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_str.side_effect = DatoInvalidoError("El receptor no puede ser vacío")
    with pytest.raises(DatoInvalidoError, match = "El receptor no puede ser vacío"):
        Comprobante(solicitud, HORARIO, "     ", 100)
    assert Comprobante.curr_id == 0
def test_comprobante_receptorNoStr_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_str.side_effect = TypeError("El receptor no es str")
    with pytest.raises(TypeError, match = "El receptor no es str"):
        Comprobante(solicitud, HORARIO, None, 100)
    assert Comprobante.curr_id == 0
def test_comprobante_fechaInvalida_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_fecha.side_effect = TypeError("La fecha debe ser datetime")
    with pytest.raises(TypeError, match = "La fecha debe ser datetime"):
        Comprobante(solicitud, "9AM", "Manuel", 100)
    assert Comprobante.curr_id == 0
def test_comprobante_montoNoNumero_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_numero.side_effect = TypeError("El monto debe ser numero")
    with pytest.raises(TypeError, match = "El monto debe ser numero"):
        Comprobante(solicitud, HORARIO, "Manuel", "Cien")
    assert Comprobante.curr_id == 0
def test_comprobante_montoNegativo_sePropaga(mock_validaciones, solicitud):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("El monto no puede ser negativo")
    with pytest.raises(DatoInvalidoError, match = "El monto no puede ser negativo"):
        Comprobante(solicitud, HORARIO, "Manuel", -100)
    assert Comprobante.curr_id == 0

def test_comprobante_noModificaSolicitud(mock_validaciones, solicitud):
    comprobante = Comprobante(solicitud, HORARIO, "Massimo", 100)
    assert solicitud.method_calls == []
