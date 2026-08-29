class Articulo:
    curr_id = 0
    def __init__(self, solicitud, peso, volumen):
        self.solicitud = solicitud
        self.peso = peso
        self.volumen = volumen
        Articulo.curr_id += 1
        self.id = Articulo.curr_id