class PoliticaOrdenamiento:
    def sugerir_orden(self, deposito, solicitudes, matriz):
        raise NotImplementedError("Las subclases deben implementar sugerir_orden")


class Vecinos(PoliticaOrdenamiento):
    def sugerir_orden(self, deposito, solicitudes, matriz):
        pendientes = list(solicitudes)
        orden = []
        actual = deposito
        while pendientes:
            siguiente = min(
                pendientes,
                key=lambda s: matriz.obtener_distancia(actual, s.destino)
            )
            orden.append(siguiente)
            actual = siguiente.destino
            pendientes.remove(siguiente)
        return orden


class VentanasTiempo(PoliticaOrdenamiento):
    def sugerir_orden(self, deposito, solicitudes, matriz):
        return sorted(solicitudes, key=lambda s: s.ventana_inicio)