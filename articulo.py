from excepciones import DatoInvalidoError
from math import isfinite

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
    def getter_id(self):
        return self.id

    @staticmethod
    def validar_numero(valor):
        if isinstance(valor, (int, float)) and not isinstance(valor, bool):
            if isfinite(valor) and valor > 0:
                return valor
            raise DatoInvalidoError(f"El valor {valor} debe ser finito y mayor a 0")
        raise TypeError(f"El valor {valor} debe ser un número positivo")

    @staticmethod
    def validar_descripcion(cadena):
        if isinstance(cadena, str):
            if cadena.strip():
                return cadena
            raise DatoInvalidoError(f"La descripcion {cadena} no debe estar vacia")
        raise TypeError(f"La descripcion {cadena} debe ser una cadena str")

    def __str__(self):
        return f"Artículo {self.id}: {self.descripcion} ({self.peso}kg, {self.volumen}m³)"
    def __repr__(self):
        return f"<Articulo {self.id} '{self.descripcion}'>"
    def __eq__(self, otro):
        if isinstance(otro, Articulo):
            return self.id == otro.getter_id()
        return False
    def __hash__(self):
        return hash(self.id)
