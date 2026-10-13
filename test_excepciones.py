import pytest
from excepciones import (
    FlotaError, DatoInvalidoError, DNIInvalidoError, VentanaInvalidaError, SolicitudDuplicadaError,
    CapacidadExcedidaError, ExcesoPesoError, ExcesoVolumenError, RutaIncompletaError,
    VentanaIncumplidaError, TransicionIlegalError, EstadoInvalidoError, ViajeVacioError,
    SinParadasPendientesError, ViajeIncompletoError,
)

# Jerarquía
def test_flotaError_esException():
    assert issubclass(FlotaError, Exception)

def test_familia_datoInvalido():
    assert issubclass(DatoInvalidoError, FlotaError)
    assert issubclass(DNIInvalidoError, DatoInvalidoError)
    assert issubclass(VentanaInvalidaError, DatoInvalidoError)
    assert issubclass(SolicitudDuplicadaError, DatoInvalidoError)

def test_familia_capacidadExcedida():
    assert issubclass(CapacidadExcedidaError, FlotaError)
    assert issubclass(ExcesoPesoError, CapacidadExcedidaError)
    assert issubclass(ExcesoVolumenError, CapacidadExcedidaError)

def test_familia_transicionIlegal():
    assert issubclass(TransicionIlegalError, FlotaError)
    assert issubclass(EstadoInvalidoError, TransicionIlegalError)
    assert issubclass(ViajeVacioError, TransicionIlegalError)
    assert issubclass(SinParadasPendientesError, TransicionIlegalError)
    assert issubclass(ViajeIncompletoError, TransicionIlegalError)

def test_excepciones_sueltas():
    assert issubclass(RutaIncompletaError, FlotaError)
    assert issubclass(VentanaIncumplidaError, FlotaError)

def test_familias_independientes():
    assert not issubclass(CapacidadExcedidaError, DatoInvalidoError)
    assert not issubclass(TransicionIlegalError, DatoInvalidoError)
    assert not issubclass(DatoInvalidoError, CapacidadExcedidaError)
    assert not issubclass(ExcesoPesoError, ExcesoVolumenError)
    assert not issubclass(RutaIncompletaError, TransicionIlegalError)

# Mensajes de las excepciones que llevan datos
def test_mensaje_dniInvalido():
    assert str(DNIInvalidoError(12345678)) == "El DNI 12345678 ya está registrado"
def test_mensaje_ventanaInvalida_sinNombre():
    assert str(VentanaInvalidaError("09:00", "08:00")) == "El inicio de la ventana (09:00) debe ser anterior al fin (08:00)"
    assert str(VentanaInvalidaError("09:00", "08:00", nombre_inicio = "fecha de salida")) == "El inicio de la ventana (09:00) debe ser anterior al fin (08:00)"
def test_mensaje_ventanaInvalida_conNombre():
    assert str(VentanaInvalidaError("09:00", "08:00", "fecha de salida del viaje", "fecha de entrega")) == "La fecha de salida del viaje (09:00) debe ser anterior a la fecha de entrega (08:00)"
def test_mensaje_solicitudDuplicada():
    assert str(SolicitudDuplicadaError(7)) == "Solicitud duplicada: La solicitud 7 ya pertenece a un viaje planificado o en curso"
def test_mensaje_excesoPeso():
    assert str(ExcesoPesoError(100, 150)) == "Capacidad excedida: El peso 150 supera el peso máximo del transporte 100"
def test_mensaje_excesoVolumen():
    assert str(ExcesoVolumenError(8, 10)) == "Capacidad excedida: El volumen 10 supera el volumen máximo del transporte 8"
def test_mensaje_rutaIncompleta():
    assert str(RutaIncompletaError("A", "B"))  == "Ruta incompleta: No existe distancia de A a B"
def test_mensaje_ventanaIncumplida():
    assert str(VentanaIncumplidaError("Destino A", "10:30", "10:00")) == "Ventana incumplida: Se llegará a Destino A a las 10:30 superando el límite 10:00"
def test_mensaje_estadoInvalido():
    assert str(EstadoInvalidoError("iniciar_viaje", "EN_CURSO")) == "Estado invalido: No se puede iniciar_viaje porque el estado es EN_CURSO"
def test_mensaje_sinParadasPendientes():
    assert str(SinParadasPendientesError("registrar_entrega")) == "Sin paradas pendientes: No se puede registrar_entrega porque todas las paradas ya tienen resultado"
def test_mensaje_viajeIncompleto():
    assert str(ViajeIncompletoError(3)) == "Viaje incompleto: No se puede finalizar porque quedan 3 paradas pendientes"
# Faltan argumentos
def test_excepciones_faltanArgumentos():
    with pytest.raises(TypeError):
        DNIInvalidoError()
    with pytest.raises(TypeError):
        ExcesoPesoError(100)
    with pytest.raises(TypeError):
        VentanaIncumplidaError("Destino A", "10:30")
    with pytest.raises(TypeError):
        ViajeIncompletoError()
    with pytest.raises(TypeError):
        VentanaInvalidaError("09:00")
    with pytest.raises(TypeError):
        SolicitudDuplicadaError()
    with pytest.raises(TypeError):
        ExcesoVolumenError(8)
    with pytest.raises(TypeError):
        RutaIncompletaError("A")
    with pytest.raises(TypeError):
        EstadoInvalidoError("iniciar_viaje")
    with pytest.raises(TypeError):
        SinParadasPendientesError()

# Excepciones sin datos propios: usan el mensaje que se les pase
def test_flotaError_mensaje():
    assert str(FlotaError("mensaje")) == "mensaje"
def test_datoInvalido_mensaje():
    assert str(DatoInvalidoError("dato malo")) == "dato malo"
def test_capacidadExcedida_mensaje():
    assert str(CapacidadExcedidaError("no entra")) == "no entra"
def test_transicionIlegal_mensaje():
    assert str(TransicionIlegalError("transición no permitida")) == "transición no permitida"
def test_viajeVacio_mensaje():
    assert str(ViajeVacioError("Viaje Vacio: No hay solicitudes")) == "Viaje Vacio: No hay solicitudes"

# Atrapar excepciones
def test_atrapar_por_clase():
    with pytest.raises(ExcesoPesoError):
        raise ExcesoPesoError(100, 200)

def test_atrapar_por_familia():
    with pytest.raises(CapacidadExcedidaError):
        raise ExcesoVolumenError(8, 10)
    with pytest.raises(DatoInvalidoError):
        raise VentanaInvalidaError("09:00", "08:00")
    with pytest.raises(TransicionIlegalError):
        raise ViajeIncompletoError(2)

def test_atrapar_por_flotaError():
    with pytest.raises(FlotaError):
        raise RutaIncompletaError("A", "B")
    with pytest.raises(FlotaError):
        raise DNIInvalidoError(12345678)

def test_excepciones_sePropagan():
    with pytest.raises(DNIInvalidoError):
        with pytest.raises(TransicionIlegalError):
            raise DNIInvalidoError(12345678)