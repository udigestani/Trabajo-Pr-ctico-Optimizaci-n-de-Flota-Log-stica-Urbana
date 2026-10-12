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
    assert solicitud.destino == "Destino 1"
    assert solicitud.ventana_inicio == INICIO
    assert solicitud.ventana_fin == FIN
    assert solicitud.articulos == (articulo1,)
    assert solicitud.viaje is None
    assert solicitud.comprobante is None
    # id
    assert solicitud.id == 1
    solicitud2 = Solicitud("Destino 2", INICIO, FIN, articulo1, articulo2)
    assert solicitud2.id == 2
    # Varios articulos
    assert solicitud2.articulos == (articulo1, articulo2)
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
    assert solicitud.articulos == (articulo1, )
    with pytest.raises(AttributeError):
        solicitud.setter_destino("Destino 100")
    assert solicitud.destino == "Destino 1"
    with pytest.raises(AttributeError):
        solicitud.setter_ventana_inicio(FIN)
    assert solicitud.ventana_inicio == INICIO
    with pytest.raises(AttributeError):
        solicitud.setter_ventana_fin(INICIO)
    assert solicitud.ventana_fin == FIN
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