from excepciones import DatoInvalidoError, EstadoInvalidoError
from comprobante import Comprobante
from solicitud import Solicitud
from datetime import datetime

class Parada:
    curr_id = 0
    id_comprobante = 0

    def __init__(self, orden, solicitud, hora_prev, hora_real, resultado = "PENDIENTE"):
        self.orden = self.validar_orden(orden)
        self.solicitud = self.validar_solicitud(solicitud)
        self.hora_prev, self.hora_real = self.validar_hora(hora_prev, hora_real)
        self.resultado = resultado

        Parada.curr_id += 1
        self.id = Parada.curr_id
        self.estado = "PENDIENTE"

    def generar_comprobante(self, receptor, fecha, monto):
        if self.estado == "PENDIENTE":
            self.comprobante = Comprobante(self.solicitud, fecha, receptor, monto)
            self.solicitud.setter_comprobante(self.comprobante)
            self.hora_real = fecha
            self.estado = "ENTREGADA"
            return self.comprobante
        raise EstadoInvalidoError("generar_comprobante", self.estado)


    @staticmethod
    def validar_orden(valor):
        if isinstance(valor, int):
            if valor > 0:
                return valor
            raise DatoInvalidoError(f"El orden de la parada debe ser mayor a 0")
        raise TypeError(f"El valor {valor} debe ser un entero positivo")

    @staticmethod
    def validar_solicitud(solicitud):
        if isinstance(solicitud, Solicitud):
            return solicitud
        raise TypeError(f"La solicitud {solicitud} debe ser un objeto de clase Solicitud")

    @staticmethod
    def validar_hora(hora_prev, hora_real):
        if not isinstance(hora_prev, datetime) or not isinstance(hora_real, (datetime, type(None))):
            raise TypeError("hora_prev y hora_real deben ser objetos datetime")
        else:
            return hora_prev, hora_real

    def __str__(self):
        hora = self.hora_prev.strftime('%H:%M')
        if self.hora_real:
            hora = f"{self.hora_real.strftime('%H:%M')} (REAL)"
        return f"Parada {self.orden} [{self.estado}] -> {self.solicitud.getter_destino()} a las {hora}"

    def __repr__(self):
        return f"<Parada {self.orden} {self.estado}>"

    def getter_estado(self):
        return self.estado
    def setter_estado(self, estado):
        self.estado = estado
        return None
    def setter_hora_real(self, hora_real):
        self.hora_real = hora_real
        return None
    def getter_solicitud(self):
        return self.solicitud
    def getter_orden(self):
        return self.orden
    def getter_hora_prev(self):
        return self.hora_prev
    def getter_hora_real(self):
        return self.hora_real