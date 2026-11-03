import csv
from pathlib import Path
from excepciones import DatoInvalidoError

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
