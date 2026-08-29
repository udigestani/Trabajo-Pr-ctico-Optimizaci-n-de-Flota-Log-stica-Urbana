from comprobante import Comprobante

class Solicitud:
    curr_id = 0
    def __init__(self, articulos, ubi_ini , ubi_desti, horario, estado):
        self.articulos = articulos
        self.ubi_ini = ubi_ini
        self.ubi_desti = ubi_desti
        self.horario = horario
        self.estado = estado
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, monto, receptor):
        self.comprobante = Comprobante(fecha_Hora, monto, receptor)
        return self.comprobante