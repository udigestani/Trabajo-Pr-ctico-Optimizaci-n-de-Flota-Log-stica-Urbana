from incidente import Incidente
from parada import Parada
from transporte import Transporte

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

    #Quizas lo registra la parada
    def registrar_incidente(self, tipo, fecha, descripcion):
        self.incidente = Incidente(tipo, fecha, descripcion)
        return self.incidente
    
    def agregar_parada(self, orden, hora_prev, hora_real, ubicacion):
        parada = Parada(orden, hora_prev, hora_real, ubicacion)
        self.paradas.append(parada)
        return parada

    #Fuera de alcance la asignación de flota??
    # # aca lo que pense es primero ver cuanto pesa, despues con el peso ver cual de las tres opciones puede llevar ese peso. De ahi elegimos el tipo con un setter. El tema tmb es que el peso se calcula multiplicando el atributo peso de la clase articulo y sumando todos los articulos. Entonces tenemso que hacer un getter y un quilombito mas. Todo eso para setear el tipo de vehiculo. no? que opinan? dsp la velocidad la podemos calcular. entonces no se pasa como un atributo. Ahora lo saco 
    # def setter_Transporte(self,peso, costo_viaje):
    #     if peso>=1000:
    #         self.transporte = "Camion"
    #         factor_ambiental=1.5
    #     elif peso<1000 and peso>500:
    #         self.transporte ="Furgoneta"
    #         factor_ambiental=1.0
    #     else:
    #         self.transporte ="Moto"
    #         factor_ambiental=0.5
    #     self.transporte = Transporte( peso, costo_viaje, factor_ambiental, tipo)
    #     return self.transporte
    