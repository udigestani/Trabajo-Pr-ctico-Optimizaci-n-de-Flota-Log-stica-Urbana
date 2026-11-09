import pytest
from datetime import datetime
from persona import Persona, Administrador
from transporte import Furgoneta
from matrizdistancia import MatrizDistancia
from solicitud import Solicitud
from articulo import Articulo
from politicaordenamiento import Vecinos
from excepciones import VentanaIncumplidaError

# Tests de integración con clases reales: ejemplo de aceptación del README
# Furgoneta: 500 kg, 8 m³, 30 km/h, $2 por km, $5 por parada, 0,27 kg CO₂/km. Sale a las 09:00.
# S1: 100 kg, 2 m³, a 15 km del depósito, ventana 09:20-10:00
# S2: 150 kg, 3 m³, a 10 km de S1 y a 20 km del depósito, ventana 10:00-11:00

def hora(horas, minutos = 0):
    return datetime(2026, 10, 11, horas, minutos)

@pytest.fixture(autouse = True)
def limpiar_dnis():
    Persona.limpiar_dnis_registrados()

@pytest.fixture
def admin():
    return Administrador("Admin", 12345678, 1122334455)

@pytest.fixture
def matriz():
    matriz = MatrizDistancia()
    matriz.cargar_matriz([("Deposito", "S1", 15), ("S1", "Deposito", 15),
                          ("Deposito", "S2", 20), ("S2", "Deposito", 20),
                          ("S1", "S2", 10), ("S2", "S1", 10)])
    return matriz

@pytest.fixture
def s1():
    return Solicitud("S1", hora(9, 20), hora(10), Articulo("Caja", 100, 2))

@pytest.fixture
def s2():
    return Solicitud("S2", hora(10), hora(11), Articulo("Libros", 150, 3))

@pytest.fixture
def viaje(admin, matriz):
    return admin.crear_viaje(Furgoneta(), "Deposito", hora(9), matriz)

@pytest.fixture
def viaje_con_solicitudes(viaje, s1, s2):
    viaje.agregar_solicitud(s1)
    viaje.agregar_solicitud(s2)
    return viaje

# Ejemplo de aceptación: carga, horarios, distancia, costo e impacto
def test_aceptacion_ok(viaje_con_solicitudes, s1, s2):
    viaje = viaje_con_solicitudes
    assert viaje.getter_solicitudes() == [s1, s2]
    assert viaje.getter_peso() == 250
    assert viaje.getter_volumen() == 5
    # Llega a S1 a las 09:30 (termina 09:40) y a S2 a las 10:00
    assert viaje.calcular_horarios([s1, s2]) == [hora(9, 30), hora(10)]
    assert viaje.validar_recorrido([s1, s2]) is True
    assert viaje.distancia_total() == 45
    assert viaje.costo_total() == 100
    assert round(viaje.impacto_ambiental(), 2) == 22.5
# Si la ventana de S2 termina a las 09:55 se rechaza y el viaje conserva solo S1
def test_aceptacion_ventanaIncumplida(viaje, s1):
    s2_tarde = Solicitud("S2", hora(9, 30), hora(9, 55), Articulo("Libros", 150, 3))
    viaje.agregar_solicitud(s1)
    with pytest.raises(VentanaIncumplidaError):
        viaje.agregar_solicitud(s2_tarde)
    assert viaje.getter_solicitudes() == [s1]
    assert viaje.getter_peso() == 100
    assert viaje.getter_volumen() == 2
    assert s2_tarde.getter_viaje() is None
# La política de vecino más cercano solo sugiere: no crea ni modifica ningún viaje
def test_aceptacion_politicaVecinos(viaje, matriz, s1, s2):
    assert Vecinos.sugerir_orden("Deposito", [s1, s2], matriz) == [s1, s2]
    assert Vecinos.sugerir_orden("Deposito", [s2, s1], matriz) == [s1, s2]
    assert viaje.getter_solicitudes() == []
    assert s1.getter_viaje() is None
    assert s2.getter_viaje() is None
# Se ejecuta el viaje completo
def test_aceptacion_viajeCompleto(admin, viaje_con_solicitudes, s1, s2):
    viaje = viaje_con_solicitudes
    Administrador.iniciar_viaje(viaje)
    assert viaje.getter_estado() == "EN_CURSO"
    paradas = viaje.getter_paradas()
    assert list(map(lambda p: p.getter_solicitud(), paradas)) == [s1, s2]
    assert list(map(lambda p: p.getter_hora_prev(), paradas)) == [hora(9, 30), hora(10)]
    comprobante1 = Administrador.registrar_entrega(viaje, hora(9, 35), "Juan", 100)
    assert viaje.getter_estado() == "EN_CURSO"
    assert s1.esta_entregada()
    comprobante2 = Administrador.registrar_entrega(viaje, hora(10, 5), "Ana", 150)
    assert viaje.getter_estado() == "FINALIZADO"
    assert s2.getter_comprobante() is comprobante2
    assert s1.getter_comprobante() is comprobante1
    assert list(map(lambda p: p.getter_estado(), viaje.getter_paradas())) == ["ENTREGADA", "ENTREGADA"]

# Incidente de alcance SOLICITUD: la parada sigue pendiente y se puede entregar
def test_incidenteSolicitud_ySeEntrega(viaje_con_solicitudes, s1):
    viaje = viaje_con_solicitudes
    Administrador.iniciar_viaje(viaje)
    incidente = Administrador.registrar_incidente(viaje, "DAÑO", hora(9, 32), "Caja golpeada", alcance = "SOLICITUD")
    assert incidente.getter_afectado() is s1
    assert viaje.getter_incidentes() == [incidente]
    assert len(viaje.paradas_pendientes()) == 2
    assert viaje.paradas_pendientes()[0].getter_estado() == "PENDIENTE"
    comprobante = Administrador.registrar_entrega(viaje, hora(9, 35), "Juan", 100)
    assert s1.getter_comprobante() is comprobante
    assert len(viaje.paradas_pendientes()) == 1
    assert viaje.getter_estado() == "EN_CURSO"
# Incidentes de los tres alcances: el viaje finaliza al resolver todas las paradas
def test_incidentesDeLosTresAlcances_finalizaElViaje(viaje_con_solicitudes, s2):
    viaje = viaje_con_solicitudes
    transporte = viaje.getter_transporte()
    Administrador.iniciar_viaje(viaje)
    # Parada 1: incidente del transporte y de la solicitud, y se entrega
    inc_transporte = Administrador.registrar_incidente(viaje, "RETRASO", hora(9, 31), "Pinchazo", alcance = "TRANSPORTE")
    inc_solicitud = Administrador.registrar_incidente(viaje, "DAÑO", hora(9, 32), "Caja golpeada", alcance = "SOLICITUD")
    assert inc_transporte.getter_afectado() is transporte
    assert len(viaje.paradas_pendientes()) == 2
    Administrador.registrar_entrega(viaje, hora(9, 35), "Juan", 100)
    assert viaje.getter_estado() == "EN_CURSO"
    # Parada 2: falla la entrega
    inc_falla = Administrador.registrar_incidente(viaje, "AUSENTE", hora(10, 5), "No había nadie")
    assert inc_falla.getter_afectado() is s2
    assert viaje.getter_estado() == "FINALIZADO"
    assert viaje.paradas_pendientes() == []
    assert viaje.getter_incidentes() == [inc_transporte, inc_solicitud, inc_falla]
    assert list(map(lambda p: p.getter_estado(), viaje.getter_paradas())) == ["ENTREGADA", "FALLIDA"]
    assert not s2.esta_entregada()
