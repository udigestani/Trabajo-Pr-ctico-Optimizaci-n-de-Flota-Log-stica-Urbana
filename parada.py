class Parada:
    curr_id = 0
    def __init__(self, orden, hora_prev, hora_real, ubicacion):
        self.orden = orden
        self.hora_prev = hora_prev
        self.hora_real = hora_real
        # self.ubicacion = ubicacion??
        Parada.curr_id += 1
        self.id = Parada.curr_id