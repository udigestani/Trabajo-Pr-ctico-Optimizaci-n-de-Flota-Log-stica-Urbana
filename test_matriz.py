import pytest
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError, RutaIncompletaError

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("matrizdistancia.Validaciones")
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    mock.validar_str.side_effect = lambda *valores, **kwargs: valores
    return mock

@pytest.fixture
def matriz(mock_validaciones):
    return MatrizDistancia()

@pytest.fixture
def matriz_cargada(matriz):
    matriz.agregar_distancia("Deposito", "Destino 1", 5)
    matriz.agregar_distancia("Destino 1", "Deposito", 7.5)
    return matriz

# Funcionamiento normal (dividido en dos tests)
def test_matriz_vacia_ok(matriz):
    # Vacía
    assert matriz.distancias == {}
    assert matriz.obtener_distancia("Deposito", "Deposito") == 0
    assert matriz.getter_distancias() == {}
    # Getter es copia
    assert matriz.getter_distancias() is not matriz.distancias
    copia = matriz.getter_distancias()
    copia[(1, 2)] = 5
    assert matriz.getter_distancias().get((1,2)) == None
def test_matriz_cargada_ok(matriz_cargada):
    # Con valores
    assert matriz_cargada.distancias[("Deposito", "Destino 1")] == 5
    assert matriz_cargada.getter_distancias()[("Deposito", "Destino 1")] == 5
    assert matriz_cargada.obtener_distancia("Deposito", "Destino 1") == 5
    assert matriz_cargada.distancias[("Destino 1", "Deposito")] == 7.5
    assert matriz_cargada.getter_distancias()[("Destino 1", "Deposito")] == 7.5
    assert matriz_cargada.obtener_distancia("Destino 1", "Deposito") == 7.5
    # Agregar distancia
    matriz_cargada.agregar_distancia("Deposito", "Destino 2", 10)
    assert matriz_cargada.distancias[("Deposito", "Destino 2")] == 10
    assert matriz_cargada.obtener_distancia("Deposito", "Destino 2") == 10
    matriz_cargada.agregar_distancia("Lugar", "Lugar", 0)
    assert matriz_cargada.obtener_distancia("Lugar", "Lugar") == 0
# Distancia cero es valida
def test_matriz_distanciaCero(matriz):
    matriz.agregar_distancia("Deposito", "Destino 1", 0)
    assert matriz.obtener_distancia("Deposito", "Destino 1") == 0
# Correción de distancia
def test_matriz_correcionDistancia(matriz):
    matriz.agregar_distancia("Deposito", "Destino 1", 8)
    matriz.agregar_distancia("Deposito", "Destino 1", 9)
    assert matriz.obtener_distancia("Deposito", "Destino 1") == 9
# Simetría
def test_matriz_noSimetrica(matriz):
    matriz.agregar_distancia("Deposito", "Destino 1", 5)
    with pytest.raises(RutaIncompletaError):
        matriz.obtener_distancia("Destino 1", "Deposito")
# Distancia entre un lugar y si mismo inválida
def test_matriz_mismoLugar_distanciaNoCero(matriz):
    with pytest.raises(DatoInvalidoError, match = "La distancia entre Deposito y si mismo debe ser 0"):
        matriz.agregar_distancia("Deposito", "Deposito", 5)
    assert matriz.getter_distancias() == {}
    assert matriz.obtener_distancia("Deposito", "Deposito") == 0
# Ruta incompleta
def test_matriz_rutaIncompleta(matriz_cargada):
    matrizPrevia = matriz_cargada.getter_distancias()
    with pytest.raises(RutaIncompletaError, match = "No existe distancia de Deposito a Lugar"):
        matriz_cargada.obtener_distancia("Deposito", "Lugar")
    assert matriz_cargada.getter_distancias() == matrizPrevia
# Cargar matriz
def test_matriz_cargarMatriz_ok(matriz):
    matriz.cargar_matriz([("Deposito", "Destino 1", 5), ("Destino 1", "Destino 2", 3), ("Destino 2", "Deposito", 4.5)])
    assert matriz.obtener_distancia("Deposito", "Destino 1") == 5
    assert matriz.obtener_distancia("Destino 1", "Destino 2") == 3
    assert matriz.obtener_distancia("Destino 2", "Deposito") == 4.5
def test_matriz_cargarMatrizVacia(matriz):
    matriz.cargar_matriz([])
    assert matriz.getter_distancias() == {}
def test_matriz_cargarMatriz_llamaAAgregar(mocker):
    mock = mocker.Mock(spec = MatrizDistancia)
    MatrizDistancia.cargar_matriz(mock, [("Deposito", "Destino 1", 5), ("Destino 1", "Destino 2", 7.5), ("Destino 2", "Deposito", 6)])
    assert mock.agregar_distancia.call_count == 3
    mock.agregar_distancia.assert_any_call("Deposito", "Destino 1", 5)
    mock.agregar_distancia.assert_any_call("Destino 1", "Destino 2", 7.5)
    mock.agregar_distancia.assert_any_call("Destino 2", "Deposito", 6)
# Validacion
def test_matriz_validacion(matriz, mock_validaciones):
    matriz.agregar_distancia("A", "B", 5)
    mock_validaciones.validar_numero.assert_called_once_with(5, cero = True, nombre = "distancia")
def test_matriz_cargarMatrizValidaCadaTramo(matriz, mock_validaciones):
    matriz.cargar_matriz([("Deposito", "Destino 1", 5), ("Destino 1", "Deposito", 7)])
    assert mock_validaciones.validar_numero.call_count == 2
    mock_validaciones.validar_numero.assert_any_call(5, cero = True, nombre = "distancia")
    mock_validaciones.validar_numero.assert_any_call(7, cero = True, nombre = "distancia")
# Errores en validaciones. Propagación
def test_matriz_distanciaNegativa_sePropaga(matriz, mock_validaciones):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("La distancia no puede ser negativa")
    with pytest.raises(DatoInvalidoError, match = "La distancia no puede ser negativa"):
        matriz.agregar_distancia("Deposito", "Destino 1", -1)
    assert matriz.getter_distancias() == {}
def test_matriz_distanciaNoNumero_sePropaga(matriz, mock_validaciones):
    mock_validaciones.validar_numero.side_effect = TypeError("La distancia debe ser número")
    with pytest.raises(TypeError, match = "La distancia debe ser número"):
        matriz.agregar_distancia("Deposito", "Destino 1", "Cinco")
    assert matriz.getter_distancias() == {}
def test_matriz_cargarMatriz_distanciaInvalida_sePropaga(matriz, mock_validaciones):
    mock_validaciones.validar_numero.side_effect = [5, DatoInvalidoError("La distancia no puede ser negativa")]
    with pytest.raises(DatoInvalidoError, match = "La distancia no puede ser negativa"):
        matriz.cargar_matriz([("Deposito", "Destino 1", 5), ("Destino 1", "Destino 2", -3)])

# # Test a futuro - Si cargar matriz falla, no se aplica ninguna distancia
# # Deberíamos implementar así
# def test_matriz_cargarMatriz_distanciaInvalida_noModificaMatriz(matriz, mock_validaciones):
#     mock_validaciones.validar_numero.side_effect = [5, DatoInvalidoError("La distancia no puede ser negativa")]
#     with pytest.raises(DatoInvalidoError):
#         matriz.cargar_matriz([("Deposito", "Destino 1", 5), ("Destino 1", "Destino 2", -3)])
#     assert matriz.getter_distancias() == {}
