from nodo import Nodo

class ListaEnlazada:
    def __init__(self):
        self.inicio = None
        self.final = None
        self.tamanio = 0
    def agregar_al_final(self, dato):
        nuevo_nodo = Nodo(dato)
        if self.es_vacia():
            self.inicio = nuevo_nodo
        else:
            self.final.siguiente = nuevo_nodo
        self.final = nuevo_nodo
        self.tamanio +=1
    def __len__(self):
        return self.tamanio
    def es_vacia(self):
        return self.inicio is None
    def agregar_al_inicio(self, valor):
        nodo = Nodo(valor)
        if self.es_vacia():
            self.final = nodo
        else:
            nodo.siguiente = self.inicio
        self.inicio = nodo
        self.tamanio +=1
    def __iter__(self):
        actual = self.inicio
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
    def __str__(self):
        return " --> ".join(map(str, self))
    def buscar(self, dato):
        return any(map(lambda elemento: elemento == dato, self))
    def insertar_despues(self, anterior, dato):
        actual = self.inicio
        while actual is not None and actual.dato != anterior:
            actual = actual.siguiente
        if actual is None:
            raise ValueError(f"No se puede insertar después de {anterior} porque no está en la lista")
        nodo = Nodo(dato)
        nodo.siguiente = actual.siguiente
        actual.siguiente = nodo
        if actual is self.final:
            self.final = nodo
        self.tamanio += 1
    def insertar_antes(self, posterior, dato):
        if self.es_vacia():
            raise ValueError(f"No se puede insertar antes de {posterior} porque no está en la lista")
        if self.inicio.dato == posterior:
            self.agregar_al_inicio(dato)
            return None
        anterior = self.inicio
        while anterior.siguiente is not None and anterior.siguiente.dato != posterior:
            anterior = anterior.siguiente
        if anterior.siguiente is None:
            raise ValueError(f"No se puede insertar antes de {posterior} porque no está en la lista")
        nodo = Nodo(dato)
        nodo.siguiente = anterior.siguiente
        anterior.siguiente = nodo
        self.tamanio += 1
    def eliminar(self, dato):
        if self.es_vacia():
            return False
        if self.inicio.dato == dato:
            if self.inicio is self.final:
                self.final = None
            self.inicio = self.inicio.siguiente
            self.tamanio -=1
            return True
        anterior, auxiliar = self.inicio, self.inicio.siguiente
        while auxiliar is not None:
            if auxiliar.dato == dato:
                anterior.siguiente = auxiliar.siguiente
                if auxiliar is self.final:
                    self.final = anterior
                self.tamanio -= 1
                return True
            anterior, auxiliar = auxiliar, auxiliar.siguiente
        return False
