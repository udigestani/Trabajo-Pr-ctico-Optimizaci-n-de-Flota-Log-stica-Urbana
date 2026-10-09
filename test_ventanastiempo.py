import pytest
from datetime import datetime
from politicaordenamiento import PoliticaOrdenamiento, VentanasTiempo
from solicitud import Solicitud
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError

@pytest.fixture
def mock_matriz(mocker):
    return mocker.Mock(spec=MatrizDistancia)

def crear_solicitud_falsa(mocker, hora_inicio):
    solicitud = mocker.Mock(spec=Solicitud)
    solicitud.getter_ventana_inicio.return_value = datetime(2025, 1, 1, hora_inicio, 0)
    return solicitud

# test 1 --> no recibe solicitudes --> No ordena
def test_ventana_ceroSolicitudes(mock_matriz):
    resultado = VentanasTiempo.sugerir_orden("Deposito", (), mock_matriz)
    assert resultado == []

# test 2 --> única solicitud
def test_ventana_unaSolicitud(mocker, mock_matriz):
    mock_solicitud = crear_solicitud_falsa(mocker, 9)
    resultado = VentanasTiempo.sugerir_orden("Deposito", (mock_solicitud,), mock_matriz)
    assert resultado == [mock_solicitud]

# test 3 --> funcionamiento normal
def test_ventana_ok(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, 10)
    mock_s2 = crear_solicitud_falsa(mocker, 13)
    mock_s3 = crear_solicitud_falsa(mocker, 11)
    mock_s4 = crear_solicitud_falsa(mocker, 9)
    solicitudes = (mock_s1, mock_s2, mock_s3, mock_s4)
    resultado = VentanasTiempo.sugerir_orden("Deposito", solicitudes, mock_matriz)
    assert resultado == [mock_s4, mock_s1, mock_s3, mock_s2]
    assert tuple(resultado) != solicitudes #Para ver que no modifica las solicitudes, solo devuelve el orden
    assert solicitudes == (mock_s1, mock_s2, mock_s3, mock_s4) # la lista original sigue con su orden de entrada

# test 4 --> solicitudes que ya estaban ordenadas no cambian
def test_ventana_sinModificacion(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, 10)
    mock_s2 = crear_solicitud_falsa(mocker, 12)
    mock_s3 = crear_solicitud_falsa(mocker, 13)
    mock_s4 = crear_solicitud_falsa(mocker, 14)
    solicitudes = (mock_s1, mock_s2, mock_s3, mock_s4)
    resultado = VentanasTiempo.sugerir_orden("Deposito", solicitudes, mock_matriz)
    assert resultado == [mock_s1, mock_s2, mock_s3, mock_s4]
    assert tuple(resultado) == solicitudes

# test 5 --> hay empates
def test_ventana_empates(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, 12)
    mock_s2 = crear_solicitud_falsa(mocker, 13)
    mock_s3 = crear_solicitud_falsa(mocker, 15)
    mock_s4 = crear_solicitud_falsa(mocker, 13)
    mock_s5 = crear_solicitud_falsa(mocker, 11)
    solicitudes = (mock_s1, mock_s2, mock_s3, mock_s4, mock_s5)
    resultado = VentanasTiempo.sugerir_orden("Deposito", solicitudes, mock_matriz)
    assert resultado in ([mock_s5, mock_s1, mock_s2, mock_s4, mock_s3], [mock_s5, mock_s1, mock_s4, mock_s2, mock_s3])    

# test 6 --> verificar que no depende del depósito, ni de las distancias, ni de otros atributos de las solicitudes
def test_ventana_ignoraMatrizYDeposito(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, 14)
    mock_s2 = crear_solicitud_falsa(mocker, 9)
    
    solicitudes = (mock_s1, mock_s2)
    resultado_a = VentanasTiempo.sugerir_orden("Deposito A", solicitudes, mock_matriz)
    resultado_b = VentanasTiempo.sugerir_orden("Deposito B", solicitudes, mock_matriz)

    assert resultado_a == resultado_b == [mock_s2, mock_s1]
    mock_matriz.obtener_distancia.assert_not_called()

    #tambien ignora atributos de solicitud que no necesitamos
    mock_s1.getter_destino.assert_not_called()
    mock_s1.getter_ventana_fin.assert_not_called()
    mock_s1.getter_id.assert_not_called()

# test 7 --> ventana hereda de politica
def test_ventana_heredaDePolitica():
    ventana = VentanasTiempo()
    assert isinstance(ventana, VentanasTiempo)
    assert isinstance(ventana, PoliticaOrdenamiento)

# test 8 --> el metodo es estático
def test_ventana_estatico(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, 14)
    mock_s2 = crear_solicitud_falsa(mocker, 9)
    solicitudes = (mock_s1, mock_s2)

    orden_clase = VentanasTiempo.sugerir_orden("Deposito", solicitudes, mock_matriz)
    orden_instancia = VentanasTiempo().sugerir_orden("Deposito", solicitudes, mock_matriz)

    assert orden_clase == orden_instancia == [mock_s2, mock_s1]

# test 9 --> TypeError cuando solicitudes no pasa un iterable
def test_ventana_solicitudesNoIterable(mock_matriz):
    with pytest.raises(TypeError, match = "La solicitudes None debe ser de tipo tuple"):
        VentanasTiempo.sugerir_orden("Deposito", None, mock_matriz) #podriamos probar str, int

# test 10 --> TypeError cuando las solicitudes no son solicitudes
def test_ventana_elementoNoSolicitud(mock_matriz):
    with pytest.raises(TypeError, match = "La solicitudes contiene 5, que no es un objeto de clase Solicitud"):
        VentanasTiempo.sugerir_orden("Deposito", (5, 12, 8, 3), mock_matriz) #podriamos probar str, int

# test 11 --> TypeError si la fehca no es datetime
def test_ventana_fechaNoValida(mocker, mock_matriz):
    mock_s1 = crear_solicitud_falsa(mocker, 12)
    mock_s2 = mocker.Mock(spec = Solicitud)
    mock_s2.getter_ventana_inicio.return_value = 8   # podríamos probar con otros tipos de fecha que también debería dar error
    
    solicitudes = (mock_s1, mock_s2)

    with pytest.raises(TypeError, match = "La ventanas contiene 8, que no es un objeto de clase datetime"):
        VentanasTiempo.sugerir_orden("Deposito", solicitudes, mock_matriz)

# test 12 --> DatoInvalidoError si deposito.strip() es vacio
def test_ventana_depositoInvalido(mock_matriz):
    with pytest.raises(DatoInvalidoError, match="El deposito no debe estar vacío"):
        VentanasTiempo.sugerir_orden("      ", [], mock_matriz)
    

# test 13 --> TypeError si la matriz no es MatrizDistancia
def test_ventana_matrizInvalida(mocker):
    mock_s1 = crear_solicitud_falsa(mocker, 10)
    mock_s2 = crear_solicitud_falsa(mocker, 13)
    solicitudes = (mock_s1, mock_s2)
    matriz = {("Deposito", "D1"):10}
    with pytest.raises(TypeError, match="debe ser un objeto de clase MatrizDistancia"):
        VentanasTiempo.sugerir_orden("Deposito", solicitudes, matriz)