from solicitud import solicitud 

class Cliente:
     
    def __init__(self, nombre: str, dni: int, edad: int):
        self.historial = []
        self.nombre = nombre
        self.dni = self.validar_numero(dni)
        self.edad = self.validar_edad(edad)

    @staticmethod
    def validar_edad(numero):
        if isinstance(numero, int):
            if numero > 0:
                return numero
            raise ValueError(f"El número {numero} debe ser mayor a 0")
        raise TypeError(f"El número {numero} debe ser un número")

    @staticmethod
    def validar_dni(numero):
        if isinstance(numero, int):
            if numero > 0:
                return numero
            raise ValueError(f"El número {numero} debe ser mayor a 0")
        raise TypeError(f"El número {numero} debe ser un número")
    #HAY QUE VALIDAR QUE NO REPITA

    @staticmethod
    def validar_nombre(nombre):
        if isinstance(nombre, str):
            if nombre:
                return nombre
            raise ValueError(f"El nombre no puede ser vacío")
        raise TypeError(f"El nombre {nombre} debe ser una cadena str")
    
   
    def crear_solicitud(self,articulos, ubi_ini , destino, ventana_inicio, ventana_fin, estado):
        self.solicitud= solicitud(articulos, ubi_ini , destino, ventana_inicio, ventana_fin, estado)
        return self.solicitud
