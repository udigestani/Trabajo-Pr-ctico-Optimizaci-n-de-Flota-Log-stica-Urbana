from comprobante import Comprobante
from solicitud import Solicitud

from datetime import datetime

class Parada:
    curr_id = 0
    id_comprobante = 0

    def __init__(self, orden, solicitud, hora_prev, hora_real):
        self.orden = self.validar_orden(orden)
        self.solicitud = self.validar_solicitud(solicitud)
        self.hora_prev, self.hora_real = self.validar_hora(hora_prev, hora_real)
        # self.ubicacion = ubicacion?? --> Ubicación dentro de solicitud?
        # self.ubicacion = solicitud.getter_ubicacion()
        Parada.curr_id += 1
        self.id = Parada.curr_id
        self.estado = "PENDIENTE"

    def generar_comprobante(self, receptor, fecha):
        if self.estado == "PENDIENTE":
            self.estado = "ENTREGADO"
            self.comprobante = Comprobante(Parada.id_comprobante, receptor, fecha)
            return self.comprobante
        raise Exception(f"El estado de la parada ya es {self.estado}")


    @staticmethod
    def validar_orden(valor):
        if isinstance(valor, int):
            if valor > 0:
                return valor
            raise ValueError(f"El orden de la parada debe ser mayor a 0")
        raise TypeError(f"El valor {valor} debe ser un entero positivo")

    @staticmethod
    def validar_solicitud(solicitud):
        if isinstance(solicitud, Solicitud):
            return solicitud
        raise TypeError(f"La solicitud {solicitud} debe ser un objeto de clase Solicitud")

    @staticmethod
    def validar_hora(hora_prev, hora_real):
        if not isinstance(hora_prev, datetime) or not isinstance(hora_real, datetime):
            raise TypeError("hora_prev y hora_real deben ser objetos datetime")
        else:
            return hora_prev, hora_real

        
    # @staticmethod
    # def validar_hora(hora):     ???