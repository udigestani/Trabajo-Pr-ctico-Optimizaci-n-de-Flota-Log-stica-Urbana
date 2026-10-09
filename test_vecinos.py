import pytest
from datetime import datetime
from politicaordenamiento import PoliticaOrdenamiento, Vecinos
from solicitud import Solicitud
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError, RutaIncompletaError

DISTANCIAS = {
    ("Deposito", "mock_s1"): 11, ("Deposito", "mock_s2"): 12, ("Deposito", "mock_s3"): 8, ("Deposito", "mock_s4"): 10,
    ("mock_s1", "mock_s2"): 12, ("mock_s1", "mock_s3"): 16, ("mock_s1", "mock_s4"): 10,
    ("mock_s2", "mock_s1"): 20, ("mock_s2", "mock_s3"): 15, ("mock_s2", "mock_s4"): 17,
    ("mock_s3", "mock_s1"): 11, ("mock_s3", "mock_s2"): 13, ("mock_s3", "mock_s4"): 12.5,
    ("mock_s4", "mock_s1"): 18, ("mock_s4", "mock_s2"): 15, ("mock_s4", "mock_s3"): 12,
}

@pytest.fixture
def mock_matriz(mocker):
    distancias = dict(DISTANCIAS)
    def distancia_falsa(origen, destino):
        if (origen, destino) not in distancias:
            raise RutaIncompletaError(origen, destino)
        return distancias[(origen, destino)]
    matriz = mocker.Mock(spec=MatrizDistancia)
    matriz.obtener_distancia.side_effect = distancia_falsa
    matriz.getter_distancias.return_value = distancias
    return matriz

def crear_solicitud_falsa(mocker, destino):
    solicitud = mocker.Mock(spec=Solicitud)
    solicitud.getter_destino.return_value = destino
    return solicitud

# test 1 --> no recibe solicitudes --> No ordena
def test_vecinos_ceroSolicitudes(mock_matriz):
    resultado = Vecinos.sugerir_orden("Deposito", [], mock_matriz)
    assert resultado == []

# test 2 --> unica solicitud
def test_vecinos_unaSolicitud(mocker, mock_matriz):
    mock_solicitud = crear_solicitud_falsa(mocker, "mock_s1")
    resultado = Vecinos.sugerir_orden("Deposito", [mock_solicitud], mock_matriz)
    assert resultado == [mock_solicitud]

# 
def test_vecinos_ok(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, "mock_s1")
    mock_s2 = crear_solicitud_falsa(mocker, "mock_s2")
    mock_s3 = crear_solicitud_falsa(mocker, "mock_s3")
    mock_s4 = crear_solicitud_falsa(mocker, "mock_s4")

    assert mock_matriz.obtener_distancia(mock_s1.getter_destino(), mock_s2.getter_destino()) == 12
    assert mock_matriz.obtener_distancia(mock_s2.getter_destino(), mock_s1.getter_destino()) == 20
    
    solicitudes = [mock_s1, mock_s2, mock_s3, mock_s4]
    resultado = Vecinos.sugerir_orden("Deposito", solicitudes, mock_matriz)
    assert resultado == [mock_s3, mock_s1, mock_s4, mock_s2]
    assert resultado != solicitudes # No modifica solicitudes, solo devuelve el orden
    assert solicitudes == [mock_s1, mock_s2, mock_s3, mock_s4] # la lista original sigue con su orden de entrada
    assert set(resultado) == set(solicitudes) # Aparecen todas las solicitudes
    assert len(resultado) == len(solicitudes) # Cada solicitud una sola vez

    # Verifica que los llame
    mock_matriz.obtener_distancia.assert_called()
    mock_s1.getter_destino.assert_called()
    # Verifica que no los llame
    mock_s1.getter_ventana_inicio.assert_not_called()
    mock_s1.getter_ventana_fin.assert_not_called()
    mock_s1.getter_id.assert_not_called()


# test 4 --> Ya estaban ordenadas
def test_vecinos_sinModificacion(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, "mock_s1")
    mock_s3 = crear_solicitud_falsa(mocker, "mock_s3")
    mock_s4 = crear_solicitud_falsa(mocker, "mock_s4")
    solicitudes = [mock_s3, mock_s1, mock_s4]
    resultado = Vecinos.sugerir_orden("Deposito", solicitudes, mock_matriz)
    assert resultado == [mock_s3, mock_s1, mock_s4]
    assert resultado == solicitudes

# Cuando no está la distancia en la matriz
def test_vecinos_rutaIncompleta(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, "mock_s1")
    mock_s5 = crear_solicitud_falsa(mocker, "mock_s5")
    solicitudes = [mock_s1, mock_s5]
    with pytest.raises(RutaIncompletaError):
        Vecinos.sugerir_orden("Deposito", solicitudes, mock_matriz)

# Es válido incluso faltando algunas distancias
def test_vecinos_rutaParcial(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, "mock_s1")
    mock_s5 = crear_solicitud_falsa(mocker, "mock_s5")
    mock_matriz.getter_distancias()[("mock_s1", "mock_s5")] = 7   # s5 solo es alcanzable desde s1
    resultado = Vecinos.sugerir_orden("Deposito", [mock_s5, mock_s1], mock_matriz)
    assert resultado == [mock_s1, mock_s5]

# hereda
def test_vecinos_heredaDePolitica():
    vecinos = Vecinos()
    assert isinstance(vecinos, Vecinos)
    assert isinstance(vecinos, PoliticaOrdenamiento)

# el metodo es estático
def test_vecinos_estatico(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, "mock_s1")
    mock_s3 = crear_solicitud_falsa(mocker, "mock_s3")
    solicitudes = [mock_s1, mock_s3]

    orden_clase = Vecinos.sugerir_orden("Deposito", solicitudes, mock_matriz)
    orden_instancia = Vecinos().sugerir_orden("Deposito", solicitudes, mock_matriz)

    assert orden_clase == orden_instancia == [mock_s3, mock_s1]

# DatoInvalido si deposito.strip() es vacio
def test_vecinos_depositoInvalido(mock_matriz):
    with pytest.raises(DatoInvalidoError, match="El deposito no debe estar vacío"):
        Vecinos.sugerir_orden("      ", [], mock_matriz)

# TypeError cuando las solicitudes no son solicitudes
def test_vecinos_elementoNoSolicitud(mock_matriz):
    with pytest.raises(TypeError, match = "La solicitudes contiene 5, que no es un objeto de clase Solicitud"):
        Vecinos.sugerir_orden("Deposito", [5, 12, 8, 3], mock_matriz)

# TypeError si la matriz no es MatrizDistancia
def test_vecinos_matrizInvalida(mocker):
    mock_s1 = crear_solicitud_falsa(mocker, 10)
    mock_s2 = crear_solicitud_falsa(mocker, 13)
    solicitudes = [mock_s1, mock_s2]
    matriz = {("Deposito", "D1"):10}
    with pytest.raises(TypeError, match="debe ser un objeto de clase MatrizDistancia"):
        Vecinos.sugerir_orden("Deposito", solicitudes, matriz)

# TypeError si la distancia no es (int, float)
def test_vecinos_distanciaNoValida(mocker, mock_matriz):

    mock_s1 = crear_solicitud_falsa(mocker, "mock_s1")
    mock_s5 = crear_solicitud_falsa(mocker, "mock_s5")
    mock_matriz.getter_distancias()[("mock_s1", "mock_s5")] = "Cinco"
    solicitudes = [mock_s1, mock_s5]
    with pytest.raises(TypeError, match = "La distancias contiene Cinco, que no es un objeto de clase int, float"):
        Vecinos.sugerir_orden("Deposito", solicitudes, mock_matriz)

def test_vecinos_destinoNoStr(mocker, mock_matriz):
    mock_solicitud = crear_solicitud_falsa(mocker, None)
    with pytest.raises(TypeError, match = "La destinos contiene None, que no es un objeto de clase str"):
        Vecinos.sugerir_orden("Deposito", [mock_solicitud], mock_matriz)

# TypeError si las solicitudes no son una lista
def test_vecinos_solicitudesNoLista(mock_matriz):
    with pytest.raises(TypeError, match = "debe ser de tipo list"):
        Vecinos.sugerir_orden("Deposito", None, mock_matriz)

# Empate de distancias --> conserva el primero encontrado
def test_vecinos_empate(mocker, mock_matriz):
    mock_s5 = crear_solicitud_falsa(mocker, "mock_s5")
    mock_s6 = crear_solicitud_falsa(mocker, "mock_s6")
    mock_matriz.getter_distancias()[("Deposito", "mock_s5")] = 20   
    mock_matriz.getter_distancias()[("Deposito", "mock_s6")] = 20   
    mock_matriz.getter_distancias()[("mock_s5", "mock_s6")] = 5
    mock_matriz.getter_distancias()[("mock_s6", "mock_s5")] = 5
    assert Vecinos.sugerir_orden("Deposito", [mock_s5, mock_s6], mock_matriz) == [mock_s5, mock_s6]
    assert Vecinos.sugerir_orden("Deposito", [mock_s6, mock_s5], mock_matriz) == [mock_s6, mock_s5]