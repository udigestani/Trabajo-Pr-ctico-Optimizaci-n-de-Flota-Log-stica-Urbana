# Tu implementacion va aqui
def hola_mundo():
    return "hola_mundo"



class Comprobante:
    curr_id = 0
    def __init__(self, Fecha_Hora, Monto, Receptor):
        self.Fecha_Hora = Fecha_Hora
        self.Monto = Monto
        self.Receptor = Receptor
        Comprobante.curr_id += 1
        self.Id = Comprobante.curr_id


class Solicitud:
    curr_id = 0
    def __init__(self,Articulos,Ubi_Ini,Ubi_Desti,Horario,Estado):
        self.Articulos = Articulos
        self.Ubi_Ini = Ubi_Ini
        self.Ubi_Desti = Ubi_Desti
        self.Horario = Horario
        self.Estado = Estado
        Solicitud.curr_id += 1
        self.Id = Solicitud.curr_id

    def generar_comprobante(self, Fecha_Hora, Monto, Receptor):
        self.Comprobante = Comprobante(Fecha_Hora, Monto, Receptor)
        return self.Comprobante

class Articulo:
    curr_id = 0
    def __init__(self,Solicitud,Peso_Volumen):
        self.Solicitud = Solicitud
        self.Peso_Volumen = Peso_Volumen
        Articulo.curr_id += 1
        self.Id = Articulo.curr_id

class Viaje:
    curr_id = 0
    def __init__(self,Transporte,Deposito,Solicitud,Horario,Estado):
        self.Transporte = Transporte??
        self.Deposito = Deposito
        self.Solicitud = Solicitud??
        self.Horario = Horario
        self.Estado = Estado
        self.Paradas = []
        Viaje.curr_id += 1
        self.Id = Viaje.curr_id
    def registrar_incidente(self, Tipo, Fecha, Descripcion):
        self.Incidente = Incidente(Tipo, Fecha, Descripcion)
        return self.Incidente
    def agregar_parada(self, Orden, Hora_prev, Hora_real, Ubicacion):
        parada = Parada(Orden, Hora_prev, Hora_real, Ubicacion)
        self.Paradas.append(parada)
        return parada

class Incidente:
    curr_id = 0
    def __init__(self,Tipo,Fecha,Descripcion):
        self.Tipo = Tipo
        self.Fecha = Fecha
        self.Descripcion = Descripcion
        Incidente.curr_id += 1
        self.Id = Incidente.curr_id

class Parada:
    curr_id = 0
    def __init__(self,Orden,Hora_prev,Hora_real,Ubicacion):
        self.Orden = Orden
        self.Hora_prev = Hora_prev
        self.Hora_real = Hora_real
        self.Ubicacion = Ubicacion??
        Parada.curr_id += 1
        self.Id = Parada.curr_id

class Ubicacion:
    curr_id = 0                 
    def __init__(self,Descripcion,Latitud,Longitud):
        self.Descripcion = Descripcion
        self.Latitud = Latitud
        self.Longitud = Longitud
        Ubicacion.curr_id += 1      
        self.Id = Ubicacion.curr_id         

class Transporte:
    curr_id = 0
    def __init__(self,Capacidad,Peso_Max,Velocidad,Costo_Viaje,Factor_Ambiental,Solicitud):
        self.Capacidad = Capacidad
        self.Peso_Max = Peso_Max
        self.Velocidad = Velocidad
        self.Costo_Viaje = Costo_Viaje
        self.Factor_Ambiental = Factor_Ambiental
        self.Solicitud = Solicitud??
        Transporte.curr_id += 1      
        self.Id = Transporte.curr_id         
        
    

def main():
    # Aqui ejecutas tus soluciones hola
    print(hola_mundo())
   

# No cambiar a partir de aqui
if __name__ == "__main__":
    main()