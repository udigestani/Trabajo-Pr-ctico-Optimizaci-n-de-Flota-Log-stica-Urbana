from datetime import datetime
from comprobante import Comprobante
from articulo import Articulo
from excepciones import EstadoInvalidoError, DatoInvalidoError
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
    
    def serializar(self):
        if self.viaje:
            id_viaje = self.viaje.getter_id()
        else:
            id_viaje = ""
        if self.comprobante:
            id_comprobante = self.comprobante.getter_id()
        else:
            id_comprobante = ""
        return [self.id, self.destino, self.ventana_inicio, self.ventana_fin, ",".join(map(lambda x: str(x.getter_id()), self.articulos)), id_viaje, id_comprobante]

    @classmethod
    def deserializar(cls, archivo, contexto):
        # Dicc {id: art}
        dicc_articulos = dict(map(lambda art: (art.getter_id(), art), contexto[Articulo]))
        # Deserializamos las solicitudes
        solicitudes = []
        for fila in archivo[1:]:
            if fila:
                if not fila[4]:
                    raise DatoInvalidoError("La solicitud debe tener al menos un artículo")
                articulos = map(lambda id: dicc_articulos[int(id)], fila[4].split(","))
                solicitud = cls(fila[1], datetime.fromisoformat(fila[2]), datetime.fromisoformat(fila[3]), *articulos)
                solicitud.id = int(fila[0])
                solicitudes.append(solicitud)
        cls.curr_id = max(cls.curr_id, 0, *map(lambda s: s.id, solicitudes))
        return solicitudes

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
    def getter_peso(self):
        return sum(map(lambda art: art.getter_peso(), self.articulos))
    def getter_volumen(self):
        return sum(map(lambda art: art.getter_volumen(), self.articulos))
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
        from viaje import Viaje
        if not (viaje is None or isinstance(viaje, Viaje)):
            raise DatoInvalidoError(f"El viaje {viaje} debe ser de clase Viaje o None")
        self.viaje = viaje 
        return None
    def getter_comprobante(self):
        return self.comprobante
    def setter_comprobante(self, comprobante):
        if self.comprobante:
            raise EstadoInvalidoError("generar_comprobante", "la solicitud ya tiene comprobante")
        if not (comprobante is None or isinstance(comprobante, Comprobante)):
            raise DatoInvalidoError("El comprobante debe ser de clase Comprobante o None")
        self.comprobante = comprobante
        return None
    def esta_entregada(self):
        return self.comprobante is not None
    def esta_asignada(self):
        return self.viaje is not None and self.viaje.getter_estado() in {"EN_CURSO", "PLANIFICADO"}