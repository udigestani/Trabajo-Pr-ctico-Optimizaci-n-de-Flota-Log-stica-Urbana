import pytest
from datetime import datetime
from persona import Persona, Administrador, Solicitante
from viaje import Viaje
from articulo import Articulo
from excepciones import DNIInvalidoError, EstadoInvalidoError

@pytest.fixture(autouse=True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

@pytest.fixture
def solicitante():
    return Solicitante("Manuel", 87654321, 1199998888)

@pytest.fixture
def mock_viaje(mocker):
    return mocker.Mock(spec = Viaje)

@pytest.fixture
def mock_articulo(mocker):
    return mocker.Mock(spec = Articulo)

@pytest.fixture
def inicio():
    return datetime(2026, 10, 9, 9, 0)

@pytest.fixture
def fin():
    return datetime(2026, 10, 9, 12, 0)

# Funcionamiento normal
def test_solicitante_ok(solicitante):
    assert solicitante.getter_nombre() == "Manuel"
    assert solicitante.getter_dni() == 87654321
    assert solicitante.getter_telefono() == 1199998888
    assert isinstance(solicitante, Solicitante)
    assert isinstance(solicitante, Persona)
    assert not isinstance(solicitante, Administrador)
    assert issubclass(Solicitante, Persona)
    assert Persona.getter_dnis_registrados() == {87654321: solicitante}

# DNIInvalidoError si el DNI ya está registrado
def test_solicitante_dniRepetido():
    Administrador("Massimo", 12345678, 1122334455)
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Solicitante("Juan", 12345678, 1199998888)

def test_crearSolicitud_ok(solicitante, mock_viaje, mock_articulo, inicio, fin):
    resultado = solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    mock_viaje.crear_solicitud.assert_called_once_with("Destino", inicio, fin, mock_articulo)
    assert resultado == mock_viaje.crear_solicitud.return_value

# Dos articulos (args)
def test_crearSolicitud_variosArticulos(solicitante, mock_viaje, mocker, inicio, fin):
    articulo1 = mocker.Mock(spec = Articulo)
    articulo2 = mocker.Mock(spec = Articulo)
    solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, articulo1, articulo2)
    mock_viaje.crear_solicitud.assert_called_once_with("Destino", inicio, fin, articulo1, articulo2)

# Ningún articulo -- valida viaje no crear_solicitud
def test_crearSolicitud_sinArticulos(solicitante, mock_viaje, inicio, fin):
    solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin)
    mock_viaje.crear_solicitud.assert_called_once_with("Destino", inicio, fin)

# estático
def test_crearSolicitud_estatico(solicitante, mock_viaje, mock_articulo, inicio, fin):
    respuestaClase = Solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    respuestaInstancia = solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    assert mock_viaje.crear_solicitud.call_count == 2
    assert respuestaClase == respuestaInstancia

# TypeError si el viaje no es un Viaje
def test_crearSolicitud_viajeInvalido(solicitante, mock_articulo, inicio, fin):
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        solicitante.crear_solicitud("viaje", "Destino", inicio, fin, mock_articulo)

# Comportamiento si el viaje da error por estar EN_CURSO
def test_crearSolicitud_viajeEnCurso(solicitante, mock_viaje, mock_articulo, inicio, fin):
    mock_viaje.crear_solicitud.side_effect = EstadoInvalidoError("crear_solicitud", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError):
        solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
