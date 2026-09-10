from viaje import Viaje
from solicitud import Solicitud
from datetime import datetime 
from transporte import Transporte

class Persona:
    def __init__(self, nombre, dni, telefono):
        self.nombre = nombre
        self.dni = dni
        self.telefono = telefono

    @staticmethod
    def validar_dni(dni):
        if isinstance(dni, int) and len(str(dni)) == 8:
            return dni
        raise ValueError(f"El DNI {dni} debe ser un número entero de 8 dígitos")

    @staticmethod
    def validar_telefono(telefono):
        if isinstance(telefono, int) and len(str(telefono)) == 10:
            return telefono
        raise ValueError(f"El teléfono {telefono} debe ser un número entero de 10 dígitos")

    @staticmethod
    def validar_nombre(nombre):
        if isinstance(nombre, str) and len(nombre) > 0:
            return nombre
        raise ValueError(f"El nombre {nombre} debe ser una cadena de caracteres no vacía")

class Administrador(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)
        

    def crear_viaje(self, transporte, deposito, horario):
        viaje = Viaje(transporte, deposito, horario)
        return viaje

class Solicitante(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)

    def crear_solicitud(self, articulos, destino, ventana_inicio, ventana_fin):
        solicitud = Solicitud(articulos, destino, ventana_inicio, ventana_fin)
        return solicitud
    
moto=Transporte("Moto", 100, 1)
juan=Administrador("Juan Perez", 12345678, 1234567890)
viaje = Administrador.crear_viaje(juan, moto, "Deposito1", datetime(2023, 6, 1, 10, 0, 0))
print(viaje.horario)