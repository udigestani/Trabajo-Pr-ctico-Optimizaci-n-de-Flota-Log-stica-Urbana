from incidente import Incidente 
from transporte import Transporte
from datetime import datetime, timedelta
from solicitud import Solicitud
from parada import Parada
from cola import Cola
from pila import Pila
from validaciones import Validaciones
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError, ExcesoPesoError, ExcesoVolumenError, EstadoInvalidoError, VentanaIncumplidaError, ViajeVacioError, SinParadasPendientesError, ViajeIncompletoError, SolicitudDuplicadaError, TransicionIlegalError

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, matriz):
        self.transporte = Validaciones.validar_instancia(transporte, clase = Transporte, nombre = "transporte")
        self.deposito = Validaciones.validar_str(deposito, nombre = "depósito")
        self.horario = Validaciones.validar_fecha(horario, nombre = "horario de salida del viaje")
        self.matriz = Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")
        self.estado = "PLANIFICADO"

        self.solicitudes = []
        self.incidentes = []
        self.paradas = Cola()
        self.paradas_resueltas = []
        self.historial_solicitudes = Pila()
        Viaje.curr_id += 1
        self.id = Viaje.curr_id

    def validar_estado(self, accion, estado_requerido):
        if self.estado != estado_requerido:
            raise EstadoInvalidoError(accion, self.estado)

    def crear_solicitud(self, destino, ventana_inicio, ventana_fin, *articulos):
        self.validar_estado("crear_solicitud", "PLANIFICADO")
        nueva_solicitud = Solicitud(destino, ventana_inicio, ventana_fin, *articulos)
        self.agregar_solicitud(nueva_solicitud)
        return nueva_solicitud

    def calcular_horarios(self, recorrido, indice = 0, horario = None, ubicacion = None):
        if horario is None:
            horario = self.horario
        if ubicacion is None:
            ubicacion = self.deposito
        if indice == len(recorrido):
            return []
        solicitud = recorrido[indice]
        lugar = solicitud.getter_destino()
        distancia = self.matriz.obtener_distancia(ubicacion, lugar)
        tiempo_hrs = distancia / self.transporte.getter_velocidad()
        llegada = horario + timedelta(hours=tiempo_hrs)
        if llegada > solicitud.getter_ventana_fin():
            raise VentanaIncumplidaError(lugar, llegada, solicitud.getter_ventana_fin())
        if llegada < solicitud.getter_ventana_inicio():
            llegada = solicitud.getter_ventana_inicio()
        return [llegada] + self.calcular_horarios(recorrido, indice = indice + 1, horario = llegada + timedelta(minutes=10), ubicacion = lugar)

    def validar_recorrido(self, recorrido):
        self.calcular_horarios(recorrido)
        ultimo_lugar = self.deposito
        if recorrido:
            ultimo_lugar = recorrido[-1].getter_destino()
        self.matriz.obtener_distancia(ultimo_lugar, self.deposito)
        return True

    def distancia_total(self, ubicacion = None, restantes = None):
        if ubicacion is None:
            ubicacion = self.deposito
        if restantes is None:
            restantes = self.solicitudes
        if not restantes:
            return self.matriz.obtener_distancia(ubicacion, self.deposito)
        lugar = restantes[0].getter_destino()
        distancia = self.matriz.obtener_distancia(ubicacion, lugar)
        return distancia + self.distancia_total(lugar, restantes[1:])

    def costo_total(self, orden = None):
        if orden is None:
            orden = self.solicitudes
        costo_distancia = self.distancia_total(self.deposito, orden) * self.transporte.getter_costo_km()
        costo_paradas = len(orden) * self.transporte.getter_costo_parada()
        return costo_distancia + costo_paradas

    def impacto_ambiental(self):
        return self.transporte.calcular_impacto_ambiental(self.distancia_total(self.deposito, self.solicitudes), self.getter_peso())
    def ultimo_lugar(self):
        if self.solicitudes:
            return self.solicitudes[-1].getter_destino()
        return self.deposito
    def getter_horario(self):
        return self.horario
    def getter_matriz(self):
        return self.matriz
    def getter_estado(self):
        return self.estado
    def getter_peso(self):
        return sum(map(lambda s: s.getter_peso(), self.solicitudes))
    def getter_volumen(self):
        return sum(map(lambda s: s.getter_volumen(), self.solicitudes))
    def getter_peso_max(self):
        return self.transporte.getter_peso_max()
    def getter_volumen_max(self):
        return self.transporte.getter_volumen()
    def getter_solicitudes(self):
        return self.solicitudes.copy()
    def getter_id(self):
        return self.id
    def setter_id(self, id):
        self.id = id
    def setter_estado(self, estado):
        self.estado = Validaciones.validar_en(estado, opciones = ("PLANIFICADO", "EN_CURSO", "FINALIZADO"), nombre = "estado")
    def setter_solicitudes(self, solicitudes):
        self.solicitudes = list(solicitudes)
    def setter_incidentes(self, incidentes):
        self.incidentes = list(incidentes)
    def setter_paradas(self, paradas):
        self.paradas = Cola()
        for parada in paradas:
            self.paradas.encolar(parada)
    def setter_paradas_resueltas(self, paradas):
        self.paradas_resueltas = list(paradas)
    def setter_historial_solicitudes(self, solicitudes):
        self.historial_solicitudes = Pila()
        for solicitud in solicitudes:
            self.historial_solicitudes.apilar(solicitud)
    def getter_deposito(self):
        return self.deposito
    def getter_transporte(self):
        return self.transporte
    def getter_incidentes(self):
        return self.incidentes.copy()
    def getter_paradas(self):
        return self.paradas_resueltas + self.paradas_pendientes()
    def paradas_pendientes(self):
        return list(self.paradas)
    def es_parada_actual(self, parada):
        return self.estado == "EN_CURSO" and not self.paradas.esVacia() and self.paradas.frente() is parada

    def serializar(self):
        return [self.id, self.transporte.getter_id(), self.deposito, self.horario, self.estado, ",".join(map(lambda x: str(x.getter_id()), self.solicitudes)), ",".join(map(lambda x: str(x.getter_id()), self.incidentes)), ",".join(map(lambda x: str(x.getter_id()), self.paradas)), ",".join(map(lambda x: str(x.getter_id()), self.paradas_resueltas)), ",".join((list(map(lambda x: str(x.getter_id()), self.historial_solicitudes)))[::-1])]
    
    @classmethod
    def deserializar(cls, archivo, contexto):
        matriz = contexto[MatrizDistancia]
        transportes = dict(map(lambda tr: (tr.getter_id(), tr), contexto[Transporte]))
        solicitudes = dict(map(lambda sol: (sol.getter_id(), sol), contexto[Solicitud]))
        incidentes = dict(map(lambda inc: (inc.getter_id(), inc), contexto.get(Incidente, [])))
        paradas = dict(map(lambda par: (par.getter_id(), par), contexto.get(Parada, [])))
        viajes = []
        for fila in archivo[1:]:
            if fila:
                ids = list(map(lambda celda: list(map(int, filter(None, celda.split(",")))), fila[5:10]))
                viaje = cls(transportes[int(fila[1])], fila[2], datetime.fromisoformat(fila[3]), matriz)
                viaje.setter_id(int(fila[0]))
                viaje.setter_estado(fila[4])
                viaje.setter_solicitudes(map(lambda i: solicitudes[i], ids[0]))
                for solicitud in viaje.getter_solicitudes():
                    solicitud.setter_viaje(viaje)
                viaje.setter_incidentes(map(lambda i: incidentes[i], ids[1]))
                viaje.setter_paradas(map(lambda i: paradas[i], ids[2]))
                viaje.setter_paradas_resueltas(map(lambda i: paradas[i], ids[3]))
                viaje.setter_historial_solicitudes(map(lambda i: solicitudes[i], ids[4]))
                viajes.append(viaje)
        cls.curr_id = max(cls.curr_id, 0, *map(lambda v: v.getter_id(), viajes))
        return viajes

    def agregar_solicitud(self, nueva_solicitud):
        Validaciones.validar_instancia(nueva_solicitud, clase = Solicitud, nombre = "solicitud")
        self.validar_estado("agregar_solicitud", "PLANIFICADO")
        if nueva_solicitud in self.solicitudes or nueva_solicitud.esta_asignada() or nueva_solicitud.esta_entregada():
            raise SolicitudDuplicadaError(nueva_solicitud.getter_id())
        if nueva_solicitud.getter_destino() == self.deposito:
            raise DatoInvalidoError(f"El destino de la solicitud {nueva_solicitud.getter_id()} no puede ser el depósito ({self.deposito})")
        peso = self.getter_peso() + nueva_solicitud.getter_peso()
        volumen = self.getter_volumen() + nueva_solicitud.getter_volumen()
        if peso > self.getter_peso_max():
            raise ExcesoPesoError(self.getter_peso_max(), peso)
        elif volumen > self.getter_volumen_max():
            raise ExcesoVolumenError(self.getter_volumen_max(), volumen)
        self.validar_recorrido([*self.solicitudes, nueva_solicitud])
        self.solicitudes.append(nueva_solicitud)
        self.historial_solicitudes.apilar(nueva_solicitud)
        nueva_solicitud.setter_viaje(self)
        return None

    def deshacer_ultima_solicitud(self):
        self.validar_estado("deshacer_ultima_solicitud", "PLANIFICADO")
        if self.historial_solicitudes.esVacia():
            raise ViajeVacioError("Viaje Vacio: No hay solicitudes para deshacer")
        solicitud = self.historial_solicitudes.desapilar()
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

    # DESDE ACÁ EL VIAJE ESTÁ INICIADO
    def comenzar(self, solicitudes, paradas):
        self.validar_estado("iniciar_viaje", "PLANIFICADO")
        self.setter_solicitudes(solicitudes)
        self.setter_paradas(paradas)
        self.setter_paradas_resueltas([])
        self.setter_estado("EN_CURSO")

    def parada_actual(self, accion):
        self.validar_estado(accion, "EN_CURSO")
        if self.paradas.esVacia():
            raise SinParadasPendientesError(accion)
        return self.paradas.frente()

    def validar_hora_resolucion(self, hora, nombre_fin):
        if self.paradas_resueltas:
            inicio = self.paradas_resueltas[-1].getter_hora_real()
            Validaciones.validar_ventana(inicio, hora, nombre_inicio = "fecha de la parada previa", nombre_fin = nombre_fin)
        else:
            Validaciones.validar_ventana(self.horario, hora, nombre_inicio = "fecha de salida del viaje", nombre_fin = nombre_fin)

    def cerrar_parada_actual(self):
        self.paradas_resueltas.append(self.paradas.desencolar())
        if self.paradas.esVacia():
            self.finalizar_viaje()

    def agregar_incidente(self, incidente):
        self.incidentes.append(incidente)

    def finalizar_viaje(self):
        self.validar_estado("finalizar_viaje", "EN_CURSO")
        if not self.paradas.esVacia():
            raise ViajeIncompletoError(self.paradas.get_longitud())
        self.estado = "FINALIZADO"
