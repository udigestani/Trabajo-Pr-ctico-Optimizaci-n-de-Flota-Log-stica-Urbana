from validaciones import Validaciones
from excepciones import ExcesoPesoError, DatoInvalidoError

class Transporte:
    curr_id = 0
    UNIDAD_IMPACTO = "kg CO₂"
    def __init__(self, peso_max, volumen, velocidad, costo_km, costo_parada, factor_ambiental):
        self.peso_max = Validaciones.validar_numero(peso_max, nombre = "peso_max")
        self.costo_km = Validaciones.validar_numero(costo_km, nombre = "costo_km")
        self.factor_ambiental = Validaciones.validar_numero(factor_ambiental, nombre = "factor_ambiental")
        self.volumen = Validaciones.validar_numero(volumen, nombre = "volumen")
        self.velocidad = Validaciones.validar_numero(velocidad, nombre = "velocidad")
        self.costo_parada = Validaciones.validar_numero(costo_parada, cero = True, nombre = "costo_parada")

        Transporte.curr_id += 1      
        self.id = Transporte.curr_id

    def _validar_carga(self, distancia, peso):
        Validaciones.validar_numero(distancia, cero = True, nombre = "distancia")
        Validaciones.validar_numero(peso, cero = True, nombre = "peso")
        if peso > self.peso_max:
            raise ExcesoPesoError(self.peso_max, peso)

    def calcular_impacto_ambiental(self, distancia, peso):
        self._validar_carga(distancia, peso)
        return self.factor_ambiental * distancia
    
    def getter_id(self):
        return self.id
    
    def getter_peso_max(self):
        return self.peso_max
    
    def getter_volumen(self):
        return self.volumen

    def getter_velocidad(self):
        return self.velocidad

    def getter_costo_km(self):
        return self.costo_km

    def getter_costo_parada(self):
        return self.costo_parada

    def getter_tipo(self):
        return self.__class__.__name__

    def serializar(self):
        return [self.__class__.__name__, self.id, self.peso_max, self.volumen, self.velocidad, self.costo_km, self.costo_parada, self.factor_ambiental]

    @staticmethod
    def deserializar(archivo, contexto = None):
        clases = {"Furgoneta": Furgoneta, "Motocicleta": Motocicleta, "Camion": Camion}
        transportes = []
        for fila in archivo[1:]:
            if fila and fila[0] == "Transporte":
                transporte = Transporte(*map(float, fila[2:8]))
                transporte.id = int(fila[1])
                transportes.append(transporte)
            elif fila and fila[0] in clases:
                clase = clases[fila[0]]
                transporte = clase()
                transporte.id = int(fila[1])
                transportes.append(transporte)
            elif fila:
                raise DatoInvalidoError(f"Tipo de transporte desconocido: {fila[0]}")
        Transporte.curr_id = max(Transporte.curr_id, 0, *map(lambda t: t.id, transportes))
        return transportes

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
        self._validar_carga(distancia, peso)
        return (self.factor_ambiental + peso/10000)*distancia

