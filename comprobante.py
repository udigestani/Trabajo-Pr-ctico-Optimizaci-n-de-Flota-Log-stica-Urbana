class Comprobante:
    curr_id = 0
    def __init__(self, fecha_Hora, monto, receptor):
        self.fecha_Hora = fecha_Hora
        self.monto = monto
        self.receptor = receptor
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id