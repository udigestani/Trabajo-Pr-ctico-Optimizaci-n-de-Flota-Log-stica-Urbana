class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
    def getter_dato(self):
        return self.dato
    def getter_siguiente(self):
        return self.siguiente
    def setter_siguiente(self, siguiente):
        self.siguiente = siguiente
        return None
    def __str__(self):
        return f"{self.dato}"
    def __repr__(self):
        return f"Nodo({self.dato})"