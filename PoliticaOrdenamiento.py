class PoliticaOrdenamiento:
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pass

class Vecinos(PoliticaOrdenamiento):
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pendientes = list(solicitudes)
        orden = []
        id_actual = deposito.id
        while len(pendientes) > 0:
            siguiente = min(
                pendientes,
                key = lambda x: matriz.obtener_distancia(id_actual, x.destino.id)
            )
            orden.append(siguiente)
            id_actual = siguiente.destino.id
            pendientes.remove(siguiente)
        return orden

class VentanasTiempo(PoliticaOrdenamiento):
    def sugerir_orden(self, deposito, solicitudes, matriz):
        return sorted(solicitudes, key=lambda s: s.ventana_inicio)