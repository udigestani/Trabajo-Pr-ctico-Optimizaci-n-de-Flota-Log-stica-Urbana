from viaje import Viaje
from validaciones import Validaciones
from excepciones import DatoInvalidoError

class Persona:
    dnis_registrados = set()
    def __init__(self, nombre, dni, telefono):
        self.nombre = Validaciones.validar_str(nombre, nombre = "nombre")
        self.dni = Validaciones.validar_dni(dni, Persona.dnis_registrados)
        self.telefono = Validaciones.validar_digitos(telefono, 10, "teléfono")
        Persona.dnis_registrados.add(self.dni)

    def getter_nombre(self):
        return self.nombre
    def getter_dni(self):
        return self.dni
    def getter_telefono(self):
        return self.telefono

    @classmethod
    def getter_dnis_registrados(cls):
        return cls.dnis_registrados.copy()
    @classmethod
    def limpiar_dnis_registrados(cls):
        cls.dnis_registrados.clear()
        return None

    def __str__(self):
        return f"Persona de nombre {self.nombre} y DNI: {self.dni}"
    def __repr__(self):
        return f"<Persona {self.nombre} - {self.dni}>"
    def __eq__(self, other):
        if not isinstance(other, Persona):
            return False
        return self.dni == other.getter_dni()
    def __hash__(self):
        return hash(self.dni)    

    def serializar(self):
        return [self.__class__.__name__, self.nombre, self.dni, self.telefono]

    @staticmethod
    def deserializar(archivo, contexto = None):
        clases = {"Persona": Persona, "Administrador": Administrador, "Solicitante": Solicitante}
        personas = []
        for fila in archivo[1:]:
            if fila and fila[0] in clases:
                cls = clases[fila[0]]
                personas.append(cls(fila[1], int(fila[2]), int(fila[3])))
            elif fila and fila[0] not in clases:
                raise DatoInvalidoError(f"Clase de persona desconocida: {fila[0]}")
        return personas

class Administrador(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)
        

    def crear_viaje(self, transporte, deposito, horario, matriz):
        viaje = Viaje(transporte, deposito, horario, matriz)
        return viaje

class Solicitante(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)

    @staticmethod
    def crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, *articulos):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        return viaje.crear_solicitud(destino, ventana_inicio, ventana_fin, *articulos)
