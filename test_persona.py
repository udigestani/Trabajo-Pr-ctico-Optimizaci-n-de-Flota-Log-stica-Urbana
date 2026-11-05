import pytest
from persona import Persona, Administrador, Solicitante
from excepciones import DatoInvalidoError, DNIInvalidoError

@pytest.fixture(autouse=True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

# DNIs que hay en el árbol, ordenados
def dnis_registrados():
    arbol = Persona.getter_dnis_registrados()
    return list(map(lambda par: par[0], arbol.inorden(arbol.getter_raiz())))

# Mock de Validaciones --> Asumimos que funciona y devuelve el valor
@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("persona.Validaciones")
    mock.validar_str.side_effect = lambda valor, nombre = "valor": valor
    mock.validar_dni.side_effect = lambda dni, registrados = None: dni
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
    # La persona queda guardada en el árbol de DNIs
    arbol = Persona.getter_dnis_registrados()
    assert dnis_registrados() == [12345678]
    assert arbol.buscar(arbol.getter_raiz(), 12345678) is persona_base
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
    assert dnis_registrados() == [12345678, 24680000, 87654321]
    arbol = Persona.getter_dnis_registrados()
    assert arbol.buscar(arbol.getter_raiz(), 24680000) is persona1
    assert arbol.buscar(arbol.getter_raiz(), 87654321) is persona2
    assert arbol.buscar(arbol.getter_raiz(), 11111111) is None
    Persona.limpiar_dnis_registrados()
    assert Persona.getter_dnis_registrados().esVacio()
    assert dnis_registrados() == []

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
    mock_validaciones.validar_dni.assert_called_once_with(12345678, Persona.getter_dnis_registrados())

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
    assert dnis_registrados() == []
    mock_validaciones.validar_dni.assert_not_called()
    mock_validaciones.validar_digitos.assert_not_called()

def test_persona_nombreTipoInvalido(mock_validaciones):
    mock_validaciones.validar_str.side_effect = TypeError("El nombre 5 debe ser una cadena str")
    with pytest.raises(TypeError, match = "debe ser una cadena str"):
        Persona(5, 12345678, 1123456789)
    assert dnis_registrados() == []

def test_persona_dniInvalido(mock_validaciones):
    mock_validaciones.validar_dni.side_effect = DatoInvalidoError("El DNI 123 debe ser un número entero positivo de 7 o 8 dígitos")
    with pytest.raises(DatoInvalidoError, match = "El DNI 123 debe ser"):
        Persona("Manuel", 123, 1123456789)
    assert dnis_registrados() == []
    mock_validaciones.validar_digitos.assert_not_called()

# Dni duplicado mock
def test_persona_dniDuplicado(persona_base, mock_validaciones):
    mock_validaciones.validar_dni.side_effect = DNIInvalidoError(12345678)
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        noExiste = None
        noExiste = Persona("Uriel", 12345678, 1123456789)
    assert persona_base.getter_dni() == 12345678
    assert dnis_registrados() == [12345678]
    assert noExiste is None

# Dni duplicado real 
def test_persona_dniDuplicado_real():
    original = Persona("Juan", 12345678, 1123456789)
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        noExiste = None
        noExiste = Persona("Uriel", 12345678, 1198765432)
    assert original.getter_dni() == 12345678
    assert dnis_registrados() == [12345678]
    arbol = Persona.getter_dnis_registrados()
    assert arbol.buscar(arbol.getter_raiz(), 12345678) is original
    assert noExiste is None

def test_persona_telefonoInvalido(mock_validaciones):
    mock_validaciones.validar_digitos.side_effect = DatoInvalidoError("El teléfono 1234 debe ser un número entero positivo de 10 dígitos")
    with pytest.raises(DatoInvalidoError, match = "El teléfono 1234 debe ser"):
        Persona("Manuel", 12345678, 1234)
    assert dnis_registrados() == []


# ---------- buscar_persona ----------
# Árbol con 20000000 en la raíz, 10000000 a la izquierda y 30000000 a la derecha
@pytest.fixture
def personas_buscables(mock_validaciones):
    raiz = Persona("Raiz", 20000000, 1123456789)
    izquierda = Persona("Izquierda", 10000000, 1123456789)
    derecha = Persona("Derecha", 30000000, 1123456789)
    return raiz, izquierda, derecha

# Funcionamiento normal: devuelve la persona y los saltos desde la raíz
def test_buscarPersona_ok(personas_buscables):
    raiz, izquierda, derecha = personas_buscables
    assert Persona.buscar_persona(20000000) == (raiz, 0)
    assert Persona.buscar_persona(10000000) == (izquierda, 1)
    assert Persona.buscar_persona(30000000) == (derecha, 1)
    persona, saltos = Persona.buscar_persona(30000000)
    assert persona is derecha
# Si no existe devuelve None y los saltos hasta llegar a un lugar vacío
def test_buscarPersona_noExiste(personas_buscables):
    assert Persona.buscar_persona(99999999) == (None, 2)
    assert Persona.buscar_persona(1111111) == (None, 2)
    assert Persona.buscar_persona(25000000) == (None, 2)
# Árbol vacío
def test_buscarPersona_arbolVacio():
    assert Persona.buscar_persona(12345678) == (None, 0)
# Se puede llamar desde una instancia y desde las subclases
def test_buscarPersona_desdeInstanciaYSubclases(persona_base, mock_validaciones):
    admin = Administrador("Ana", 23456789, 1111111111)
    solicitante = Solicitante("Luis", 34567890, 1122222222)
    assert persona_base.buscar_persona(12345678)[0] is persona_base
    assert Administrador.buscar_persona(23456789)[0] is admin
    assert Solicitante.buscar_persona(34567890)[0] is solicitante
    assert Persona.buscar_persona(23456789)[0] is admin
# La búsqueda no modifica el árbol
def test_buscarPersona_noModificaElArbol(personas_buscables):
    Persona.buscar_persona(10000000)
    Persona.buscar_persona(99999999)
    assert dnis_registrados() == [10000000, 20000000, 30000000]
# Delega la búsqueda en el árbol de DNIs
def test_buscarPersona_delegaEnElArbol(mocker):
    mock_arbol = mocker.patch.object(Persona, "dnis_registrados")
    mock_arbol.buscar_con_saltos.return_value = ("persona", 3)
    assert Persona.buscar_persona(12345678) == ("persona", 3)
    mock_arbol.buscar_con_saltos.assert_called_once_with(12345678)


# ---------- orden_arbol ----------
# Personas con DNI 1000001 a 1000007 insertadas en orden creciente (árbol degenerado)
@pytest.fixture
def siete_personas(mock_validaciones):
    return list(map(lambda dni: Persona(f"Persona {dni}", dni, 1123456789), range(1000001, 1000008)))

# Funcionamiento normal: devuelve las personas en el orden en que quedan insertadas
def test_ordenArbol_ok(siete_personas):
    resultado = Persona.orden_arbol()
    assert list(map(lambda p: p.getter_dni(), resultado)) == [1000004, 1000002, 1000001, 1000003, 1000006, 1000005, 1000007]
    assert sorted(resultado, key = lambda p: p.getter_dni()) == siete_personas
# Antes el árbol es lineal; después queda balanceado
def test_ordenArbol_balancea(siete_personas):
    assert Persona.buscar_persona(1000007)[1] == 6
    Persona.orden_arbol()
    saltos = list(map(lambda dni: Persona.buscar_persona(dni)[1], range(1000001, 1000008)))
    assert max(saltos) == 2
    assert Persona.buscar_persona(1000004) == (siete_personas[3], 0)
# No pierde personas ni cambia el orden de los DNIs
def test_ordenArbol_conservaPersonas(siete_personas):
    Persona.orden_arbol()
    assert dnis_registrados() == list(range(1000001, 1000008))
    for persona in siete_personas:
        assert Persona.buscar_persona(persona.getter_dni())[0] is persona
# Conserva el tipo de cada persona
def test_ordenArbol_conservaSubclases(mock_validaciones):
    persona = Persona("Juan", 1000001, 1123456789)
    admin = Administrador("Ana", 1000002, 1111111111)
    solicitante = Solicitante("Luis", 1000003, 1122222222)
    resultado = Persona.orden_arbol()
    assert resultado == [admin, persona, solicitante]
    assert Persona.buscar_persona(1000002)[0] is admin
    assert type(Persona.buscar_persona(1000003)[0]) is Solicitante
# Árbol vacío
def test_ordenArbol_arbolVacio():
    assert Persona.orden_arbol() == []
    assert Persona.getter_dnis_registrados().esVacio()
# Se puede llamar más de una vez: el resultado es el mismo
def test_ordenArbol_variasVeces(siete_personas):
    primero = Persona.orden_arbol()
    segundo = Persona.orden_arbol()
    assert primero == segundo
    assert dnis_registrados() == list(range(1000001, 1000008))
# Se pueden seguir registrando personas después de ordenar
def test_ordenArbol_seguirRegistrando(siete_personas, mock_validaciones):
    Persona.orden_arbol()
    nueva = Persona("Nueva", 1000100, 1123456789)
    assert Persona.buscar_persona(1000100)[0] is nueva
    assert dnis_registrados() == [1000001, 1000002, 1000003, 1000004, 1000005, 1000006, 1000007, 1000100]
# Usa el árbol para ordenar: inorden --> ordenar --> arma un árbol nuevo
def test_ordenArbol_delegaEnElArbol(mocker):
    mock_arbol_viejo = mocker.patch.object(Persona, "dnis_registrados")
    mock_arbol_nuevo = mocker.patch("persona.Arbol").return_value
    persona1 = mocker.Mock(spec = Persona)
    persona2 = mocker.Mock(spec = Persona)
    persona3 = mocker.Mock(spec = Persona)
    mock_arbol_viejo.getter_raiz.return_value = "raiz"
    mock_arbol_viejo.inorden.return_value = [(1, persona1), (2, persona2), (3, persona3)]
    mock_arbol_viejo.ordenar.return_value = [(2, persona2), (1, persona1), (3, persona3)]
    resultado = Persona.orden_arbol()
    mock_arbol_viejo.inorden.assert_called_once_with("raiz")
    mock_arbol_viejo.ordenar.assert_called_once_with([(1, persona1), (2, persona2), (3, persona3)])
    # Inserta en el árbol nuevo en el orden que devolvió ordenar
    assert mock_arbol_nuevo.insertar.call_args_list == [mocker.call(2, persona2), mocker.call(1, persona1), mocker.call(3, persona3)]
    mock_arbol_viejo.insertar.assert_not_called()
    assert Persona.getter_dnis_registrados() is mock_arbol_nuevo
    assert resultado == [persona2, persona1, persona3]


# ---------- serializar ----------
def test_persona_serializar(persona_base):
    assert persona_base.serializar() == ["Persona", "Juan", 12345678, 1123456789]

# ---------- deserializar ----------
ENCABEZADO = ["clase", "nombre", "dni", "telefono", "Persona"]
# Funcionamiento normal (con validaciones reales)
def test_persona_deserializar_ok():
    archivo = [ENCABEZADO,
               ["Persona", "Juan", "12345678", "1123456789"],
               [],
               ["Administrador", "Ana", "23456789", "1111111111"],
               ["Solicitante", "Luis", "34567890", "1122222222"]]
    personas = Persona.deserializar(archivo)
    assert len(personas) == 3
    persona, admin, solicitante = personas
    assert type(persona) is Persona
    assert type(admin) is Administrador
    assert type(solicitante) is Solicitante
    assert persona.getter_nombre() == "Juan"
    assert persona.getter_dni() == 12345678
    assert persona.getter_telefono() == 1123456789
    assert admin.getter_nombre() == "Ana"
    assert solicitante.getter_dni() == 34567890
    # Quedan registradas en el árbol de DNIs
    arbol = Persona.getter_dnis_registrados()
    assert dnis_registrados() == [12345678, 23456789, 34567890]
    assert arbol.buscar(arbol.getter_raiz(), 23456789) is admin
# Reemplaza las personas registradas antes de cargar
def test_persona_deserializar_limpiaElArbol():
    Persona("Viejo", 11111111, 1123456789)
    personas = Persona.deserializar([ENCABEZADO, ["Persona", "Juan", "12345678", "1123456789"]])
    assert dnis_registrados() == [12345678]
    # Un DNI registrado antes de cargar se puede volver a usar
    Persona.deserializar([ENCABEZADO, ["Persona", "Viejo", "11111111", "1123456789"]])
    assert dnis_registrados() == [11111111]
# Sin filas
def test_persona_deserializar_soloEncabezado():
    Persona("Viejo", 11111111, 1123456789)
    assert Persona.deserializar([ENCABEZADO]) == []
    assert Persona.getter_dnis_registrados().esVacio()
# Clase desconocida
def test_persona_deserializar_claseDesconocida():
    with pytest.raises(DatoInvalidoError, match = "Clase de persona desconocida: Robot"):
        Persona.deserializar([ENCABEZADO, ["Robot", "R2", "12345678", "1123456789"]])
# DNI repetido en el archivo
def test_persona_deserializar_dniRepetido():
    archivo = [ENCABEZADO, ["Persona", "Juan", "12345678", "1123456789"], ["Solicitante", "Ana", "12345678", "1111111111"]]
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Persona.deserializar(archivo)
# Lo serializado se puede volver a cargar
def test_persona_serializar_deserializar():
    originales = [Persona("Juan", 12345678, 1123456789), Administrador("Ana", 23456789, 1111111111), Solicitante("Luis", 34567890, 1122222222)]
    archivo = [ENCABEZADO] + list(map(lambda p: list(map(str, p.serializar())), originales))
    copias = Persona.deserializar(archivo)
    assert list(map(lambda p: type(p), copias)) == [Persona, Administrador, Solicitante]
    assert copias == originales
    assert list(map(lambda p: p.getter_nombre(), copias)) == ["Juan", "Ana", "Luis"]
    assert list(map(lambda p: p.getter_telefono(), copias)) == [1123456789, 1111111111, 1122222222]
