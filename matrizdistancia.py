from excepciones import DatoInvalidoError, RutaIncompletaError
from math import isfinite

class MatrizDistancia:
    def __init__(self):
        self.distancias = {}

    def agregar_distancia(self, id_origen, id_destino, km):
        if not isinstance(km, (int, float)) or isinstance(km, bool):
            raise TypeError(f"La distancia {km} debe ser un int o un float")
        if not isfinite(km):
            raise DatoInvalidoError(f"La distancia {km} debe ser un número finito")
        if km < 0:
            raise DatoInvalidoError(f"La distancia {km} no puede ser negativa, solo nula o positiva")
        elif id_origen == id_destino and km != 0:
            self.distancias[(id_origen, id_destino)] = 0
            raise DatoInvalidoError(f"La distancia entre {id_origen} y si mismo debe ser 0")
        else:
            self.distancias[(id_origen, id_destino)] = km

    def cargar_matriz(self, lista_tramos):
        for id_origen, id_destino, km in lista_tramos:
            self.agregar_distancia(id_origen, id_destino, km)

    def obtener_distancia(self, id_origen, id_destino):
        if id_origen == id_destino:
            return 0
        try:
            return self.distancias[(id_origen, id_destino)]
        except KeyError:
            raise RutaIncompletaError(id_origen, id_destino)

    def getter_distancias(self):
        return self.distancias.copy()
    
