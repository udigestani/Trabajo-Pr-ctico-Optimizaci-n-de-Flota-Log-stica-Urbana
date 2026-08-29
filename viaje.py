from incidente import Incidente
from parada import Parada

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, solicitud, horario, estado):
        # self.transporte = transporte??
        self.deposito = deposito
        # self.solicitud = solicitud??
        self.horario = horario
        self.estado = estado
        self.paradas = []
        Viaje.curr_id += 1
        self.id = Viaje.curr_id
    def registrar_incidente(self, tipo, fecha, descripcion):
        self.incidente = Incidente(tipo, fecha, descripcion)
        return self.incidente
    def agregar_parada(self, orden, hora_prev, hora_real, ubicacion):
        parada = Parada(orden, hora_prev, hora_real, ubicacion)
        self.paradas.append(parada)
        return parada