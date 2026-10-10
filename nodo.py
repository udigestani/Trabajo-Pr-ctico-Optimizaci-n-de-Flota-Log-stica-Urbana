class Nodo:
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None
    def __str__(self):
        return f"{self.dato}"
    def __repr__(self):
        return f"Nodo({self.dato})"