import pytest
from transporte import Transporte, Furgoneta
from excepciones import DatoInvalidoError, ExcesoPesoError

@pytest.fixture(autouse=True)
def reset_id():
    Transporte.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("transporte.Validaciones")
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def furgoneta(mock_validaciones):
    return Furgoneta()

@pytest.fixture
def furgoneta_real():
    return Furgoneta()

# Atributos de Furgoneta ctes
def test_furgoneta_atributosClase():
    assert Furgoneta.PESO_MAX == 500
    assert Furgoneta.VOLUMEN == 8
    assert Furgoneta.VELOCIDAD == 30
    assert Furgoneta.COSTO_KM == 2
    assert Furgoneta.COSTO_PARADA == 5
    assert Furgoneta.FACTOR_AMBIENTAL == 0.27

# Funcionamiento normal
def test_furgoneta_ok(furgoneta):
    assert furgoneta.peso_max == 500
    assert furgoneta.volumen == 8
    assert furgoneta.velocidad == 30
    assert furgoneta.costo_km == 2
    assert furgoneta.costo_parada == 5
    assert furgoneta.factor_ambiental == 0.27
    # id
    assert furgoneta.id == 1
    furgoneta2 = Furgoneta()
    assert furgoneta2.id == 2
# Getters
def test_furgoneta_getters(furgoneta):
    assert furgoneta.getter_peso_max() == 500
    assert furgoneta.getter_volumen() == 8
    assert furgoneta.getter_velocidad() == 30
    assert furgoneta.getter_tipo() == "Furgoneta"
# Métodos mágicos
def test_furgoneta_metodosMagicos(furgoneta):
    assert str(furgoneta) == f"Furgoneta {furgoneta.id} (Max: 500kg, 8m³)"
    assert repr(furgoneta) == f"<Furgoneta {furgoneta.id}>"
# Herencia
def test_furgoneta_herencia(furgoneta):
    assert isinstance(furgoneta, Transporte)
    assert issubclass(Furgoneta, Transporte)
# Validaciones
def test_furgoneta_validaciones(mock_validaciones):
    Furgoneta()
    assert mock_validaciones.validar_numero.call_count == 6
    mock_validaciones.validar_numero.assert_any_call(500, nombre = "peso_max")
    mock_validaciones.validar_numero.assert_any_call(8, nombre = "volumen")
    mock_validaciones.validar_numero.assert_any_call(30, nombre = "velocidad")
    mock_validaciones.validar_numero.assert_any_call(2, nombre = "costo_km")
    mock_validaciones.validar_numero.assert_any_call(5, nombre = "costo_parada")
    mock_validaciones.validar_numero.assert_any_call(0.27, nombre = "factor_ambiental")

# Impacto ambiental
def test_furgoneta_impactoAmbiental_ok(furgoneta):
    assert furgoneta.calcular_impacto_ambiental(10, 100) == 2.7
    assert furgoneta.calcular_impacto_ambiental(10, 0) == 2.7
    assert furgoneta.calcular_impacto_ambiental(0, 50) == 0
# Errores en impacto ambiental
def test_furgoneta_distanciaNegativa(furgoneta_real):
    with pytest.raises(DatoInvalidoError):
        furgoneta_real.calcular_impacto_ambiental(-10, 100)

def test_furgoneta_distanciaInvalida(furgoneta_real):
    with pytest.raises(TypeError):
        furgoneta_real.calcular_impacto_ambiental("Cinco", 50)
    
def test_furgoneta_pesoNegativo(furgoneta_real):
    with pytest.raises(DatoInvalidoError):
        furgoneta_real.calcular_impacto_ambiental(10, -100)

def test_furgoneta_pesoInvalido(furgoneta_real):
    with pytest.raises(TypeError):
        furgoneta_real.calcular_impacto_ambiental(10, "Cien")

def test_furgoneta_excesoPeso(furgoneta):
    with pytest.raises(ExcesoPesoError):
        furgoneta.calcular_impacto_ambiental(10, 600)

# distanciaInvalida con mock validaciones
def test_furgoneta_distanciaInvalidaMock(mocker):
    furgoneta = Furgoneta()
    mock = mocker.patch("transporte.Validaciones")
    mock.validar_numero.side_effect = DatoInvalidoError("distancia inválida")
    with pytest.raises(DatoInvalidoError, match = "distancia inválida"):
        furgoneta.calcular_impacto_ambiental(10, 100)
    mock.validar_numero.assert_called_once_with(10, cero = True, nombre = "distancia")
# pesoInvalido con mock validaciones
def test_furgoneta_pesoInvalidoMock(mocker):
    furgoneta = Furgoneta()
    mock = mocker.patch("transporte.Validaciones")
    mock.validar_numero.side_effect = [10, DatoInvalidoError("peso inválido")]
    with pytest.raises(DatoInvalidoError):
        furgoneta.calcular_impacto_ambiental(10, 100)
    mock.validar_numero.assert_any_call(10, cero = True, nombre = "distancia")
    mock.validar_numero.assert_called_with(100, cero = True, nombre = "peso")
