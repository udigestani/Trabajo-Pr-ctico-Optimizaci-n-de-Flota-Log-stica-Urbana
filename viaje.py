from incidente import Incidente 
from transporte import Transporte
from datetime import datetime, timedelta
from solicitud import Solicitud
from parada import Parada
from cola import Cola
from pila import Pila
from politicaordenamiento import Vecinos, VentanasTiempo
from validaciones import Validaciones
from excepciones import DatoInvalidoError, ExcesoPesoError, ExcesoVolumenError, EstadoInvalidoError, VentanaIncumplidaError, ViajeVacioError, SinParadasPendientesError, ViajeIncompletoError, SolicitudDuplicadaError, RutaIncompletaError, TransicionIlegalError
from functools import reduce
from itertools import chain

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, matriz, estado = "PLANIFICADO"):
        self.transporte = Validaciones.validar_instancia(transporte, clase = Transporte, nombre = "transporte")
        self.deposito = Validaciones.validar_str(deposito, nombre = "depósito")
        self.horario = Validaciones.validar_fecha(horario, nombre = "horario de salida del viaje")
        self.matriz = self.validar_matriz(matriz)
        self.estado = Validaciones.validar_en(estado, opciones = "PLANIFICADO, EN_CURSO, FINALIZADO", nombre = "estado del viaje")

        self.peso_total = 0
        self.volumen_total = 0
        self.solicitudes = []
        self.incidentes = []
        self.paradas = Cola()
        self.paradas_resueltas = []
        self.historial_solicitudes = Pila()
        Viaje.curr_id += 1
        self.id = Viaje.curr_id


    def crear_solicitud(self, destino, ventana_inicio, ventana_fin, *articulos):
        if self.estado != "PLANIFICADO":
            raise EstadoInvalidoError("crear_solicitud", self.estado)
        nueva_solicitud = Solicitud(destino, ventana_inicio, ventana_fin, *articulos)
        self.agregar_solicitud(nueva_solicitud)
        return nueva_solicitud

    @staticmethod
    def validar_matriz(matriz):
        from matrizdistancia import MatrizDistancia
        return Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")

    def validar_recorrido(self, recorrido_nuevo):
        horario = self.horario
        ubicacion = self.deposito
        for solicitud in recorrido_nuevo:
            lugar = solicitud.getter_destino()
            distancia = self.matriz.obtener_distancia(ubicacion, lugar)
            tiempo_hrs = distancia / self.transporte.getter_velocidad()
            llegada = horario + timedelta(hours=tiempo_hrs)
            if llegada > solicitud.getter_ventana_fin():
                raise VentanaIncumplidaError(lugar, llegada, solicitud.getter_ventana_fin())
            if llegada < solicitud.getter_ventana_inicio():
                llegada = solicitud.getter_ventana_inicio()
            horario = llegada + timedelta(minutes=10)
            ubicacion = lugar
        # distancia = self.matriz.obtener_distancia(ubicacion, self.deposito) #NO LO ESTAMOS USANDO, desde acá ya es True a menos que la matriz esté incompleta
        # tiempo_hrs = distancia / self.transporte.getter_velocidad()
        # llegada = horario + timedelta(hours=tiempo_hrs)
        return True

    def distancia_total(self):
        ubicacion = self.deposito
        distancia = 0
        for solicitud in self.solicitudes:
            lugar = solicitud.getter_destino()
            distancia += self.matriz.obtener_distancia(ubicacion, lugar)
            ubicacion = lugar
        distancia += self.matriz.obtener_distancia(ubicacion, self.deposito)
        return distancia
    def getter_estado(self):
        return self.estado
    def getter_peso(self):
        return self.peso_total
    def getter_volumen(self):
        return self.volumen_total
    def getter_peso_max(self):
        return self.transporte.getter_peso_max()
    def getter_volumen_max(self):
        return self.transporte.getter_volumen()
    def getter_solicitudes(self):
        return self.solicitudes.copy()
    def getter_id(self):
        return self.id
    def getter_transporte(self):
        return self.transporte
    def getter_incidentes(self):
        return self.incidentes.copy()
    def getter_paradas(self):
        return self.paradas_resueltas + self.paradas_pendientes()
    def paradas_pendientes(self):
        return list(self.paradas)
    def setter_estado(self, estado):
        if self.estado == "FINALIZADO" or (self.estado == "EN_CURSO" and estado != "FINALIZADO") or (self.estado == "PLANIFICADO" and estado != "EN_CURSO"):
            raise TransicionIlegalError(f"El ciclo de un viaje es PLANIFICADO -> EN_CURSO -> FINALIZADO")
        self.estado = Validaciones.validar_en(estado, opciones = "PLANIFICADO, EN_CURSO, FINALIZADO", nombre = "estado del viaje")
        return None
    def setter_peso(self, peso):
        self.peso_total = Validaciones.validar_numero(peso, cero = True, nombre = "peso")
        return None
    def setter_volumen(self, volumen):
        self.volumen_total = Validaciones.validar_numero(volumen, cero = True, nombre = "volumen")
        return None

    def agregar_solicitud(self, nueva_solicitud):
        Validaciones.validar_instancia(nueva_solicitud, clase = Solicitud, nombre = "solicitud")
        if self.estado != "PLANIFICADO":
            raise EstadoInvalidoError("agregar_solicitud", self.estado)
        viaje_anterior = nueva_solicitud.getter_viaje()
        if viaje_anterior is not None and (viaje_anterior.getter_estado() in ("PLANIFICADO", "EN_CURSO") or nueva_solicitud.getter_comprobante() is not None):
            raise SolicitudDuplicadaError(nueva_solicitud.getter_id())
        articulos = nueva_solicitud.getter_articulos()
        peso = reduce(lambda x, y: x + y, map(lambda a: a.getter_peso(), articulos), self.peso_total)
        volumen = reduce(lambda x, y: x + y, map(lambda a: a.getter_volumen(), articulos), self.volumen_total)
        if peso > self.transporte.getter_peso_max():
            raise ExcesoPesoError(self.transporte.getter_peso_max(), peso)
        elif volumen > self.transporte.getter_volumen():
            raise ExcesoVolumenError(self.transporte.getter_volumen(), volumen)
        self.validar_recorrido(chain(self.solicitudes, (nueva_solicitud,)))
        self.peso_total = peso
        self.volumen_total = volumen
        self.solicitudes.append(nueva_solicitud)
        self.historial_solicitudes.apilar(nueva_solicitud)
        nueva_solicitud.setter_viaje(self)
        return None

    def deshacer_ultima_solicitud(self):
        if self.estado != "PLANIFICADO":
            raise EstadoInvalidoError("deshacer_ultima_solicitud", self.estado)
        if self.historial_solicitudes.esVacia():
            raise ViajeVacioError("Viaje Vacio: No hay solicitudes para deshacer")
        solicitud = self.historial_solicitudes.desapilar()
        articulos = solicitud.getter_articulos()
        self.peso_total -= sum(map(lambda a: a.getter_peso(), articulos))
        self.volumen_total -= sum(map(lambda a: a.getter_volumen(), articulos))
        self.solicitudes.remove(solicitud)
        solicitud.setter_viaje(None)
        return solicitud
    def __str__(self):
        tipo_transporte = self.transporte.getter_tipo()
        fecha = self.horario.strftime('%Y-%m-%d %H:%M')
        return f"Viaje {self.id} [{self.estado}] - {tipo_transporte} saliendo de {self.deposito} a las {fecha}"
    def __repr__(self):
        return f"<Viaje {self.id} {self.estado} paradas={len(self.solicitudes)}>"
        
    def __eq__(self, otro):
        if isinstance(otro, Viaje):
            return self.id == otro.getter_id()
        return False
    def __hash__(self):
        return hash(self.id)

    def ordenar_solicitudes(self):
        try:
            orden = Vecinos.sugerir_orden(self.deposito, self.solicitudes, self.matriz)
            self.validar_recorrido(orden)
            return orden
        except (VentanaIncumplidaError, RutaIncompletaError):
            try:
                orden = VentanasTiempo.sugerir_orden(self.deposito, self.solicitudes, self.matriz)
                self.validar_recorrido(orden)
                return orden
            except (VentanaIncumplidaError, RutaIncompletaError):
                return self.solicitudes

    # DESDE ACÁ EL VIAJE ESTÁ INICIADO
    def iniciar_viaje(self):
        if self.estado != "PLANIFICADO":
            raise EstadoInvalidoError("iniciar_viaje", self.estado)
        if not self.solicitudes:
            raise ViajeVacioError("Viaje Vacio: El viaje aún no tiene solicitudes")
        
        self.solicitudes = self.ordenar_solicitudes()
        self.paradas = Cola()
        self.paradas_resueltas = []
        horario = self.horario
        ubicacion = self.deposito
        for i in range(len(self.solicitudes)):
            solicitud = self.solicitudes[i]
            lugar = solicitud.getter_destino()
            distancia = self.matriz.obtener_distancia(ubicacion, lugar)
            tiempo_hrs = distancia / self.transporte.getter_velocidad()
            horario += timedelta(hours=tiempo_hrs)
            if horario < solicitud.getter_ventana_inicio():
                horario = solicitud.getter_ventana_inicio()
            nueva_parada = Parada(orden=i+1, solicitud=solicitud, hora_prev=horario, hora_real=None)
            self.paradas.encolar(nueva_parada)
            horario += timedelta(minutes=10)
            ubicacion = lugar
        self.estado = "EN_CURSO"

    def registrar_entrega(self, hora_real, receptor, monto):
        if self.estado != "EN_CURSO":
            raise EstadoInvalidoError("registrar_entrega", self.estado)
        Validaciones.validar_fecha(hora_real, nombre = "hora de entrega")
        if hora_real < self.horario:
            raise DatoInvalidoError("La hora de entrega no puede ser anterior al horario de salida del viaje")
        if self.paradas_resueltas and hora_real < self.paradas_resueltas[-1].getter_hora_real():
            raise DatoInvalidoError("La hora de entrega no puede ser anterior a la de la parada previa")
        if self.paradas.esVacia():
            raise SinParadasPendientesError("registrar_entrega")
        parada_pendiente = self.paradas.frente()
        comprobante = parada_pendiente.generar_comprobante(receptor, hora_real, monto)
        self.paradas_resueltas.append(self.paradas.desencolar())
        if self.paradas.esVacia():
            self.finalizar_viaje()
        return comprobante

    def registrar_incidente(self, tipo, fecha, descripcion, **detalles):
        if self.estado != "EN_CURSO":
            raise EstadoInvalidoError("registrar_incidente", self.estado)
        Validaciones.validar_fecha(fecha, nombre = "fecha del incidente")
        if fecha < self.horario:
            raise DatoInvalidoError("La fecha del incidente no puede ser anterior al horario de salida del viaje")
        if self.paradas_resueltas and fecha < self.paradas_resueltas[-1].getter_hora_real():
            raise DatoInvalidoError("La fecha del incidente no puede ser anterior a la de la parada previa")
        if self.paradas.esVacia():
            raise SinParadasPendientesError("registrar_incidente")
        parada_pendiente = self.paradas.frente()
        incidente = Incidente(tipo, fecha, descripcion, parada_pendiente.getter_solicitud(), **detalles)
        parada_pendiente.setter_estado("FALLIDA")
        parada_pendiente.setter_hora_real(fecha)
        self.incidentes.append(incidente)
        self.paradas_resueltas.append(self.paradas.desencolar())
        if self.paradas.esVacia():
            self.finalizar_viaje()
        return incidente

    def finalizar_viaje(self):
        if self.estado != "EN_CURSO":
            raise EstadoInvalidoError("finalizar_viaje", self.estado)
        if not self.paradas.esVacia():
            raise ViajeIncompletoError(self.paradas.get_longitud())
        self.estado = "FINALIZADO"
        print(f"VIAJE FINALIZADO: {self.deposito}", self.paradas_resueltas, sep=", ")