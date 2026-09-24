from comprobante import Comprobante
from articulo import Articulo
from datetime import datetime
from excepciones import DatoInvalidoError, VentanaInvalidaError

class Solicitud:
    curr_id = 0
    def __init__(self, articulos, destino, ventana_inicio, ventana_fin):
        self.articulos = self.validar_articulos(articulos)
        self.destino = self.validar_ubicacion(destino)
        self.ventana_inicio, self.ventana_fin = self.validar_ventana_horaria(ventana_inicio, ventana_fin) # hice esta validacion y cambie que los parametroz sea ventana_inicio y ventana_fin, asumiendo que entran 2 parametros y no como una tupla de ultima lo cambiamos dsp tipo antes habia ventana horaria, entonces deberia ser tipo ventana_horaria = (ventana_inicio, ventana_fin), pero queda mas prolijo asi
        self.viaje = None
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self,fecha_Hora, receptor, monto):
        self.comprobante = Comprobante(self, fecha_Hora, receptor, monto)
        return self.comprobante
                  
    # def calcular_peso(self):
    #     total = 0
    #     for articulo in self.articulos:
    #         total += articulo.getter_peso()
    #     return total

    # def calcular_volumen(self):
    #     total = 0
    #     for articulo in self.articulos:
    #         total += articulo.getter_volumen()
    #     return total
    
    @staticmethod
    def validar_ubicacion(ubicacion):
        if isinstance(ubicacion, str):
            if not ubicacion.strip():
                raise DatoInvalidoError(f"La ubicación debe ser no vacía")
            return ubicacion
        raise TypeError(f"La ubicacion debe ser una cadena str")

    @staticmethod
    def validar_articulos(articulos):
        if isinstance(articulos, list): #creo que es isinstance(articulos, list):
            if len(articulos) == 0:
                raise DatoInvalidoError(f"La solicitud debe contener por lo menos un artículo")
            for articulo in articulos:
                if not isinstance(articulo, Articulo):
                    raise TypeError(f"La lista de articulos {articulos} contiene un articulo {articulo} no válido")
            return articulos
        raise TypeError(f"La lista de articulos {articulos} debe ser una lista")

    @staticmethod
    def validar_ventana_horaria(ventana_inicio, ventana_fin):
        if not isinstance(ventana_inicio, datetime) or not isinstance(ventana_fin, datetime):
            raise TypeError("La ventana horaria debe estar compuesta por objetos datetime")
        if ventana_inicio > ventana_fin:
            raise VentanaInvalidaError(ventana_inicio, ventana_fin)
        else:
            return ventana_inicio, ventana_fin
    def __str__(self):
        return f"Solicitud {self.id} hacia {self.destino} (Ventana: {self.ventana_inicio.strftime('%H:%M')}-{self.ventana_fin.strftime('%H:%M')})"

    def __repr__(self):
        return f"<Solicitud {self.id} -> {self.destino}>"

    def __eq__(self, otro):
        if isinstance(otro, Solicitud):
            return self.id == otro.id
        return False

    def getter_articulos(self):
        return self.articulos


# art1 = Articulo("Maquinaria", 200, 4)
# art2 = Articulo("Maquinaria", 150, 3.5)


# solicitud = Solicitud([art1,art2,art2,art1,art2], ubi1, datetime(2023, 6, 1, 10, 0), datetime(2023, 6, 1, 13, 0))
# print(solicitud.calcular_peso(), solicitud.calcular_volumen())
# solicitud1 = Solicitud([art2], datetime(2023, 6, 1, 10, 0), datetime(2023, 6, 1, 12, 0))
# print(solicitud1.calcular_peso(), solicitud1.calcular_volumen())
# solicitud.generar_comprobante(datetime(2023, 6, 1, 10, 0), "Juan Perez", 1500)
# print(solicitud.comprobante.id, solicitud.comprobante.fecha_Hora, solicitud.comprobante.receptor, solicitud.comprobante.monto)
