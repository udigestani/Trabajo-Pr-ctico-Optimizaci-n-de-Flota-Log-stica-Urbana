import pytest
from datetime import datetime
from incidente import Incidente
from solicitud import Solicitud
from transporte import Transporte
from excepciones import DatoInvalidoError

FECHA = datetime(2026, 10, 11, 14, 30)

@pytest.fixture(autouse=True)
def reset_id():
    Incidente.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("incidente.Validaciones")
    mock.validar_en.side_effect = lambda valor, **kwargs: valor
    mock.validar_fecha.side_effect = lambda valor, **kwargs: valor
    mock.validar_str.side_effect = lambda valor, **kwargs: valor
    mock.validar_instancia.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def afectado(mocker):
    solicitud = mocker.MagicMock(spec=Solicitud)
    solicitud.__str__.return_value = "Solicitud 1 hacia Destino1"
    return solicitud

@pytest.fixture
def incidente(mock_validaciones, afectado):
    return Incidente("DAÑO", FECHA, "Caja rota", afectado)

# Funcionamiento normal
def test_incidente_ok(incidente, mock_validaciones, afectado):
    assert incidente.getter_tipo() == "DAÑO"
    assert incidente.getter_fecha() == FECHA
    assert incidente.getter_descripcion() == "Caja rota"
    assert incidente.getter_afectado() is afectado
    assert incidente.getter_detalles() == {}
    assert incidente.getter_id() == 1
    # id
    inc2 = Incidente("DAÑO", FECHA, "Uno", afectado)
    assert inc2.getter_id() == 2

def test_incidente_detalles(mock_validaciones, afectado):
    incidente = Incidente("DAÑO", FECHA, "Caja rota", afectado, camion="Camion 1")
    assert incidente.getter_detalles() == {"camion": "Camion 1"}

def test_incidente_descripcionStrip(mock_validaciones, afectado):
    incidente = Incidente("AUSENTE", FECHA, "   Nadie en casa   ", afectado)
    assert incidente.getter_descripcion() == "Nadie en casa"
# Getters
def test_incidente_getters(incidente, afectado):
    assert incidente.getter_tipo() == "DAÑO"
    assert incidente.getter_afectado() is afectado
    assert incidente.getter_id() == 1
    assert incidente.getter_fecha() == FECHA
    assert incidente.getter_descripcion() == "Caja rota"
    assert incidente.getter_detalles() == {}

# Setter id
def test_incidente_setterId(incidente):
    incidente.setter_id(7)
    assert incidente.getter_id() == 7

def test_incidente_getterDetalles_copia(mock_validaciones, afectado):
    incidente = Incidente("DAÑO", FECHA, "Caja rota", afectado, camion="ABC123")
    assert incidente.getter_detalles() == {"camion": "ABC123"}
    detalles = incidente.getter_detalles()
    detalles.clear()
    assert incidente.getter_detalles() == {"camion": "ABC123"}
# Metodos mágicos
def test_incidente_metodosMagicos(incidente, mock_validaciones, afectado):
    assert str(incidente) == "Incidente 1 [DAÑO] a las 14:30: Caja rota"
    assert repr(incidente) == "Incidente(DAÑO, 2026-10-11 14:30:00, Caja rota, Solicitud 1 hacia Destino1, **{})"
    # Detalles
    incidente2 = Incidente("DAÑO", FECHA, "Caja rota", afectado, camion="ABC123", minutos=20)
    assert str(incidente2) == "Incidente 2 [DAÑO] a las 14:30: Caja rota, camion=ABC123, minutos=20"
    assert repr(incidente2) == "Incidente(DAÑO, 2026-10-11 14:30:00, Caja rota, Solicitud 1 hacia Destino1, **{'camion': 'ABC123', 'minutos': 20})"

# Validaciones
def test_incidente_validaciones(mock_validaciones, afectado):
    Incidente("RETRASO", FECHA, "Tránsito", afectado)
    mock_validaciones.validar_en.assert_called_once_with("RETRASO", opciones = "DAÑO, AUSENTE, RETRASO", nombre = "tipo del incidente")
    mock_validaciones.validar_fecha.assert_called_once_with(FECHA, nombre = "fecha del incidente")
    mock_validaciones.validar_str.assert_called_once_with("Tránsito", nombre = "descripción")
    mock_validaciones.validar_instancia.assert_called_once_with(afectado, clase = (Solicitud, Transporte), nombre = "afectado")

# Errores en validaciones. Propagación
def test_incidente_errorTipoSePropaga(mock_validaciones, afectado):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("tipo inválido")
    with pytest.raises(DatoInvalidoError, match = "tipo inválido"):
        Incidente("TIPO NO VALIDO", FECHA, "Caja rota", afectado)

def test_incidente_errorFechaSePropaga(mock_validaciones, afectado):
    mock_validaciones.validar_fecha.side_effect = TypeError("fecha inválida")
    with pytest.raises(TypeError, match = "fecha inválida"):
        Incidente("DAÑO", "19:00", "Caja rota", afectado)

def test_incidente_errorDescripcionSePropaga(mock_validaciones, afectado):
    mock_validaciones.validar_str.side_effect = DatoInvalidoError("descripción vacía")
    with pytest.raises(DatoInvalidoError, match = "descripción vacía"):
        Incidente("DAÑO", FECHA, "    ", afectado)

def test_incidente_errorAfectadoSePropaga(mock_validaciones):
    mock_validaciones.validar_instancia.side_effect = TypeError("afectado no es Solicitud")
    with pytest.raises(TypeError, match = "afectado no es Solicitud"):
        Incidente("DAÑO", FECHA, "Caja rota", "Solicitud")

def test_incidente_detalleInvalidoSePropaga(mock_validaciones, afectado):
    mock_validaciones.validar_str.side_effect = ["Caja rota", DatoInvalidoError("detalle vacío")]
    with pytest.raises(DatoInvalidoError, match = "detalle vacío"):
        Incidente("DAÑO", FECHA, "Caja rota", afectado, camion="   ")

# Detalles
def test_incidente_validarDetalles_ok(mock_validaciones):
    detalles = {"camion": "ABC123", "minutos": 20}
    assert Incidente.validar_detalles(detalles) == detalles

def test_incidente_validarDetalles_str(mock_validaciones):
    Incidente.validar_detalles({"camión": "ABC123", "minutos": 20})
    mock_validaciones.validar_str.assert_called_once_with("ABC123", nombre = "detalle camión")

def test_incidente_validarDetalles_noStr(mock_validaciones):
    Incidente.validar_detalles({"minutos": 20, "grave": True})
    mock_validaciones.validar_str.assert_not_called()

# incidente invalido
def test_incidente_invalido_id(mock_validaciones, afectado):
    mock_validaciones.validar_en.side_effect = DatoInvalidoError("tipo inválido")
    with pytest.raises(DatoInvalidoError):
        Incidente("ROBO", FECHA, "Caja rota", afectado)
    assert Incidente.curr_id == 0

# Afectado puede ser Solicitud o Transporte
def test_incidente_afectadoEsTransporte(mocker):
    transporte = mocker.Mock(spec=Transporte)
    incidente = Incidente("RETRASO", FECHA, "Pinchadura", transporte)
    assert incidente.getter_afectado() is transporte

def test_incidente_afectadoEsSolicitud(mocker):
    solicitud = mocker.Mock(spec=Solicitud)
    incidente = Incidente("AUSENTE", FECHA, "Nadie en casa", solicitud)
    assert incidente.getter_afectado() is solicitud

def test_incidente_noModificaAfectado(mock_validaciones, afectado):
    Incidente("DAÑO", FECHA, "Caja rota", afectado)
    assert afectado.method_calls == []


# ---------- serializar ----------
def test_incidente_serializar_afectadoSolicitud(incidente, afectado):
    afectado.getter_id.return_value = 7
    assert incidente.serializar() == [1, "DAÑO", FECHA, "Caja rota", "Solicitud", 7, ""]
def test_incidente_serializar_afectadoTransporte(mock_validaciones, mocker):
    transporte = mocker.Mock(spec = Transporte)
    transporte.getter_id.return_value = 3
    incidente = Incidente("RETRASO", FECHA, "Pinchazo", transporte)
    assert incidente.serializar() == [1, "RETRASO", FECHA, "Pinchazo", "Transporte", 3, ""]
def test_incidente_serializar_detalles(mock_validaciones, afectado):
    afectado.getter_id.return_value = 7
    incidente = Incidente("DAÑO", FECHA, "Caja rota", afectado, rueda = "delantera", costo = 500)
    assert incidente.serializar() == [1, "DAÑO", FECHA, "Caja rota", "Solicitud", 7, "rueda=delantera,costo=500"]

# ---------- deserializar ----------
ENCABEZADO = ["id", "tipo", "fecha", "descripcion", "clase_afectado", "id_afectado", "detalles", "Incidente"]
@pytest.fixture
def transporte(mocker):
    mock = mocker.Mock(spec = Transporte)
    mock.getter_id.return_value = 3
    return mock
@pytest.fixture
def contexto(afectado, transporte):
    afectado.getter_id.return_value = 7
    return {Solicitud: [afectado], Transporte: [transporte]}
# Funcionamiento normal
def test_incidente_deserializar_ok(mock_validaciones, contexto, afectado, transporte):
    archivo = [ENCABEZADO,
               ["2", "DAÑO", "2026-10-11 14:30:00", "Caja rota", "Solicitud", "7", ""],
               [],
               ["5", "RETRASO", "2026-10-11 15:00:00", "Pinchazo", "Furgoneta", "3", "rueda=delantera,costo=500"]]
    incidentes = Incidente.deserializar(archivo, contexto)
    assert len(incidentes) == 2
    assert incidentes[0].getter_id() == 2
    assert incidentes[0].getter_tipo() == "DAÑO"
    assert incidentes[0].getter_fecha() == FECHA
    assert incidentes[0].getter_descripcion() == "Caja rota"
    assert incidentes[0].getter_afectado() is afectado
    assert incidentes[0].getter_detalles() == {}
    assert incidentes[1].getter_id() == 5
    assert incidentes[1].getter_tipo() == "RETRASO"
    # Cualquier clase que no sea Solicitud es un transporte
    assert incidentes[1].getter_afectado() is transporte
    assert incidentes[1].getter_detalles() == {"rueda": "delantera", "costo": "500"}
    # El próximo id continúa desde el mayor
    assert Incidente.curr_id == 5
# Sin filas
def test_incidente_deserializar_soloEncabezado(mock_validaciones, contexto):
    assert Incidente.deserializar([ENCABEZADO], contexto) == []
    assert Incidente.curr_id == 0
# Afectado inexistente
def test_incidente_deserializar_afectadoInexistente(mock_validaciones, contexto):
    with pytest.raises(KeyError):
        Incidente.deserializar([ENCABEZADO, ["1", "DAÑO", "2026-10-11 14:30:00", "Caja rota", "Solicitud", "999", ""]], contexto)
# Lo serializado se puede volver a cargar
def test_incidente_serializar_deserializar(mock_validaciones, contexto, afectado):
    original = Incidente("DAÑO", FECHA, "Caja rota", afectado, rueda = "delantera")
    fila = list(map(str, original.serializar()))
    copia = Incidente.deserializar([ENCABEZADO, fila], contexto)[0]
    assert copia.getter_id() == original.getter_id()
    assert copia.getter_tipo() == original.getter_tipo()
    assert copia.getter_fecha() == original.getter_fecha()
    assert copia.getter_descripcion() == original.getter_descripcion()
    assert copia.getter_afectado() is afectado
    assert copia.getter_detalles() == original.getter_detalles()
