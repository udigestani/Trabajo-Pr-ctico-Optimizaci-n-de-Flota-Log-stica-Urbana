from excepciones import DatoInvalidoError
from datetime import datetime
from math import isfinite

class Comprobante:
    curr_id = 0
    def __init__(self,solicitud, fecha_Hora, receptor,monto):
        self.solicitud = self.validar_solicitud(solicitud)
        self.receptor = self.validar_receptor(receptor)
        self.fecha_Hora = self.validar_fecha_hora(fecha_Hora)
        self.monto=self.validar_monto(monto)
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    @staticmethod
    def validar_receptor(receptor):
        if not isinstance(receptor, str):
            raise TypeError(f"El receptor {receptor} debe ser una cadena str")
        if receptor and receptor.strip():
            return receptor
        raise DatoInvalidoError(f"El receptor no puede ser vacio")

    @staticmethod
    def validar_fecha_hora(fecha_hora):
        if not isinstance(fecha_hora, datetime):
            raise TypeError("La fecha_hora del comprobante debe ser un objeto datetime")
        return fecha_hora

    @staticmethod
    def validar_solicitud(solicitud):
        from solicitud import Solicitud
        if not isinstance(solicitud, Solicitud):
            raise TypeError("La solicitud debe ser un objeto de la clase Solicitud")
        return solicitud
    
    @staticmethod
    def validar_monto(monto):
        if not isinstance(monto, (int, float)) or isinstance(monto, bool):
            raise TypeError("El monto debe ser un número")
        elif not isfinite(monto):
            raise DatoInvalidoError("El monto debe ser un número finito")
        if monto < 0:
            raise DatoInvalidoError("El monto no puede ser negativo")
        return monto
    def getter_solicitud(self):
        return self.solicitud
    def getter_receptor(self):
        return self.receptor
    def getter_monto(self):
        return self.monto

    def __str__(self):
        fecha_str = self.fecha_Hora.strftime('%Y-%m-%d %H:%M')
        return f"Comprobante {self.id} | Solicitud {self.solicitud.getter_id()} | Recibió: {self.receptor} el {fecha_str} | Monto: ${self.monto}"
