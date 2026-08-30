class Comprobante:
    curr_id = 0
    def __init__(self, fecha_Hora, receptor):
        self.receptor = self.comprbar_receptor(receptor)
        self.fecha_Hora = fecha_Hora
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    @staticmethod
    def comprobar_receptor(receptor):
        if receptor and receptor.strip():
            return receptor
        raise ValueError(f"El receptor no puede ser vacio")
    