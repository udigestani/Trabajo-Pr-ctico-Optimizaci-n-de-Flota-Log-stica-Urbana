import pytest
from pila import Pila

# Funcionamiento normal
def test_pila_ok():
    # Pila vacía
    pila = Pila()
    assert pila.esVacia()
    assert pila.get_longitud() == 0
    assert list(pila) == []

    # Con nodos
    pila.apilar(1)
    pila.apilar(2)
    pila.apilar(3)
    assert pila.get_longitud() == 3  # Subió con apilar
    assert pila.ver_tope() == 3      # Último en entrar primero en salir LIFO / UEPS
    assert pila.ver_tope() == 3      # Tope no modifica la pila
    assert pila.desapilar() == 3
    assert pila.desapilar() == 2
    # Un solo nodo
    assert pila.get_longitud() == 1    # Bajó con desapilar
    assert pila.ver_tope() == 1
    assert pila.tope.siguiente is None  # Con un solo nodo, no apunta a nada
    assert pila.desapilar() == 1
    assert pila.esVacia()
    assert pila.get_longitud() == 0
    # No se borra si esVacia
    pila.apilar(4)
    pila.apilar(5)
    pila.desapilar()
    pila.apilar(6)
    assert list(pila) == [6, 4]

# Enlaces
def test_pila_enlaces():
    pila = Pila()
    pila.apilar(1)
    nodo_anterior = pila.tope
    pila.apilar(2)
    assert pila.tope.siguiente is nodo_anterior
    pila.desapilar()
    assert pila.tope is nodo_anterior

# Iterar no modifica la pila
def test_pila_iterar():
    pila = Pila()
    pila.apilar(1)
    pila.apilar(2)
    pila.apilar(3)
    assert list(pila) == [3, 2, 1]
    assert list(pila) == [3, 2, 1]     # iterar no modifica la pila
    assert pila.get_longitud() == 3

# ValueError por desapilar pila vacia
def test_pila_desapilarVacia():
    pila = Pila()
    pila.apilar(1)
    pila.desapilar()
    with pytest.raises(ValueError, match = "No se pueden desapilar datos porque la pila está vacía"):
        pila.desapilar()

# ValueError por ver el tope de una pila vacia
def test_pila_topeVacio():
    with pytest.raises(ValueError, match = "No se puede ver el tope porque la pila está vacía"):
        Pila().ver_tope()
