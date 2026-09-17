class MatrizDistancia:
    def __init__(self):
        self.distancias = {}

    def agregar_distancia(self, id_origen, id_destino, km):
        if not isinstance(km, (int, float)):
            raise TypeError(f"La distancia {km} debe ser un int o un float")
        if km < 0:
            raise ValueError(f"La distancia {km} no puede ser negativa, solo nula o positiva")
        else:
            self.distancias[(id_origen, id_destino)] = km

    def cargar_matriz(self, lista_tramos):
        for id_origen, id_destino, km in lista_tramos:
            self.agregar_distancia(id_origen, id_destino, km)

    def obtener_distancia(self, id_origen, id_destino):
        if id_origen == id_destino:
            return 0
        if (id_origen, id_destino) in self.distancias:
            return self.distancias[(id_origen, id_destino)]
        else:
            raise ValueError(f"No existe distancia registrada de {id_origen} a {id_destino}")

    