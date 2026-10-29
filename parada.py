from datetime import datetime
from excepciones import EstadoInvalidoError
from validaciones import Validaciones
from comprobante import Comprobante
from solicitud import Solicitud

class Parada:
    curr_id = 0

    def __init__(self, orden, solicitud, hora_prev, hora_real):
        self.orden = Validaciones.validar_numero(orden, entero = True, nombre = "orden de la parada")
        self.solicitud = Validaciones.validar_instancia(solicitud, clase = Solicitud, nombre = "solicitud")
        self.hora_prev = Validaciones.validar_fecha(hora_prev, nombre = "hora_prev")
        self.hora_real = Validaciones.validar_fecha(hora_real, vacio = True, nombre = "hora_real")
        self.comprobante = None

        Parada.curr_id += 1
        self.id = Parada.curr_id
        self.estado = "PENDIENTE"

    def generar_comprobante(self, receptor, fecha, monto):
        if self.estado == "PENDIENTE":
            if self.solicitud.getter_comprobante():
                raise EstadoInvalidoError("generar_comprobante", "la solicitud ya tiene comprobante")
            self.comprobante = Comprobante(self.solicitud, fecha, receptor, monto)
            self.solicitud.setter_comprobante(self.comprobante)
            self.hora_real = fecha
            self.estado = "ENTREGADA"
            return self.comprobante
        raise EstadoInvalidoError("generar_comprobante", self.estado)


    def serializar(self):
        if self.hora_real:
            hora_real = self.hora_real
        else:
            hora_real = ""
        if self.comprobante:
            id_comprobante = self.comprobante.getter_id()
        else:
            id_comprobante = ""
        return [self.id, self.orden, self.solicitud.getter_id(), self.hora_prev, hora_real, self.estado, id_comprobante]

    @classmethod
    def deserializar(cls, archivo, contexto):
        dicc_solicitudes = dict(map(lambda sol: (sol.getter_id(), sol), contexto[Solicitud]))
        dicc_comprobantes = dict(map(lambda comp: (comp.getter_id(), comp), contexto[Comprobante]))
        paradas = []
        for fila in archivo[1:]:
            if fila:
                hora_real = None
                if fila[4]:
                    hora_real = datetime.fromisoformat(fila[4])
                parada = cls(int(fila[1]), dicc_solicitudes[int(fila[2])], datetime.fromisoformat(fila[3]), hora_real)
                parada.id = int(fila[0])
                if fila[6]:
                    parada.comprobante = dicc_comprobantes[int(fila[6])]
                if fila[5] != "PENDIENTE":
                    estado = Validaciones.validar_en(fila[5], opciones = "FALLIDA, ENTREGADA", nombre = "estado")
                    parada.setter_estado(estado)
                paradas.append(parada)
        cls.curr_id = max(cls.curr_id, 0, *map(lambda p: p.id, paradas))
        return paradas

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
        if self.estado != "PENDIENTE":
            raise EstadoInvalidoError(f"settear estado a {estado}", f"la parada es {self.estado}")
        if estado == "ENTREGADA" and self.comprobante is None:
            raise EstadoInvalidoError("settear parada a ENTREGADA", "no tiene comprobante")
        self.estado = Validaciones.validar_en(estado, opciones = "FALLIDA, ENTREGADA", nombre = "estado")
        return None
    def setter_hora_real(self, hora_real):
        if self.estado == "PENDIENTE":
            raise EstadoInvalidoError("settear hora_real", "de la parada es PENDIENTE")
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
    def getter_comprobante(self):
        return self.comprobante
    def getter_id(self):
        return self.id