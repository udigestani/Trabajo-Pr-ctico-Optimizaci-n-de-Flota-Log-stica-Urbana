from excepciones import EstadoInvalidoError
from validaciones import Validaciones
from comprobante import Comprobante
from solicitud import Solicitud

class Parada:
    curr_id = 0
    id_comprobante = 0

    def __init__(self, orden, solicitud, hora_prev, hora_real):
        self.orden = Validaciones.validar_numero(orden, entero = True, nombre = "orden de la parada")
        self.solicitud = Validaciones.validar_instancia(solicitud, clase = Solicitud, nombre = "solicitud")
        self.hora_prev = Validaciones.validar_fecha(hora_prev, nombre = "hora_prev")
        self.hora_real = Validaciones.validar_fecha(hora_real, vacio = True, nombre = "hora_real")

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
        self.estado = Validaciones.validar_en(estado, opciones = "FALLIDA, ENTREGADA", nombre = "estado")
        return None
    def setter_hora_real(self, hora_real):
        self.hora_real = Validaciones.validar_fecha(hora_real, nombre = "hora_real")
        return None
    def getter_solicitud(self):
        return self.solicitud
    def getter_orden(self):
        return self.orden
    def getter_hora_prev(self):
        return self.hora_prev
    def getter_hora_real(self):
        return self.hora_real