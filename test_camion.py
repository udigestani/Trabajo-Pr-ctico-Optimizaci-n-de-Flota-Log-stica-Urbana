import pytest
from transporte import Transporte, Camion
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
def camion(mock_validaciones):
    return Camion()

@pytest.fixture
def camion_real():
    return Camion()

# Atributos de Camión ctes
def test_camion_atributosClase():
    assert Camion.PESO_MAX == 1500
    assert Camion.VOLUMEN == 20
    assert Camion.VELOCIDAD == 25
    assert Camion.COSTO_KM == 3.5
    assert Camion.COSTO_PARADA == 10
    assert Camion.FACTOR_AMBIENTAL == 1

# Funcionamiento normal
def test_camion_ok(camion):
    assert camion.peso_max == 1500
    assert camion.volumen == 20
    assert camion.velocidad == 25
    assert camion.costo_km == 3.5
    assert camion.costo_parada == 10
    assert camion.factor_ambiental == 1
    # id
    assert camion.id == 1
    camion2 = Camion()
    assert camion2.id == 2
# Getters
def test_camion_getters(camion):
    assert camion.getter_peso_max() == 1500
    assert camion.getter_volumen() == 20
    assert camion.getter_velocidad() == 25
    assert camion.getter_tipo() == "Camion"
# Métodos mágicos
def test_camion_metodosMagicos(camion):
    assert str(camion) == f"Camion {camion.id} (Max: 1500kg, 20m³)"
    assert repr(camion) == f"<Camion {camion.id}>"
# Herencia
def test_camion_herencia(camion):
    assert isinstance(camion, Transporte)
    assert issubclass(Camion, Transporte)
# Validaciones
def test_camion_validaciones(mock_validaciones):
    Camion()
    assert mock_validaciones.validar_numero.call_count == 6
    mock_validaciones.validar_numero.assert_any_call(1500, nombre = "peso_max")
    mock_validaciones.validar_numero.assert_any_call(20, nombre = "volumen")
    mock_validaciones.validar_numero.assert_any_call(25, nombre = "velocidad")
    mock_validaciones.validar_numero.assert_any_call(3.5, nombre = "costo_km")
    mock_validaciones.validar_numero.assert_any_call(10, nombre = "costo_parada")
    mock_validaciones.validar_numero.assert_any_call(1, nombre = "factor_ambiental")

# Impacto ambiental
def test_camion_impactoAmbiental_ok(camion):
    assert camion.calcular_impacto_ambiental(10, 1000) == 11
    assert camion.calcular_impacto_ambiental(10, 0) == 10
    assert camion.calcular_impacto_ambiental(10, 1000) < camion.calcular_impacto_ambiental(10, 1500)
    assert camion.calcular_impacto_ambiental(0, 1000) == 0
#Errores en impacto ambiental
def test_camion_distanciaNegativa(camion_real):
    with pytest.raises(DatoInvalidoError):
        camion_real.calcular_impacto_ambiental(-10, 1000)

def test_camion_distanciaInvalida(camion_real):
    with pytest.raises(TypeError):
        camion_real.calcular_impacto_ambiental("Cinco", 1000)

def test_camion_pesoNegativo(camion_real):
    with pytest.raises(DatoInvalidoError):
        camion_real.calcular_impacto_ambiental(10, -1000)

def test_camion_pesoInvalido(camion_real):
    with pytest.raises(TypeError):
        camion_real.calcular_impacto_ambiental(10, "Mil")

def test_camion_excesoPeso(camion):
    with pytest.raises(ExcesoPesoError):
        camion.calcular_impacto_ambiental(10, 1600)

# distanciaInvalida con mock validaciones
def test_camion_distanciaInvalidaMock(mocker):
    camion = Camion()
    mock_validaciones = mocker.patch("transporte.Validaciones")
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("distancia inválida")
    with pytest.raises(DatoInvalidoError,  match = "distancia inválida"):
        camion.calcular_impacto_ambiental(10, 1000)
    mock_validaciones.validar_numero.assert_called_once_with(10, cero = True, nombre = "distancia")
# pesoInvalido con mock validaciones
def test_camion_pesoInvalidoMock(mocker):
    camion = Camion()
    mock_validaciones = mocker.patch("transporte.Validaciones")
    mock_validaciones.validar_numero.side_effect = [10, DatoInvalidoError("peso inválido")]
    with pytest.raises(DatoInvalidoError):
        camion.calcular_impacto_ambiental(10, 1000)
    mock_validaciones.validar_numero.assert_any_call(10, cero = True, nombre = "distancia")
    mock_validaciones.validar_numero.assert_called_with(1000, cero = True, nombre = "peso")
