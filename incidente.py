from excepciones import DatoInvalidoError
from datetime import datetime
from solicitud import Solicitud


class Incidente:
    curr_id = 0
    def __init__(self, tipo, fecha, descripcion, afectado, **detalles):
        self.tipo = self.validar_tipo(tipo)
        self.fecha = self.validar_fecha(fecha)
        self.descripcion = self.validar_descripcion(descripcion)
        self.afectado = self.validar_afectado(afectado)
        self.detalles = self.validar_detalles(detalles)
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
            if cadena.strip():
                return cadena.strip()
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

    @staticmethod
    def validar_detalles(detalles):
        for clave, valor in detalles.items():
            if isinstance(valor, str) and not valor.strip():
                raise DatoInvalidoError(f"El detalle {clave} no puede ser una cadena vacía")
        return detalles
    def getter_tipo(self):
        return self.tipo
    def getter_afectado(self):
        return self.afectado
    def getter_detalles(self):
        return self.detalles.copy()

    def __str__(self):
        fecha_str = self.fecha.strftime('%H:%M')
        base = f"Incidente {self.id} [{self.tipo}] a las {fecha_str}: {self.descripcion}"
        for clave, valor in self.detalles.items():
            base += f", {clave}={valor}"
        return base
    def __repr__(self):
        return f"Incidente({self.tipo}, {self.fecha}, {self.descripcion}, {self.afectado}, **{self.detalles})"