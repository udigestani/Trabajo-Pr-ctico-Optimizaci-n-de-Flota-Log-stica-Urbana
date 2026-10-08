from comprobante import Comprobante
from articulo import Articulo
from excepciones import EstadoInvalidoError
from validaciones import Validaciones

class Solicitud:
    curr_id = 0
    def __init__(self, destino, ventana_inicio, ventana_fin, *articulos):
        self.articulos = Validaciones.validar_coleccion(articulos, tipo = tuple, clase = Articulo, nombre = "lista de artículos")
        self.destino = Validaciones.validar_str(destino, nombre = "destino")
        self.ventana_inicio, self.ventana_fin = Validaciones.validar_ventana(ventana_inicio, ventana_fin) # hice esta validacion y cambie que los parametroz sea ventana_inicio y ventana_fin, asumiendo que entran 2 parametros y no como una tupla de ultima lo cambiamos dsp tipo antes habia ventana horaria, entonces deberia ser tipo ventana_horaria = (ventana_inicio, ventana_fin), pero queda mas prolijo asi
        self.viaje = None
        self.comprobante = None
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, receptor, monto):
        if self.comprobante:
            raise EstadoInvalidoError("generar_comprobante", "ya tiene comprobante")
        self.comprobante = Comprobante(self, fecha_Hora, receptor, monto)
        return self.comprobante
    
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