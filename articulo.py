class Articulo:
    curr_id = 0
    def __init__(self, solicitud, peso_volumen):
        self.solicitud = solicitud
        self.peso_volumen = peso_volumen
        Articulo.curr_id += 1
        self.id = Articulo.curr_id