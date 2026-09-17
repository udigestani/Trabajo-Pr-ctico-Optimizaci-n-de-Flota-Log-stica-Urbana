from solicitud import Solicitud

class Cliente:
     
    def __init__(self, nombre: str, dni: int, edad: int):
        self.historial = []
        self.nombre = nombre
        self.dni = self.validar_numero(dni)
        self.edad = self.validar_edad(edad)
    
