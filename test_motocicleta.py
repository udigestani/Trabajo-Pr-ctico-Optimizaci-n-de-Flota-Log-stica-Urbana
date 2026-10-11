import pytest
from transporte import Transporte, Motocicleta
from excepciones import DatoInvalidoError, ExcesoPesoError

@pytest.fixture(autouse=True)
def resetearId():
    Transporte.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("transporte.Validaciones")
    mock.validar_numero.side_effect = lambda valor, **kwargs: valor
    return mock

@pytest.fixture
def moto(mock_validaciones):
    return Motocicleta()

@pytest.fixture
def moto_real():
    return Motocicleta()

# Atributos de Motocicleta ctes
def test_motocicleta_atributosClase():
    assert Motocicleta.PESO_MAX == 40
    assert Motocicleta.VOLUMEN == 1
    assert Motocicleta.VELOCIDAD == 45
    assert Motocicleta.COSTO_KM == 1
    assert Motocicleta.COSTO_PARADA == 3
    assert Motocicleta.FACTOR_AMBIENTAL == 0.27

# Funcionamiento normal
def test_motocicleta_ok(moto):
    assert moto.peso_max == 40
    assert moto.volumen == 1
    assert moto.velocidad == 45
    assert moto.costo_km == 1
    assert moto.costo_parada == 3
    assert moto.factor_ambiental == 0.27
    # id
    assert moto.id == 1
    moto2 = Motocicleta()
    assert moto2.id == 2
# Getters
def test_motocicleta_getters(moto):
    assert moto.getter_peso_max() == 40
    assert moto.getter_volumen() == 1
    assert moto.getter_velocidad() == 45
    assert moto.getter_tipo() == "Motocicleta"
# Métodos mágicos
def test_motocicleta_metodosMagicos(moto):
    assert str(moto) == f"Motocicleta {moto.id} (Max: 40kg, 1m³)"
    assert repr(moto) == f"<Motocicleta {moto.id}>"
# Herencia
def test_motocicleta_herencia(moto):
    assert isinstance(moto, Transporte)
    assert issubclass(Motocicleta, Transporte)
# Validaciones
def test_motocicleta_validaciones(mock_validaciones):
    Motocicleta()
    assert mock_validaciones.validar_numero.call_count == 6
    mock_validaciones.validar_numero.assert_any_call(40, nombre = "peso_max")
    mock_validaciones.validar_numero.assert_any_call(1, nombre = "volumen")
    mock_validaciones.validar_numero.assert_any_call(45, nombre = "velocidad")
    mock_validaciones.validar_numero.assert_any_call(1, nombre = "costo_km")
    mock_validaciones.validar_numero.assert_any_call(3, nombre = "costo_parada")
    mock_validaciones.validar_numero.assert_any_call(0.27, nombre = "factor_ambiental")

# Impacto ambiental
def test_motocicleta_impactoAmbiental_ok(moto):
    assert moto.calcular_impacto_ambiental(10, 20) == 2.7    
    assert moto.calcular_impacto_ambiental(10, 0) == 2.7
    assert moto.calcular_impacto_ambiental(0, 10) == 0
#Errores en impacto ambiental
def test_motocicleta_distanciaNegativa(moto_real):
    with pytest.raises(DatoInvalidoError):
        moto_real.calcular_impacto_ambiental(-10, 20)

def test_motocicleta_distanciaInvalida(moto_real):
    with pytest.raises(TypeError):
        moto_real.calcular_impacto_ambiental("Cinco", 50)

def test_motocicleta_pesoNegativo(moto_real):
    with pytest.raises(DatoInvalidoError):
        moto_real.calcular_impacto_ambiental(10, -20)

def test_motocicleta_pesoInvalido(moto_real):
    with pytest.raises(TypeError):
        moto_real.calcular_impacto_ambiental(10, "Veinte")

def test_motocicleta_excesoPeso(moto):
    with pytest.raises(ExcesoPesoError):
        moto.calcular_impacto_ambiental(10, 50)

# distanciaInvalida con mock validaciones
def test_motocicleta_distanciaInvalidaMock(mocker):
    motocicleta = Motocicleta()
    mock = mocker.patch("transporte.Validaciones")
    mock.validar_numero.side_effect = DatoInvalidoError("distancia inválida")
    with pytest.raises(DatoInvalidoError, match = "distancia inválida"):
        motocicleta.calcular_impacto_ambiental(10, 20)
    mock.validar_numero.assert_called_once_with(10, cero = True, nombre = "distancia")
# pesoInvalido con mock validaciones
def test_motocicleta_pesoInvalidoMock(mocker):
    motocicleta = Motocicleta()
    mock = mocker.patch("transporte.Validaciones")
    mock.validar_numero.side_effect = [10, DatoInvalidoError("peso inválido")]
    with pytest.raises(DatoInvalidoError):
        motocicleta.calcular_impacto_ambiental(10, 20)
    mock.validar_numero.assert_any_call(10, cero = True, nombre = "distancia")
    mock.validar_numero.assert_called_with(20, cero = True, nombre = "peso")
