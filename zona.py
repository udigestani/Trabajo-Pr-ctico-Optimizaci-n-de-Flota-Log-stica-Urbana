from validaciones import Validaciones

class Zona:
    curr_id = 0
    def __init__(self, nombre, ubicaciones = ()):
        self.nombre = Validaciones.validar_str(nombre, nombre = "nombre de la zona")
        self.ubicaciones = set()
        for ubicacion in ubicaciones:
            self.agregar_ubicacion(ubicacion)

        Zona.curr_id += 1
        self.id = Zona.curr_id

    def agregar_ubicacion(self, ubicacion):
        self.ubicaciones.add(Validaciones.validar_str(ubicacion, nombre = "ubicación de la zona"))
        return None

    def contiene(self, ubicacion):
        return ubicacion in self.ubicaciones

    def getter_id(self):
        return self.id
    def getter_nombre(self):
        return self.nombre
    def getter_ubicaciones(self):
        return self.ubicaciones.copy()

    def serializar(self):
        return [self.id, self.nombre, "|".join(sorted(self.ubicaciones))]

    @classmethod
    def deserializar(cls, archivo, contexto = None):
        zonas = []
        for fila in archivo[1:]:
            if fila:
                zona = cls(fila[1], filter(None, fila[2].split("|")))
                zona.id = int(fila[0])
                zonas.append(zona)
        cls.curr_id = max(cls.curr_id, 0, *map(lambda z: z.id, zonas))
        return zonas

    def _clave(self):
        return self.nombre.lower()

    def __eq__(self, otra):
        if isinstance(otra, Zona):
            return self._clave() == otra._clave()
        return False
    def __hash__(self):
        return hash(self._clave())
    def __str__(self):
        return self.nombre
    def __repr__(self):
        return f"<Zona {self.id} {self.nombre}>"
