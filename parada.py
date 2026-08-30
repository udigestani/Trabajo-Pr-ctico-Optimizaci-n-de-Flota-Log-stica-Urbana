from comprobante import Comprobante
from solicitud import Solicitud

class Parada:
    curr_id = 0
    id_comprobante = 0

    def __init__(self, orden, solicitud, hora_prev, hora_real):
        self.orden = orden
        self.solicitud = solicitud
        self.hora_prev = hora_prev
        self.hora_real = hora_real
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

    