from validaciones import Validaciones
from solicitud import Solicitud
from matrizdistancia import MatrizDistancia
from datetime import datetime

class PoliticaOrdenamiento:
    @staticmethod
    def sugerir_orden(deposito, solicitudes, matriz):
        raise NotImplementedError("Las subclases deben implementar sugerir_orden")


class Vecinos(PoliticaOrdenamiento):
    @staticmethod
    def sugerir_orden(deposito, solicitudes, matriz):
        pendientes = list(solicitudes)
        orden = []
        actual = deposito
        while pendientes:
            siguiente = min(
                pendientes,
                key=lambda s: matriz.obtener_distancia(actual, s.getter_destino())
            )
            orden.append(siguiente)
            actual = siguiente.getter_destino()
            pendientes.remove(siguiente)
        return orden


class VentanasTiempo(PoliticaOrdenamiento):
    @staticmethod
    def sugerir_orden(deposito, solicitudes, matriz):
        Validaciones.validar_str(deposito, nombre = "deposito")
        Validaciones.validar_coleccion(solicitudes, tipo = tuple, clase = Solicitud, vacia = True, nombre = "solicitudes")
        Validaciones.validar_coleccion(map(lambda s: s.getter_ventana_inicio(),solicitudes), clase = datetime, vacia = True, nombre = "ventanas")
        Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")
        return sorted(solicitudes, key=lambda s: s.getter_ventana_inicio())