from comprobante import Comprobante
from articulo import Articulo
from datetime import datetime
from excepciones import DatoInvalidoError, VentanaInvalidaError, EstadoInvalidoError

class Solicitud:
    curr_id = 0
    def __init__(self, destino, ventana_inicio, ventana_fin, *articulos):
        self.articulos = self.validar_articulos(articulos)
        self.destino = self.validar_ubicacion(destino)
        self.ventana_inicio, self.ventana_fin = self.validar_ventana_horaria(ventana_inicio, ventana_fin) # hice esta validacion y cambie que los parametroz sea ventana_inicio y ventana_fin, asumiendo que entran 2 parametros y no como una tupla de ultima lo cambiamos dsp tipo antes habia ventana horaria, entonces deberia ser tipo ventana_horaria = (ventana_inicio, ventana_fin), pero queda mas prolijo asi
        self.viaje = None
        self.comprobante = None
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, receptor, monto):
        if self.comprobante:
            raise EstadoInvalidoError("generar_comprobante", "ya tiene comprobante")
        self.comprobante = Comprobante(self, fecha_Hora, receptor, monto)
        return self.comprobante
    
    @staticmethod
    def validar_ubicacion(ubicacion):
        if isinstance(ubicacion, str):
            if not ubicacion.strip():
                raise DatoInvalidoError(f"La ubicación debe ser no vacía")
            return ubicacion
        raise TypeError(f"La ubicacion debe ser una cadena str")

    @staticmethod
    def validar_articulos(articulos):
        if isinstance(articulos, tuple):
            if len(articulos) == 0:
                raise DatoInvalidoError(f"La solicitud debe contener por lo menos un artículo")
            for articulo in articulos:
                if not isinstance(articulo, Articulo):
                    raise TypeError(f"La lista de articulos {articulos} contiene un articulo {articulo} no válido")
            return articulos
        raise TypeError(f"Los articulos {articulos} deben ser una tupla")

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
            return self.id == otro.getter_id()
        return False
    def __hash__(self):
        return hash(self.id)

    def getter_articulos(self):
        return self.articulos
    def getter_id(self):
        return self.id
    def getter_destino(self):
        return self.destino
    def getter_ventana_inicio(self):
        return self.ventana_inicio
    def getter_ventana_fin(self):
        return self.ventana_fin
    def getter_viaje(self):
        return self.viaje
    def setter_viaje(self, viaje):
        self.viaje = viaje
        return None
    def getter_comprobante(self):
        return self.comprobante
    def setter_comprobante(self, comprobante):
        self.comprobante = comprobante
        return None