from viaje import Viaje
from solicitud import Solicitud
from datetime import datetime 
from transporte import Transporte

class Persona:
    dnis_registrados = []
    def __init__(self, nombre, dni, telefono):
        self.nombre = self.validar_nombre(nombre)
        self.dni = self.validar_dni(dni)
        self.telefono = self.validar_telefono(telefono)

    @classmethod
    def validar_dni(cls, dni):
        if isinstance(dni, int) and len(str(dni)) == 8:
            if dni in cls.dnis_registrados:
                raise ValueError(f"El DNI {dni} ya está registrado")
            cls.dnis_registrados.append(dni)
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
        

    def crear_viaje(self, transporte, deposito, horario, matriz):
        viaje = Viaje(transporte, deposito, horario, matriz)
        return viaje

class Solicitante(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)

    @staticmethod
    def crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, **articulos):
        if viaje.estado != "PLANIFICADO":
            raise ValueError(f"No se pueden agregar solicitudes a un viaje ya iniciado o terminado")
        peso = viaje.peso_total
        volumen = viaje.volumen_total
        for articulo in articulos.values():
            peso += articulo.getter_peso()
            volumen += articulo.getter_volumen()
        if peso > viaje.transporte.peso_max:
            raise ValueError(f"El peso total de la solicitud ({peso}) excede el peso máximo del transporte ({viaje.transporte.peso_max})")
        elif volumen > viaje.transporte.volumen:
            raise ValueError(f"El volumen total de la solicitud ({volumen}) excede el volumen máximo del transporte ({viaje.transporte.volumen})")
        articulos = list(articulos.values())
        nueva_solicitud = Solicitud(articulos, destino, ventana_inicio, ventana_fin)
        if not viaje.validar_recorrido(viaje.solicitudes + [nueva_solicitud]):
            raise ValueError(f"La solicitud no cumple con las ventanas horarias")
        viaje.peso_total = peso
        viaje.volumen_total = volumen
        viaje.solicitudes.append(nueva_solicitud)
        return nueva_solicitud


    
# moto = Transporte("Moto", 100, 1)
# juan=Administrador("Juan Perez", 12345678, 1234567890)
# viaje = Administrador.crear_viaje(juan, moto, "Deposito1", datetime(2023, 6, 1, 10, 0, 0))
# print(viaje.horario)
        
        
