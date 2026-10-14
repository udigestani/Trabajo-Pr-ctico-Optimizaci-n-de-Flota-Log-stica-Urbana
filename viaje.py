from incidente import Incidente 
from transporte import Transporte
from datetime import datetime, timedelta
from solicitud import Solicitud
from parada import Parada
from cola import Cola
from pila import Pila
from politicaordenamiento import Vecinos, VentanasTiempo
from validaciones import Validaciones
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError, ExcesoPesoError, ExcesoVolumenError, EstadoInvalidoError, VentanaIncumplidaError, ViajeVacioError, SinParadasPendientesError, ViajeIncompletoError, SolicitudDuplicadaError, RutaIncompletaError, TransicionIlegalError
from itertools import chain

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, matriz):
        self.transporte = Validaciones.validar_instancia(transporte, clase = Transporte, nombre = "transporte")
        self.deposito = Validaciones.validar_str(deposito, nombre = "depósito")
        self.horario = Validaciones.validar_fecha(horario, nombre = "horario de salida del viaje")
        self.matriz = Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")
        self.estado = "PLANIFICADO"

        self.peso_total = 0
        self.volumen_total = 0
        self.solicitudes = []
        self.incidentes = []
        self.paradas = Cola()
        self.paradas_resueltas = []
        self.historial_solicitudes = Pila()
        Viaje.curr_id += 1
        self.id = Viaje.curr_id

    def _validar_estado(self, accion, estado_requerido):
        if self.estado != estado_requerido:
            raise EstadoInvalidoError(accion, self.estado)

    def crear_solicitud(self, destino, ventana_inicio, ventana_fin, *articulos):
        self._validar_estado("crear_solicitud", "PLANIFICADO")
        nueva_solicitud = Solicitud(destino, ventana_inicio, ventana_fin, *articulos)
        self.agregar_solicitud(nueva_solicitud)
        return nueva_solicitud

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
        estado = Validaciones.validar_en(estado, opciones = "PLANIFICADO, EN_CURSO, FINALIZADO", nombre = "estado del viaje")
        if self.estado == "FINALIZADO" or (self.estado == "EN_CURSO" and estado != "FINALIZADO") or (self.estado == "PLANIFICADO" and estado != "EN_CURSO"):
            raise TransicionIlegalError("El ciclo de un viaje es PLANIFICADO -> EN_CURSO -> FINALIZADO")
        self.estado = estado
        return None
    def setter_peso(self, peso):
        peso = Validaciones.validar_numero(peso, cero = True, nombre = "peso")
        if peso > self.transporte.getter_peso_max():
            raise ExcesoPesoError(self.transporte.getter_peso_max(), peso)
        self.peso_total = peso
        return None
    def setter_volumen(self, volumen):
        volumen = Validaciones.validar_numero(volumen, cero = True, nombre = "volumen")
        if volumen > self.transporte.getter_volumen():
            raise ExcesoVolumenError(self.transporte.getter_volumen(), volumen)
        self.volumen_total = volumen
        return None

    def agregar_solicitud(self, nueva_solicitud):
        Validaciones.validar_instancia(nueva_solicitud, clase = Solicitud, nombre = "solicitud")
        self._validar_estado("agregar_solicitud", "PLANIFICADO")
        if nueva_solicitud in self.solicitudes or nueva_solicitud.esta_asignada() or nueva_solicitud.esta_entregada():
            raise SolicitudDuplicadaError(nueva_solicitud.getter_id())
        if nueva_solicitud.getter_destino() == self.deposito:
            raise DatoInvalidoError(f"El destino de la solicitud {nueva_solicitud.getter_id()} no puede ser el depósito ({self.deposito})")
        peso = self.peso_total + nueva_solicitud.getter_peso()
        volumen = self.volumen_total + nueva_solicitud.getter_volumen()
        if peso > self.transporte.getter_peso_max():
            raise ExcesoPesoError(self.transporte.getter_peso_max(), peso)
        elif volumen > self.transporte.getter_volumen():
            raise ExcesoVolumenError(self.transporte.getter_volumen(), volumen)
        self.validar_recorrido([*self.solicitudes, nueva_solicitud])
        self.peso_total = peso
        self.volumen_total = volumen
        self.solicitudes.append(nueva_solicitud)
        self.historial_solicitudes.apilar(nueva_solicitud)
        nueva_solicitud.setter_viaje(self)
        return None

    def deshacer_ultima_solicitud(self):
        self._validar_estado("deshacer_ultima_solicitud", "PLANIFICADO")
        if self.historial_solicitudes.esVacia():
            raise ViajeVacioError("Viaje Vacio: No hay solicitudes para deshacer")
        solicitud = self.historial_solicitudes.desapilar()
        self.peso_total -= solicitud.getter_peso()
        self.volumen_total -= solicitud.getter_volumen()
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
        self._validar_estado("iniciar_viaje", "PLANIFICADO")
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
        self._validar_estado("registrar_entrega", "EN_CURSO")
        if self.paradas_resueltas:
            inicio = self.paradas_resueltas[-1].getter_hora_real()
            Validaciones.validar_ventana(inicio, hora_real, nombre_inicio = "fecha de la parada previa", nombre_fin = "fecha de entrega")
        else:
            Validaciones.validar_ventana(self.horario, hora_real, nombre_inicio = "fecha de salida del viaje", nombre_fin = "fecha de entrega")
        if self.paradas.esVacia():
            raise SinParadasPendientesError("registrar_entrega")
        parada_pendiente = self.paradas.frente()
        comprobante = parada_pendiente.generar_comprobante(receptor, hora_real, monto)
        self.paradas_resueltas.append(self.paradas.desencolar())
        if self.paradas.esVacia():
            self.finalizar_viaje()
        return comprobante

    def registrar_incidente(self, tipo, fecha, descripcion, **detalles):
        self._validar_estado("registrar_incidente", "EN_CURSO")
        if self.paradas_resueltas:
            inicio = self.paradas_resueltas[-1].getter_hora_real()
            Validaciones.validar_ventana(inicio, fecha, nombre_inicio = "fecha de la parada previa", nombre_fin = "fecha del incidente")
        else:
            Validaciones.validar_ventana(self.horario, fecha, nombre_inicio = "fecha de salida del viaje", nombre_fin = "fecha del incidente")
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
        self._validar_estado("finalizar_viaje", "EN_CURSO")
        if not self.paradas.esVacia():
            raise ViajeIncompletoError(self.paradas.get_longitud())
        self.estado = "FINALIZADO"
        print(f"VIAJE FINALIZADO: {self.deposito}", self.paradas_resueltas, sep=", ")