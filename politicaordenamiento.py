from validaciones import Validaciones
from solicitud import Solicitud
from matrizdistancia import MatrizDistancia
from datetime import datetime
from excepciones import RutaIncompletaError

class PoliticaOrdenamiento:
    @staticmethod
    def sugerir_orden(deposito, solicitudes, matriz):
        raise NotImplementedError("Las subclases deben implementar sugerir_orden")


class Vecinos(PoliticaOrdenamiento):
    @staticmethod
    def sugerir_orden(deposito, solicitudes, matriz):
        Validaciones.validar_str(deposito, nombre = "deposito")
        Validaciones.validar_coleccion(solicitudes, tipo = list, clase = Solicitud, vacia = True, nombre = "solicitudes")
        Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")
        Validaciones.validar_coleccion(matriz.getter_distancias().values(), clase = (int, float), vacia = True, nombre = "distancias")
        Validaciones.validar_coleccion(map(lambda s:s.getter_destino(), solicitudes), clase = str, vacia = True, nombre = "destinos")
        pendientes = list(solicitudes)
        orden = []
        actual = deposito
        while pendientes:
            alcanzables = []
            for s in pendientes:
                try:
                    matriz.obtener_distancia(actual, s.getter_destino())
                    alcanzables.append(s)
                except RutaIncompletaError as errorConMensaje:
                    error = errorConMensaje
            if not alcanzables:
                raise error
            siguiente = min(alcanzables, key=lambda s: matriz.obtener_distancia(actual, s.getter_destino()))
            orden.append(siguiente)
            actual = siguiente.getter_destino()
            pendientes.remove(siguiente)
        return orden


class VentanasTiempo(PoliticaOrdenamiento):
    @staticmethod
    def sugerir_orden(deposito, solicitudes, matriz):
        Validaciones.validar_str(deposito, nombre = "deposito")
        Validaciones.validar_coleccion(solicitudes, tipo = list, clase = Solicitud, vacia = True, nombre = "solicitudes")
        Validaciones.validar_coleccion(map(lambda s: s.getter_ventana_inicio(),solicitudes), clase = datetime, vacia = True, nombre = "ventanas")
        Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")
        return sorted(solicitudes, key=lambda s: s.getter_ventana_inicio())