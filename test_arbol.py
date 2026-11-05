import pytest
from arbol import Arbol, Nodo_arbol

@pytest.fixture
def nodo():
    return Nodo_arbol(5, "instancia 5")

# Solo los datos (sin instancias) que devuelve inorden, ordenados
def datos_inorden(arbol):
    return list(map(lambda par: par[0], arbol.inorden(arbol.getter_raiz())))

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
    assert datos_inorden(arbol) == [1, 2, 3, 4, 5, 6, 7]
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
    assert datos_inorden(arbol) == [9]
    # Se puede volver a insertar después de vaciarlo
    arbol.setter_raiz(None)
    arbol.insertar(3, "instancia 3")
    assert datos_inorden(arbol) == [3]


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
    assert datos_inorden(arbol) == [1, 2, 3, 4, 5, 6, 7]


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
    assert datos_inorden(arbol) == [1, 2, 3, 4, 5, 6, 7]
    assert arbol.inorden(arbol.getter_raiz().getter_derecho()) == [(5, "instancia 5"), (6, "instancia 6"), (7, "instancia 7")]
# Devuelve pares (dato, instancia)
def test_arbol_inorden_devuelveDatoEInstancia(arbol):
    assert arbol.inorden(arbol.getter_raiz()) == [(1, "instancia 1"), (2, "instancia 2"), (3, "instancia 3"), (4, "instancia 4"), (5, "instancia 5"), (6, "instancia 6"), (7, "instancia 7")]
def test_arbol_inorden_ordenaDatosDesordenados():
    arbol = Arbol()
    for dato in (50, 10, 80, 30, 20, 70):
        arbol.insertar(dato, dato)
    assert datos_inorden(arbol) == [10, 20, 30, 50, 70, 80]
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


# ---------- ordenar ----------
# Lista de pares (dato, instancia) ya ordenada por dato, como la que devuelve inorden
def pares(cantidad):
    return list(map(lambda dato: (dato, f"instancia {dato}"), range(1, cantidad + 1)))
# Datos de una lista de pares
def datos(lista):
    return list(map(lambda par: par[0], lista))
# Altura máxima (saltos) de un árbol armado insertando los pares en ese orden
def maximo_saltos(lista):
    arbol = Arbol()
    for dato, instancia in lista:
        arbol.insertar(dato, instancia)
    return max(map(lambda par: arbol.buscar_con_saltos(par[0])[1], lista))

# Lista vacía o de uno o dos elementos: queda igual
def test_arbol_ordenar_pocosElementos():
    arbol = Arbol()
    assert arbol.ordenar([]) == []
    assert arbol.ordenar(pares(1)) == pares(1)
    assert arbol.ordenar(pares(2)) == pares(2)
# El del medio va primero (será la raíz)
def test_arbol_ordenar_tresElementos():
    assert datos(Arbol().ordenar(pares(3))) == [2, 1, 3]
def test_arbol_ordenar_sieteElementos():
    # Es el mismo orden con el que se armó el árbol de la fixture
    assert datos(Arbol().ordenar(pares(7))) == [4, 2, 1, 3, 6, 5, 7]
# Cantidad par e impar de elementos
def test_arbol_ordenar_cuatroElementos():
    assert datos(Arbol().ordenar(pares(4))) == [3, 1, 2, 4]
def test_arbol_ordenar_cincoElementos():
    assert datos(Arbol().ordenar(pares(5))) == [3, 1, 2, 4, 5]
# La raíz es siempre el elemento del medio de la lista
def test_arbol_ordenar_raizEsElDelMedio():
    arbol = Arbol()
    assert arbol.ordenar(pares(9))[0] == (5, "instancia 5")
    assert arbol.ordenar(pares(10))[0] == (6, "instancia 6")
    assert arbol.ordenar(pares(11))[0] == (6, "instancia 6")
# No pierde ni repite elementos, y mantiene cada instancia con su dato
def test_arbol_ordenar_mantieneTodosLosElementos():
    resultado = Arbol().ordenar(pares(20))
    assert len(resultado) == 20
    assert sorted(resultado) == pares(20)
# No modifica la lista original
def test_arbol_ordenar_noModificaLaOriginal():
    original = pares(7)
    Arbol().ordenar(original)
    assert original == pares(7)
# Al insertar en el orden que devuelve, el árbol queda balanceado
def test_arbol_ordenar_arbolBalanceado():
    assert maximo_saltos(Arbol().ordenar(pares(7))) == 2
    assert maximo_saltos(Arbol().ordenar(pares(15))) == 3
    assert maximo_saltos(Arbol().ordenar(pares(34))) == 5
    # Sin ordenar, los datos en orden dan un árbol degenerado
    assert maximo_saltos(pares(15)) == 14
# Los dos lados de la raíz difieren a lo sumo en 1 elemento
def test_arbol_ordenar_ladosParejos():
    for cantidad in range(3, 20):
        arbol = Arbol()
        for dato, instancia in arbol.ordenar(pares(cantidad)):
            arbol.insertar(dato, instancia)
        raiz = arbol.getter_raiz()
        izquierdo = len(arbol.inorden(raiz.getter_izquierdo()))
        derecho = len(arbol.inorden(raiz.getter_derecho()))
        assert abs(izquierdo - derecho) <= 1
# Con un árbol real: al reinsertar conserva las instancias
def test_arbol_ordenar_conInorden(arbol):
    resultado = arbol.ordenar(arbol.inorden(arbol.getter_raiz()))
    nuevo = Arbol()
    for dato, instancia in resultado:
        nuevo.insertar(dato, instancia)
    assert nuevo.inorden(nuevo.getter_raiz()) == arbol.inorden(arbol.getter_raiz())
    assert nuevo.getter_raiz().getter_dato() == 4