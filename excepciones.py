# Definir excepciones propias para datos inválidos, capacidad excedida, ruta incompleta, ventana incumplida y transición ilegal.

class FlotaError(Exception):
    pass

class DatoInvalidoError(FlotaError):
    pass
class DNIInvalidoError(DatoInvalidoError):
    def __init__(self, dni):
        super().__init__(f"El DNI {dni} ya está registrado")
class VentanaInvalidaError(DatoInvalidoError):
    def __init__(self, inicio, fin):
        super().__init__(f"El inicio de la ventana ({inicio}) debe ser anterior al fin ({fin})")
class SolicitudDuplicadaError(DatoInvalidoError):
    def __init__(self, solicitud_id):
        super().__init__(f"Solicitud duplicada: La solicitud {solicitud_id} ya pertenece a un viaje planificado o en curso")

class CapacidadExcedidaError(FlotaError):
    pass
class ExcesoPesoError(CapacidadExcedidaError):
    def __init__(self, peso_max, peso_total):
        super().__init__(f"Capacidad excedida: El peso {peso_total} supera el peso máximo del transporte {peso_max}")
class ExcesoVolumenError(CapacidadExcedidaError):
    def __init__(self, vol_max, vol_total):
        super().__init__(f"Capacidad excedida: El volumen {vol_total} supera el volumen máximo del transporte {vol_max}")

class RutaIncompletaError(FlotaError):
    def __init__(self, origen, destino):
        super().__init__(f"Ruta incompleta: No existe distancia de {origen} a {destino} ")

class VentanaIncumplidaError(FlotaError):
    def __init__(self, lugar, hora_llegada, hora_fin):
        super().__init__(f"Ventana incumplida: Se llegará a {lugar} a las {hora_llegada} superando el límite {hora_fin}")

class TransicionIlegalError(FlotaError):
    pass
class EstadoInvalidoError(TransicionIlegalError):
    def __init__(self, accion, estado):
        super().__init__(f"Estado invalido: No se puede {accion} porque el estado es {estado}")
class ViajeVacioError(TransicionIlegalError):
    pass
class SinParadasPendientesError(TransicionIlegalError):
    def __init__(self, accion):
        super().__init__(f"Sin paradas pendientes: No se puede {accion} porque todas las paradas ya tienen resultado")
class ViajeIncompletoError(TransicionIlegalError):
    def __init__(self, pendientes):
        super().__init__(f"Viaje incompleto: No se puede finalizar porque quedan {pendientes} paradas pendientes")
