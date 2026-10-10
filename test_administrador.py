import pytest
from datetime import datetime
from persona import Persona, Administrador
from viaje import Viaje
from transporte import Transporte
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError, DNIInvalidoError


@pytest.fixture(autouse=True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

@pytest.fixture
def admin():
    return Administrador("Juan", 12345678, 1122334455)

@pytest.fixture
def mock_transporte(mocker):
    return mocker.Mock(spec = Transporte)

@pytest.fixture
def mock_matriz(mocker):
    return mocker.Mock(spec = MatrizDistancia)

@pytest.fixture
def horario():
    return datetime(2026, 10, 9, 8, 0)

# Funcionamiento normal
def test_admin_ok(admin):
    assert admin.getter_nombre() == "Juan"
    assert admin.getter_dni() == 12345678
    assert admin.getter_telefono() == 1122334455
    assert isinstance(admin, Administrador)
    assert isinstance(admin, Persona)
    assert issubclass(Administrador, Persona)
    assert Persona.getter_dnis_registrados() == {12345678: admin}
    assert str(admin) == "Persona de nombre Juan y DNI: 12345678"
    assert repr(admin) == "<Persona Juan - 12345678>"

# DNIInvalidoError si el DNI ya está registrado
def test_admin_dniRepetido(admin):
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Administrador("Uriel", 12345678, 1155556666)

# # Datos invalidos
# def test_admin_datosInvalidos():
#     with pytest.raises(DatoInvalidoError, match = "El nombre no debe estar vacío"):
#         Administrador("      ", 12345678, 1122334455)
#     with pytest.raises(DatoInvalidoError, match = "El DNI 123 debe ser un número entero positivo de 7 o 8 dígitos"):
#         Administrador("Ana", 123, 1122334455)
#     with pytest.raises(DatoInvalidoError, match = "El teléfono 112233 debe ser un número entero positivo de 10 dígitos"):
#         Administrador("Ana", 12345678, 112233)
# VA PARA PERSONA

def test_crearViaje_ok(admin, mock_transporte, mock_matriz, horario):
    viaje = admin.crear_viaje(mock_transporte, "Deposito", horario, mock_matriz)
    assert isinstance(viaje, Viaje)
    assert viaje.transporte is mock_transporte
    assert viaje.deposito == "Deposito"
    assert viaje.horario == horario
    assert viaje.matriz is mock_matriz
    assert viaje.estado == "PLANIFICADO"
    assert viaje.solicitudes == viaje.incidentes == viaje.paradas_resueltas == []
    assert viaje.peso_total == 0

def test_crearViaje_dosViajes(admin, mock_transporte, mock_matriz, horario):
    viaje1 = admin.crear_viaje(mock_transporte, "Deposito", horario, mock_matriz)
    viaje2 = admin.crear_viaje(mock_transporte, "Deposito", horario, mock_matriz)
    assert viaje1 is not viaje2
    assert viaje1.id != viaje2.id

def test_crearViaje_datosInvalidos(admin, mock_transporte, mock_matriz, horario):
    # transporte invalido
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Transporte"):
        admin.crear_viaje("camion", "Deposito", horario, mock_matriz)
    # deposito invalido
    with pytest.raises(DatoInvalidoError, match = "El depósito no debe estar vacío"):
        admin.crear_viaje(mock_transporte, "      ", horario, mock_matriz)
    # horario invalido
    with pytest.raises(TypeError, match = "debe ser un objeto datetime"):
        admin.crear_viaje(mock_transporte, "Deposito", "8:00", mock_matriz)
    # matriz invalida
    matriz = {("Deposito", "D1"): 10}
    with pytest.raises(TypeError, match = "debe ser un objeto de clase MatrizDistancia"):
        admin.crear_viaje(mock_transporte, "Deposito", horario, matriz)