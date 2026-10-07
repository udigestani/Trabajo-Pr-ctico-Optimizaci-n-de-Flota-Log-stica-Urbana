from nodo import Nodo

class Cola:
    def __init__(self):
        self.inicio = None
        self.final = None
        self.longitud = 0
    def esVacia(self):
        return self.inicio == None
    def frente(self):
        if self.esVacia():
            raise ValueError("No se puede pedir el primer elemento porque la cola está vacia")
        return self.inicio.dato
    def encolar(self, dato):
        nodo = Nodo(dato)
        if self.esVacia():
            self.inicio, self.final = nodo, nodo
            self.longitud = 1
        else:
            self.final.siguiente = nodo
            self.final = nodo
            self.longitud +=1
    def desencolar(self):
        if self.esVacia():
            raise ValueError(f"No se pueden desencolar datos porque la cola está vacía")
        elif self.inicio is not self.final:
            dato = self.inicio.dato
            self.inicio = self.inicio.siguiente
            self.longitud -=1
            return dato
        else:
            dato = self.inicio.dato
            self.inicio, self.final = None, None
            self.longitud = 0
            return dato
    def __iter__(self):
        actual = self.inicio
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
    def get_longitud(self):
        return self.longitud