from incidente import Incidente
from parada import Parada
from ubicacion import Ubicacion
from transporte import Transporte

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, estado = "PLANIFICADO"):
        # Dice que hay que tomar en cuenta las solicitudes. Habría que agregarlo por acá me parece
        # self.transporte = validar_transporte(transporte)
        self.deposito = self.validar_deposito(deposito)
        self.horario = horario
        self.estado = self.validar_estado(estado)

        self.paradas = []
        self.incidentes = []
        Viaje.curr_id += 1
        self.id = Viaje.curr_id

    #Quizas lo registra la parada
    def registrar_incidente(self, tipo, fecha, descripcion):
        incidente = Incidente(tipo, fecha, descripcion)
        self.incidentes.append(incidente)
        return incidente
    
    def agregar_parada(self, orden, hora_prev, hora_real, ubicacion):
        parada = Parada(orden, hora_prev, hora_real, ubicacion)
        self.paradas.append(parada)
        return parada

    # @staticmethod
    # def validar_transporte(transporte):
    #     if isinstance(transporte, Transporte):
    #         return transporte
    #     raise TypeError(f"El transporte {transporte} debe ser de clase trasporte")
    
    @staticmethod
    def validar_deposito(deposito):
        if isinstance(deposito, Ubicacion):
            return deposito
        raise TypeError(f"El depósito {deposito} no es una ubicación")

    @staticmethod
    def validar_estado(estado):
        if not isinstance(estado, str):
            raise TypeError(f"El estado del viaje debe ser PLANIFICADO, EN_CURSO o FINALIZADO")
        if estado not in("PLANIFICADO", "EN_CURSO", "FINALIZADO"):
            raise ValueError(f"El estado del viaje debe ser PLANIFICADO, EN_CURSO o FINALIZADO")
        return estado

    # @staticmethod
    # def validar_horario(horario):     #???





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
    