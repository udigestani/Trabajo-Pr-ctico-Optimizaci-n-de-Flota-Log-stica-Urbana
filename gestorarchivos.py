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
from zona import Zona

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
        rutas = {'zonas.csv': Zona, 'articulos.csv': Articulo, 'matriz.csv': MatrizDistancia, 'personas.csv': Persona, 'transportes.csv': Transporte, 'solicitudes.csv': Solicitud, 'comprobantes.csv': Comprobante, 'incidentes.csv': Incidente, 'paradas.csv': Parada, 'viajes.csv': Viaje}
        contexto = {}
        for ruta, clase in rutas.items():
            lineas = GestorArchivos.leer(carpeta / ruta)
            contexto[clase] = clase.deserializar(lineas, contexto = contexto)
        return contexto

    @staticmethod
    def guardar_todos(contexto):
        carpeta = Path('archivos persistencia')
        rutas = {'zonas.csv': (Zona, "id,nombre,ubicaciones,Zona"),
                  'articulos.csv': (Articulo, "id,descripcion,peso,volumen,Articulo"),
                  'matriz.csv': (MatrizDistancia, "origen,destino,km,MatrizDistancia"), 
                  'personas.csv': (Persona, "clase,nombre,dni,telefono,Persona"), 
                  'transportes.csv': (Transporte, "tipo,id,peso_max,volumen,velocidad,costo_km,costo_parada,factor_ambiental,zonas_habilitadas,Transporte"), 
                  'solicitudes.csv': (Solicitud, "id,destino,ventana_inicio,ventana_fin,articulos,id_viaje,id_comprobante,Solicitud"), 
                  'comprobantes.csv': (Comprobante, "id,id_solicitud,fecha_hora,receptor,monto,Comprobante"), 
                  'incidentes.csv': (Incidente, "id,tipo,fecha,descripcion,clase_afectado,id_afectado,detalles,Incidente"), 
                  'paradas.csv': (Parada, "id,orden,id_solicitud,hora_prev,hora_real,estado,id_comprobante,Parada"), 
                  'viajes.csv': (Viaje, "id,id_transporte,deposito,horario,estado,solicitudes,incidentes,paradas,paradas_resueltas,historial_solicitudes,Viaje")}
        for ruta, (clase, linea1) in rutas.items():
            datos = contexto[clase]
            if clase is MatrizDistancia:
                datos = datos.serializar()
            else:
                datos = list(map(lambda x: x.serializar(), datos))
            GestorArchivos.escribir(linea1.split(","), datos, carpeta / ruta)
        return None

# contexto = GestorArchivos.leer_todos()
# GestorArchivos.guardar_todos(contexto)