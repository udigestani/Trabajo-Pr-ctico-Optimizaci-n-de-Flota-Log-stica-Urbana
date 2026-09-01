
from datetime import datetime


class Incidente:
    curr_id = 0
    def __init__(self, tipo, fecha, descripcion):
        self.tipo = self.validar_tipo(tipo)
        self.fecha = self.validar_fecha(fecha)
        self.descripcion = self.validar_descripcion(descripcion)
        Incidente.curr_id += 1
        self.id = Incidente.curr_id

    @staticmethod
    def validar_tipo(tipo):
        if not isinstance(tipo, str):
            raise TypeError(f"El tipo del incidente debe ser DAÑO, AUSENTE o RETRASO")
        if tipo not in ("DANO", "AUSENTE", "RETRASO"):
            raise ValueError(f"El tipo del incidente debe ser DAÑO, AUSENTE o RETRASO")
        return tipo

    @staticmethod
    def validar_descripcion(cadena):
        if isinstance(cadena, str):
            if cadena:
                return cadena
            raise ValueError(f"La descripcion {cadena} no debe estar vacia")
        raise TypeError(f"La descripcion {cadena} debe ser una cadena str")

    @staticmethod
    def validar_fecha(fecha):
        if not isinstance(fecha, datetime):
            raise TypeError("fecha debe ser un objeto datetime")
        return fecha

    # @staticmethod
    # def validar_fecha(fecha):          ?