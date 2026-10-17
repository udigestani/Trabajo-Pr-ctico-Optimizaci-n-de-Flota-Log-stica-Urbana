import csv
from pathlib import Path
from excepciones import DatoInvalidoError
from persona import Persona
from articulo import Articulo
from transporte import Transporte
from matrizdistancia import MatrizDistancia
from solicitud import Solicitud
from comprobante import Comprobante
from incidente import Incidente
from parada import Parada
from viaje import Viaje

class GestorArchivos:
    @staticmethod
    def existe(ruta):
        return Path(ruta).is_file()

    @staticmethod
    def escribir(linea1, lista, ruta):
        with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(linea1)
            escritor.writerows(lista)

    @staticmethod
    def agregar(lista, ruta):
        if not GestorArchivos.existe(ruta):
            raise DatoInvalidoError(f"La ruta {ruta} no corresponde a ningún archivo")
        with open(ruta, mode = 'a', newline = '', encoding = 'utf-8') as archivo:
            csv.writer(archivo).writerows(lista)

    @staticmethod
    def leer(ruta):
        if not GestorArchivos.existe(ruta):
            return []
        with open(ruta, mode = 'r', newline = '', encoding = 'utf-8') as archivo:
            return list(csv.reader(archivo))

    @staticmethod
    def leer_todos():
        # articulos, matriz, personas, transportes, solicitudes, comprobantes, incidentes, paradas, viajes
        carpeta = Path('archivos persistencia')
        rutas = {'articulos.csv': Articulo, 'matriz.csv': MatrizDistancia, 'personas.csv': Persona, 'transportes.csv': Transporte, 'solicitudes.csv': Solicitud, 'comprobantes.csv': Comprobante, 'incidentes.csv': Incidente, 'paradas.csv': Parada, 'viajes.csv': Viaje}
        contexto = {}
        for ruta, clase in rutas.items():
            lineas = GestorArchivos.leer(carpeta / ruta)
            contexto[clase] = clase.deserializar(lineas, contexto = contexto)
        return contexto