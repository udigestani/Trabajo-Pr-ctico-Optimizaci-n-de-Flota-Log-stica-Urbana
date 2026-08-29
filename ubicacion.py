class Ubicacion:
    curr_id = 0                 
    def __init__(self, descripcion, latitud, longitud):
        self.descripcion = descripcion
        self.latitud = latitud
        self.longitud = longitud
        Ubicacion.curr_id += 1      
        self.id = Ubicacion.curr_id  