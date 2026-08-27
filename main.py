# Tu implementacion va aqui
def hola_mundo():
    return "hola_mundo"


class COMPROBANTE:
    def __init__(self, Id, Solicitud, Fecha_Hora, Monto, Receptor):
        self.Id = Id
        self.Solicitud = Solicitud
        self.Fecha_Hora = Fecha_Hora
        self.Monto = Monto
        self.Receptor = Receptor


class SOLICITUD:
    def __init__(self,Id,Articulos,Ubi_Ini,Ubi_Desti,Horario,Comprobante,Estado):
        self.Id = Id
        self.Articulos = Articulos
        self.Ubi_Ini = Ubi_Ini
        self.Ubi_Desti = Ubi_Desti
        self.Horario = Horario
        self.Comprobante = Comprobante??
        self.Estado = Estado

class ARTICULO:
    def __init__(self,Id,Solicitud,Peso_Volumen):
        self.Id = Id
        self.Solicitud = Solicitud
        self.Peso_Volumen = Peso_Volumen

class VIAJE:
    def __init__(self,Id,Transporte,Deposito,Solicitud,Horario,Estado,Paradas,Incidentes):
        self.Id = Id
        self.Transporte = Transporte??
        self.Deposito = Deposito
        self.Solicitud = Solicitud??
        self.Horario = Horario
        self.Estado = Estado
        self.Paradas = Paradas??
        self.Incidentes = Incidentes??

class INCIDENTE:
    def __init__(self,Id,Tipo,Fecha,Descripcion,Viaje):
        self.Id = Id
        self.Tipo = Tipo
        self.Fecha = Fecha
        self.Descripcion = Descripcion
        self.Viaje = Viaje??

class PARADA:
    def __init__(self,Id,Orden,Hora_prev,Hora_real,Ubicacion):
        self.Id = Id
        self.Orden = Orden
        self.Hora_prev = Hora_prev
        self.Hora_real = Hora_real
        self.Ubicacion = Ubicacion??

class UBICACION:
    def __init__(self,Id,Descripcion):
        self.Id = Id
        self.Descripcion = Descripcion

class TRANSPORTE:
    def __init__(self,Capacidad,Peso_Max,Velocidad,Costo_Viaje,Factor_Ambiental,Solicitud):
        self.Capacidad = Capacidad
        self.Peso_Max = Peso_Max
        self.Velocidad = Velocidad
        self.Costo_Viaje = Costo_Viaje
        self.Factor_Ambiental = Factor_Ambiental
        self.Solicitud = Solicitud??

def main():
    # Aqui ejecutas tus soluciones hola
    print(hola_mundo())


# No cambiar a partir de aqui
if __name__ == "__main__":
    main()