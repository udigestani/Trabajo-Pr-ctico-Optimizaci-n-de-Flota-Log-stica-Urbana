import pytest
from datetime import datetime
from solicitud import Solicitud
from articulo import Articulo
from comprobante import Comprobante
from viaje import Viaje
from excepciones import DatoInvalidoError, EstadoInvalidoError, VentanaInvalidaError

INICIO = datetime(2026, 10, 11, 9, 0)
FIN = datetime(2026, 10, 11, 12, 0)

@pytest.fixture(autouse = True)
def resetearId():
    Solicitud.curr_id = 0

@pytest.fixture
def mock_validaciones(mocker):
    mock = mocker.patch("solicitud.Validaciones")
    mock.validar_coleccion.side_effect = lambda valor, **kwargs: valor
    mock.validar_str.side_effect = lambda valor, **kwargs: valor
    mock.validar_ventana.side_effect = lambda inicio, fin, **kwargs: (inicio, fin)
    return mock

@pytest.fixture
def articulo1(mocker):
    mock = mocker.Mock(spec = Articulo)
    mock.getter_peso.return_value = 5
    mock.getter_volumen.return_value = 0.5
    return mock

@pytest.fixture
def articulo2(mocker):
    mock = mocker.Mock(spec = Articulo)
    mock.getter_peso.return_value = 3
    mock.getter_volumen.return_value = 1.5
    return mock

@pytest.fixture
def viaje(mocker):
    return mocker.Mock(spec = Viaje)

@pytest.fixture
def comprobante(mocker):
    return mocker.Mock(spec = Comprobante)

@pytest.fixture
def solicitud(mock_validaciones, articulo1):
    return Solicitud("Destino 1", INICIO, FIN, articulo1)

@pytest.fixture
def solicitud_falsa_igual(mocker):
    mock = mocker.MagicMock(spec = Solicitud)
    mock.getter_id.return_value = 1
    mock.__hash__.return_value = hash(mock.getter_id())
    return mock

# Funcionamiento normal
def test_solicitud_ok(solicitud, articulo1, articulo2, mock_validaciones):
    assert solicitud.getter_destino() == "Destino 1"
    assert solicitud.getter_ventana_inicio() == INICIO
    assert solicitud.getter_ventana_fin() == FIN
    assert solicitud.getter_articulos() == (articulo1,)
    assert solicitud.getter_viaje() is None
    assert solicitud.getter_comprobante() is None
    # id
    assert solicitud.getter_id() == 1
    solicitud2 = Solicitud("Destino 2", INICIO, FIN, articulo1, articulo2)
    assert solicitud2.getter_id() == 2
    # Varios articulos
    assert solicitud2.getter_articulos() == (articulo1, articulo2)
# Getters
def test_solicitud_getters(solicitud, mock_validaciones, articulo1, articulo2):
    assert solicitud.getter_id() == 1
    assert solicitud.getter_destino() == "Destino 1"
    assert solicitud.getter_ventana_inicio() == INICIO
    assert solicitud.getter_ventana_fin() == FIN
    assert solicitud.getter_articulos() == (articulo1,)
    assert isinstance(solicitud.getter_articulos(), tuple)
    assert solicitud.getter_viaje() is None
    assert solicitud.getter_comprobante() is None
    # Peso y volumen
    assert solicitud.getter_peso() == 5
    assert solicitud.getter_volumen() == 0.5
    solicitud2 = Solicitud("Destino 2", INICIO, FIN, articulo1, articulo2)
    assert solicitud2.getter_peso() == 8
    assert solicitud2.getter_volumen() == 2
# Inmutabilidad
def test_solicitud_setters(solicitud, articulo1, articulo2):
    with pytest.raises(AttributeError):
        solicitud.setter_articulos((articulo1, articulo2))
    assert solicitud.getter_articulos() == (articulo1, )
    with pytest.raises(AttributeError):
        solicitud.setter_destino("Destino 100")
    assert solicitud.getter_destino() == "Destino 1"
    with pytest.raises(AttributeError):
        solicitud.setter_ventana_inicio(FIN)
    assert solicitud.getter_ventana_inicio() == INICIO
    with pytest.raises(AttributeError):
        solicitud.setter_ventana_fin(INICIO)
    assert solicitud.getter_ventana_fin() == FIN
    with pytest.raises(AttributeError):
        solicitud.setter_peso(100)
    assert solicitud.getter_peso() == 5
    with pytest.raises(AttributeError):
        solicitud.setter_volumen(100)
    assert solicitud.getter_volumen() == 0.5
# Metodos mágicos
def test_solicitud_metodosMagicos(solicitud, mock_validaciones, articulo1, solicitud_falsa_igual):
    assert str(solicitud) == "Solicitud 1 hacia Destino 1 (Ventana: 09:00-12:00)"
    assert repr(solicitud) == "<Solicitud 1 -> Destino 1>"
    # eq
    solicitud2 = Solicitud("Destino 1", INICIO, FIN, articulo1)
    assert solicitud != solicitud2
    assert solicitud ==  solicitud_falsa_igual
    assert solicitud == solicitud
    assert solicitud != (articulo1, )
    assert solicitud != articulo1
    # hash - por si necesitamos set o dicc
    assert hash(solicitud) == hash(solicitud.getter_id())
    assert hash(solicitud) == hash(solicitud_falsa_igual)
    assert hash(solicitud) != hash(solicitud2)
    solicitudes = {solicitud, solicitud_falsa_igual, solicitud2, solicitud}
    assert solicitud in solicitudes
    assert solicitud2 in solicitudes
    assert len(solicitudes) == 2
    dicc = {solicitud: 1}
    assert dicc[solicitud] == 1
# Setter viaje
def test_solicitud_setterViaje(solicitud, viaje):
    solicitud.setter_viaje(viaje)
    assert solicitud.getter_viaje() is viaje
    solicitud.setter_viaje(None)
    assert solicitud.getter_viaje() is None
def test_solicitud_setterViaje_invalido(solicitud):
    with pytest.raises(DatoInvalidoError):
        solicitud.setter_viaje("Viaje 1")
    assert solicitud.getter_viaje() is None
# Setter comprobante
def test_solicitud_setterComprobante(solicitud, comprobante):
    solicitud.setter_comprobante(comprobante)
    assert solicitud.getter_comprobante() is comprobante
def test_solicitud_setterComprobante_none(solicitud):
    solicitud.setter_comprobante(None)
    assert solicitud.getter_comprobante() is None
def test_solicitud_dobleComprobante(solicitud, comprobante, mocker):
    comprobante2 = mocker.Mock(spec = Comprobante)
    solicitud.setter_comprobante(comprobante)
    with pytest.raises(EstadoInvalidoError):
        solicitud.setter_comprobante(comprobante2)
    assert solicitud.getter_comprobante() is comprobante
def test_solicitud_setterComprobante_invalido(solicitud):
    with pytest.raises(DatoInvalidoError):
        solicitud.setter_comprobante("Comprobante 1")
    assert solicitud.getter_comprobante() is None
# Estado
def test_solicitud_estaEntregada(solicitud, comprobante):
    assert solicitud.esta_entregada() is False
    solicitud.setter_comprobante(comprobante)
    assert solicitud.esta_entregada() is True
def test_solicitud_estaAsignada(solicitud, viaje):
    assert solicitud.esta_asignada() is False
    solicitud.setter_viaje(viaje)
    viaje.getter_estado.return_value = "PLANIFICADO"
    assert solicitud.esta_asignada() is True
    viaje.getter_estado.return_value = "EN_CURSO"
    assert solicitud.esta_asignada() is True
    viaje.getter_estado.return_value = "FINALIZADO"
    assert solicitud.esta_asignada() is False
    viaje.getter_estado.return_value = "PLANIFICADO"
    assert solicitud.esta_asignada() is True
    solicitud.setter_viaje(None)
    assert solicitud.esta_asignada() is False
def test_solicitud_estaPendiente(solicitud, viaje, comprobante):
    assert solicitud.esta_pendiente() is True
    # Asignada a un viaje (planificado o en curso)
    solicitud.setter_viaje(viaje)
    viaje.getter_estado.return_value = "PLANIFICADO"
    assert solicitud.esta_pendiente() is False
    viaje.getter_estado.return_value = "EN_CURSO"
    assert solicitud.esta_pendiente() is False
    # Viaje finalizado sin entrega: vuelve a estar pendiente
    viaje.getter_estado.return_value = "FINALIZADO"
    assert solicitud.esta_pendiente() is True
    # Entregada
    solicitud.setter_comprobante(comprobante)
    assert solicitud.esta_pendiente() is False
    solicitud.setter_viaje(None)
    assert solicitud.esta_pendiente() is False
# Setter id
def test_solicitud_setterId(solicitud):
    solicitud.setter_id(7)
    assert solicitud.getter_id() == 7
# Validaciones
def test_solicitud_validaciones(mock_validaciones, articulo1, articulo2):
    Solicitud("Destino 1", INICIO, FIN, articulo1, articulo2)
    mock_validaciones.validar_coleccion.assert_called_once_with((articulo1, articulo2), tipo = tuple, clase = Articulo, nombre = "lista de artículos")
    mock_validaciones.validar_str.assert_called_once_with("Destino 1", nombre = "destino")
    mock_validaciones.validar_ventana.assert_called_once_with(INICIO, FIN)
# Errores en __init__. Propagación
def test_solicitud_sinArticulos_sePropaga(mock_validaciones):
    mock_validaciones.validar_coleccion.side_effect = DatoInvalidoError("La lista de artículos no debe estar vacía")
    with pytest.raises(DatoInvalidoError, match = "La lista de artículos no debe estar vacía"):
        Solicitud("Destino 1", INICIO, FIN)
    assert Solicitud.curr_id == 0
def test_solicitud_articuloInvalido_sePropaga(mock_validaciones):
    mock_validaciones.validar_coleccion.side_effect = TypeError("Debe ser Articulo")
    with pytest.raises(TypeError, match = "Debe ser Articulo"):
        Solicitud("Destino 1", INICIO, FIN, "Articulo str")
    assert Solicitud.curr_id == 0
def test_solicitud_destinoVacio_sePropaga(mock_validaciones, articulo1):
    mock_validaciones.validar_str.side_effect = DatoInvalidoError("El destino no puede ser vacío")
    with pytest.raises(DatoInvalidoError, match = "El destino no puede ser vacío"):
        Solicitud("   ", INICIO, FIN, articulo1)
    assert Solicitud.curr_id == 0
def test_solicitud_destinoNoStr_sePropaga(mock_validaciones, articulo1):
    mock_validaciones.validar_str.side_effect = TypeError("El destino no es str")
    with pytest.raises(TypeError, match = "El destino no es str"):
        Solicitud(None, INICIO, FIN, articulo1)
    assert Solicitud.curr_id == 0
def test_solicitud_ventanaInvalida_sePropaga(mock_validaciones, articulo1):
    mock_validaciones.validar_ventana.side_effect = VentanaInvalidaError(FIN, INICIO)
    with pytest.raises(VentanaInvalidaError, match = "debe ser anterior al fin"):
        Solicitud("Destino 1", FIN, INICIO, articulo1)
    assert Solicitud.curr_id == 0
def test_solicitud_ventanaNoDatetime_sePropaga(mock_validaciones, articulo1):
    mock_validaciones.validar_ventana.side_effect = TypeError("La ventana debe ser datetime")
    with pytest.raises(TypeError, match = "La ventana debe ser datetime"):
        Solicitud("Destino 1", "09:00", "12:00", articulo1)
    assert Solicitud.curr_id == 0


# ---------- serializar ----------
def test_solicitud_serializar(solicitud, articulo1):
    articulo1.getter_id.return_value = 1
    assert solicitud.serializar() == [1, "Destino 1", INICIO, FIN, "1", "", ""]
def test_solicitud_serializar_variosArticulos(mock_validaciones, articulo1, articulo2):
    articulo1.getter_id.return_value = 1
    articulo2.getter_id.return_value = 2
    solicitud = Solicitud("Destino 1", INICIO, FIN, articulo1, articulo2)
    assert solicitud.serializar()[4] == "1,2"
def test_solicitud_serializar_conViajeYComprobante(solicitud, articulo1, viaje, comprobante):
    articulo1.getter_id.return_value = 1
    viaje.getter_id.return_value = 4
    comprobante.getter_id.return_value = 9
    solicitud.setter_viaje(viaje)
    solicitud.setter_comprobante(comprobante)
    assert solicitud.serializar() == [1, "Destino 1", INICIO, FIN, "1", 4, 9]

# ---------- deserializar ----------
ENCABEZADO = ["id", "destino", "ventana_inicio", "ventana_fin", "articulos", "id_viaje", "id_comprobante", "Solicitud"]
@pytest.fixture
def contexto(articulo1, articulo2):
    articulo1.getter_id.return_value = 1
    articulo2.getter_id.return_value = 2
    return {Articulo: [articulo1, articulo2]}
# Funcionamiento normal
def test_solicitud_deserializar_ok(mock_validaciones, contexto, articulo1, articulo2):
    archivo = [ENCABEZADO,
               ["5", "Destino 1", "2026-10-11 09:00:00", "2026-10-11 12:00:00", "1,2", "", ""],
               [],
               ["6", "Destino 2", "2026-10-11 10:00:00", "2026-10-11 13:00:00", "2", "", ""]]
    solicitudes = Solicitud.deserializar(archivo, contexto)
    assert len(solicitudes) == 2
    assert solicitudes[0].getter_id() == 5
    assert solicitudes[0].getter_destino() == "Destino 1"
    assert solicitudes[0].getter_ventana_inicio() == INICIO
    assert solicitudes[0].getter_ventana_fin() == FIN
    assert list(solicitudes[0].getter_articulos()) == [articulo1, articulo2]
    assert solicitudes[1].getter_id() == 6
    assert solicitudes[1].getter_destino() == "Destino 2"
    assert list(solicitudes[1].getter_articulos()) == [articulo2]
    # El viaje y el comprobante los asignan el Viaje y el Comprobante al cargarse
    assert solicitudes[0].getter_viaje() is None
    assert solicitudes[0].getter_comprobante() is None
    # El próximo id continúa desde el mayor
    assert Solicitud.curr_id == 6
# Sin filas
def test_solicitud_deserializar_soloEncabezado(mock_validaciones, contexto):
    assert Solicitud.deserializar([ENCABEZADO], contexto) == []
    assert Solicitud.curr_id == 0
# Una solicitud sin artículos es inválida
def test_solicitud_deserializar_sinArticulos(mock_validaciones, contexto):
    with pytest.raises(DatoInvalidoError, match = "La solicitud debe tener al menos un artículo"):
        Solicitud.deserializar([ENCABEZADO, ["5", "Destino 1", "2026-10-11 09:00:00", "2026-10-11 12:00:00", "", "", ""]], contexto)
# Artículo inexistente
def test_solicitud_deserializar_articuloInexistente(mock_validaciones, contexto):
    with pytest.raises(KeyError):
        Solicitud.deserializar([ENCABEZADO, ["5", "Destino 1", "2026-10-11 09:00:00", "2026-10-11 12:00:00", "99", "", ""]], contexto)
# Lo serializado se puede volver a cargar
def test_solicitud_serializar_deserializar(mock_validaciones, contexto, articulo1, articulo2):
    original = Solicitud("Destino 1", INICIO, FIN, articulo1, articulo2)
    fila = list(map(str, original.serializar()))
    copia = Solicitud.deserializar([ENCABEZADO, fila], contexto)[0]
    assert copia.getter_id() == original.getter_id()
    assert copia.getter_destino() == original.getter_destino()
    assert copia.getter_ventana_inicio() == original.getter_ventana_inicio()
    assert copia.getter_ventana_fin() == original.getter_ventana_fin()
    assert list(copia.getter_articulos()) == list(original.getter_articulos())
