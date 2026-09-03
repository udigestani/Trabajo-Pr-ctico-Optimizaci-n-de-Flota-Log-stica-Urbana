
from datetime import datetime

class Comprobante:
    curr_id = 0
    def __init__(self,solicitud, fecha_Hora, receptor):
        self.solicitud = self.validar_solicitud(solicitud)
        self.receptor = self.validar_receptor(receptor)
        self.fecha_Hora = self.validar_fecha_hora(fecha_Hora)
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    @staticmethod
    def validar_receptor(receptor):
        if not isinstance(receptor, str):
            raise TypeError(f"El receptor {receptor} debe ser una cadena str")
        if receptor and receptor.strip():
            return receptor
        raise ValueError(f"El receptor no puede ser vacio")

    @staticmethod
    def validar_fecha_hora(fecha_hora):
        if not isinstance(fecha_hora, datetime):
            raise TypeError("La fecha_hora del comprobante debe ser un objeto datetime")
        return fecha_hora


    # @staticmethod
    # def validar_fecha_hora():     ? Libreria?