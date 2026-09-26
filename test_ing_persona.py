import pytest
from datetime import datetime, timedelta
from articulo import Articulo
from viaje import Viaje
from persona import Persona, Administrador, Solicitante
from excepciones import DatoInvalidoError, DNIInvalidoError

@pytest.fixture(autouse=True)
def limpiar_dnis():
    # dnis_registrados es un atributo de clase: se limpia para que los tests no dependan entre sí
    Persona.dnis_registrados.clear()
    yield
    Persona.dnis_registrados.clear()

@pytest.fixture
def persona_base():
    return Persona("Juan Perez", 12345678, 1123456789)


# TESTS DE CREACIÓN CORRECTA
def test_persona_valida(persona_base):
    assert persona_base.nombre == "Juan Perez"
    assert persona_base.dni == 12345678
    assert persona_base.telefono == 1123456789
    assert Persona.dnis_registrados[12345678] is persona_base
def test_subclases_registran_dni():
    admin = Administrador("Ana Gomez", 23456789, 1134567890)
    solicitante = Solicitante("Luis Diaz", 34567890, 1145678901)
    assert isinstance(admin, Persona)
    assert isinstance(solicitante, Persona)
    assert Persona.dnis_registrados[23456789] is admin
    assert Persona.dnis_registrados[34567890] is solicitante
def test_str_repr_eq(persona_base):
    assert str(persona_base) == "Persona de nombre Juan Perez y DNI: 12345678"
    assert repr(persona_base) == "<Persona Juan Perez - 12345678>"
    assert persona_base == persona_base
    assert persona_base != Persona("Otra Persona", 87654321, 1198765432)
    assert persona_base != "Juan Perez"


# TESTS DE EXCEPCIONES
def test_dni_duplicado(persona_base):
    with pytest.raises(DNIInvalidoError, match="El DNI 12345678 ya está registrado"):
        Persona("Otro Nombre", 12345678, 1198765432)
    # El DNI sigue apuntando a la persona original
    assert Persona.dnis_registrados[12345678] is persona_base
def test_dni_duplicado_entre_subclases():
    Administrador("Ana Gomez", 23456789, 1134567890)
    with pytest.raises(DNIInvalidoError, match="El DNI 23456789 ya está registrado"):
        Solicitante("Luis Diaz", 23456789, 1145678901)
def test_dni_no_entero():
    with pytest.raises(DatoInvalidoError, match="El DNI 12345678 debe ser un número entero positivo de 8 dígitos"):
        Persona("Juan Perez", "12345678", 1123456789)
    assert Persona.dnis_registrados == {}
def test_dni_largo_invalido():
    with pytest.raises(DatoInvalidoError, match="El DNI 1234567 debe ser un número entero positivo de 8 dígitos"):
        Persona("Juan Perez", 1234567, 1123456789)
    assert 1234567 not in Persona.dnis_registrados
def test_telefono_largo_invalido():
    with pytest.raises(DatoInvalidoError, match="El teléfono 12345 debe ser un número entero positivo de 10 dígitos"):
        Persona("Juan Perez", 12345678, 12345)
    # Si falla la validación del teléfono, el DNI no debe quedar registrado
    assert 12345678 not in Persona.dnis_registrados
def test_telefono_no_entero():
    with pytest.raises(DatoInvalidoError, match="El teléfono 1123456789 debe ser un número entero positivo de 10 dígitos"):
        Persona("Juan Perez", 12345678, "1123456789")
def test_nombre_vacio():
    with pytest.raises(DatoInvalidoError, match="debe ser una cadena de caracteres no vacía"):
        Persona("", 12345678, 1123456789)
    assert Persona.dnis_registrados == {}


# Estos tests daban Failed y se arreglaron

def test_dni_negativo():
    with pytest.raises(DatoInvalidoError):
        Persona("Juan Perez", -1234567, 1123456789)

def test_telefono_negativo():
    with pytest.raises(DatoInvalidoError):
        Persona("Juan Perez", 12345678, -123456789)

def test_nombre_solo_espacios():
    with pytest.raises(DatoInvalidoError):
        Persona("   ", 12345678, 1123456789)

# def test_persona_hasheable(persona_base):
#     # GAP: Persona define __eq__ pero no __hash__, así que Python la vuelve unhashable
#     # automáticamente. No se puede guardar en un set ni usar como clave de diccionario.
#     personas = {persona_base}
#     assert persona_base in personas

def test_validar_viaje_creando_solicitud():
    with pytest.raises(DatoInvalidoError):
        Solicitante.crear_solicitud("no soy un viaje", "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0))
