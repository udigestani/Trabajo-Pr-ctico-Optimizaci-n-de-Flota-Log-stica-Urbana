class Articulo:
    curr_id = 0
    def __init__(self, descripcion, peso, volumen):
        self.descripcion = self.validar_descripcion(descripcion)
        self.peso = self.validar_numero(peso)
        self.volumen = self.validar_numero(volumen)
        Articulo.curr_id += 1
        self.id = Articulo.curr_id

    def getter_peso(self):
        return self.peso
    def getter_volumen(self):
        return self.volumen

    @staticmethod
    def validar_numero(valor):
        if isinstance(valor, (int, float)):
            if valor > 0:
                return valor
            raise ValueError(f"El valor {valor} debe ser mayor a 0")
        raise TypeError(f"El valor {valor} debe ser un número positivo")

    @staticmethod
    def validar_descripcion(cadena):
        if isinstance(cadena, str):
            if cadena:
                return cadena
            raise ValueError(f"La descripcion {cadena} no debe estar vacia")
        raise TypeError(f"La descripcion {cadena} debe ser una cadena str")

    def __str__(self):
        return f"Artículo {self.id}: {self.descripcion} ({self.peso}kg, {self.volumen}m³)"
    def __repr__(self):
        return f"<Articulo {self.id} '{self.descripcion}'>"
    def __eq__(self, otro):
        if isinstance(otro, Articulo):
            return self.id == otro.id
        return False

# art1 = Articulo("Producto", 1, 7)
art1 = Articulo("Producto", 1, 7)
art_2 = Articulo("Producto 2", 2, 5)
articulos = [Articulo(f"Producto {i}", i, i*2) for i in range(1, 11)]