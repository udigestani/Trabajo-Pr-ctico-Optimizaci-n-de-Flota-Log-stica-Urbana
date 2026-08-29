class Comprobante:
    curr_id = 0
    def __init__(self, fecha_Hora, receptor):
        self.setter_receptor(receptor)
        self.fecha_Hora = fecha_Hora
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    def setter_receptor(self, receptor):
        if receptor and receptor.strip():
            self.receptor = receptor
        else:
            raise ValueError(f"El receptor no puede ser vacio")