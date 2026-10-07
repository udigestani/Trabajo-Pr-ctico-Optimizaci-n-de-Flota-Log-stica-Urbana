from excepciones import DatoInvalidoError
from math import isfinite

class Transporte:
    curr_id = 0
    def __init__(self, peso_max, volumen, velocidad, costo_km, costo_parada, factor_ambiental):
        self.peso_max = self.validar_positivo(peso_max)
        self.costo_km = self.validar_positivo(costo_km)
        self.factor_ambiental = self.validar_positivo(factor_ambiental)
        self.volumen = self.validar_positivo(volumen)
        self.velocidad = self.validar_positivo(velocidad)
        self.costo_parada = self.validar_positivo(costo_parada)

        Transporte.curr_id += 1      
        self.id = Transporte.curr_id

    @staticmethod
    def validar_positivo(numero):
        if isinstance(numero, (int, float)) and not isinstance(numero, bool) and isfinite(numero) and numero > 0:
            return numero
        raise DatoInvalidoError(f"Los valores de instancia del transporte deben ser positivos")
        

    def calcular_impacto_ambiental(self, distancia, peso):
        return self.factor_ambiental * distancia
    
    def getter_peso_max(self):
        return self.peso_max
    
    def getter_volumen(self):
        return self.volumen

    def getter_velocidad(self):
        return self.velocidad

    def getter_tipo(self):
        return self.__class__.__name__

    def __str__(self):
        return f"{self.__class__.__name__} {self.id} (Max: {self.peso_max}kg, {self.volumen}m³)"
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.id}>"
    
class Furgoneta(Transporte):
    PESO_MAX = 500
    VOLUMEN = 8
    VELOCIDAD = 30
    COSTO_KM = 2
    COSTO_PARADA = 5
    FACTOR_AMBIENTAL = 0.27

    def __init__(self):
        super().__init__(
            self.PESO_MAX, 
            self.VOLUMEN, 
            self.VELOCIDAD, 
            self.COSTO_KM, 
            self.COSTO_PARADA, 
            self.FACTOR_AMBIENTAL
        )

class Motocicleta(Transporte):
    PESO_MAX = 40
    VOLUMEN = 1
    VELOCIDAD = 45
    COSTO_KM = 1
    COSTO_PARADA = 3
    FACTOR_AMBIENTAL = 0.27

    def __init__(self):
        super().__init__(
            self.PESO_MAX, 
            self.VOLUMEN, 
            self.VELOCIDAD, 
            self.COSTO_KM, 
            self.COSTO_PARADA, 
            self.FACTOR_AMBIENTAL
        )

class Camion(Transporte):
    PESO_MAX = 1500
    VOLUMEN = 20
    VELOCIDAD = 25
    COSTO_KM = 3.5
    COSTO_PARADA = 10
    FACTOR_AMBIENTAL = 1

    def __init__(self):
        super().__init__(
            self.PESO_MAX, 
            self.VOLUMEN, 
            self.VELOCIDAD, 
            self.COSTO_KM, 
            self.COSTO_PARADA, 
            self.FACTOR_AMBIENTAL
        )

    def calcular_impacto_ambiental(self, distancia, peso):
        return (self.factor_ambiental + peso/10000)*distancia

