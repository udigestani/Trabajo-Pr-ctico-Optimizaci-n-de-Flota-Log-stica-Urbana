import pytest
from arbol import Arbol, Nodo_arbol

@pytest.fixture
def nodo():
    return Nodo_arbol(5, "instancia 5")

# Árbol de 7 nodos balanceado:
#        4
#      2   6
#     1 3 5 7
@pytest.fixture
def arbol():
    arbol = Arbol()
    for dato in (4, 2, 6, 1, 3, 5, 7):
        arbol.insertar(dato, f"instancia {dato}")
    return arbol

# ---------- Nodo_arbol ----------
# Funcionamiento normal
def test_nodoArbol_ok(nodo):
    assert nodo.getter_dato() == 5
    assert nodo.getter_instancia() == "instancia 5"
    assert nodo.getter_izquierdo() is None
    assert nodo.getter_derecho() is None
    assert str(nodo) == "5"
# Enlaces
def test_nodoArbol_enlaces(nodo):
    izquierdo = Nodo_arbol(3, "instancia 3")
    derecho = Nodo_arbol(8, "instancia 8")
    assert nodo.setter_izquierdo(izquierdo) is None
    assert nodo.setter_derecho(derecho) is None
    assert nodo.getter_izquierdo() is izquierdo
    assert nodo.getter_derecho() is derecho
    # Desenlazar
    nodo.setter_izquierdo(None)
    assert nodo.getter_izquierdo() is None
    assert nodo.getter_derecho() is derecho


# ---------- Arbol ----------
# Árbol vacío
def test_arbol_vacio():
    arbol = Arbol()
    assert arbol.esVacio()
    assert arbol.getter_raiz() is None
    assert arbol.inorden(arbol.getter_raiz()) == []
    assert arbol.buscar(arbol.getter_raiz(), 5) is None
    assert arbol.buscar_con_saltos(5) == (None, 0)
# Insertar
def test_arbol_insertarRaiz():
    arbol = Arbol()
    assert arbol.insertar(5, "instancia 5") is None
    assert not arbol.esVacio()
    assert arbol.getter_raiz().getter_dato() == 5
    assert arbol.getter_raiz().getter_instancia() == "instancia 5"
def test_arbol_insertarIzquierdaYDerecha(arbol):
    raiz = arbol.getter_raiz()
    assert raiz.getter_dato() == 4
    assert raiz.getter_izquierdo().getter_dato() == 2
    assert raiz.getter_derecho().getter_dato() == 6
    assert raiz.getter_izquierdo().getter_izquierdo().getter_dato() == 1
    assert raiz.getter_izquierdo().getter_derecho().getter_dato() == 3
    assert raiz.getter_derecho().getter_izquierdo().getter_dato() == 5
    assert raiz.getter_derecho().getter_derecho().getter_dato() == 7
# Dato repetido
def test_arbol_insertarRepetido(arbol):
    with pytest.raises(ValueError, match = "El valor 3 ya está en el árbol"):
        arbol.insertar(3, "otra instancia")
    assert arbol.inorden(arbol.getter_raiz()) == [1, 2, 3, 4, 5, 6, 7]
    assert arbol.buscar(arbol.getter_raiz(), 3) == "instancia 3"
    with pytest.raises(ValueError, match = "El valor 4 ya está en el árbol"):
        arbol.insertar(4, "otra instancia")
# Raíz
def test_arbol_setterRaiz(arbol):
    assert arbol.setter_raiz(None) is None
    assert arbol.esVacio()
    assert arbol.getter_raiz() is None
    nodo = Nodo_arbol(9, "instancia 9")
    arbol.setter_raiz(nodo)
    assert arbol.getter_raiz() is nodo
    assert arbol.inorden(arbol.getter_raiz()) == [9]
    # Se puede volver a insertar después de vaciarlo
    arbol.setter_raiz(None)
    arbol.insertar(3, "instancia 3")
    assert arbol.inorden(arbol.getter_raiz()) == [3]


# ---------- buscar ----------
def test_arbol_buscar_ok(arbol):
    for dato in (1, 2, 3, 4, 5, 6, 7):
        assert arbol.buscar(arbol.getter_raiz(), dato) == f"instancia {dato}"
def test_arbol_buscar_noExiste(arbol):
    assert arbol.buscar(arbol.getter_raiz(), 0) is None
    assert arbol.buscar(arbol.getter_raiz(), 8) is None
    assert arbol.buscar(arbol.getter_raiz(), 3.5) is None
# Busca desde un subárbol
def test_arbol_buscar_subarbol(arbol):
    izquierdo = arbol.getter_raiz().getter_izquierdo()
    assert arbol.buscar(izquierdo, 3) == "instancia 3"
    assert arbol.buscar(izquierdo, 6) is None
# La búsqueda no modifica el árbol
def test_arbol_buscar_noModifica(arbol):
    arbol.buscar(arbol.getter_raiz(), 7)
    assert arbol.inorden(arbol.getter_raiz()) == [1, 2, 3, 4, 5, 6, 7]


# ---------- buscar_con_saltos ----------
# Cuenta los saltos entre nodos desde la raíz
def test_arbol_buscarConSaltos_ok(arbol):
    assert arbol.buscar_con_saltos(4) == ("instancia 4", 0)
    assert arbol.buscar_con_saltos(2) == ("instancia 2", 1)
    assert arbol.buscar_con_saltos(6) == ("instancia 6", 1)
    assert arbol.buscar_con_saltos(1) == ("instancia 1", 2)
    assert arbol.buscar_con_saltos(7) == ("instancia 7", 2)
# Si no está, cuenta los saltos hasta llegar a un lugar vacío
def test_arbol_buscarConSaltos_noExiste(arbol):
    assert arbol.buscar_con_saltos(8) == (None, 3)
    assert arbol.buscar_con_saltos(0) == (None, 3)
    assert arbol.buscar_con_saltos(3.5) == (None, 3)
# Árbol balanceado: los saltos no superan log2(n)
def test_arbol_buscarConSaltos_balanceado(arbol):
    saltos = list(map(lambda dato: arbol.buscar_con_saltos(dato)[1], range(1, 8)))
    assert max(saltos) == 2
# Árbol degenerado (datos en orden): la búsqueda es lineal, O(n)
def test_arbol_buscarConSaltos_ordenados():
    arbol = Arbol()
    for dato in range(1, 11):
        arbol.insertar(dato, dato)
    assert arbol.buscar_con_saltos(1) == (1, 0)
    assert arbol.buscar_con_saltos(10) == (10, 9)
    assert arbol.buscar_con_saltos(11) == (None, 10)


# ---------- Recorridos ----------
def test_arbol_inorden(arbol):
    # Inorden devuelve los datos ordenados
    assert arbol.inorden(arbol.getter_raiz()) == [1, 2, 3, 4, 5, 6, 7]
    assert arbol.inorden(arbol.getter_raiz().getter_derecho()) == [5, 6, 7]
def test_arbol_inorden_ordenaDatosDesordenados():
    arbol = Arbol()
    for dato in (50, 10, 80, 30, 20, 70):
        arbol.insertar(dato, dato)
    assert arbol.inorden(arbol.getter_raiz()) == [10, 20, 30, 50, 70, 80]
def test_arbol_preorden(arbol, capsys):
    assert arbol.preorden(arbol.getter_raiz()) is None
    assert capsys.readouterr().out == "4 2 1 3 6 5 7 "
def test_arbol_posorden(arbol, capsys):
    assert arbol.posorden(arbol.getter_raiz()) is None
    assert capsys.readouterr().out == "1 3 2 5 7 6 4 "
def test_arbol_recorridos_arbolVacio(capsys):
    arbol = Arbol()
    arbol.preorden(arbol.getter_raiz())
    arbol.posorden(arbol.getter_raiz())
    assert capsys.readouterr().out == ""
