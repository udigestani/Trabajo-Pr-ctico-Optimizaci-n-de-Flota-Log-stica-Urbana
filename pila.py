from nodo import Nodo

class Pila:
    def __init__(self):
        self.tope = None
        self.longitud = 0
    def esVacia(self):
        return self.tope is None
    def ver_tope(self):
        if self.esVacia():
            raise ValueError("No se puede ver el tope porque la pila está vacía")
        return self.tope.dato
    def apilar(self, dato):
        nodo = Nodo(dato)
        nodo.siguiente = self.tope
        self.tope = nodo
        self.longitud += 1
    def desapilar(self):
        if self.esVacia():
            raise ValueError("No se pueden desapilar datos porque la pila está vacía")
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self.longitud -= 1
        return dato
    def __iter__(self):
        actual = self.tope
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
    def get_longitud(self):
        return self.longitud
