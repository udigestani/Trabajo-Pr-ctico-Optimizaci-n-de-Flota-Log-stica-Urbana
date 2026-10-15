import csv

class GestorArchivos:
    def escribir(linea1, lista, ruta):
        with open(ruta, mode = 'w', newline = '', encoding = 'utf-8') as archivo:
            csv.writer(archivo).writerow(linea1)
            csv.writer(archivo).writerows(lista)


    





# from persona import *
# linea1 = ["dni", "nombre", "telefono", "clase"]
# persona1 = Solicitante("Uriel", 47348001, 1178787878)
# persona2 = Solicitante("Juan", 47348002, 1178787872)
# persona3 = Administrador("Massimo", 47348003, 1178787871)
# persona4 = Administrador("Manuel", 47348004, 1178787870)
# persona5 = Administrador("Bruno", 47348005, 1178787879)
# personas = [persona1, persona2, persona3, persona4, persona5]
# GestorArchivos.escribir(linea1, map(lambda per: per.serializar(), personas), 'archivos persistencia\personas.csv')