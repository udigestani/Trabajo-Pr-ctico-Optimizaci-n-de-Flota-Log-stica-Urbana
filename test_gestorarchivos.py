import pytest
import gestorarchivos
from gestorarchivos import GestorArchivos
from excepciones import DatoInvalidoError

ENCABEZADO = ["id", "nombre", "monto"]
FILAS = [[1, "Caja", 10.5], [2, "Libro", 3]]

@pytest.fixture
def ruta(tmp_path):
    return tmp_path / "datos.csv"

@pytest.fixture
def ruta_con_datos(ruta):
    GestorArchivos.escribir(ENCABEZADO, FILAS, ruta)
    return ruta

# ---------- existe ----------
def test_existe_ok(ruta_con_datos, tmp_path):
    assert GestorArchivos.existe(ruta_con_datos) is True
    # Acepta rutas como texto
    assert GestorArchivos.existe(str(ruta_con_datos)) is True
    assert GestorArchivos.existe(tmp_path / "no_existe.csv") is False
# Una carpeta no es un archivo
def test_existe_carpeta(tmp_path):
    assert GestorArchivos.existe(tmp_path) is False


# ---------- escribir ----------
# Funcionamiento normal
def test_escribir_ok(ruta):
    assert GestorArchivos.escribir(ENCABEZADO, FILAS, ruta) is None
    assert GestorArchivos.existe(ruta)
    # Todo se lee como texto
    assert GestorArchivos.leer(ruta) == [["id", "nombre", "monto"], ["1", "Caja", "10.5"], ["2", "Libro", "3"]]
# Solo encabezado
def test_escribir_sinFilas(ruta):
    GestorArchivos.escribir(ENCABEZADO, [], ruta)
    assert GestorArchivos.leer(ruta) == [["id", "nombre", "monto"]]
# Reemplaza el contenido anterior
def test_escribir_sobrescribe(ruta_con_datos):
    GestorArchivos.escribir(["otro"], [["x"]], ruta_con_datos)
    assert GestorArchivos.leer(ruta_con_datos) == [["otro"], ["x"]]
# Textos con comas, comillas y acentos
def test_escribir_caracteresEspeciales(ruta):
    filas = [["1,2", 'dice "hola"', "Camión ñandú"]]
    GestorArchivos.escribir(ENCABEZADO, filas, ruta)
    assert GestorArchivos.leer(ruta) == [ENCABEZADO, ["1,2", 'dice "hola"', "Camión ñandú"]]


# ---------- leer ----------
# Funcionamiento normal
def test_leer_ok(ruta_con_datos):
    assert GestorArchivos.leer(ruta_con_datos) == [["id", "nombre", "monto"], ["1", "Caja", "10.5"], ["2", "Libro", "3"]]
# Si el archivo no existe devuelve una lista vacía
def test_leer_archivoInexistente(tmp_path):
    assert GestorArchivos.leer(tmp_path / "no_existe.csv") == []
    assert not GestorArchivos.existe(tmp_path / "no_existe.csv")    # No lo crea
# Archivo vacío
def test_leer_archivoVacio(ruta):
    ruta.write_text("")
    assert GestorArchivos.leer(ruta) == []
# Lee las celdas vacías
def test_leer_celdasVacias(ruta):
    GestorArchivos.escribir(ENCABEZADO, [[1, "", ""]], ruta)
    assert GestorArchivos.leer(ruta)[1] == ["1", "", ""]


# ---------- agregar ----------
# Funcionamiento normal
def test_agregar_ok(ruta_con_datos):
    assert GestorArchivos.agregar([[3, "Taza", 7]], ruta_con_datos) is None
    assert GestorArchivos.leer(ruta_con_datos) == [["id", "nombre", "monto"], ["1", "Caja", "10.5"], ["2", "Libro", "3"], ["3", "Taza", "7"]]
# Varias filas, y lista vacía no cambia nada
def test_agregar_variasFilas(ruta_con_datos):
    GestorArchivos.agregar([[3, "Taza", 7], [4, "Mesa", 50]], ruta_con_datos)
    assert len(GestorArchivos.leer(ruta_con_datos)) == 5
    GestorArchivos.agregar([], ruta_con_datos)
    assert len(GestorArchivos.leer(ruta_con_datos)) == 5
# Ruta que no es un archivo
def test_agregar_archivoInexistente(tmp_path):
    ruta = tmp_path / "no_existe.csv"
    with pytest.raises(DatoInvalidoError, match = "no corresponde a ningún archivo"):
        GestorArchivos.agregar([[1, "Caja", 10]], ruta)
    assert not GestorArchivos.existe(ruta)    # No lo crea
def test_agregar_archivoInexistente_noAbreNada(mocker):
    mock_open = mocker.patch("builtins.open")
    mocker.patch.object(GestorArchivos, "existe", return_value = False)
    with pytest.raises(DatoInvalidoError):
        GestorArchivos.agregar([[1]], "ruta.csv")
    mock_open.assert_not_called()


# ---------- Solo lee y escribe filas ----------
# La persistencia de cada clase (leer_todos, guardar_todos) está en main.py
def test_gestorArchivos_noConoceElDominio():
    assert not hasattr(GestorArchivos, "leer_todos")
    assert not hasattr(GestorArchivos, "guardar_todos")
    for clase in ("Persona", "Articulo", "Transporte", "MatrizDistancia", "Solicitud", "Comprobante", "Incidente", "Parada", "Viaje"):
        assert not hasattr(gestorarchivos, clase)
