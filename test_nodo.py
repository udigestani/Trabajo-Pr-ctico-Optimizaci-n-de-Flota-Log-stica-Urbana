from nodo import Nodo
from parada import Parada

# Funcionamiento normal
def test_nodo_ok(mocker):
    nodo = Nodo(5)
    assert nodo.dato == 5
    assert str(nodo) == "5"
    assert repr(nodo) == "Nodo(5)"
    assert nodo.siguiente is None
    # Distintos tipos de datos
    nodo = Nodo("str")
    assert nodo.dato == "str"

    nodo = Nodo(None)    
    assert nodo.dato is None

    parada = mocker.MagicMock(spec = Parada)   # MagicMock permite configurar __str__
    parada.__str__.return_value = "Parada 1 [ENTREGADA] -> destino1 a las 15:00"
    nodo = Nodo(parada)
    assert nodo.dato == parada
    assert str(nodo) == "Parada 1 [ENTREGADA] -> destino1 a las 15:00"

# Enlaces
def test_nodo_enlazar():
    nodo1 = Nodo(1)
    nodo2 = Nodo(2)
    nodo1.siguiente = nodo2
    assert nodo1.siguiente is nodo2
    assert nodo2.siguiente is None