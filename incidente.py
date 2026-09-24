from excepciones import DatoInvalidoError
from datetime import datetime
from solicitud import Solicitud


class Incidente:
    curr_id = 0
    def __init__(self, tipo, fecha, descripcion, afectado):
        self.tipo = self.validar_tipo(tipo)
        self.fecha = self.validar_fecha(fecha)
        self.descripcion = self.validar_descripcion(descripcion)
        self.afectado = self.validar_afectado(afectado)
        Incidente.curr_id += 1
        self.id = Incidente.curr_id

    @staticmethod
    def validar_tipo(tipo):
        if not isinstance(tipo, str):
            raise TypeError(f"El tipo del incidente debe ser DAÑO, AUSENTE o RETRASO")
        if tipo not in ("DAÑO", "AUSENTE", "RETRASO"):
            raise DatoInvalidoError(f"El tipo del incidente debe ser DAÑO, AUSENTE o RETRASO")
        return tipo

    @staticmethod
    def validar_descripcion(cadena):
        if isinstance(cadena, str):
            if cadena:
                return cadena
            raise DatoInvalidoError(f"La descripcion {cadena} no debe estar vacia")
        raise TypeError(f"La descripcion {cadena} debe ser una cadena str")

    @staticmethod
    def validar_fecha(fecha):
        if not isinstance(fecha, datetime):
            raise TypeError("fecha debe ser un objeto datetime")
        return fecha

    @staticmethod
    def validar_afectado(afectado):
        if not isinstance(afectado, Solicitud):
            raise TypeError("El incidente debe referenciar a una Solicitud")
        return afectado
    def __str__(self):
        fecha_str = self.fecha.strftime('%H:%M')
        return f"Incidente {self.id} [{self.tipo}] a las {fecha_str}: {self.descripcion}"
    def __repr__(self):
        return f"Incidente({self.tipo}, {self.fecha}, {self.descripcion}, {self.afectado})"
    # @staticmethod
    # def validar_fecha(fecha):          ?