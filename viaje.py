from incidente import Incidente 
from transporte import Transporte
from datetime import datetime, timedelta
from solicitud import Solicitud
from parada import Parada
from cola import Cola
from pila import Pila
from lista_enlazada import ListaEnlazada
from politicaordenamiento import Vecinos, VentanasTiempo
from validaciones import Validaciones
from matrizdistancia import MatrizDistancia
from excepciones import DatoInvalidoError, ExcesoPesoError, ExcesoVolumenError, EstadoInvalidoError, VentanaIncumplidaError, ViajeVacioError, SinParadasPendientesError, ViajeIncompletoError, SolicitudDuplicadaError, RutaIncompletaError, TransicionIlegalError, ZonaRestringidaError

class Viaje:
    curr_id = 0
    def __init__(self, transporte, deposito, horario, matriz):
        self.transporte = Validaciones.validar_instancia(transporte, clase = Transporte, nombre = "transporte")
        self.deposito = Validaciones.validar_str(deposito, nombre = "depósito")
        self.horario = Validaciones.validar_fecha(horario, nombre = "horario de salida del viaje")
        self.matriz = Validaciones.validar_instancia(matriz, clase = MatrizDistancia, nombre = "matriz")
        self.estado = "PLANIFICADO"

        self.solicitudes = ListaEnlazada()
        self.incidentes = []
        self.paradas = Cola()
        self.paradas_resueltas = []
        self.historial_solicitudes = Pila()
        self.solicitudes_deshechas = Pila()
        Viaje.curr_id += 1
        self.id = Viaje.curr_id

    def _validar_estado(self, accion, estado_requerido):
        if self.estado != estado_requerido:
            raise EstadoInvalidoError(accion, self.estado)

    def crear_solicitud(self, destino, ventana_inicio, ventana_fin, *articulos, solicitud_anterior = None):
        self._validar_estado("crear_solicitud", "PLANIFICADO")
        nueva_solicitud = Solicitud(destino, ventana_inicio, ventana_fin, *articulos)
        self.agregar_solicitud(nueva_solicitud, solicitud_anterior)
        return nueva_solicitud

    def validar_recorrido(self, recorrido, indice = 0, horario = None, ubicacion = None):
        if horario is None:
            horario = self.horario
        if ubicacion is None:
            ubicacion = self.deposito
        if indice == len(recorrido):
            return True
        solicitud = recorrido[indice]
        lugar = solicitud.getter_destino()
        distancia = self.matriz.obtener_distancia(ubicacion, lugar)
        tiempo_hrs = distancia / self.transporte.getter_velocidad()
        llegada = horario + timedelta(hours=tiempo_hrs)
        if llegada > solicitud.getter_ventana_fin():
            raise VentanaIncumplidaError(lugar, llegada, solicitud.getter_ventana_fin())
        if llegada < solicitud.getter_ventana_inicio():
            llegada = solicitud.getter_ventana_inicio()
        return self.validar_recorrido(recorrido, indice = indice + 1, horario = llegada + timedelta(minutes=10), ubicacion = lugar)

    def validar_zonas(self, recorrido = None):
        if recorrido is None:
            recorrido = self.solicitudes
        zonas_visitadas = set().union(*map(lambda s: self.matriz.zonas_de(s.getter_destino()), recorrido))
        no_habilitadas = zonas_visitadas - self.transporte.getter_zonas_habilitadas()
        if no_habilitadas:
            raise ZonaRestringidaError(no_habilitadas)
        return True

    def distancia_total(self, ubicacion, restantes):
        if not restantes:
            return self.matriz.obtener_distancia(ubicacion, self.deposito)
        lugar = restantes[0].getter_destino()
        distancia = self.matriz.obtener_distancia(ubicacion, lugar)
        return distancia + self.distancia_total(lugar, restantes[1:])

    def costo_total(self, orden = None):
        if orden is None:
            orden = list(self.solicitudes)
        costo_distancia = self.distancia_total(self.deposito, orden) * self.transporte.getter_costo_km()
        costo_paradas = len(orden) * self.transporte.getter_costo_parada()
        return costo_distancia + costo_paradas

    def impacto_ambiental(self):
        return self.transporte.calcular_impacto_ambiental(self.distancia_total(self.deposito, list(self.solicitudes)), self.getter_peso())
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
        return list(self.solicitudes)
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

    def serializar(self):
        return [self.id, self.transporte.id, self.deposito, self.horario, self.estado, ",".join(map(lambda x: str(x.id), self.solicitudes)), ",".join(map(lambda x: str(x.id), self.incidentes)), ",".join(map(lambda x: str(x.id), self.paradas)), ",".join(map(lambda x: str(x.id), self.paradas_resueltas)), ",".join(list(map(Viaje._serializar_cambio, self.historial_solicitudes))[::-1])]

    @staticmethod
    def _serializar_cambio(cambio):
        solicitud, accion, anterior = cambio
        if anterior is True:
            anterior = "inicio"
        elif anterior is None or anterior is False:
            anterior = ""
        else:
            anterior = anterior.getter_id()
        return f"{accion}:{solicitud.getter_id()}:{anterior}"

    @staticmethod
    def _deserializar_cambio(texto, solicitudes):
        partes = texto.split(":")
        if len(partes) == 1:
            return (solicitudes[int(partes[0])], "Agregar", None)
        accion, id_solicitud, anterior = partes
        if anterior == "inicio":
            anterior = True
        elif anterior == "":
            anterior = None
        else:
            anterior = solicitudes[int(anterior)]
        return (solicitudes[int(id_solicitud)], accion, anterior)

    @classmethod
    def deserializar(cls, archivo, contexto):
        matriz = contexto[MatrizDistancia]
        transportes = dict(map(lambda tr: (tr.id, tr), contexto[Transporte]))
        solicitudes = dict(map(lambda sol: (sol.getter_id(), sol), contexto[Solicitud]))
        incidentes = dict(map(lambda inc: (inc.getter_id(), inc), contexto.get(Incidente, [])))
        paradas = dict(map(lambda par: (par.getter_id(), par), contexto.get(Parada, [])))
        viajes = []
        for fila in archivo[1:]:
            if fila:
                ids = list(map(lambda celda: list(map(int, filter(None, celda.split(",")))), fila[5:9]))
                viaje = cls(transportes[int(fila[1])], fila[2], datetime.fromisoformat(fila[3]), matriz)
                viaje.id = int(fila[0])
                viaje.estado = fila[4]
                for i in ids[0]:
                    viaje.solicitudes.agregar_al_final(solicitudes[i])
                    solicitudes[i].setter_viaje(viaje)
                viaje.incidentes = list(map(lambda i: incidentes[i], ids[1]))
                for i in ids[2]:
                    viaje.paradas.encolar(paradas[i])
                viaje.paradas_resueltas = list(map(lambda i: paradas[i], ids[3]))
                for texto in filter(None, fila[9].split(",")):
                    viaje.historial_solicitudes.apilar(cls._deserializar_cambio(texto, solicitudes))
                viajes.append(viaje)
        cls.curr_id = max(cls.curr_id, 0, *map(lambda v: v.id, viajes))
        return viajes

    def _validar_agregar(self, nueva_solicitud, solicitud_anterior):
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
        orden = list(self.solicitudes)
        if solicitud_anterior is None:
            orden.append(nueva_solicitud)
        elif solicitud_anterior is True:
            orden.insert(0, nueva_solicitud)
        elif solicitud_anterior in orden:
            orden.insert(orden.index(solicitud_anterior) + 1, nueva_solicitud)
        else:
            raise DatoInvalidoError(f"La solicitud {solicitud_anterior.getter_id()} no pertenece al viaje {self.id}")
        self.validar_recorrido(orden)
        self.validar_zonas(orden)

    def _validar_quitar(self, solicitud):
        orden = list(self.solicitudes)
        if solicitud not in orden:
            raise DatoInvalidoError(f"La solicitud {solicitud.getter_id()} no pertenece al viaje {self.id}")
        posicion = orden.index(solicitud)
        orden.remove(solicitud)
        self.validar_recorrido(orden)
        return orden[posicion - 1] if posicion > 0 else True

    def _colocar_solicitud(self, solicitud, solicitud_anterior):
        if solicitud_anterior is None:
            self.solicitudes.agregar_al_final(solicitud)
        elif solicitud_anterior is True:
            self.solicitudes.agregar_al_inicio(solicitud)
        else:
            self.solicitudes.insertar_despues(solicitud_anterior, solicitud)
        solicitud.setter_viaje(self)

    def _sacar_solicitud(self, solicitud):
        self.solicitudes.eliminar(solicitud)
        solicitud.setter_viaje(None)

    def agregar_solicitud(self, nueva_solicitud, solicitud_anterior = None):
        Validaciones.validar_instancia(nueva_solicitud, clase = Solicitud, nombre = "solicitud")
        self._validar_estado("agregar_solicitud", "PLANIFICADO")
        self._validar_agregar(nueva_solicitud, solicitud_anterior)
        self.solicitudes_deshechas.borrar_todo()
        self._colocar_solicitud(nueva_solicitud, solicitud_anterior)
        self.historial_solicitudes.apilar((nueva_solicitud, "Agregar", solicitud_anterior))
        return None

    def quitar_solicitud(self, solicitud):
        Validaciones.validar_instancia(solicitud, clase = Solicitud, nombre = "solicitud")
        self._validar_estado("quitar_solicitud", "PLANIFICADO")
        anterior = self._validar_quitar(solicitud)
        self.solicitudes_deshechas.borrar_todo()
        self._sacar_solicitud(solicitud)
        self.historial_solicitudes.apilar((solicitud, "Quitar", anterior))
        return None

    def deshacer_ultima_solicitud(self):
        self._validar_estado("deshacer_ultima_solicitud", "PLANIFICADO")
        if self.historial_solicitudes.esVacia():
            raise ViajeVacioError("Viaje Vacio: No hay solicitudes para deshacer")
        (solicitud, accion, anterior) = self.historial_solicitudes.ver_tope()
        if accion == "Agregar":
            self._validar_quitar(solicitud)
            self._sacar_solicitud(solicitud)
        else:
            self._validar_agregar(solicitud, anterior)
            self._colocar_solicitud(solicitud, anterior)
        self.historial_solicitudes.desapilar()
        self.solicitudes_deshechas.apilar((solicitud, accion, anterior))
        return solicitud

    def rehacer(self):
        self._validar_estado("rehacer solicitud", "PLANIFICADO")
        if self.solicitudes_deshechas.esVacia():
            raise ViajeVacioError("Viaje Vacio: No hay solicitudes para rehacer")
        (solicitud, accion, anterior) = self.solicitudes_deshechas.ver_tope()
        if accion == "Agregar":
            self._validar_agregar(solicitud, anterior)
            self._colocar_solicitud(solicitud, anterior)
        else:
            anterior = self._validar_quitar(solicitud)
            self._sacar_solicitud(solicitud)
        self.solicitudes_deshechas.desapilar()
        self.historial_solicitudes.apilar((solicitud, accion, anterior))
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
        opciones = {}
        error_solicitudes = None
        try:
            opciones[tuple(self.solicitudes)] = self.costo_total()
        except RutaIncompletaError as error:
            error_solicitudes = error
        try:
            orden = tuple(Vecinos.sugerir_orden(self.deposito, list(self.solicitudes), self.matriz))
            self.validar_recorrido(orden)
            costo = self.costo_total(orden)
            opciones[orden] = costo
        except (VentanaIncumplidaError, RutaIncompletaError):
            pass
        try:
            orden = tuple(VentanasTiempo.sugerir_orden(self.deposito, list(self.solicitudes), self.matriz))
            self.validar_recorrido(orden)
            costo = self.costo_total(orden)
            opciones[orden] = costo
        except (VentanaIncumplidaError, RutaIncompletaError):
            pass
        if not opciones:
            raise error_solicitudes
        orden = min(opciones.keys(), key = lambda opcion: opciones[opcion])
        return list(orden)

    # DESDE ACÁ EL VIAJE ESTÁ INICIADO
    def iniciar_viaje(self):
        self._validar_estado("iniciar_viaje", "PLANIFICADO")
        if self.solicitudes.es_vacia():
            raise ViajeVacioError("Viaje Vacio: El viaje aún no tiene solicitudes")
        self.validar_zonas()
        orden_paradas = self.ordenar_solicitudes()
        self.solicitudes = ListaEnlazada()
        for solicitud in orden_paradas:
            self.solicitudes.agregar_al_final(solicitud)
        self.historial_solicitudes.borrar_todo()
        self.solicitudes_deshechas.borrar_todo()
        self.paradas = Cola()
        self.paradas_resueltas = []
        horario = self.horario
        ubicacion = self.deposito
        for i in range(len(orden_paradas)):
            solicitud = orden_paradas[i]
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