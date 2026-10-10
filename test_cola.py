import pytest
from cola import Cola

# Funcionamiento normal
def test_cola_ok():
    # Cola vacía
    cola = Cola()
    assert cola.esVacia()
    assert cola.get_longitud() == 0
    assert list(cola) == []
    
    # Con nodos
    cola.encolar(1)
    cola.encolar(2)
    cola.encolar(3)
    assert cola.get_longitud() == 3  # Subió con encolar
    assert cola.frente() == 1      # Primera entra primera sale FIFO / PEPS
    assert cola.frente() == 1    # Frente no modifica la cola
    assert cola.final.dato == 3
    assert cola.desencolar() == 1
    assert cola.desencolar() == 2
    # Un solo nodo
    assert cola.get_longitud() == 1    # Bajo con desencolar
    assert cola.frente() == 3
    assert cola.inicio is cola.final      # Inicio y final son el mismo en colas de 1 elem
    assert cola.inicio.siguiente is None
    assert cola.desencolar() == 3
    assert cola.esVacia()
    # No se borra la cola si esVacia
    cola.encolar(4)
    cola.encolar(5)
    cola.desencolar()
    cola.encolar(6)
    assert list(cola) == [5, 6]

# Iterar no modifica la cola
def test_cola_iterar():
    cola = Cola()
    cola.encolar(1)
    cola.encolar(2)
    cola.encolar(3)
    assert list(cola) == [1, 2, 3]
    assert list(cola) == [1, 2, 3]     # iterar no modifica la cola
    assert cola.get_longitud() == 3


# ValueError por desencolar cola vacia
def test_cola_desencolarVacia():
    cola = Cola()
    cola.encolar(1)
    cola.desencolar()
    with pytest.raises(ValueError, match = "No se pueden desencolar datos porque la cola está vacía"):
        cola.desencolar()

# ValueError por pedir el frente vacio
def test_cola_frenteVacia():
    with pytest.raises(ValueError, match = "No se puede pedir el primer elemento porque la cola está vacia"):
        Cola().frente()