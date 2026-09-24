import pytest
from datetime import datetime
from matrizDistancia import MatrizDistancia
from viaje import Viaje
from transporte import Furgoneta, Camion
from articulo import Articulo
from solicitud import Solicitud
from excepciones import ExcesoPesoError, EstadoInvalidoError, ViajeVacioError, VentanaIncumplidaError

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
def viaje_base(matriz_base):
    furgoneta = Furgoneta() 
    return Viaje(furgoneta, "Deposito", datetime(2024, 6, 1, 9, 0), matriz_base)

def test_exceso_solo_de_peso_es_rechazado(viaje_base):
    art_pesado = Articulo("Yunque", 600, 2)
    with pytest.raises(ExcesoPesoError):
        # Usamos crear_solicitud como lo definiste en Viaje
        viaje_base.crear_solicitud(
            [art_pesado], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0)
        )

def test_valores_exactamente_en_capacidad_son_aceptados(viaje_base):
    art_justo = Articulo("Carga Máxima", 500, 8)
    solicitud = viaje_base.crear_solicitud(
        [art_justo], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0)
    )
    assert viaje_base.getter_peso() == 500
    assert viaje_base.getter_volumen() == 8
    assert solicitud in viaje_base.getter_solicitudes()

def test_agregado_inviable_sin_cambios_parciales(viaje_base):
    art_valido = Articulo("Caja 1", 100, 1)
    viaje_base.crear_solicitud(
        [art_valido], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0)
    )
    peso_previo = viaje_base.getter_peso()
    cantidad_solicitudes = len(viaje_base.getter_solicitudes())
    art_tarde = Articulo("Caja 2", 100, 1)
    
    with pytest.raises(VentanaIncumplidaError):
        viaje_base.crear_solicitud(
            [art_tarde], "Destino B", datetime(2024, 6, 1, 8, 0), datetime(2024, 6, 1, 8, 30)
        )
        
    assert viaje_base.getter_peso() == peso_previo
    assert len(viaje_base.getter_solicitudes()) == cantidad_solicitudes

def test_llegada_exactamente_al_fin_de_ventana(viaje_base):
    art_normal = Articulo("Caja", 10, 1)
    viaje_base.crear_solicitud(
        [art_normal], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 9, 30)
    )
    assert len(viaje_base.getter_solicitudes()) == 1

def test_impacto_ambiental_distinto_por_tipo_transporte():
    furgoneta = Furgoneta() 
    camion = Camion()       
    distancia = 100
    peso_carga = 1000
    
    impacto_furgoneta = furgoneta.calcular_impacto_ambiental(distancia, peso_carga)
    impacto_camion = camion.calcular_impacto_ambiental(distancia, peso_carga)
    
    assert impacto_furgoneta != impacto_camion
    assert impacto_furgoneta == 0.27 * 100
    assert impacto_camion == (1 + (1000 / 10000)) * 100

def test_inicio_vacio_rechazado(viaje_base):
    with pytest.raises(ViajeVacioError):
        viaje_base.iniciar_viaje()

def test_modificacion_luego_de_iniciar_rechazada(viaje_base):
    art_valido = Articulo("Caja 1", 10, 1)
    viaje_base.crear_solicitud(
        [art_valido], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0)
    )
    viaje_base.iniciar_viaje()
    
    with pytest.raises(EstadoInvalidoError):
        viaje_base.crear_solicitud(
            [art_valido], "Destino B", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 12, 0)
        )

from datetime import timedelta
from parada import Parada

def test_orden_de_resultados_y_comprobante_unico(viaje_base):
    art = Articulo("Caja", 10, 1)
    viaje_base.crear_solicitud([art], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 10, 0))
    viaje_base.crear_solicitud([art], "Destino B", datetime(2024, 6, 1, 10, 0), datetime(2024, 6, 1, 11, 0))
    viaje_base.iniciar_viaje()
    
    hora_entrega = datetime(2024, 6, 1, 9, 45)
    comprobante = viaje_base.registrar_entrega(hora_entrega, "Juan Perez", 1500)
    
    assert comprobante.receptor == "Juan Perez"
    assert comprobante.solicitud == viaje_base.getter_solicitudes()[0]
    assert viaje_base.paradas[0].estado == "ENTREGADA"
    
    assert viaje_base.paradas[1].estado == "PENDIENTE"
    assert viaje_base.getter_estado() == "EN_CURSO"

def test_registro_de_incidente(viaje_base):
    art = Articulo("Caja", 10, 1)
    viaje_base.crear_solicitud([art], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 10, 0))
    viaje_base.iniciar_viaje() 
    
    incidente = viaje_base.registrar_incidente("RETRASO", datetime(2024, 6, 1, 9, 15), "Pinchadura de neumático")
    
    assert len(viaje_base.incidentes) == 1
    assert incidente.tipo == "RETRASO"
    assert incidente.descripcion == "Pinchadura de neumático"


def test_politicas_de_ordenamiento_no_alteran_estado(viaje_base, matriz_base):
    from politicaOrdenamiento import Vecinos, VentanasTiempo
    
    s1 = Solicitud([Articulo("A", 10, 1)], "Destino B", datetime(2024, 6, 1, 11, 0), datetime(2024, 6, 1, 12, 0))
    s2 = Solicitud([Articulo("B", 10, 1)], "Destino A", datetime(2024, 6, 1, 9, 0), datetime(2024, 6, 1, 10, 0))
    
    lista_solicitudes = [s1, s2]
    
    politica_vecino = Vecinos()
    politica_ventana = VentanasTiempo()
    
    orden_vecino = politica_vecino.sugerir_orden("Deposito", lista_solicitudes, matriz_base)
    orden_ventana = politica_ventana.sugerir_orden("Deposito", lista_solicitudes, matriz_base)
    
    assert len(orden_vecino) == 2
    assert len(orden_ventana) == 2
    
    assert viaje_base.getter_estado() == "PLANIFICADO"
    assert len(viaje_base.getter_solicitudes()) == 0