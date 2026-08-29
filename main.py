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

    def setter_generar_viaje(self, transporte, deposito, horario, estado):
        if self.estado == "pendiente":
            self.viaje = Viaje(transporte, deposito,horario, estado)
            self.estado = "realizada"
            return self.viaje    
    def calcular_peso_total(self):
        total = 0
        for articulo in self.articulos:
            total += articulo.peso
        return total

class Articulo:
    curr_id = 0
    def __init__(self, solicitud, peso, volumen):
        self.solicitud = solicitud
        self.peso = peso
        self.volumen = volumen
        Articulo.curr_id += 1
        self.id = Articulo.curr_id

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, estado):
        # self.transporte = transporte??
        self.deposito = deposito
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
    # aca lo que pense es primero ver cuanto pesa, despues con el peso ver cual de las tres opciones puede llevar ese peso. De ahi elegimos el tipo con un setter. El tema tmb es que el peso se calcula multiplicando el atributo peso de la clase articulo y sumando todos los articulos. Entonces tenemso que hacer un getter y un quilombito mas. Todo eso para setear el tipo de vehiculo. no? que opinan? dsp la velocidad la podemos calcular. entonces no se pasa como un atributo. Ahora lo saco 
    def setter_Transporte(self,peso, costo_viaje):
        if peso>=1000:
            tipo="Camion"
            factor_ambiental=1.5
        elif peso<1000 and peso>500:
            tipo="Furgoneta"
            factor_ambiental=1.0
        else:
            tipo="Moto"
            factor_ambiental=0.5
        self.transporte = Transporte( peso, costo_viaje, factor_ambiental, tipo)
        return self.transporte

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
    # aca tenemos que ver como lo hacmos. lo que estoy pensando es que la velocidad, el costo de viaje y el factor hambiental son cosas que dependen de que se uso para el viaje. Todas esas cosas se caclulan dependiendo el tipo de auto qeu usamos. Entonces tendrian que empezar como cero? y dsp las cambiamos? o directamente no se pasan como parametros?    
    def __init__(self, peso,costo_viaje, factor_ambiental,tipo):
        self.peso_max = peso
        self.costo_viaje = costo_viaje
        self.factor_ambiental = factor_ambiental
        self.Tipo = tipo

        Transporte.curr_id += 1      
        self.id = Transporte.curr_id         
        
    

def main():
    # Aqui ejecutas tus soluciones hola
    print(hola_mundo())
   

# No cambiar a partir de aqui
if __name__ == "__main__":
    main()

solicitud1 = Solicitud(["articulo1", "articulo2"], "ubicacion1", "ubicacion2", "10:00", "pendiente")
solicitud1.generar_comprobante("2023-06-01 10:00", 100.0, "receptor1")
print(solicitud1.comprobante.id)
print(solicitud1.horario) 
