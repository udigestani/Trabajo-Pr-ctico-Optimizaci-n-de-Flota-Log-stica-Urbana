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

art1 = Articulo("Producto", 1, 7)