import pytest
from transporte import Transporte, Furgoneta, Camion, Motocicleta
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
def transporte(mock_validaciones):
    return Transporte(100, 10, 50, 2, 5, 0.5)

@pytest.fixture
def transporte_real():
    return Transporte(100, 10, 50, 2, 5, 0.5)

# Funcionamiento normal
def test_transporte_ok(transporte):
    assert transporte.getter_peso_max() == 100
    assert transporte.getter_volumen() == 10
    assert transporte.getter_velocidad() == 50
    assert transporte.getter_costo_km() == 2
    assert transporte.getter_costo_parada() == 5
    assert transporte.getter_factor_ambiental() == 0.5
    # id
    assert transporte.getter_id() == 1
    transporte2 = Transporte(100, 10, 50, 2, 5, 0.5)
    assert transporte2.getter_id() == 2
# Setter id
def test_transporte_setterId(transporte):
    transporte.setter_id(7)
    assert transporte.getter_id() == 7
# Unidad del impacto ambiental
def test_transporte_unidadImpacto():
    assert Transporte.UNIDAD_IMPACTO == "kg CO₂"
# Getters
def test_transporte_getters(transporte):
    assert transporte.getter_peso_max() == 100
    assert transporte.getter_volumen() == 10
    assert transporte.getter_velocidad() == 50
    assert transporte.getter_tipo() == "Transporte"
    assert transporte.getter_costo_km() == 2
    assert transporte.getter_costo_parada() == 5
# Métodos mágicos
def test_transporte_metodosMagicos(transporte):
    assert str(transporte) == "Transporte 1 (Max: 100kg, 10m³)"
    assert repr(transporte) == "<Transporte 1>"
# Herencia
def test_transporte_herencia(transporte):
    assert isinstance(transporte, Transporte)
    assert not isinstance(transporte, (Furgoneta, Motocicleta, Camion))
    assert issubclass(Camion, Transporte)
    assert issubclass(Furgoneta, Transporte)
    assert issubclass(Motocicleta, Transporte)
# Validaciones
def test_transporte_validaciones(mock_validaciones):
    Transporte(100, 10, 50, 2, 5, 0.5)
    assert mock_validaciones.validar_numero.call_count == 6
    mock_validaciones.validar_numero.assert_any_call(100, nombre = "peso_max")
    mock_validaciones.validar_numero.assert_any_call(10, nombre = "volumen")
    mock_validaciones.validar_numero.assert_any_call(50, nombre = "velocidad")
    mock_validaciones.validar_numero.assert_any_call(2, nombre = "costo_km")
    mock_validaciones.validar_numero.assert_any_call(5, cero = True, nombre = "costo_parada")
    mock_validaciones.validar_numero.assert_any_call(0.5, nombre = "factor_ambiental")

def test_transporte_errorValidacion(mock_validaciones):
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("dato inválido")
    with pytest.raises(DatoInvalidoError, match = "dato inválido"):
        Transporte(-100, 10, 50, 2, 5, 0.5)
    assert Transporte.curr_id == 0

# Errores en __init__ validaciones reales
def test_transporte_costoParadaCero_real():
    transporte = Transporte(100, 10, 50, 2, 0, 0.5)
    assert transporte.getter_costo_parada() == 0

def test_transporte_costoParadaNegativo_real():
    with pytest.raises(DatoInvalidoError):
        Transporte(100, 10, 50, 2, -5, 0.5)
    assert Transporte.curr_id == 0

def test_transporte_pesoNegativo_real():
    with pytest.raises(DatoInvalidoError):
        Transporte(-100, 10, 50, 2, 5, 0.5)

def test_transporte_velocidadCero_real():
    with pytest.raises(DatoInvalidoError):
        Transporte(100, 10, 0, 2, 5, 0.5)

def test_transporte_tipoInvalido_real():
    with pytest.raises(TypeError):
        Transporte("100", 10, 50, 2, 5, 0.5)

# Impacto ambiental
def test_transporte_impactoAmbiental_ok(transporte):
    assert transporte.calcular_impacto_ambiental(10, 50) == 5
    assert transporte.calcular_impacto_ambiental(10, 0) == 5
    assert transporte.calcular_impacto_ambiental(0, 50) == 0

def test_transporte_impactoAmbiental_validaciones(transporte, mocker):
    mock_validaciones = mocker.patch("transporte.Validaciones")
    mock_validaciones.validar_numero.side_effect = lambda valor, **kwargs: valor
    transporte.calcular_impacto_ambiental(10, 50)
    assert mock_validaciones.validar_numero.call_count == 2
    mock_validaciones.validar_numero.assert_any_call(10, cero = True, nombre = "distancia")
    mock_validaciones.validar_numero.assert_any_call(50, cero = True, nombre = "peso")

# Errores impacto ambiental
def test_transporte_distanciaNegativa_real(transporte_real):
    with pytest.raises(DatoInvalidoError):
        transporte_real.calcular_impacto_ambiental(-10, 50)

def test_transporte_pesoNegativo_impacto_real(transporte_real):
    with pytest.raises(DatoInvalidoError):
        transporte_real.calcular_impacto_ambiental(10, -50)

def test_transporte_distanciaInvalida_real(transporte_real):
    with pytest.raises(TypeError):
        transporte_real.calcular_impacto_ambiental("Diez", 50)

def test_transporte_pesoInvalido_real(transporte_real):
    with pytest.raises(TypeError):
        transporte_real.calcular_impacto_ambiental(10, "Cincuenta")

def test_transporte_excesoPeso(transporte):
    with pytest.raises(ExcesoPesoError):
        transporte.calcular_impacto_ambiental(10, 200)

# distanciaInvalida con mock validaciones
def test_transporte_distanciaInvalidaMock(mocker):
    transporte = Transporte(100, 10, 50, 2, 5, 0.5)
    mock_validaciones = mocker.patch("transporte.Validaciones")
    mock_validaciones.validar_numero.side_effect = DatoInvalidoError("distancia inválida")
    with pytest.raises(DatoInvalidoError, match = "distancia inválida"):
        transporte.calcular_impacto_ambiental(10, 50)
    mock_validaciones.validar_numero.assert_called_once_with(10, cero = True, nombre = "distancia")
# pesoInvalido con mock validaciones
def test_transporte_pesoInvalidoMock(mocker):
    transporte = Transporte(100, 10, 50, 2, 5, 0.5)
    mock_validaciones = mocker.patch("transporte.Validaciones")
    mock_validaciones.validar_numero.side_effect = [10, DatoInvalidoError("peso inválido")]
    with pytest.raises(DatoInvalidoError, match = "peso inválido"):
        transporte.calcular_impacto_ambiental(10, 50)
    mock_validaciones.validar_numero.assert_called_with(50, cero = True, nombre = "peso")


# Deserializar con un tipo desconocido
def test_transporte_deserializar_tipoDesconocido():
    archivo = [["tipo", "id", "peso_max", "volumen", "velocidad", "costo_km", "costo_parada", "factor_ambiental", "Transporte"],
               ["Bicicleta", "1", "10", "1", "20", "1", "1", "0.1"]]
    with pytest.raises(DatoInvalidoError, match = "Tipo de transporte desconocido: Bicicleta"):
        Transporte.deserializar(archivo)


# ---------- serializar ----------
def test_transporte_serializar(transporte):
    assert transporte.serializar() == ["Transporte", 1, 100, 10, 50, 2, 5, 0.5]

# ---------- deserializar ----------
ENCABEZADO = ["tipo", "id", "peso_max", "volumen", "velocidad", "costo_km", "costo_parada", "factor_ambiental", "Transporte"]
# Transporte genérico y las tres subclases
def test_transporte_deserializar_ok():
    archivo = [ENCABEZADO,
               ["Transporte", "4", "100", "10", "50", "2", "5", "0.5"],
               [],
               ["Furgoneta", "5", "500", "8", "30", "2", "5", "0.27"],
               ["Motocicleta", "6", "40", "1", "45", "1", "3", "0.27"],
               ["Camion", "9", "1500", "20", "25", "3.5", "10", "1"]]
    transportes = Transporte.deserializar(archivo)
    assert len(transportes) == 4
    generico, furgoneta, moto, camion = transportes
    assert generico.getter_tipo() == "Transporte"
    assert generico.getter_id() == 4
    assert generico.getter_peso_max() == 100.0
    assert generico.getter_volumen() == 10.0
    assert generico.getter_velocidad() == 50.0
    assert generico.getter_costo_km() == 2.0
    assert generico.getter_costo_parada() == 5.0
    assert generico.getter_factor_ambiental() == 0.5
    assert isinstance(furgoneta, Furgoneta)
    assert furgoneta.getter_id() == 5
    assert isinstance(moto, Motocicleta)
    assert moto.getter_id() == 6
    assert isinstance(camion, Camion)
    assert camion.getter_id() == 9
    # Las subclases usan sus propias constantes
    assert camion.getter_peso_max() == Camion.PESO_MAX
    # El próximo id continúa desde el mayor
    assert Transporte.curr_id == 9
# Sin filas
def test_transporte_deserializar_soloEncabezado():
    assert Transporte.deserializar([ENCABEZADO]) == []
    assert Transporte.curr_id == 0
# Datos inválidos en un transporte genérico
def test_transporte_deserializar_datoInvalido():
    with pytest.raises(DatoInvalidoError):
        Transporte.deserializar([ENCABEZADO, ["Transporte", "4", "-100", "10", "50", "2", "5", "0.5"]])
# Lo serializado se puede volver a cargar
def test_transporte_serializar_deserializar(transporte_real):
    fila = list(map(str, transporte_real.serializar()))
    copia = Transporte.deserializar([ENCABEZADO, fila])[0]
    assert copia.getter_id() == transporte_real.getter_id()
    assert copia.getter_tipo() == transporte_real.getter_tipo()
    assert copia.getter_peso_max() == transporte_real.getter_peso_max()
    assert copia.getter_costo_parada() == transporte_real.getter_costo_parada()
    assert copia.getter_factor_ambiental() == transporte_real.getter_factor_ambiental()
def test_transporte_serializar_deserializar_subclases():
    originales = [Furgoneta(), Motocicleta(), Camion()]
    archivo = [ENCABEZADO] + list(map(lambda t: list(map(str, t.serializar())), originales))
    copias = Transporte.deserializar(archivo)
    assert list(map(lambda t: t.getter_tipo(), copias)) == ["Furgoneta", "Motocicleta", "Camion"]
    assert list(map(lambda t: t.getter_id(), copias)) == list(map(lambda t: t.getter_id(), originales))
