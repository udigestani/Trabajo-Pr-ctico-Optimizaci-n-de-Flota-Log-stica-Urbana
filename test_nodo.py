from nodo import Nodo
from parada import Parada

# Funcionamiento normal
def test_nodo_ok(mocker):
    nodo = Nodo(5)
    assert nodo.getter_dato() == 5
    assert str(nodo) == "5"
    assert repr(nodo) == "Nodo(5)"
    assert nodo.getter_siguiente() is None
    # Distintos tipos de datos
    nodo = Nodo("str")
    assert nodo.getter_dato() == "str"

    nodo = Nodo(None)    
    assert nodo.getter_dato() is None

    parada = mocker.MagicMock(spec = Parada)   # MagicMock permite configurar __str__
    parada.__str__.return_value = "Parada 1 [ENTREGADA] -> destino1 a las 15:00"
    nodo = Nodo(parada)
    assert nodo.getter_dato() == parada
    assert str(nodo) == "Parada 1 [ENTREGADA] -> destino1 a las 15:00"

# Getters
def test_nodo_getters():
    nodo = Nodo(7)
    assert nodo.getter_dato() == 7
    assert nodo.getter_siguiente() is None

# Enlaces
def test_nodo_enlazar():
    nodo1 = Nodo(1)
    nodo2 = Nodo(2)
    nodo1.setter_siguiente(nodo2)
    assert nodo1.getter_siguiente() is nodo2
    assert nodo2.getter_siguiente() is None
def test_nodo_setterSiguiente_devuelveNone():
    assert Nodo(1).setter_siguiente(Nodo(2)) is None
def test_nodo_setterSiguiente_desenlazar():
    nodo1 = Nodo(1)
    nodo1.setter_siguiente(Nodo(2))
    nodo1.setter_siguiente(None)
    assert nodo1.getter_siguiente() is None
