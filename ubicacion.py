class Ubicacion:
    curr_id = 0                 
    def __init__(self, descripcion, latitud, longitud):
        self.descripcion = descripcion
        self.latitud, self.longitud = self.validar_coordenada(latitud, longitud)
        Ubicacion.curr_id += 1      
        self.id = Ubicacion.curr_id


    @staticmethod
    def validar_descripcion(cadena):
        if isinstance(cadena, str):
            if cadena:
                return cadena
            raise ValueError(f"La descripcion {cadena} no debe estar vacia")
        raise TypeError(f"La descripcion {cadena} debe ser una cadena str")

    @staticmethod
    def validar_coordenada(latitud, longitud):
        if not isinstance(latitud, (int, float)):
            raise TypeError(f"La latitud {latitud} debe ser un número")
        if not isinstance(longitud, (int, float)):
            raise TypeError(f"La longitud {longitud} debe ser un número")
        if latitud < -90 or latitud > 90:
            raise ValueError(f"La latitud {latitud} debe estar entre -90° y 90°")
        if longitud < -180 or longitud > 180:
            raise ValueError(f"La longitud {longitud} debe estar entre -180° y 180°")
        return latitud, longitud
        