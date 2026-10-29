class Nodo_arbol:
    def __init__(self, dato, instancia):
        self.dato = dato
        self.instancia = instancia
        self.izquierdo = None
        self.derecho = None
    def __str__(self):
        return f'{self.dato}'
    def getter_dato(self):
        return self.dato
    def getter_instancia(self):
        return self.instancia
    def getter_izquierdo(self):
        return self.izquierdo
    def getter_derecho(self):
        return self.derecho
    def setter_izquierdo(self, nodo):
        self.izquierdo = nodo
        return None
    def setter_derecho(self, nodo):
        self.derecho = nodo
        return None

class Arbol:
    def __init__(self):
        self.raiz = None
    def getter_raiz(self):
        return self.raiz
    def setter_raiz(self, nodo):
        self.raiz = nodo
        return None
    def insertar(self, dato, instancia):
        if self.esVacio():
            self.setter_raiz(Nodo_arbol(dato, instancia))
            return None
        aux = self.getter_raiz()
        anterior = self
        while aux is not None:
            if aux.getter_dato() == dato:
                raise ValueError(f"El valor {dato} ya está en el árbol")
            elif aux.getter_dato() > dato:
                anterior = aux
                aux = aux.getter_izquierdo()
            else:
                anterior = aux
                aux = aux.getter_derecho()
        if anterior.getter_dato() > dato:
            anterior.setter_izquierdo(Nodo_arbol(dato, instancia))
        else:
            anterior.setter_derecho(Nodo_arbol(dato, instancia))
        return None
    def buscar(self, sub_arbol, dato):
        if sub_arbol == None:
            return None
        if sub_arbol.getter_dato() == dato:
            return sub_arbol.getter_instancia()
        elif sub_arbol.getter_dato() > dato:
            return self.buscar(sub_arbol.getter_izquierdo(), dato)
        else:
            return self.buscar(sub_arbol.getter_derecho(), dato)
    def buscar_con_saltos(self, dato):
        aux = self.getter_raiz()
        saltos = 0
        while aux is not None and aux.getter_dato() != dato:
            if aux.getter_dato() > dato:
                aux = aux.getter_izquierdo()
            else:
                aux = aux.getter_derecho()
            saltos += 1
        if aux is None:
            return None, saltos
        return aux.getter_instancia(), saltos
    def esVacio(self):
        return self.raiz == None
    def preorden(self, sub_arbol):
        if sub_arbol != None:
            print(sub_arbol, end = ' ')
            self.preorden(sub_arbol.getter_izquierdo())
            self.preorden(sub_arbol.getter_derecho())
    def inorden(self, sub_arbol):
        if sub_arbol == None:
            return []
        return self.inorden(sub_arbol.getter_izquierdo()) + [sub_arbol.getter_dato()] + self.inorden(sub_arbol.getter_derecho())
    def posorden(self, sub_arbol):
        if sub_arbol != None:
            self.posorden(sub_arbol.getter_izquierdo())
            self.posorden(sub_arbol.getter_derecho())
            print(sub_arbol, end = ' ')