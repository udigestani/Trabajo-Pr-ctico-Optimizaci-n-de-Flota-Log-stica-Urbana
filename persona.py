from viaje import Viaje
from parada import Parada
from incidente import Incidente
from politicaordenamiento import Vecinos, VentanasTiempo
from validaciones import Validaciones
from excepciones import DatoInvalidoError, VentanaIncumplidaError, RutaIncompletaError, ViajeVacioError
from arbol import Arbol

class Persona:
    dnis_registrados = Arbol()
    def __init__(self, nombre, dni, telefono):
        self.nombre = Validaciones.validar_str(nombre, nombre = "nombre")
        self.dni = Validaciones.validar_dni(dni, Persona.dnis_registrados)
        self.telefono = Validaciones.validar_digitos(telefono, 10, "teléfono")
        Persona.dnis_registrados.insertar(self.dni, self)

    def getter_nombre(self):
        return self.nombre
    def getter_dni(self):
        return self.dni
    def getter_telefono(self):
        return self.telefono

    @classmethod
    def getter_dnis_registrados(cls):
        return cls.dnis_registrados
    @classmethod
    def limpiar_dnis_registrados(cls):
        cls.dnis_registrados.setter_raiz(None)
        return None

    def __str__(self):
        return f"Persona de nombre {self.nombre} y DNI: {self.dni}"
    def __repr__(self):
        return f"<Persona {self.nombre} - {self.dni}>"
    def __eq__(self, other):
        if not isinstance(other, Persona):
            return False
        return self.dni == other.getter_dni()
    def __hash__(self):
        return hash(self.dni)    

    def serializar(self):
        return [self.__class__.__name__, self.nombre, self.dni, self.telefono]

    @staticmethod
    def deserializar(archivo, contexto = None):
        Persona.limpiar_dnis_registrados()
        clases = {"Persona": Persona, "Administrador": Administrador, "Solicitante": Solicitante}
        personas = []
        for fila in archivo[1:]:
            if fila and fila[0] in clases:
                cls = clases[fila[0]]
                personas.append(cls(fila[1], int(fila[2]), int(fila[3])))
            elif fila and fila[0] not in clases:
                raise DatoInvalidoError(f"Clase de persona desconocida: {fila[0]}")
        return personas

class Administrador(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)
        

    def crear_viaje(self, transporte, deposito, horario, matriz):
        viaje = Viaje(transporte, deposito, horario, matriz)
        return viaje

    @staticmethod
    def crear_transporte(clase):
        return clase()

    @staticmethod
    def agregar_distancia(matriz, origen, destino, km):
        matriz.agregar_distancia(origen, destino, km)

    @staticmethod
    def asignar_solicitud(viaje, solicitud):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        viaje.agregar_solicitud(solicitud)

    @staticmethod
    def deshacer_ultima_solicitud(viaje):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        return viaje.deshacer_ultima_solicitud()

    @staticmethod
    def ordenar_solicitudes(viaje):
        opciones = {}
        error_solicitudes = None
        solicitudes = viaje.getter_solicitudes()
        deposito = viaje.getter_deposito()
        matriz = viaje.getter_matriz()
        try:
            viaje.validar_recorrido(solicitudes)
            opciones[tuple(solicitudes)] = viaje.costo_total(solicitudes)
        except (VentanaIncumplidaError, RutaIncompletaError) as error:
            error_solicitudes = error
        for politica in (Vecinos, VentanasTiempo):
            try:
                orden = tuple(politica.sugerir_orden(deposito, solicitudes, matriz))
                viaje.validar_recorrido(orden)
                opciones[orden] = viaje.costo_total(orden)
            except (VentanaIncumplidaError, RutaIncompletaError):
                pass
        if not opciones:
            raise error_solicitudes
        orden = min(opciones.keys(), key = lambda opcion: opciones[opcion])
        return list(orden)

    @staticmethod
    def iniciar_viaje(viaje):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        viaje.validar_estado("iniciar_viaje", "PLANIFICADO")
        if not viaje.getter_solicitudes():
            raise ViajeVacioError("Viaje Vacio: El viaje aún no tiene solicitudes")
        solicitudes = Administrador.ordenar_solicitudes(viaje)
        horarios = viaje.calcular_horarios(solicitudes)
        paradas = list(map(lambda orden, solicitud, hora: Parada(orden=orden, solicitud=solicitud, hora_prev=hora, hora_real=None), range(1, len(solicitudes) + 1), solicitudes, horarios))
        viaje.comenzar(solicitudes, paradas)

    @staticmethod
    def registrar_entrega(viaje, hora_real, receptor, monto):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        parada = viaje.parada_actual("registrar_entrega")
        viaje.validar_hora_resolucion(hora_real, "fecha de entrega")
        comprobante = parada.generar_comprobante(receptor, hora_real, monto)
        viaje.cerrar_parada_actual()
        return comprobante

    @staticmethod
    def registrar_incidente(viaje, tipo, fecha, descripcion, alcance = "FALLA", **detalles):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        parada = viaje.parada_actual("registrar_incidente")
        Validaciones.validar_en(alcance, opciones = ("FALLA", "SOLICITUD", "TRANSPORTE"), nombre = "alcance del incidente")
        viaje.validar_hora_resolucion(fecha, "fecha del incidente")
        if alcance == "TRANSPORTE":
            afectado = viaje.getter_transporte()
        else:
            afectado = parada.getter_solicitud()
        incidente = Incidente(tipo, fecha, descripcion, afectado, **detalles)
        viaje.agregar_incidente(incidente)
        if alcance == "FALLA":
            parada.setter_estado("FALLIDA")
            parada.setter_hora_real(fecha)
            viaje.cerrar_parada_actual()
        return incidente

    def __str__(self):
        return f"Administrador de nombre {self.nombre} y DNI: {self.dni}"

class Solicitante(Persona):
    def __init__(self, nombre, dni, telefono):
        super().__init__(nombre, dni, telefono)

    @staticmethod
    def crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, *articulos):
        Validaciones.validar_instancia(viaje, clase = Viaje, nombre = "viaje")
        return viaje.crear_solicitud(destino, ventana_inicio, ventana_fin, *articulos)
    def __str__(self):
        return f"Solicitante de nombre {self.nombre} y DNI: {self.dni}"
