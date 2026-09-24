from articulo import Articulo
from comprobante import Comprobante
from incidente import Incidente
from parada import Parada
from persona import Persona
from solicitud import Solicitud
from transporte import Transporte, Camion, Motocicleta, Furgoneta
from viaje import Viaje
from persona import Persona, Administrador, Solicitante
from matrizDistancia import MatrizDistancia
from datetime import datetime

def main():
    juan = Administrador("Juan", 23456789, 1144444444)
    
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
    print(matriz.distancias)
    
    camion = Camion()
    viaje = juan.crear_viaje(camion, "Deposito", datetime(2024,6,1,8,0), matriz)

    articulos = [Articulo(f"Producto {i}", i, 0.3*i) for i in range(1, 11)]

    solic = Solicitante("Solicitante", 22222222, 1199988887)

    solic.crear_solicitud(viaje, "Destino S1", datetime(2024,6,1,9,0) , datetime(2024,6,1,9,15), art_1 = articulos[0], art_2 = articulos[1], art_3 = articulos[2], art_4 = articulos[3], art_5 = articulos[4])
    solic.crear_solicitud(viaje, "Destino S2", datetime(2024,6,1,9,30) , datetime(2024,6,1,9,45), art_1 = articulos[5], art_2 = articulos[6], art_3 = articulos[7], art_4 = articulos[8], art_5 = articulos[9])
    print(camion.calcular_impacto_ambiental(viaje.distancia_total(),viaje.peso_total))
    viaje.iniciar_viaje()
    viaje.registrar_entrega(datetime(2024,6,1,9,0), "RECEPTOR", 100)
    # viaje.registrar_entrega(datetime(2024,6,1,9,40), "RECEPTOR1", 120)
    print(viaje.registrar_incidente ("DAÑO", datetime(2024,6,1,9,0), "Pinchamos goma pa"))
    print(viaje.incidentes)

    

    

# No cambiar a partir de aqui
if __name__ == "__main__":
    main()


    #LISTAS ENLAZADAS NO VA
    #DICCIONARIO SE PUEDE, LISTA DE LISTAS NO SE PUEDE
    #TESTING SI --> 3 CLASES TESTEADAS, UNA CON MUCHO CONTENIDO (IMPORTANTE)
    #USAR CONCEPTOS COMO MOCK, ASSERT, Y QUE NO SEA REDUNDANTE
    #TIENE QUE ANDAR, ESTAR COMPLETO Y HACER UNA PARTE BÁSICA DEL ENUNCIADO

