from nodo import Nodo

class Cola:
    def __init__(self):
        self.inicio = None
        self.final = None
    def esVacia(self):
        return self.inicio == None
    def frente(self):
        return self.inicio.dato
    def encolar(self, dato):
        nodo = Nodo(dato)
        if self.esVacia():
            self.inicio, self.final = nodo, nodo
        else:
            self.final.siguiente = nodo
            self.final = nodo
    def desencolar(self):
        if self.esVacia():
            raise ValueError(f"No se pueden desencolar datos porque la cola está vacía")
        elif self.inicio is not self.final:
            dato = self.inicio.dato
            self.inicio = self.inicio.siguiente
            return dato
        else:
            dato = self.inicio.dato
            self.inicio, self.final = None, None
            return dato