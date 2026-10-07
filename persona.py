from viaje import Viaje
from solicitud import Solicitud
from datetime import datetime 
from transporte import Transporte
from excepciones import DatoInvalidoError, ExcesoPesoError, ExcesoVolumenError, EstadoInvalidoError, VentanaIncumplidaError, DNIInvalidoError

class Persona:
    dnis_registrados = {}
    def __init__(self, nombre, dni, telefono):
        self.nombre = self.validar_nombre(nombre)
        self.dni = self.validar_dni(dni)
        self.telefono = self.validar_telefono(telefono)
        Persona.dnis_registrados[self.dni] = self

    @classmethod
    def validar_dni(cls, dni):
        if isinstance(dni, int) and (len(str(dni)) == 8 or len(str(dni)) == 7) and dni > 0:
            if dni in cls.dnis_registrados:
                raise DNIInvalidoError(dni)
            return dni
        raise DatoInvalidoError(f"El DNI {dni} debe ser un número entero positivo de 8 dígitos")

    @staticmethod
    def validar_telefono(telefono):
        if isinstance(telefono, int) and len(str(telefono)) == 10 and telefono > 0:
            return telefono
        raise DatoInvalidoError(f"El teléfono {telefono} debe ser un número entero positivo de 10 dígitos")

    @staticmethod
    def validar_nombre(nombre):
        if isinstance(nombre, str) and len(nombre.strip()) > 0:
            return nombre
        raise DatoInvalidoError(f"El nombre {nombre} debe ser una cadena de caracteres no vacía")

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
        if not isinstance(viaje, Viaje):
            raise DatoInvalidoError(f"El viaje debe ser un objeto de clase Viaje")
        return viaje.crear_solicitud(destino, ventana_inicio, ventana_fin, *articulos)
