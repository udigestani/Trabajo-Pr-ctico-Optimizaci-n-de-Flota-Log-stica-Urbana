from incidente import Incidente 
from transporte import Transporte
from datetime import datetime, timedelta
from solicitud import Solicitud

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, matriz, estado = "PLANIFICADO"):
        self.transporte = self.validar_transporte(transporte)
        self.deposito = self.validar_deposito(deposito)
        self.horario = self.validar_horario(horario)
        self.matriz = self.validar_matriz(matriz)
        self.estado = self.validar_estado(estado)

        self.peso_total = 0
        self.volumen_total = 0
        self.solicitudes = []
        self.incidentes = []
        Viaje.curr_id += 1
        self.id = Viaje.curr_id

    def registrar_incidente(self, tipo, fecha, descripcion):
        incidente = Incidente(tipo, fecha, descripcion)
        self.incidentes.append(incidente)
        return incidente

    def agregar_solicitud(self, articulos, destino, ventana_inicio, ventana_fin):
        if self.estado != "PLANIFICADO":
            raise ValueError("No se pueden agregar solicitudes a un viaje ya iniciado o terminado")
        peso = self.peso_total
        volumen = self.volumen_total
        for articulo in articulos:
            peso += articulo.getter_peso()
            volumen += articulo.getter_volumen()
        if peso > self.transporte.peso_max:
            raise ValueError(f"El peso total de la solicitud ({peso}) excede el peso máximo del transporte ({self.transporte.peso_max})")
        elif volumen > self.transporte.volumen:
            raise ValueError(f"El volumen total de la solicitud ({volumen}) excede el volumen máximo del transporte ({self.transporte.volumen})")

        nueva_solicitud = Solicitud(articulos, destino, ventana_inicio, ventana_fin)
        if not self.validar_recorrido(self.solicitudes + [nueva_solicitud]):
            raise ValueError("La solicitud no cumple con las ventanas horarias")

        self.peso_total = peso
        self.volumen_total = volumen
        self.solicitudes.append(nueva_solicitud)
        return nueva_solicitud

    @staticmethod
    def validar_transporte(transporte):
        if isinstance(transporte, Transporte):
            return transporte
        raise TypeError(f"El transporte {transporte} debe ser de clase trasporte")

    @staticmethod
    def validar_deposito(deposito):
        if isinstance(deposito, str) and deposito.strip():
            return deposito
        raise TypeError("El depósito debe ser una cadena str no vacía")

    @staticmethod
    def validar_matriz(matriz): 
        from matrizdistancia import MatrizDistancia
        if isinstance(matriz, MatrizDistancia):
            return matriz
        raise TypeError("La matriz debe ser un objeto de clase MatrizDistancia")

    @staticmethod
    def validar_estado(estado):
        if not isinstance(estado, str):
            raise TypeError("El estado del viaje debe ser PLANIFICADO, EN_CURSO o FINALIZADO")
        if estado not in ("PLANIFICADO", "EN_CURSO", "FINALIZADO"):
            raise ValueError("El estado del viaje debe ser PLANIFICADO, EN_CURSO o FINALIZADO")
        return estado

    @staticmethod
    def validar_horario(horario):
        if not isinstance(horario, datetime):
            raise TypeError("El horario de salida del viaje debe ser un objeto datetime")
        else:
            return horario

    def validar_recorrido(self, recorrido_nuevo):
        horario = self.horario
        ubicacion = self.deposito
        for solicitud in recorrido_nuevo:
            lugar = solicitud.destino
            distancia = self.matriz.obtener_distancia(ubicacion, lugar)
            tiempo_hrs = distancia / self.transporte.velocidad
            llegada = horario + timedelta(hours=tiempo_hrs)
            if llegada > solicitud.ventana_fin:
                return False
            if llegada < solicitud.ventana_inicio:
                llegada = solicitud.ventana_inicio
            horario = llegada + timedelta(minutes=10)
            ubicacion = lugar
        distancia = self.matriz.obtener_distancia(ubicacion, self.deposito)
        tiempo_hrs = distancia / self.transporte.velocidad
        llegada = horario + timedelta(hours=tiempo_hrs)
        return True