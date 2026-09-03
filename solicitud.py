from comprobante import Comprobante
from articulo import Articulo
from ubicacion import Ubicacion

from datetime import time

class Solicitud:
    curr_id = 0
    # Me parece que ubi_ini no va, porque solicitud no va a saber si es la 1° del viaje (sale del deposito), u otra (sale del lugar de la anterior)
    def __init__(self, articulos, ubi_ini , destino, ventana_inicio, ventana_fin, estado):
        self.articulos = self.validar_articulos(articulos)
        # self.ubi_ini = ubi_ini # ?? Va?
        self.destino = self.validar_ubicacion(destino)
        self.ventana_inicio, self.ventana_fin = self.validar_ventana_horaria(ventana_inicio, ventana_fin) # hice esta validacion y cambie que los parametroz sea ventana_inicio y ventana_fin, asumiendo que entran 2 parametros y no como una tupla de ultima lo cambiamos dsp tipo antes habia ventana horaria, entonces deberia ser tipo ventana_horaria = (ventana_inicio, ventana_fin), pero queda mas prolijo asi
        # self.estado = estado       #Me fijé y estado es algo del viaje no de la solicitud. Asumo que es porque la solicitud está lista cuando se genera el comprobante
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, monto, receptor):
        self.comprobante = Comprobante(fecha_Hora, monto, receptor)
        return self.comprobante

    def getter_ubicacion(self):
        return self.ubi_destino

    def setter_generar_viaje(self, transporte, deposito, horario, estado): #No deberia generar el viaje desde solicitud
            if self.estado == "pendiente":
                self.viaje = Viaje(transporte, deposito,horario, estado)
                self.estado = "realizada"
                return self.viaje
            
    def calcular_peso(self):
        total = 0
        for articulo in self.articulos:
            total += articulo.getter_peso()
        return total

    def calcular_volumen(self):
        total = 0
        for articulo in self.articulos:
            total += articulo.getter_volumen()
        return total
    
    @staticmethod
    def validar_ubicacion(ubicacion):
        if ubicacion.isinstance(Ubicacion): #creo que es isinstance(ubicacion, Ubicacion):
            return ubicacion
        raise TypeError(f"La ubicacion debe ser de clase Ubicacion")

    @staticmethod
    def validar_articulos(articulos):
        if articulos.isinstance(list): #creo que es isinstance(articulos, list):
            for articulo in articulos:
                if not isinstance(articulo, Articulo):
                    raise TypeError(f"La lista de articulos {articulos} contiene un articulo {articulo} no válido")
            return articulos
        raise TypeError(f"La lista de articulos {articulos} debe ser una lista")

    @staticmethod
    def validar_ventana_horaria(ventana_inicio, ventana_fin):
        if not isinstance(ventana_inicio, time) or not isinstance(ventana_fin, time):
            raise TypeError("La ventana horaria debe estar compuesta por objetos time")
        if ventana_inicio > ventana_fin:
            raise ValueError("El inicio de la ventana debe ser anterior o igual al fin")
        else:
            return ventana_inicio, ventana_fin





# art1 = Articulo("Maquinaria", 200, 4)
# art2 = Articulo("Maquinaria", 150, 3.5)

# solicitud = Solicitud([art1, art2], "ubi1", "ubi2", "10:00", "")
# print(solicitud.calcular_peso(), solicitud.calcular_volumen())
# solicitud1 = Solicitud(["articulo1", "articulo2"], "ubicacion1", "ubicacion2", "10:00", "pendiente")
# solicitud1.generar_comprobante("2023-06-01 10:00", 100.0, "receptor1")
# print(solicitud1.comprobante.id)
# print(solicitud1.horario) 