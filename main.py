from articulo import Articulo
from comprobante import Comprobante
from incidente import Incidente
from parada import Parada
from persona import Persona
from solicitud import Solicitud
from transporte import Transporte, Camion, Motocicleta, Furgoneta
from viaje import Viaje
from persona import Persona, Administrador, Solicitante
from matrizdistancia import MatrizDistancia
from datetime import datetime
from excepciones import FlotaError, DatoInvalidoError, CapacidadExcedidaError, VentanaIncumplidaError, RutaIncompletaError, TransicionIlegalError

def main():
    try:
        juan = Administrador("Juan", 23456789, 1144444444)
        solic = Solicitante("Solicitante", 22222222, 1199988887)

        matriz = MatrizDistancia()
        matriz.cargar_matriz([
            ("Deposito", "Destino S1", 15),
            ("Destino S1", "Deposito", 15),
            ("Deposito", "Destino S2", 20),
            ("Destino S2", "Deposito", 20),
            ("Deposito", "Destino S3", 10),
            ("Destino S3", "Deposito", 10),
            ("Destino S1", "Destino S2", 5),
            ("Destino S2", "Destino S1", 5),
            ("Destino S1", "Destino S3", 8),
            ("Destino S3", "Destino S1", 8),
            ("Destino S2", "Destino S3", 12),
            ("Destino S3", "Destino S2", 12)])
        print(matriz.getter_distancias())

        camion = Camion()
        viaje = juan.crear_viaje(camion, "Deposito", datetime(2024,6,1,8,0), matriz)

        articulos = []
        for i in range(1,11):
            articulos.append(Articulo(f"Prod {i}", i, 0.3*i))
    except DatoInvalidoError as e:
        print(f"Error de datos al preparar el escenario: {e}")
        return
    except (TypeError, FlotaError) as e:
        print(f"Error al preparar el escenario: {e}")
        return

    # Cada solicitud se intenta por separado: si una falla, las demás se siguen cargando
    pedidos = [
        ("Destino S1", datetime(2024,6,1,9,0), datetime(2024,6,1,9,15), articulos[0:5]),
        ("Destino S2", datetime(2024,6,1,9,30), datetime(2024,6,1,9,45), articulos[5:10]),
    ]
    for destino, inicio, fin, arts in pedidos:
        try:
            solic.crear_solicitud(viaje, destino, inicio, fin, *arts)
        except CapacidadExcedidaError as e:
            print(f"Solicitud a {destino} rechazada por capacidad: {e}")
        except VentanaIncumplidaError as e:
            print(f"Solicitud a {destino} rechazada por ventana horaria: {e}")
        except RutaIncompletaError as e:
            print(f"Solicitud a {destino} rechazada, falta la distancia: {e}")
        except DatoInvalidoError as e:
            print(f"Solicitud a {destino} con datos inválidos: {e}")
        except (TransicionIlegalError, TypeError) as e:
            print(f"Solicitud a {destino} no permitida: {e}")

    try:
        print(camion.calcular_impacto_ambiental(viaje.distancia_total(), viaje.getter_peso()))
        viaje.iniciar_viaje()
        viaje.registrar_entrega(datetime(2024,6,1,9,0), "RECEPTOR", 100)
        # viaje.registrar_entrega(datetime(2024,6,1,9,40), "RECEPTOR1", 120)
        print(viaje.registrar_incidente("DAÑO", datetime(2024,6,1,9,0), "Pinchamos goma pa", rueda="delantera"))
        print(viaje.getter_incidentes())
    except TransicionIlegalError as e:
        print(f"Operación no permitida en el estado actual del viaje: {e}")
    except DatoInvalidoError as e:
        print(f"Dato inválido en el recorrido del viaje: {e}")
    except RutaIncompletaError as e:
        print(f"No se puede calcular el recorrido: {e}")
    except (TypeError, FlotaError) as e:
        print(f"Error en el viaje: {e}")
    finally:
        print(f"Estado final del viaje: {viaje.getter_estado()}")

# No cambiar a partir de aqui
if __name__ == "__main__":
    main()


    #LISTA DE LISTAS NO SE PUEDE
    #USAR MOCK Y QUE NO SEA REDUNDANTE