import pytest
from matrizdistancia import MatrizDistancia
from solicitud import Solicitud
from politicaordenamiento import PoliticaOrdenamiento, Vecinos, VentanasTiempo


@pytest.fixture
def mock_matriz(mocker):
    return mocker.Mock(spec = MatrizDistancia)

def mock_solicitud(mocker):
    return mocker.Mock(spec = Solicitud)


# Sugerir orden tira error (NotImplementedError)
def test_politica_error(mocker, mock_matriz):
    mock_s1 = mock_solicitud(mocker)
    mock_s2 = mock_solicitud(mocker)
    mock_s3 = mock_solicitud(mocker)
    mock_s4 = mock_solicitud(mocker)
    solicitudes = [mock_s1, mock_s2, mock_s3, mock_s4]
    with pytest.raises(NotImplementedError, match = "Las subclases deben implementar sugerir_orden"):
        PoliticaOrdenamiento.sugerir_orden("Deposito", solicitudes, mock_matriz)
    assert solicitudes == [mock_s1, mock_s2, mock_s3, mock_s4] # No debe modificar solicitudes

# Herencia
def test_politica_herencia():
    assert issubclass(Vecinos, PoliticaOrdenamiento)
    assert issubclass(VentanasTiempo, PoliticaOrdenamiento)
    assert isinstance(Vecinos(), PoliticaOrdenamiento)
    assert isinstance(VentanasTiempo(), PoliticaOrdenamiento)

# Metodo estático
def test_politica_estatico(mocker, mock_matriz):
    mock_s1 = mock_solicitud(mocker)
    mock_s2 = mock_solicitud(mocker)
    try:
        resultadoClase = PoliticaOrdenamiento.sugerir_orden("Deposito", [mock_s1, mock_s2], mock_matriz)
    except Exception as e:
        resultadoClase = e
    try:
        resultadoInstancia = PoliticaOrdenamiento().sugerir_orden("Deposito", [mock_s1, mock_s2], mock_matriz)
    except Exception as e:
        resultadoInstancia = e
    assert repr(resultadoClase) == repr(resultadoInstancia)
    assert type(resultadoClase) == type(resultadoInstancia)
    # Vrrifica que devuelvan lo mismo