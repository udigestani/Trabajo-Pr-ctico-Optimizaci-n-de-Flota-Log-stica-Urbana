import pytest
from articulo import Articulo
from excepciones import DatoInvalidoError

@pytest.fixture(autouse = True)
def resetearId():
    Articulo.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("articulo.Validaciones")
    mock.validar_str.side_effect = lambda valor, **kwargs: valor
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def articulo(mock_validaciones):
    return Articulo("Caja", 10, 0.5)

@pytest.fixture
def articulo_falso_igual(mocker):
    mock = mocker.MagicMock(spec = Articulo)
    mock.getter_id.return_value = 1
    mock.__hash__.return_value = hash(1)
    return mock

# Funcionamiento normal
def test_articulo_ok(articulo):
    assert articulo.descripcion == "Caja"
    assert articulo.peso == 10
    assert articulo.volumen == 0.5
    # id
    assert articulo.id == 1
    articulo2 = Articulo("Art 2", 2, 1)
    assert articulo2.id == 2
# Getters
def test_articulo_getters(articulo):
    assert articulo.getter_id() == 1
    assert articulo.getter_peso() == 10
    assert articulo.getter_volumen() == 0.5
    assert articulo.getter_descripcion() == "Caja"
# Metodos mágicos
def test_articulo_metodosMagicos(articulo, mock_validaciones, articulo_falso_igual):
    assert str(articulo) == "Artículo 1: Caja (10kg, 0.5m³)"
    assert repr(articulo) == "<Articulo 1 'Caja'>"
    #__eq__
    articulo2 = Articulo("Caja", 10, 0.5)
    assert articulo == articulo
    assert articulo == articulo_falso_igual
    assert articulo != articulo2
    assert articulo != "Caja"
    # hash - por si necesitamos en set o dicc
    assert hash(articulo) == hash(articulo.getter_id())
    assert hash(articulo) == hash(articulo_falso_igual)
    assert hash(articulo) != hash(articulo2)
    articulos = {articulo}
    assert articulo in articulos
    diccionario = {articulo: 1}
    assert diccionario[articulo] == 1
# Peso y volummen no modificables
def test_articulo_pesoInmutable(articulo):
    with pytest.raises(AttributeError):
        articulo.setter_peso(20)
    assert articulo.getter_peso() == 10
def test_articulo_volumenInmutable(articulo):
    with pytest.raises(AttributeError):
        articulo.setter_volumen(2)
    assert articulo.getter_volumen() == 0.5
# Validaciones
def test_articulo_validaciones(mock_validaciones):
    Articulo("Caja", 10, 0.5)
    mock_validaciones.validar_str.assert_called_once_with("Caja", nombre = "descripción")
    assert mock_validaciones.validar_numero.call_count == 2
    mock_validaciones.validar_numero.assert_any_call(10, nombre = "peso") # cero = False x defecto
    mock_validaciones.validar_numero.assert_any_call(0.5, nombre = "volumen") # cero = False x defecto
# Errores en __init__
def test_articulo_descripcionVacia_sePropaga(mock_validaciones):
    mock_validaciones.validar_str.side_effect = DatoInvalidoError("La descripción no puede ser vacía")
    with pytest.raises(DatoInvalidoError, match = "La descripción no puede ser vacía"):
        Articulo("   ", 10, 0.5)
    assert Articulo.curr_id == 0
def test_articulo_descripcionNoStr_sePropaga(mock_validaciones):
    mock_validaciones.validar_str.side_effect = TypeError("La descripción no es str")
    with pytest.raises(TypeError, match = "La descripción no es str"):
        Articulo(123, 10, 0.5)
    assert Articulo.curr_id == 0
def test_articulo_pesoInvalido_sePropaga(mock_validaciones):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("El peso debe ser positivo")
    with pytest.raises(DatoInvalidoError, match = "El peso debe ser positivo"):
        Articulo("Caja", 0, 0.5)
    assert Articulo.curr_id == 0
def test_articulo_pesoNoNumero_sePropaga(mock_validaciones):
    mock_validaciones.validar_numero.side_effect = TypeError("El peso debe ser número")
    with pytest.raises(TypeError, match = "El peso debe ser número"):
        Articulo("Caja", "Cinco", 0.5)
    assert Articulo.curr_id == 0
def test_articulo_volumenInvalido_sePropaga(mock_validaciones):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("El volumen debe ser positivo")
    with pytest.raises(DatoInvalidoError, match = "El volumen debe ser positivo"):
        Articulo("Caja", 10, -4)
    assert Articulo.curr_id == 0
def test_articulo_volumenNoNumero_sePropaga(mock_validaciones):
    mock_validaciones.validar_numero.side_effect = TypeError("El volumen debe ser número")
    with pytest.raises(TypeError, match = "El volumen debe ser número"):
        Articulo("Caja", 10, "Uno")
    assert Articulo.curr_id == 0