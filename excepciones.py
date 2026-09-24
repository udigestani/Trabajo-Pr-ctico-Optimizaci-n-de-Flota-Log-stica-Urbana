# Definir excepciones propias para datos inválidos, capacidad excedida, ruta incompleta, ventana incumplida y transición ilegal.
class DatoInvalidoError(Exception):
    pass
class ExcesoPesoError(Exception):
    def __init__(self, peso_max, peso_total):
        super().__init__(f"Capacidad excedida: El peso {peso_total} supera el peso máximo del transporte {peso_max}")
class ExcesoVolumenError(Exception):
    def __init__(self, vol_max, vol_total):
        super().__init__(f"Capacidad excedida: El volumen {vol_total} supera el volumen máximo del transporte {vol_max}")
class RutaIncompletaError(Exception):
    def __init__(self, origen, destino):
        super().__init__(f"Ruta incompleta: No existe distancia de {origen} a {destino} ")
class EstadoInvalidoError(Exception):
    def __init__(self, accion, estado):
        super().__init__(f"Estado invalido: No se puede {accion} porque el estado es {estado}")
class VentanaIncumplidaError(Exception):
    def __init__(self, lugar, hora_llegada, hora_fin):
        super().__init__(f"Ventana incumplida: Se llegará a {lugar} a las {hora_llegada} superando el límite {hora_fin}")
class DNIInvalidoError(Exception):
    def __init__(self, dni):
        super().__init__(f"El DNI {dni} ya está registrado")
class VentanaInvalidaError(Exception):
    def __init__(self, inicio, fin):
        super().__init__(f"El inicio de la ventana ({inicio}) debe ser anterior al fin ({fin})")
class ViajeVacioError(Exception):
    pass