import pytest
from viaje import Viaje
from datetime import datetime, timedelta
from solicitud import Solicitud
from articulo import Articulo
from matrizdistancia import MatrizDistancia
from transporte import Furgoneta, Camion, Transporte
from excepciones import ExcesoPesoError, ExcesoVolumenError, VentanaIncumplidaError, EstadoInvalidoError, DatoInvalidoError, ViajeIncompletoError, ViajeVacioError, SinParadasPendientesError, SolicitudDuplicadaError, TransicionIlegalError

@pytest.fixture
def matriz_base():
    matriz = MatrizDistancia()
    matriz.cargar_matriz([
        ("Deposito", "Destino A", 15),
        ("Destino A", "Deposito", 15),
        ("Deposito", "Destino B", 25),
        ("Destino B", "Deposito", 25),
        ("Destino A", "Destino B", 10), 
        ("Destino B", "Destino A", 10),
    ])
    return matriz
@pytest.fixture
def transporte_base():
    return Furgoneta()  # O Camion(), según lo que quieras probar
@pytest.fixture
def viaje_base(matriz_base, transporte_base):
    return Viaje(transporte_base, "Deposito", datetime(2024, 6, 1, 9, 0), matriz_base)

# def test_transporte_invalido():
#     with pytest.raises(DatoInvalidoError, match="El transporte TRANSPORTE debe ser de clase transporte"):
#         Viaje("TRANSPORTE", "Deposito", datetime(2024, 6, 1, 9, 0), MatrizDistancia())
# def test_deposito_invalido(transporte_base):
#     with pytest.raises(DatoInvalidoError, match="El depósito debe ser una cadena str no vacía"):
#         Viaje(transporte_base, 123, datetime(2024, 6, 1, 9, 0), MatrizDistancia())


#  ESTOS TESTS SON TODOS LOS DEL ESTADO INVÁLIDO EN DISTINTAS FUNCIONES
def test_estado_invalido_crear_solicitud(viaje_base):
    viaje_base.setter_estado("EN_CURSO")
    viaje_base.setter_estado("FINALIZADO")
    with pytest.raises(EstadoInvalidoError, match="Estado invalido: No se puede crear_solicitud porque el estado es FINALIZADO"):
        viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
def test_estado_invalido_iniciar_viaje(viaje_base):
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
    with pytest.raises(EstadoInvalidoError, match="Estado invalido: No se puede iniciar_viaje porque el estado es EN_CURSO"):
        viaje_base.setter_estado("EN_CURSO")
        viaje_base.iniciar_viaje()
def test_estado_invalido_registrar_entrega(viaje_base):
    with pytest.raises(EstadoInvalidoError, match="Estado invalido: No se puede registrar_entrega porque el estado es FINALIZADO"):
        viaje_base.setter_estado("EN_CURSO")
        viaje_base.setter_estado("FINALIZADO")
        viaje_base.registrar_entrega(datetime(2024, 6, 1, 10, 0), "RECEPTOR", 100)
def test_estado_invalido_registrar_incidente(viaje_base):
    with pytest.raises(EstadoInvalidoError, match="Estado invalido: No se puede registrar_incidente porque el estado es PLANIFICADO"):
        assert viaje_base.getter_estado() == "PLANIFICADO"
        viaje_base.registrar_incidente("DAÑO", datetime(2024, 6, 1, 10, 0), "Pinchazo")
def test_estado_invalido_finalizar_viaje(viaje_base):
    with pytest.raises(EstadoInvalidoError, match="Estado invalido: No se puede finalizar_viaje porque el estado es PLANIFICADO"):
        assert viaje_base.getter_estado() == "PLANIFICADO"
        viaje_base.finalizar_viaje()



def test_transporte_invalido(matriz_base):
    with pytest.raises(TypeError, match="El transporte TRANSPORTE debe ser de clase"):
        Viaje("TRANSPORTE", "Deposito", datetime(2024, 6, 1, 9, 0), matriz_base)
def test_deposito_invalido(transporte_base, matriz_base):
    with pytest.raises(DatoInvalidoError, match="El depósito debe ser una cadena str no vacía"):
        Viaje(transporte_base, "", datetime(2024, 6, 1, 9, 0), matriz_base)
def test_exceso_peso(viaje_base):
    with pytest.raises(ExcesoPesoError, match="Capacidad excedida: El peso 600 supera el peso máximo del transporte 500"):
        viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Pesado", 600, 1))
def test_exceso_volumen(viaje_base):
    with pytest.raises(ExcesoVolumenError, match="Capacidad excedida: El volumen 9 supera el volumen máximo del transporte 8"):
        viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Grande", 10, 9))
def test_ventana_incumplida(viaje_base):
    # Deposito -> Destino A son 15 km a 30 km/h: llega 9:30, después del fin de ventana 9:15
    with pytest.raises(VentanaIncumplidaError, match="Ventana incumplida: Se llegará a Destino A a las 2024-06-01 09:30:00 superando el límite 2024-06-01 09:15:00"):
        viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 9, 15), Articulo("Producto", 10, 1))
def test_viaje_vacio(viaje_base):
    with pytest.raises(ViajeVacioError, match="Viaje Vacio: El viaje aún no tiene solicitudes"):
        viaje_base.iniciar_viaje()
def test_entrega_hora_anterior_a_salida(viaje_base):
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
    viaje_base.iniciar_viaje()
    with pytest.raises(DatoInvalidoError, match="La hora de entrega no puede ser anterior al horario de salida del viaje"):
        viaje_base.registrar_entrega(datetime(2024, 6, 1, 8, 0), "RECEPTOR", 100)
def test_sin_paradas_pendientes(viaje_base):
    viaje_base.setter_estado("EN_CURSO")
    with pytest.raises(SinParadasPendientesError, match="Sin paradas pendientes: No se puede registrar_entrega"):
        viaje_base.registrar_entrega(datetime(2024, 6, 1, 10, 0), "RECEPTOR", 100)
def test_viaje_incompleto(viaje_base):
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
    viaje_base.iniciar_viaje()
    with pytest.raises(ViajeIncompletoError, match="Viaje incompleto: No se puede finalizar porque quedan 1 paradas pendientes"):
        viaje_base.finalizar_viaje()
def test_solicitud_duplicada(viaje_base, transporte_base, matriz_base):
    solicitud = viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
    otro_viaje = Viaje(transporte_base, "Deposito", datetime(2024, 6, 1, 9, 0), matriz_base)
    with pytest.raises(SolicitudDuplicadaError, match="Solicitud duplicada"):   #ESTE ERROR HAY QUE ESCRIBIRLO DE FORMA MAS LINDA
        otro_viaje.agregar_solicitud(solicitud)




#  TESTS DE FUNCIONAMIENTO NORMAL (ASSERTS)
@pytest.fixture
def viaje_con_solicitudes(viaje_base):
    # A: 150 kg, 3 m³ - ventana 9:00 a 12:00
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Caja", 100, 2), Articulo("Bolsa", 50, 1))
    # B: 200 kg, 3 m³ - ventana 10:30 a 13:00 (el transporte llega antes y tiene que esperar)
    viaje_base.crear_solicitud("Destino B", datetime(2024, 6, 1, 10, 30), datetime(2024, 6, 1, 13, 0), Articulo("Mueble", 200, 3))
    return viaje_base

def test_viaje_recien_creado(viaje_base, transporte_base):
    assert viaje_base.getter_estado() == "PLANIFICADO"
    assert viaje_base.getter_peso() == 0
    assert viaje_base.getter_volumen() == 0
    assert viaje_base.getter_solicitudes() == []
    assert viaje_base.getter_incidentes() == []
    assert viaje_base.getter_peso_max() == 500
    assert viaje_base.getter_volumen_max() == 8
    assert viaje_base.getter_transporte() is transporte_base
    assert hash(viaje_base) is not None

def test_crear_solicitud_acumula_carga(viaje_con_solicitudes):
    solicitudes = viaje_con_solicitudes.getter_solicitudes()
    assert len(solicitudes) == 2
    assert viaje_con_solicitudes.getter_peso() == 350
    assert viaje_con_solicitudes.getter_volumen() == 6
    assert list(map(lambda s: s.getter_destino(), solicitudes)) == ["Destino A", "Destino B"]
    assert all(map(lambda s: s.getter_viaje() is viaje_con_solicitudes, solicitudes))
    # getter_solicitudes devuelve una copia: modificarla no afecta al viaje
    solicitudes.clear()
    assert len(viaje_con_solicitudes.getter_solicitudes()) == 2

def test_solicitud_rechazada_no_modifica_viaje(viaje_con_solicitudes):
    with pytest.raises(ExcesoPesoError):
        viaje_con_solicitudes.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 18, 0), Articulo("Pesado", 200, 1))
    with pytest.raises(VentanaIncumplidaError):
        viaje_con_solicitudes.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 9, 5), Articulo("Liviano", 1, 1))
    assert viaje_con_solicitudes.getter_peso() == 350
    assert viaje_con_solicitudes.getter_volumen() == 6
    assert len(viaje_con_solicitudes.getter_solicitudes()) == 2

def test_distancia_total(viaje_con_solicitudes):
    # Deposito -> A (15) -> B (10) -> Deposito (25)
    assert viaje_con_solicitudes.distancia_total() == 50

def test_iniciar_viaje_genera_paradas(viaje_con_solicitudes):
    viaje_con_solicitudes.iniciar_viaje()
    paradas = viaje_con_solicitudes.getter_paradas()
    assert viaje_con_solicitudes.getter_estado() == "EN_CURSO"
    assert len(paradas) == 2
    assert list(map(lambda p: p.getter_orden(), paradas)) == [1, 2]
    assert all(map(lambda p: p.getter_estado() == "PENDIENTE" and p.getter_hora_real() is None, paradas))
    # 15 km a 30 km/h = 30 min -> llega 9:30
    assert paradas[0].getter_hora_prev() == datetime(2024, 6, 1, 9, 30)
    # 9:30 + 10 min de parada + 20 min de viaje = 10:00, pero la ventana abre 10:30
    assert paradas[1].getter_hora_prev() == datetime(2024, 6, 1, 10, 30)

def test_recorrido_completo_con_entrega_e_incidente(viaje_con_solicitudes):
    viaje_con_solicitudes.iniciar_viaje()
    solicitud_a, solicitud_b = viaje_con_solicitudes.getter_solicitudes()

    comprobante = viaje_con_solicitudes.registrar_entrega(datetime(2024, 6, 1, 9, 35), "Juan Perez", 1500)
    assert comprobante.getter_solicitud() is solicitud_a
    assert comprobante.getter_receptor() == "Juan Perez"
    assert comprobante.getter_monto() == 1500
    assert viaje_con_solicitudes.getter_paradas()[0].getter_estado() == "ENTREGADA"
    assert viaje_con_solicitudes.getter_paradas()[0].getter_hora_real() == datetime(2024, 6, 1, 9, 35)
    assert viaje_con_solicitudes.getter_estado() == "EN_CURSO"

    incidente = viaje_con_solicitudes.registrar_incidente("AUSENTE", datetime(2024, 6, 1, 10, 40), "No había nadie")
    assert incidente.getter_afectado() is solicitud_b
    assert incidente.getter_tipo() == "AUSENTE"
    assert viaje_con_solicitudes.getter_incidentes() == [incidente]
    assert viaje_con_solicitudes.getter_paradas()[1].getter_estado() == "FALLIDA"
    # Al no quedar paradas pendientes el viaje se finaliza solo
    assert viaje_con_solicitudes.getter_estado() == "FINALIZADO"

def test_incidente_con_detalles_kwargs(viaje_con_solicitudes):
    viaje_con_solicitudes.iniciar_viaje()
    incidente = viaje_con_solicitudes.registrar_incidente("DAÑO", datetime(2024, 6, 1, 9, 40), "Pinchazo", rueda="delantera", costo=15000)
    assert incidente.getter_detalles() == {"rueda": "delantera", "costo": 15000}
    assert str(incidente) == f"Incidente {incidente.id} [DAÑO] a las 09:40: Pinchazo, rueda=delantera, costo=15000"
    incidente.getter_detalles()["rueda"] = "otra"
    assert incidente.getter_detalles()["rueda"] == "delantera"

def test_incidente_sin_detalles(viaje_con_solicitudes):
    viaje_con_solicitudes.iniciar_viaje()
    incidente = viaje_con_solicitudes.registrar_incidente("AUSENTE", datetime(2024, 6, 1, 9, 40), "No había nadie")
    assert incidente.getter_detalles() == {}
    assert str(incidente) == f"Incidente {incidente.id} [AUSENTE] a las 09:40: No había nadie"

def test_incidente_detalle_vacio_invalido(viaje_con_solicitudes):
    viaje_con_solicitudes.iniciar_viaje()
    with pytest.raises(DatoInvalidoError, match="El detalle rueda no puede ser una cadena vacía"):
        viaje_con_solicitudes.registrar_incidente("DAÑO", datetime(2024, 6, 1, 9, 40), "Pinchazo", rueda="  ")

def test_metodos_magicos(viaje_con_solicitudes, transporte_base, matriz_base):
    otro = Viaje(transporte_base, "Deposito", datetime(2024, 6, 1, 9, 0), matriz_base)
    assert viaje_con_solicitudes == viaje_con_solicitudes
    assert viaje_con_solicitudes != otro
    assert viaje_con_solicitudes != "no soy un viaje"
    assert otro.getter_id() == viaje_con_solicitudes.getter_id() + 1
    assert str(viaje_con_solicitudes) == f"Viaje {viaje_con_solicitudes.getter_id()} [PLANIFICADO] - Furgoneta saliendo de Deposito a las 2024-06-01 09:00"
    assert repr(viaje_con_solicitudes) == f"<Viaje {viaje_con_solicitudes.getter_id()} PLANIFICADO paradas=2>"

def test_solicitud_reutilizada(viaje_con_solicitudes, transporte_base, matriz_base):
    viaje_con_solicitudes.iniciar_viaje()
    solicitud_a, solicitud_b = viaje_con_solicitudes.getter_solicitudes()
    viaje_con_solicitudes.registrar_entrega(datetime(2024, 6, 1, 9, 35), "Juan Perez", 1500)
    viaje_con_solicitudes.registrar_incidente("AUSENTE", datetime(2024, 6, 1, 10, 40), "No había nadie")
    assert viaje_con_solicitudes.getter_estado() == "FINALIZADO"

    otro_viaje = Viaje(transporte_base, "Deposito", datetime(2024, 6, 1, 9, 0), matriz_base)
    with pytest.raises(SolicitudDuplicadaError):
        otro_viaje.agregar_solicitud(solicitud_a)


# ORDENAMIENTO AL INICIAR EL VIAJE
def _destinos_paradas(viaje):
    return [p.getter_solicitud().getter_destino() for p in viaje.getter_paradas()]

def test_iniciar_viaje_ordena_por_vecinos(viaje_base):
    viaje_base.crear_solicitud("Destino B", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 18, 0), Articulo("Producto", 10, 1))
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 18, 0), Articulo("Producto", 10, 1))
    viaje_base.iniciar_viaje()
    assert _destinos_paradas(viaje_base) == ["Destino A", "Destino B"]
    assert [s.getter_destino() for s in viaje_base.getter_solicitudes()] == ["Destino A", "Destino B"]

def test_iniciar_viaje_usa_ventanas_si_vecinos_es_invalido(viaje_base):
    # Vecinos daria A, B y B llegaria 10:00 (> 9:55); por ventanas queda B, A
    viaje_base.crear_solicitud("Destino B", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 9, 55), Articulo("Producto", 10, 1))
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 10), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
    viaje_base.iniciar_viaje()
    assert _destinos_paradas(viaje_base) == ["Destino B", "Destino A"]

def test_iniciar_viaje_mantiene_orden_original_si_ninguna_politica_es_valida(viaje_base):
    # Vecinos y ventanas darian A, B (B llegaria 10:00 > 9:55); el orden de creacion B, A es el unico valido
    viaje_base.crear_solicitud("Destino B", datetime(2024, 6, 1, 9, 10), datetime(2024, 6, 1, 9, 55), Articulo("Producto", 10, 1))
    viaje_base.crear_solicitud("Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0), Articulo("Producto", 10, 1))
    viaje_base.iniciar_viaje()
    assert _destinos_paradas(viaje_base) == ["Destino B", "Destino A"]

def test_setear_peso_negativo(viaje_base):
    with pytest.raises(DatoInvalidoError):
        viaje_base.setter_peso(-5)

def test_setear_peso_str(viaje_base):
    with pytest.raises((DatoInvalidoError, TypeError)):
        viaje_base.setter_peso("Cinco")

def test_setear_volumen_negativos(viaje_base):
    with pytest.raises(DatoInvalidoError):
        viaje_base.setter_volumen(-1)

def test_estado_del_viaje_1(viaje_base):
    viaje_base.setter_estado("EN_CURSO")
    viaje_base.setter_estado("FINALIZADO")
    with pytest.raises(TransicionIlegalError):
        viaje_base.setter_estado("PLANIFICADO")

def test_estado_del_viaje_2(viaje_base):
    viaje_base.setter_estado("EN_CURSO")
    with pytest.raises(TransicionIlegalError):
        viaje_base.setter_estado("PLANIFICADO")

@pytest.fixture
def viaje_en_curso(viaje_base):
    inicio, fin = datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 18, 0)
    viaje_base.crear_solicitud("Destino A", inicio, fin, Articulo("P", 1, 1))
    viaje_base.crear_solicitud("Destino B", inicio, fin, Articulo("P", 1, 1))
    viaje_base.iniciar_viaje()
    return viaje_base

def test_coherencia_temporal_entrega(viaje_en_curso):
    viaje_en_curso.registrar_entrega(datetime(2024, 6, 1, 10, 0), "Juan", 100)
    with pytest.raises(DatoInvalidoError):
        viaje_en_curso.registrar_entrega(datetime(2024, 6, 1, 9, 30), "Ana", 100)

def test_coherencia_temporal_incidente(viaje_en_curso):
    viaje_en_curso.registrar_entrega(datetime(2024, 6, 1, 10, 0), "Juan", 100)
    with pytest.raises(DatoInvalidoError):
        viaje_en_curso.registrar_incidente("AUSENTE", datetime(2024, 6, 1, 9, 30), "No había nadie")
