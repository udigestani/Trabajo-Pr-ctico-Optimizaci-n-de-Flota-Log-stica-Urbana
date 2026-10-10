import pytest
from persona import Persona, Administrador, Solicitante
from excepciones import DatoInvalidoError, DNIInvalidoError

@pytest.fixture(autouse=True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

# Mock de Validaciones --> Asumimos que funciona y devuelve el valor
@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("persona.Validaciones")
    mock.validar_str.side_effect = lambda valor, nombre = "valor": valor
    mock.validar_dni.side_effect = lambda dni, registrados = (): dni
    mock.validar_digitos.side_effect = lambda valor, cantidades, nombre = "valor": valor
    return mock

@pytest.fixture
def persona_base(mock_validaciones):
    return Persona("Juan", 12345678, 1123456789)

@pytest.fixture
def mock_persona_igual(mocker):
    mock_persona = mocker.Mock(spec = Persona)
    mock_persona.getter_dni.return_value = 12345678
    return mock_persona

@pytest.fixture
def mock_persona_distinta(mocker):
    mock_persona = mocker.Mock(spec = Persona)
    mock_persona.getter_dni.return_value = 87654321
    return mock_persona

# Funcionamiento normal
def test_persona_ok(persona_base):
    assert persona_base.getter_nombre() == "Juan"
    assert persona_base.getter_dni() == 12345678
    assert persona_base.getter_telefono() == 1123456789
    assert Persona.getter_dnis_registrados() == {12345678: persona_base}
    assert Persona.getter_dnis_registrados()[12345678] is persona_base
# Metodos magicos
def test_persona_metodosMagicos(persona_base, mock_persona_igual, mock_persona_distinta):
    assert str(persona_base) == "Persona de nombre Juan y DNI: 12345678"
    assert repr(persona_base) == "<Persona Juan - 12345678>"
    assert persona_base == persona_base
    assert persona_base == mock_persona_igual # Mismo dni
    mock_persona_igual.getter_dni.assert_called_once()
    assert persona_base != mock_persona_distinta
    assert persona_base not in {"Juan", 12345678, 1123456789, None, Persona}
# Hashable (por si necesitamos después dicc y set)
def test_persona_hash(persona_base):
    assert hash(persona_base) == hash(12345678)
    personas = {persona_base}
    assert persona_base in personas
    diccionario = {persona_base: 1}
    assert diccionario[persona_base] == 1
# Varias personas
def test_persona_variasPersonas(persona_base, mock_validaciones):
    persona1 = Persona("Manuel", 24680000, 1123456789)
    persona2 = Persona("Massimo", 87654321, 1198765432)
    assert Persona.getter_dnis_registrados() == {12345678: persona_base, 24680000: persona1, 87654321: persona2}
    Persona.getter_dnis_registrados().clear()
    assert Persona.dnis_registrados != {}
    Persona.limpiar_dnis_registrados()
    assert Persona.dnis_registrados == {}

# Herencia
def test_persona_herencia(persona_base):
    assert isinstance(persona_base, Persona)
    assert not isinstance(persona_base, (Solicitante, Administrador))
    assert issubclass(Administrador, Persona)
    assert issubclass(Solicitante, Persona)

# Validaciones
def test_persona_validaciones(mock_validaciones):
    Persona("Juan", 12345678, 1123456789)
    mock_validaciones.validar_str.assert_called_once_with("Juan", nombre = "nombre")
    mock_validaciones.validar_digitos.assert_called_once_with(1123456789, 10, "teléfono")
    mock_validaciones.validar_dni.assert_called_once_with(12345678, Persona.dnis_registrados)

def test_persona_usaValorValidado(mocker):
    mock_validar = mocker.patch("persona.Validaciones")
    mock_validar.validar_str.return_value = "Nombre validado"
    mock_validar.validar_dni.return_value = "Dni validado"
    mock_validar.validar_digitos.return_value = "Teléfono validado"
    persona = Persona("   nombre   ", 12345678, 1123456789)
    assert persona.getter_nombre() == "Nombre validado"
    assert persona.getter_dni() == "Dni validado"
    assert persona.getter_telefono() == "Teléfono validado"

# Datos invalidos
def test_persona_nombreInvalido(mock_validaciones):
    mock_validaciones.validar_str.side_effect = DatoInvalidoError("El nombre no debe estar vacío")
    with pytest.raises(DatoInvalidoError, match = "El nombre no debe estar vacío"):
        Persona("     ", 12345678, 1123456789)
    assert Persona.dnis_registrados == {}
    mock_validaciones.validar_dni.assert_not_called()
    mock_validaciones.validar_digitos.assert_not_called()

def test_persona_nombreTipoInvalido(mock_validaciones):
    mock_validaciones.validar_str.side_effect = TypeError("El nombre 5 debe ser una cadena str")
    with pytest.raises(TypeError, match = "debe ser una cadena str"):
        Persona(5, 12345678, 1123456789)
    assert Persona.dnis_registrados == {}

def test_persona_dniInvalido(mock_validaciones):
    mock_validaciones.validar_dni.side_effect = DatoInvalidoError("El DNI 123 debe ser un número entero positivo de 7 o 8 dígitos")
    with pytest.raises(DatoInvalidoError, match = "El DNI 123 debe ser"):
        Persona("Manuel", 123, 1123456789)
    assert Persona.dnis_registrados == {}
    mock_validaciones.validar_digitos.assert_not_called()

# Dni duplicado mock
def test_persona_dniDuplicado(persona_base, mock_validaciones):
    mock_validaciones.validar_dni.side_effect = DNIInvalidoError(12345678)
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Persona("Uriel", 12345678, 1123456789)
    assert Persona.dnis_registrados[12345678] is persona_base
    assert "Uriel" not in map(lambda per: per.nombre, Persona.dnis_registrados.values())
# Dni duplicado real 
def test_persona_dniDuplicado_real():
    original = Persona("Juan", 12345678, 1123456789)
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Persona("Uriel", 12345678, 1198765432)
    assert Persona.getter_dnis_registrados() == {12345678: original}
    assert Persona.dnis_registrados[12345678] is original
    assert Persona.dnis_registrados[12345678].getter_nombre() == "Juan"

def test_persona_telefonoInvalido(mock_validaciones):
    mock_validaciones.validar_digitos.side_effect = DatoInvalidoError("El teléfono 1234 debe ser un número entero positivo de 10 dígitos")
    with pytest.raises(DatoInvalidoError, match = "El teléfono 1234 debe ser"):
        Persona("Manuel", 12345678, 1234)
    assert Persona.dnis_registrados == {}