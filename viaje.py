from incidente import Incidente 
from transporte import Transporte
from datetime import datetime, timedelta
from solicitud import Solicitud

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, estado = "PLANIFICADO"):
        # Dice que hay que tomar en cuenta las solicitudes. Habría que agregarlo por acá me parece
        self.transporte = self.validar_transporte(transporte)
        self.deposito = self.validar_deposito(deposito)
        self.horario = self.validar_horario(horario)
        self.estado = self.validar_estado(estado)

        self.peso_total=0
        self.volumen_total=0
        self.solicitudes = []
        self.incidentes = []
        Viaje.curr_id += 1
        self.id = Viaje.curr_id

    #Quizas lo registra la parada
    def registrar_incidente(self, tipo, fecha, descripcion):
        incidente = Incidente(tipo, fecha, descripcion)
        self.incidentes.append(incidente)
        return incidente
    
    def agregar_solicitud(self, articulos, destino, ventana_inicio, ventana_fin): 
        if self.estado != "PLANIFICADO":
            raise ValueError(f"No se pueden agregar solicitudes a un viaje ya iniciado o terminado")
        peso = self.peso_total
        volumen = self.volumen_total
        for articulo in articulos:
            peso += articulo.getter_peso()
            volumen += articulo.getter_volumen()
        if peso > self.transporte.peso_max:
            raise ValueError(f"El peso total de la solicitud ({peso}) excede el peso máximo del transporte ({self.transporte.peso_max})")
        elif volumen > self.transporte.volumen:
            raise ValueError(f"El volumen total de la solicitud ({volumen}) excede el volumen máximo del transporte ({self.transporte.volumen})")

        nueva_solicitud = Solicitud(articulos, destino, ventana_inicio, ventana_fin)
        if not self.validar_recorrido(self.solicitudes + [nueva_solicitud]):
            raise ValueError(f"La solicitud no cumple con las ventanas horarias")
        
        
        self.peso_total = peso
        self.volumen_total = volumen
        self.solicitudes.append(nueva_solicitud)
        return nueva_solicitud

    @staticmethod
    def validar_transporte(transporte):
        if isinstance(transporte, Transporte):
            return transporte
        raise TypeError(f"El transporte {transporte} debe ser de clase trasporte")
    
    # @staticmethod
    # def validar_deposito(deposito):
    #     if isinstance(deposito, Ubicacion):
    #         return deposito
    #     raise TypeError(f"El depósito {deposito} no es una ubicación")

    @staticmethod
    def validar_estado(estado):
        if not isinstance(estado, str):
            raise TypeError(f"El estado del viaje debe ser PLANIFICADO, EN_CURSO o FINALIZADO")
        if estado not in("PLANIFICADO", "EN_CURSO", "FINALIZADO"):
            raise ValueError(f"El estado del viaje debe ser PLANIFICADO, EN_CURSO o FINALIZADO")
        return estado

    @staticmethod
    def validar_horario(horario):
        if not isinstance(horario, datetime):
            raise TypeError("El horario de salida del viaje debe ser un objeto datetime")
        else:
            return horario


    def validar_recorrido(self, recorrido_nuevo):
        horario = self.horario
        ubicacion = self.deposito
        for solicitud in recorrido_nuevo:
            lugar = solicitud.destino
            distancia = self.matriz[ubicacion][lugar]
            tiempo_hrs = distancia / self.transporte.velocidad
            llegada = horario + timedelta(hours=tiempo_hrs)
            if llegada > solicitud.ventana_fin:
                return False
            if llegada < solicitud.ventana_inicio:
                llegada = solicitud.ventana_inicio
            horario = llegada + timedelta(minutes=10)
            ubicacion = lugar
        distancia = self.matriz[ubicacion]["Deposito"]
        tiempo_hrs = distancia / self.transporte.velocidad
        llegada = horario + timedelta(hours=tiempo_hrs)
        return True


# matriz = {
#         "Deposito": {"Ubic1": 15, "Ubic2":20, "Ubic3":18},
#         "Ubic1": {"Deposito": 15, "Ubic2":10, "Ubic3":12},
#         "Ubic2": {"Deposito": 20, "Ubic1":10, "Ubic3":14},
#         "Ubic3": {"Deposito": 18, "Ubic1":12, "Ubic2":14}
#     }



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
    