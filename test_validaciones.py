import re
import pytest
from datetime import datetime, date
from validaciones import Validaciones
from excepciones import DatoInvalidoError, DNIInvalidoError, VentanaInvalidaError, FlotaError
from articulo import Articulo
from cola import Cola
from transporte import Transporte, Camion

INICIO = datetime(2025, 1, 1, 9, 0)
FIN = datetime(2025, 1, 1, 12, 0)
OPCIONES = ("DAÑO", "AUSENTE", "RETRASO")

# validar_ventana y validar_dni llaman a otras validaciones: ahí se reemplazan por mocks
@pytest.fixture
def mock_fecha(mocker):
    return mocker.patch.object(Validaciones, "validar_fecha")

@pytest.fixture
def mock_digitos(mocker):
    return mocker.patch.object(Validaciones, "validar_digitos")

@pytest.fixture
def articulo_falso(mocker):
    return mocker.Mock(spec = Articulo)

@pytest.fixture
def camion_falso(mocker):
    return mocker.Mock(spec = Camion)

@pytest.fixture
def cola_falsa(mocker):
    return mocker.Mock(spec = Cola)


# _resultado
def test_validaciones_resultado():
    assert Validaciones._resultado(("Valor")) == "Valor"
    assert Validaciones._resultado(("Valor", 15, None)) == ("Valor", 15, None)
    assert Validaciones._resultado(("Str1", "Str2", "Str3")) == ("Str1", "Str2", "Str3")
    unico_valor = (7, )
    assert Validaciones._resultado(unico_valor) == unico_valor[0] == 7
    assert Validaciones()._resultado(unico_valor) == unico_valor[0]
    with pytest.raises(TypeError, match = "Se debe pasar al menos un valor para validar"):
        Validaciones._resultado(())

# ---------- validar_str ----------
# Funcionamiento normal
def test_validarStr_ok():
    assert Validaciones.validar_str("Caja") == "Caja"
    assert Validaciones.validar_str("  Caja  ") == "Caja"  # strip()
    assert Validaciones.validar_str("a", "b", "c", "  d  ") == ("a", "b", "c", "d")
    assert Validaciones.validar_str(*("a", "b")) == ("a", "b")
# Errores
def test_validarStr_vacio():
    with pytest.raises(DatoInvalidoError, match = "no debe estar vacío"):
        Validaciones.validar_str("")
    with pytest.raises(DatoInvalidoError, match = "El administrador no debe estar vacío"):
        Validaciones.validar_str("      ", nombre = "administrador")
    with pytest.raises(DatoInvalidoError, match = "no debe estar vacío"):
        Validaciones.validar_str("  \n  ")
    # Varios
    with pytest.raises(DatoInvalidoError, match = "El valor no debe estar vacío"):
        Validaciones.validar_str("a", "    ", "c")
    # Ninguno
    with pytest.raises(TypeError):
        Validaciones.validar_str()
def test_validarStr_tipoInvalido():
    with pytest.raises(TypeError, match = "debe ser una cadena str"):
        Validaciones.validar_str(100)
    with pytest.raises(TypeError, match = "El comprobante None debe ser una cadena str"):
        Validaciones.validar_str(None, nombre = "comprobante")
    with pytest.raises(TypeError, match = "debe ser una cadena str"):
        Validaciones.validar_str(["a", "b"])
    # Varios
    with pytest.raises(TypeError, match = "El articulo 98 debe ser una cadena str"):
        Validaciones.validar_str("a", "b", 98, nombre = "articulo")


# ---------- validar_numero ----------
# Funcionamiento normal
def test_numero_ok():
    assert Validaciones.validar_numero(1, nombre = "peso") == 1
    assert Validaciones.validar_numero(0.5, nombre = "volumen") == 0.5
    assert Validaciones.validar_numero(30, nombre = "velocidad") == 30
    assert Validaciones.validar_numero(0.0001) == 0.0001
    # cero = True
    assert Validaciones.validar_numero(0, cero = True, nombre = "monto") == 0
    assert Validaciones.validar_numero(10, cero = True, nombre = "monto") == 10
    assert Validaciones.validar_numero(-0, cero = True) == 0
    # Varios numeros
    assert Validaciones.validar_numero(0, 8, 0.0, 15, 12.3, cero = True, nombre = "monto") == (0, 8, 0.0, 15, 12.3)
    assert Validaciones.validar_numero(15, 8, 12, 15, 100, entero = True) == (15, 8, 12, 15, 100)
    assert Validaciones.validar_numero(10.0, 8, 0.01, 15, 12.3) == (10.0, 8, 0.01, 15, 12.3)
    assert Validaciones.validar_numero(*(10.0, 8, 0.01, 15, 12.3), cero = True) == (10.0, 8, 0.01, 15, 12.3)
    # entero = True
    assert Validaciones.validar_numero(1, entero = True, nombre = "orden") == 1
    assert Validaciones.validar_numero(100, entero = True, nombre = "orden") == 100
    assert Validaciones.validar_numero(1499038190, entero = True) == 1499038190
    assert Validaciones.validar_numero(10, cero = True, entero = True) == 10
    assert Validaciones.validar_numero(0, cero = True, entero = True) == 0
# Error por cota
def test_numero_negativos():
    with pytest.raises(DatoInvalidoError, match = "El monto -10 debe ser finito y no negativo"):
        Validaciones.validar_numero(-10, cero = True, nombre = "monto")
    with pytest.raises(DatoInvalidoError, match = "El peso -10 debe ser finito y mayor a 0"):
        Validaciones.validar_numero(-10, nombre = "peso")
    with pytest.raises(DatoInvalidoError, match = "no negativo"):
        Validaciones.validar_numero(-0.0001, cero = True)
    with pytest.raises(DatoInvalidoError, match = "El velocidad 0 debe ser finito y mayor a 0"):
        Validaciones.validar_numero(0, nombre = "velocidad")
    with pytest.raises(DatoInvalidoError, match = "El orden 0 debe ser finito y mayor a 0"):
        Validaciones.validar_numero(0, cero = False, entero = True, nombre = "orden")
    with pytest.raises(DatoInvalidoError, match = "mayor a 0"):
        Validaciones.validar_numero(0.0, cero = False)
    # Varios numero
    with pytest.raises(DatoInvalidoError, match = "no negativo"):
        Validaciones.validar_numero(5, 0, -10, cero = True)
    with pytest.raises(DatoInvalidoError, match = "mayor a 0"):
        Validaciones.validar_numero(5, 4, -0.0001, 3)
    with pytest.raises(DatoInvalidoError, match = "El volumen -0.001 debe ser finito y no negativo"):
        Validaciones.validar_numero(2, -0.001, 3, cero = True, nombre = "volumen")
    with pytest.raises(DatoInvalidoError, match = "mayor a 0"):
        Validaciones.validar_numero(5, 5, 0, 5)
    with pytest.raises(DatoInvalidoError, match = "mayor a 0"):
        Validaciones.validar_numero(6, 2, 5, 0, 2, cero = False, entero = True)
    with pytest.raises(DatoInvalidoError, match = "El peso 0.0 debe ser finito y mayor a 0"):
        Validaciones.validar_numero(3, 0.0, 2, nombre = "peso")
# Error por float
def test_numero_decimalNoAceptado():
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(10.0, entero = True)
    with pytest.raises(TypeError, match = "El orden 2.5 debe ser un entero"):
        Validaciones.validar_numero(2.5, entero = True, nombre = "orden")
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(float(5), entero = True)
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(float(0), cero = True, entero = True)
    # Varios numeros
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(3, 10.0, 4, entero = True)
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(1, 2.5, entero = True)
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(5, float(5), entero = True)
    with pytest.raises(TypeError, match = "debe ser un entero"):
        Validaciones.validar_numero(float(0), 1, cero = True, entero = True)
# Error x no número
def test_numero_noNumerico():
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero("10")
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero([10], cero = True)
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero((10, ))
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero(None)
    # bool
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero(True)
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero(False, cero = True)
    # varios numeros
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero(1, "10")
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero(3, None, 6)
    with pytest.raises(TypeError, match = "debe ser un número"):
        Validaciones.validar_numero(True, 5, 2, cero = True)
    # sin numeros
    with pytest.raises(TypeError):
        Validaciones.validar_numero()
# Error x infinito
def test_numero_noFinito():
    with pytest.raises(DatoInvalidoError, match = "debe ser finito"):
        Validaciones.validar_numero(float("inf"))
    with pytest.raises(DatoInvalidoError, match = "debe ser finito"):
        Validaciones.validar_numero(float("inf"), cero = True)
    with pytest.raises(DatoInvalidoError, match = "debe ser finito"):
        Validaciones.validar_numero(float("-inf"))
    with pytest.raises(DatoInvalidoError, match = "debe ser finito"):
        Validaciones.validar_numero(float("nan"), cero = True)
    # varios numeros
    with pytest.raises(DatoInvalidoError, match = "debe ser finito"):
        Validaciones.validar_numero(5, 1, float("-inf"))
    with pytest.raises(DatoInvalidoError, match = "debe ser finito"):
        Validaciones.validar_numero(5, float("nan"), 0, cero = True)


# ---------- validar_fecha ----------
# Funcionamiento normal
def test_fecha_ok():
    assert Validaciones.validar_fecha(INICIO) == INICIO
    # varias
    assert Validaciones.validar_fecha(INICIO, FIN, nombre = "ventana") == (INICIO, FIN)
    # vacío = True
    assert Validaciones.validar_fecha(None, vacio = True) is None
    assert Validaciones.validar_fecha(INICIO, None, vacio = True) == (INICIO, None)
# Error x tipo inválido
def test_fecha_tipoInvalido():
    with pytest.raises(TypeError, match = "La hora 10:00 debe ser un objeto datetime"):
        Validaciones.validar_fecha("10:00", nombre = "hora")
    with pytest.raises(TypeError, match = "La fecha None debe ser un objeto datetime"):
        Validaciones.validar_fecha(None)
    # varios valores
    with pytest.raises(TypeError, match = "debe ser un objeto datetime"):
        Validaciones.validar_fecha(INICIO, 100, vacio = True)
    with pytest.raises(TypeError, match = "La ventana True debe ser un objeto datetime"):
        Validaciones.validar_fecha(FIN, True, nombre = "ventana")
    with pytest.raises(TypeError, match = "debe ser un objeto datetime"):
        Validaciones.validar_fecha(date(2025, 1, 1))
    with pytest.raises(TypeError):
        Validaciones.validar_fecha(INICIO, "10:30")
    # sin valores
    with pytest.raises(TypeError):
        Validaciones.validar_fecha()


# ---------- validar_ventana ----------
# Funcionamiento normal
def test_ventana_ok(mock_fecha):
    inicio, fin = Validaciones.validar_ventana(INICIO, FIN)
    mock_fecha.assert_any_call(INICIO, nombre = "fecha de la ventana")
    mock_fecha.assert_any_call(FIN, nombre = "fecha de la ventana")
    assert inicio == INICIO
    assert fin == FIN
    assert Validaciones.validar_ventana(INICIO, INICIO) == (INICIO, INICIO)
    Validaciones.validar_ventana(INICIO, FIN, nombre_inicio = "fecha de salida", nombre_fin = "fecha de entrega")
    mock_fecha.assert_any_call(INICIO, nombre = "fecha de salida")
    mock_fecha.assert_any_call(FIN, nombre = "fecha de entrega")
def test_ventana_fechaInvalida_sePropaga(mock_fecha):
    mock_fecha.side_effect = TypeError("La fecha de la ventana None debe ser un objeto datetime")
    with pytest.raises(TypeError, match = "La fecha de la ventana None debe ser un objeto datetime"):
        Validaciones.validar_ventana(INICIO, None)
def test_ventana_fechaInvalida_real():
    with pytest.raises(TypeError, match = "La fecha de entrega None debe ser un objeto datetime"):
        Validaciones.validar_ventana(INICIO, None, nombre_inicio = "fecha de salida", nombre_fin = "fecha de entrega")
def test_ventana_ventanaInvertida(mock_fecha):
    with pytest.raises(VentanaInvalidaError, match = "La fecha de salida .* a la fecha de entrega"):
        Validaciones.validar_ventana(FIN, INICIO, nombre_inicio = "fecha de salida", nombre_fin = "fecha de entrega")
    with pytest.raises(DatoInvalidoError):
        Validaciones.validar_ventana(FIN, INICIO)


# ---------- validar_digitos ----------
# Funcionamiento normal
def test_digitos_ok():
    assert Validaciones.validar_digitos(12345, (5,)) == 12345
    assert Validaciones.validar_digitos(1234567, (7, 8), nombre = "dni") == 1234567
    assert Validaciones.validar_digitos(12345678, (7, 8), nombre = "dni") == 12345678
    assert Validaciones.validar_digitos(9, (1,)) == 9
    # Única cantidad
    assert Validaciones.validar_digitos(12345678, 8) == 12345678
    assert Validaciones.validar_digitos(12345, 5) == 12345
# Errores
def test_digitos_enteroInvalido():
    # x cantidad de dígitos
    with pytest.raises(DatoInvalidoError, match = "El dni 999 debe tener 7 o 8 dígitos"):
        Validaciones.validar_digitos(999, (7, 8), nombre = "dni")
    with pytest.raises(DatoInvalidoError, match = "dígitos"):
        Validaciones.validar_digitos(999888777666, (7, 8), nombre = "dni")    
    # x número negativo
    with pytest.raises(DatoInvalidoError, match = "El teléfono -123456789 debe ser positivo"):
        Validaciones.validar_digitos(-123456789, 10, nombre = "teléfono")
def test_digitos_tipoInvalido():
    with pytest.raises(TypeError, match = "El dni 12345678 debe ser un objeto int"):
        Validaciones.validar_digitos("12345678", (7, 8), nombre = "dni")
    with pytest.raises(TypeError):
        Validaciones.validar_digitos(1234.5, 5)
    with pytest.raises(TypeError):
        Validaciones.validar_digitos(None, 4)
    with pytest.raises(TypeError):
        Validaciones.validar_digitos([1, 2, 3, 4, 5], 5)


# ---------- validar_dni ----------
# Funcionamiento normal
def test_dni_ok(mock_digitos):
    # sin dnis registrados
    assert Validaciones.validar_dni(12345678) == 12345678
    mock_digitos.assert_called_once_with(12345678, (7, 8), "DNI")
    assert Validaciones.validar_dni(12345678, registrados = None) == 12345678
    # con dnis registrados
    assert Validaciones.validar_dni(44445555, registrados = {11111111, 22222222}) == 44445555
    assert Validaciones.validar_dni(67676767, registrados = [11111111]) == 67676767
    mock_digitos.assert_any_call(44445555, (7, 8), "DNI")
    mock_digitos.assert_any_call(67676767, (7, 8), "DNI")
# Errores
def test_dni_duplicado(mock_digitos):
    # Captura dni invalido
    with pytest.raises(DNIInvalidoError, match = "El DNI 12345678 ya está registrado"):
        Validaciones.validar_dni(12345678, registrados = {12345678})
    # Captura dato invalido (jerarquizacion)
    with pytest.raises(DatoInvalidoError):
        Validaciones.validar_dni(12345678, registrados = (12345678,))
def test_dni_digitosInvalidos_sePropaga(mocker, mock_digitos):
    dnis_registrados = mocker.MagicMock(spec = set)
    mock_digitos.side_effect = [DatoInvalidoError("El DNI 999 debe tener 7 u 8 dígitos"), 999]
    with pytest.raises(DatoInvalidoError, match = "El DNI 999 debe tener 7 u 8 dígitos"):
        Validaciones.validar_dni(999, registrados = dnis_registrados)
    dnis_registrados.__contains__.assert_not_called()
    Validaciones.validar_dni(45323232, registrados = dnis_registrados)
    dnis_registrados.__contains__.assert_called_once_with(45323232)


# ---------- validar_en ----------
# Funcionamiento normal
def test_en_ok():
    # tuplas, listas, sets
    assert Validaciones.validar_en("DAÑO", opciones = OPCIONES) == "DAÑO"
    assert Validaciones.validar_en("DAÑO", "AUSENTE", opciones = OPCIONES) == ("DAÑO", "AUSENTE")
    assert Validaciones.validar_en("A", opciones = ["A", "B"]) == "A"
    assert Validaciones.validar_en("A", opciones = {"A", "B"}) == "A"
    # str separado por comas
    assert Validaciones.validar_en("FALLIDA", opciones = "FALLIDA, ENTREGADA") == "FALLIDA"
    assert Validaciones.validar_en("ENTREGADA", opciones = "FALLIDA, ENTREGADA") == "ENTREGADA"
    # con nombre
    estados = ("PLANIFICADO", "EN_CURSO", "FINALIZADO")
    assert Validaciones.validar_en("EN_CURSO", opciones = estados, nombre = "estado del viaje") == "EN_CURSO"
def test_en_noPertenece():
    estados = ("PLANIFICADO", "EN_CURSO", "FINALIZADO")
    with pytest.raises(DatoInvalidoError, match = "El estado del viaje ESTADO INVALIDO debe ser uno de: PLANIFICADO, EN_CURSO, FINALIZADO"):
        Validaciones.validar_en("ESTADO INVALIDO", opciones = estados, nombre = "estado del viaje")
    # varios valores
    with pytest.raises(DatoInvalidoError, match = "El valor AUS debe ser uno de: DAÑO, AUSENTE, RETRASO"):
        Validaciones.validar_en("DAÑO", "AUS", opciones = OPCIONES)
def test_en_tipoInvalido():
    with pytest.raises(TypeError, match = "El tipo de incidente None debe ser una cadena str"):
        Validaciones.validar_en(None, opciones = OPCIONES, nombre = "tipo de incidente")
    with pytest.raises(TypeError, match = re.escape(f"El tipo de incidente {str(('DAÑO',))} debe ser una cadena str")):
        Validaciones.validar_en(("DAÑO", ), opciones = OPCIONES, nombre = "tipo de incidente")
def test_en_opcionesNoStr():
    with pytest.raises(TypeError, match = "Las opciones de valor deben ser cadenas str, pero 1 no lo es"):
        Validaciones.validar_en("x", opciones = ("x", 1))
    with pytest.raises(TypeError, match = "Las opciones de estado deben ser cadenas str"):
        Validaciones.validar_en("1", opciones = (1, 2), nombre = "estado")
def test_en_opcionesObligatorio():
    with pytest.raises(TypeError, match = "missing"):
        Validaciones.validar_en("DAÑO")
def test_en_sinValores():
    with pytest.raises(TypeError, match = "Se debe pasar al menos un valor para validar"):
        Validaciones.validar_en(opciones = OPCIONES)


# ---------- validar_instancia ----------
# Funcionamiento normal
def test_instancia_ok(camion_falso, mocker,):
    assert Validaciones.validar_instancia(camion_falso, clase = Camion) is camion_falso
    # herencia
    assert Validaciones.validar_instancia(camion_falso, clase = Transporte) is camion_falso
    # varios objetos
    otro = mocker.Mock(spec = Camion)
    assert Validaciones.validar_instancia(camion_falso, otro, clase = Camion) == (camion_falso, otro)
    # varias clases
    assert Validaciones.validar_instancia(5, clase = (int, str)) == 5
    assert Validaciones.validar_instancia("a", 1, clase = (int, str)) == ("a", 1)
# Errores
def test_instancia_otraClase(articulo_falso):
    with pytest.raises(TypeError, match = "El articulo Articulo 5 debe ser un objeto de clase Articulo"):
        Validaciones.validar_instancia("Articulo 5", clase = Articulo, nombre = "articulo")
    with pytest.raises(TypeError, match = "debe ser un objeto de clase Articulo"):
        Validaciones.validar_instancia((articulo_falso, ), clase = Articulo)
    # un objeto de otra clase de varios
    with pytest.raises(TypeError, match = "El articulo None debe ser un objeto de clase Articulo"):
        Validaciones.validar_instancia(articulo_falso, None, clase = Articulo, nombre = "articulo")
def test_instancia_claseNoIndicada():
    with pytest.raises(TypeError, match = "missing"):
        Validaciones.validar_instancia(5)
def test_instancia_sinValores():
    with pytest.raises(TypeError, match = "Se debe pasar al menos un valor para validar"):
        Validaciones.validar_instancia(clase = Articulo)


# ---------- validar_coleccion ----------
# Funcionamiento normal
def test_coleccion_ok():
    coleccion = (1, 2)
    assert Validaciones.validar_coleccion(coleccion) is coleccion
    assert Validaciones.validar_coleccion([1, 2]) == [1, 2]
    assert Validaciones.validar_coleccion({1, 2}) == {1, 2}
    assert Validaciones.validar_coleccion("abc") == "abc"
    # con nombre
    assert Validaciones.validar_coleccion((1, ), nombre = "lista de paradas") == (1, )
def test_coleccion_tipo():
    assert Validaciones.validar_coleccion((1, 2), tipo = tuple) == (1, 2)
    assert Validaciones.validar_coleccion([1, 2], tipo = list) == [1, 2]
    assert Validaciones.validar_coleccion({"a": 1}, tipo = dict) == {"a": 1}
def test_coleccion_clase(articulo_falso):
    articulos = (articulo_falso, articulo_falso)
    assert Validaciones.validar_coleccion(articulos, clase = Articulo) == articulos
    assert Validaciones.validar_coleccion(articulos, tipo = tuple, clase = Articulo) == articulos
    # en dicc valida la clave, no el valor
    assert Validaciones.validar_coleccion({articulo_falso: 1}, clase = Articulo) == {articulo_falso: 1}
    # varias clases
    assert Validaciones.validar_coleccion([1, "a"], clase = (int, str)) == [1, "a"]
    # claves de un dict
    assert Validaciones.validar_coleccion({"a": 1, "b": 2}, clase = str) == {"a": 1, "b": 2}
def test_coleccion_vaciaPermitida():
    assert Validaciones.validar_coleccion((), vacia = True) == ()
    assert Validaciones.validar_coleccion(set(), vacia = True) == set()
    # con clase y/o tipo especificado
    assert Validaciones.validar_coleccion([], clase = Articulo, vacia = True) == []
    assert Validaciones.validar_coleccion([], tipo = list, vacia = True) == []
    assert Validaciones.validar_coleccion((), tipo = tuple, clase = Articulo, vacia = True) == ()
def test_coleccion_cola(cola_falsa):
    # cola no vacía (usa esVacia())
    cola_falsa.esVacia.return_value = False
    assert Validaciones.validar_coleccion(cola_falsa) is cola_falsa
    cola_falsa.esVacia.assert_called_once()
    # cola vacia, y vacia = True
    cola_falsa.esVacia.return_value = True
    assert Validaciones.validar_coleccion(cola_falsa, vacia = True) is cola_falsa
# Errores
def test_coleccion_vacia(cola_falsa):
    with pytest.raises(DatoInvalidoError, match = "La colección no debe estar vacía"):
        Validaciones.validar_coleccion(())
    with pytest.raises(DatoInvalidoError, match = "La colección no debe estar vacía"):
        Validaciones.validar_coleccion(set())
    # con nombre
    with pytest.raises(DatoInvalidoError, match = "La lista de artículos no debe estar vacía"):
        Validaciones.validar_coleccion((), tipo = tuple, clase = Articulo, nombre = "lista de artículos")
    # cola vacia
    cola_falsa.esVacia.return_value = True
    with pytest.raises(DatoInvalidoError, match = "La cola de paradas no debe estar vacía"):
        Validaciones.validar_coleccion(cola_falsa, nombre = "cola de paradas")
    cola_falsa.esVacia.assert_called_once()
def test_coleccion_noEsColeccion():
    with pytest.raises(TypeError, match = "La colección 5 debe ser una colección"):
        Validaciones.validar_coleccion(5)
    with pytest.raises(TypeError, match = "La colección None debe ser una colección"):
        Validaciones.validar_coleccion(None)
    # con nombre
    with pytest.raises(TypeError, match = "La lista de artículos True debe ser una colección"):
        Validaciones.validar_coleccion(True, nombre = "lista de artículos")
def test_coleccion_tipoIncorrecto(articulo_falso):
    with pytest.raises(TypeError, match = "debe ser de tipo list"):
        Validaciones.validar_coleccion((1, 2), tipo = list)
    # con nombre
    articulos = [articulo_falso]
    with pytest.raises(TypeError, match = re.escape(f"La lista de artículos {articulos} debe ser de tipo tuple")):
        Validaciones.validar_coleccion(articulos, tipo = tuple, nombre = "lista de artículos")
def test_coleccion_elementoDeOtraClase(articulo_falso):
    with pytest.raises(TypeError, match = "La colección contiene Articulo 8, que no es un objeto de clase Articulo"):
        Validaciones.validar_coleccion((articulo_falso, "Articulo 8"), clase = Articulo)
    with pytest.raises(TypeError, match = "La colección contiene 1, que no es un objeto de clase str"):
        Validaciones.validar_coleccion({1: "a"}, clase = str)
    with pytest.raises(TypeError, match = "La lista de artículos contiene None, que no es un objeto de clase Articulo"):
        Validaciones.validar_coleccion([articulo_falso, None], clase = Articulo, nombre = "lista de artículos")
    # varias clases
    with pytest.raises(TypeError, match = "La colección contiene None, que no es un objeto de clase int, str"):
        Validaciones.validar_coleccion([1, "a", None], clase = (int, str), vacia = True)

# ---------- General ----------
# Errores de valor
def test_validaciones_erroresDeValorSonFlotaError():
    with pytest.raises(FlotaError):
        Validaciones.validar_str("")
    with pytest.raises(FlotaError):
        Validaciones.validar_numero(-1)
    with pytest.raises(FlotaError):
        Validaciones.validar_ventana(FIN, INICIO)
    with pytest.raises(FlotaError):
        Validaciones.validar_digitos(1, (8,))
    with pytest.raises(FlotaError):
        Validaciones.validar_dni(12345678, registrados = {12345678})
    with pytest.raises(FlotaError):
        Validaciones.validar_en("x", opciones = ("a",))
    with pytest.raises(FlotaError):
        Validaciones.validar_coleccion((), tipo = tuple, vacia = False)
# Errores de tipo
def test_validaciones_erroresDeTipoNoSonFlotaError(mocker):
    # 
    mock_error = mocker.patch("validaciones.DatoInvalidoError")
    with pytest.raises(TypeError):
        Validaciones.validar_str(1)
    with pytest.raises(TypeError):
        Validaciones.validar_numero("1")
    with pytest.raises(TypeError):
        Validaciones.validar_en("a", opciones = (1, ))
    with pytest.raises(TypeError):
        Validaciones.validar_coleccion(5)
    mock_error.assert_not_called()
    with pytest.raises(Exception):
        Validaciones.validar_str("   ")
    mock_error.assert_called_once()
