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

def hola_mundo():
    return "hola_mundo"     
        
def main():
    print(hola_mundo())
    admin = Administrador("Admin", 23456789, 1144444444)
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
    camion = Camion()
    viaje = admin.crear_viaje(camion, "Deposito", datetime(2024,6,1,8,0), matriz)
    articulos = [Articulo(f"Producto {i}", i, 4) for i in range(1, 11)]
    solic = Solicitante("Solicitante", 22222222, 1199988887)
    solic.crear_solicitud(viaje, "Destino S1", datetime(2024,6,1,9,0) , datetime(2024,6,1,9,15), art_1 = articulos[0], art_2 = articulos[1], art_3 = articulos[2], art_4 = articulos[3], art_5 = articulos[4])








# No cambiar a partir de aqui
if __name__ == "__main__":
    main()


    #LISTAS ENLAZADAS NO VA
    #DICCIONARIO SE PUEDE, LISTA DE LISTAS NO SE PUEDE
    #TESTING SI --> 3 CLASES TESTEADAS, UNA CON MUCHO CONTENIDO (IMPORTANTE)
    #USAR CONCEPTOS COMO MOCK, ASSERT, Y QUE NO SEA REDUNDANTE
    #TIENE QUE ANDAR, ESTAR COMPLETO Y HACER UNA PARTE BÁSICA DEL ENUNCIADO




# Traceback (most recent call last):
#   File "c:\Users\pacoe\Downloads\ESTRUCTURA DE DATOS\Trabajo-Pr-ctico-Optimizaci-n-de-Flota-Log-stica-Urbana\main.py", line 48, in <module>
#     main()
#   File "c:\Users\pacoe\Downloads\ESTRUCTURA DE DATOS\Trabajo-Pr-ctico-Optimizaci-n-de-Flota-Log-stica-Urbana\main.py", line 37, in main
#     solic.crear_solicitud(viaje, "Destino S1", datetime(2024,6,1,9,0) , datetime(2024,6,1,8,0), art_1 = articulos[0], art_2 = articulos[1], art_3 = articulos[2], art_4 = articulos[3], art_5 = articulos[4])
#   File "c:\Users\pacoe\Downloads\ESTRUCTURA DE DATOS\Trabajo-Pr-ctico-Optimizaci-n-de-Flota-Log-stica-Urbana\persona.py", line 59, in crear_solicitud
#     raise ValueError(f"El volumen total de la solicitud ({volumen}) excede el volumen máximo del transporte ({viaje.transporte.volumen})")
# ValueError: El volumen total de la solicitud (30) excede el volumen máximo del transporte (20)
# PS C:\Users\pacoe\Downloads\ESTRUCTURA DE DATOS> 