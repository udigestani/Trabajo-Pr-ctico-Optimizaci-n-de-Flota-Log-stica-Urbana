# Tu implementacion va aqui
def hola_mundo():
    return "hola_mundo"



class Comprobante:
    curr_id = 0
    def __init__(self, fecha_Hora, monto, receptor):
        self.fecha_Hora = fecha_Hora
        self.monto = monto
        self.receptor = receptor
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id


class Solicitud:
    curr_id = 0
    def __init__(self, articulos, ubi_ini , ubi_desti, horario, estado):
        self.articulos = articulos
        self.ubi_ini = ubi_ini
        self.ubi_desti = ubi_desti
        self.horario = horario
        self.estado = estado
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, monto, receptor):
        self.comprobante = Comprobante(fecha_Hora, monto, receptor)
        return self.comprobante

class Articulo:
    curr_id = 0
    def __init__(self, solicitud, peso_volumen):
        self.solicitud = solicitud
        self.peso_volumen = peso_volumen
        Articulo.curr_id += 1
        self.id = Articulo.curr_id

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, solicitud, horario, estado):
        # self.transporte = transporte??
        self.deposito = deposito
        # self.solicitud = solicitud??
        self.horario = horario
        self.estado = estado
        self.paradas = []
        Viaje.curr_id += 1
        self.id = Viaje.curr_id
    def registrar_incidente(self, tipo, fecha, descripcion):
        self.incidente = Incidente(tipo, fecha, descripcion)
        return self.incidente
    def agregar_parada(self, orden, hora_prev, hora_real, ubicacion):
        parada = Parada(orden, hora_prev, hora_real, ubicacion)
        self.paradas.append(parada)
        return parada

class Incidente:
    curr_id = 0
    def __init__(self, tipo, fecha, descripcion):
        self.tipo = tipo
        self.fecha = fecha
        self.descripcion = descripcion
        Incidente.curr_id += 1
        self.id = Incidente.curr_id

class Parada:
    curr_id = 0
    def __init__(self, orden, hora_prev, hora_real, ubicacion):
        self.orden = orden
        self.hora_prev = hora_prev
        self.hora_real = hora_real
        # self.ubicacion = ubicacion??
        Parada.curr_id += 1
        self.id = Parada.curr_id

class Ubicacion:
    curr_id = 0                 
    def __init__(self, descripcion, latitud, longitud):
        self.descripcion = descripcion
        self.latitud = latitud
        self.longitud = longitud
        Ubicacion.curr_id += 1      
        self.id = Ubicacion.curr_id         

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
        
    

def main():
    # Aqui ejecutas tus soluciones hola
    print(hola_mundo())
   

# No cambiar a partir de aqui
if __name__ == "__main__":
    main()