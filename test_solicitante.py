import pytest
from datetime import datetime
from persona import Persona, Administrador, Solicitante
from viaje import Viaje
from articulo import Articulo
from solicitud import Solicitud
from excepciones import DNIInvalidoError, EstadoInvalidoError, DatoInvalidoError, ExcesoPesoError

@pytest.fixture(autouse=True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

@pytest.fixture
def mock_solicitud_clase(mocker):
    return mocker.patch("persona.Solicitud")

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
    arbol = Persona.getter_dnis_registrados()
    assert arbol.buscar(arbol.getter_raiz(), 87654321) is solicitante

# DNIInvalidoError si el DNI ya está registrado
def test_solicitante_dniRepetido():
    Administrador("Massimo", 12345678, 1122334455)
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Solicitante("Juan", 12345678, 1199998888)

def test_crearSolicitud_ok(solicitante, mock_viaje, mock_solicitud_clase, mock_articulo, inicio, fin):
    resultado = solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    # Crea la solicitud y se la pasa al viaje para que la agregue
    mock_viaje.validar_estado.assert_called_once_with("crear_solicitud", "PLANIFICADO")
    mock_solicitud_clase.assert_called_once_with("Destino", inicio, fin, mock_articulo)
    mock_viaje.agregar_solicitud.assert_called_once_with(mock_solicitud_clase.return_value)
    assert resultado is mock_solicitud_clase.return_value

# Dos articulos (args)
def test_crearSolicitud_variosArticulos(solicitante, mock_viaje, mock_solicitud_clase, mocker, inicio, fin):
    articulo1 = mocker.Mock(spec = Articulo)
    articulo2 = mocker.Mock(spec = Articulo)
    solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, articulo1, articulo2)
    mock_solicitud_clase.assert_called_once_with("Destino", inicio, fin, articulo1, articulo2)
    mock_viaje.agregar_solicitud.assert_called_once_with(mock_solicitud_clase.return_value)

# Ningún articulo -- los valida Solicitud, no crear_solicitud
def test_crearSolicitud_sinArticulos(solicitante, mock_viaje, mock_solicitud_clase, inicio, fin):
    solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin)
    mock_solicitud_clase.assert_called_once_with("Destino", inicio, fin)
    mock_viaje.agregar_solicitud.assert_called_once_with(mock_solicitud_clase.return_value)

# estático
def test_crearSolicitud_estatico(solicitante, mock_viaje, mock_solicitud_clase, mock_articulo, inicio, fin):
    respuestaClase = Solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    respuestaInstancia = solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    assert mock_solicitud_clase.call_count == 2
    assert mock_viaje.agregar_solicitud.call_count == 2
    assert respuestaClase == respuestaInstancia

# Cada llamada crea una solicitud nueva
def test_crearSolicitud_solicitudesDistintas(solicitante, mock_viaje, mock_solicitud_clase, mocker, mock_articulo, inicio, fin):
    solicitud1 = mocker.Mock(spec = Solicitud)
    solicitud2 = mocker.Mock(spec = Solicitud)
    mock_solicitud_clase.side_effect = [solicitud1, solicitud2]
    assert solicitante.crear_solicitud(mock_viaje, "Destino A", inicio, fin, mock_articulo) is solicitud1
    assert solicitante.crear_solicitud(mock_viaje, "Destino B", inicio, fin, mock_articulo) is solicitud2
    assert mock_viaje.agregar_solicitud.call_args_list == [mocker.call(solicitud1), mocker.call(solicitud2)]

# TypeError si el viaje no es un Viaje
def test_crearSolicitud_viajeInvalido(solicitante, mock_solicitud_clase, mock_articulo, inicio, fin):
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Viaje"):
        solicitante.crear_solicitud("viaje", "Destino", inicio, fin, mock_articulo)
    mock_solicitud_clase.assert_not_called()

# Comportamiento si el viaje da error por estar EN_CURSO: no se crea la solicitud
def test_crearSolicitud_viajeEnCurso(solicitante, mock_viaje, mock_solicitud_clase, mock_articulo, inicio, fin):
    mock_viaje.validar_estado.side_effect = EstadoInvalidoError("crear_solicitud", "EN_CURSO")
    with pytest.raises(EstadoInvalidoError, match = "Estado invalido: No se puede crear_solicitud porque el estado es EN_CURSO"):
        solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    mock_solicitud_clase.assert_not_called()
    mock_viaje.agregar_solicitud.assert_not_called()

# Si los datos de la solicitud son inválidos, no se agrega al viaje
def test_crearSolicitud_solicitudInvalida(solicitante, mock_viaje, mock_solicitud_clase, mock_articulo, inicio, fin):
    mock_solicitud_clase.side_effect = DatoInvalidoError("El destino no debe estar vacío")
    with pytest.raises(DatoInvalidoError, match = "El destino no debe estar vacío"):
        solicitante.crear_solicitud(mock_viaje, "   ", inicio, fin, mock_articulo)
    mock_viaje.agregar_solicitud.assert_not_called()

# Si el viaje rechaza la solicitud, el error se propaga
def test_crearSolicitud_viajeRechazaSolicitud(solicitante, mock_viaje, mock_solicitud_clase, mock_articulo, inicio, fin):
    mock_viaje.agregar_solicitud.side_effect = ExcesoPesoError(500, 600)
    with pytest.raises(ExcesoPesoError, match = "Capacidad excedida: El peso 600 supera el peso máximo del transporte 500"):
        solicitante.crear_solicitud(mock_viaje, "Destino", inicio, fin, mock_articulo)
    mock_solicitud_clase.assert_called_once_with("Destino", inicio, fin, mock_articulo)


# ---------- serializar ----------
def test_solicitante_serializar(solicitante):
    assert solicitante.serializar() == ["Solicitante", "Manuel", 87654321, 1199998888]
def test_solicitante_str(solicitante):
    assert str(solicitante) == "Solicitante de nombre Manuel y DNI: 87654321"
