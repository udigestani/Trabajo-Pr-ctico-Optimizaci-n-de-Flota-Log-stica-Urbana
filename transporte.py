class Transporte:
    curr_id = 0
    def __init__(self, capacidad, peso_max, velocidad, costo_viaje, factor_ambiental, solicitud):
        self.capacidad = capacidad
        self.peso_max = peso_max
        self.velocidad = velocidad
        self.costo_viaje = costo_viaje
        self.factor_ambiental = factor_ambiental
        # self.solicitud = solicitud??
        Transporte.curr_id += 1      
        self.id = Transporte.curr_id