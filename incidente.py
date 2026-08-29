class Incidente:
    curr_id = 0
    def __init__(self, tipo, fecha, descripcion):
        self.tipo = tipo
        self.fecha = fecha
        self.descripcion = descripcion
        Incidente.curr_id += 1
        self.id = Incidente.curr_id