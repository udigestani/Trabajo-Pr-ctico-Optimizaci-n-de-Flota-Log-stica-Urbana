class Articulo:
    curr_id = 0
    def __init__(self, descripcion, peso, volumen):
        self.descripcion = descripcion
        self.peso = peso
        self.volumen = volumen
        Articulo.curr_id += 1
        self.id = Articulo.curr_id

    def getter_peso(self):
        return self.peso
    def getter_volumen(self):
        return self.volumen