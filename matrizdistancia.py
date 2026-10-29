from excepciones import DatoInvalidoError, RutaIncompletaError
from validaciones import Validaciones

class MatrizDistancia:
    def __init__(self):
        self.distancias = {}

    def agregar_distancia(self, id_origen, id_destino, km):
        id_origen, id_destino = Validaciones.validar_str(id_origen, id_destino, nombre = "ubicación")
        Validaciones.validar_numero(km, cero = True, nombre = "distancia")
        if id_origen == id_destino and km != 0:
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

    def serializar(self):
        lista = []
        for (origen, destino), km in self.distancias.items():
            lista.append([origen, destino, km])
        return lista

    @classmethod
    def deserializar(cls, archivo, contexto = None):
        matriz = cls()
        matriz.cargar_matriz(list(map(lambda fila: (fila[0], fila[1], float(fila[2])), filter(None, archivo[1:]))))
        return matriz

