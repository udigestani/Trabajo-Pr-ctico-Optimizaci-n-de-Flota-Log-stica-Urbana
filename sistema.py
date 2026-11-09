from pathlib import Path
from articulo import Articulo
from transporte import Transporte, Furgoneta, Motocicleta, Camion
from persona import Persona, Administrador, Solicitante
from matrizdistancia import MatrizDistancia
from solicitud import Solicitud
from gestorarchivos import GestorArchivos
from viaje import Viaje
from comprobante import Comprobante
from incidente import Incidente
from parada import Parada
from excepciones import FlotaError, DatoInvalidoError


class Sistema:
    NOMBRES_TRANSPORTE = ("Furgoneta", "Motocicleta", "Camión")
    CLASES_TRANSPORTE = (Furgoneta, Motocicleta, Camion)
    TIPOS_INCIDENTE = ("DAÑO", "AUSENTE", "RETRASO")
    ALCANCES_INCIDENTE = ("FALLA", "SOLICITUD", "TRANSPORTE")
    DESCRIPCIONES_ALCANCE = ("Falla la entrega de la parada actual", "Afecta a la solicitud actual, pero se puede entregar", "Afecta al transporte")
    ROL_ADMINISTRADOR = "ADMINISTRADOR"
    ROL_SOLICITANTE = "SOLICITANTE"
    ROL_OTRO = "OTRO"

    def __init__(self):
        self.contexto = self.leer_todos()
        self.usuario = None
        self.solicitud_deshecha = None

    def getter_contexto(self):
        return self.contexto
    def getter_usuario(self):
        return self.usuario
    def setter_usuario(self, usuario):
        self.usuario = usuario
    def getter_solicitud_deshecha(self):
        return self.solicitud_deshecha
    def setter_solicitud_deshecha(self, solicitud):
        self.solicitud_deshecha = solicitud

    # Persistencia
    def leer_todos(self):
        carpeta = Path('archivos persistencia')
        rutas = {'articulos.csv': Articulo, 'matriz.csv': MatrizDistancia, 'personas.csv': Persona, 'transportes.csv': Transporte, 'solicitudes.csv': Solicitud, 'comprobantes.csv': Comprobante, 'incidentes.csv': Incidente, 'paradas.csv': Parada, 'viajes.csv': Viaje}
        contexto = {}
        for ruta, clase in rutas.items():
            lineas = GestorArchivos.leer(carpeta / ruta)
            contexto[clase] = clase.deserializar(lineas, contexto = contexto)
        return contexto
    def guardar_todos(self):
        carpeta = Path('archivos persistencia')
        rutas = {'articulos.csv': (Articulo, "id,descripcion,peso,volumen,Articulo"),
                  'matriz.csv': (MatrizDistancia, "origen,destino,km,MatrizDistancia"),
                  'personas.csv': (Persona, "clase,nombre,dni,telefono,Persona"),
                  'transportes.csv': (Transporte, "tipo,id,peso_max,volumen,velocidad,costo_km,costo_parada,factor_ambiental,Transporte"),
                  'solicitudes.csv': (Solicitud, "id,destino,ventana_inicio,ventana_fin,articulos,id_viaje,id_comprobante,Solicitud"),
                  'comprobantes.csv': (Comprobante, "id,id_solicitud,fecha_hora,receptor,monto,Comprobante"),
                  'incidentes.csv': (Incidente, "id,tipo,fecha,descripcion,clase_afectado,id_afectado,detalles,Incidente"),
                  'paradas.csv': (Parada, "id,orden,id_solicitud,hora_prev,hora_real,estado,id_comprobante,Parada"),
                  'viajes.csv': (Viaje, "id,id_transporte,deposito,horario,estado,solicitudes,incidentes,paradas,paradas_resueltas,historial_solicitudes,Viaje")}
        for ruta, (clase, linea1) in rutas.items():
            datos = self.contexto[clase]
            if clase is MatrizDistancia:
                datos = datos.serializar()
            elif clase is not Persona:
                datos = list(map(lambda x: x.serializar(), datos))
            else:
                datos = Persona.orden_arbol()
                datos = list(map(lambda x: x.serializar(), datos))
            GestorArchivos.escribir(linea1.split(","), datos, carpeta / ruta)

    # Ayudas internas
    def elegir_de(self, lista, indice):
        if not isinstance(indice, int) or not 0 <= indice < len(lista):
            raise DatoInvalidoError("Numero invalido.")
        return lista[indice]
    def obtener_viaje(self, indice, estado = None):
        viaje = self.elegir_de(self.contexto[Viaje], indice)
        if estado is not None and viaje.getter_estado() != estado:
            raise DatoInvalidoError(f"El viaje no está en estado {estado}.")
        return viaje
    def aviso_si_finalizo(self, viaje):
        if viaje.getter_estado() == "FINALIZADO":
            return f"\nVIAJE FINALIZADO: {viaje.getter_deposito()}, {viaje.getter_paradas()}"
        return ""

    # Inicio
    def iniciar_sesion(self, dni):
        registrados = Persona.getter_dnis_registrados()
        persona = registrados.buscar(registrados.getter_raiz(), dni)
        if persona is None:
            return None
        self.setter_usuario(persona)
        if isinstance(persona, Administrador):
            return Sistema.ROL_ADMINISTRADOR
        if isinstance(persona, Solicitante):
            return Sistema.ROL_SOLICITANTE
        return Sistema.ROL_OTRO

    def crear_solicitante(self, nombre, dni, telefono):
        solicitante = Solicitante(nombre, dni, telefono)
        self.contexto[Persona].append(solicitante)
        return f"SOLICITANTE CREADO: {solicitante}"

    def crear_administrador(self, nombre, dni, telefono):
        administrador = Administrador(nombre, dni, telefono)
        self.contexto[Persona].append(administrador)
        return f"ADMINISTRADOR CREADO: {administrador}"

    def ver_registrados(self):
        return list(map(str, self.contexto[Persona]))

    def salir(self):
        self.guardar_todos()

    def descripcion_usuario(self):
        return str(self.getter_usuario())

    def cerrar_sesion(self):
        self.guardar_todos()
        self.setter_usuario(None)

    # Consultas compartidas

    def opciones_viajes(self, estado = None):
        viajes = self.contexto[Viaje]
        if not viajes:
            raise DatoInvalidoError("Todavia no hay ningun viaje creado.")
        indices = list(filter(lambda i: estado is None or viajes[i].getter_estado() == estado, range(len(viajes))))
        if not indices:
            raise DatoInvalidoError(f"No hay ningun viaje en estado: {estado}.")
        return list(map(lambda i: f"{i}) {viajes[i]}", indices))

    def ver_viajes(self):
        return list(map(str, self.contexto[Viaje]))

    def ver_impacto_ambiental(self):
        lineas = []
        total = 0
        for viaje in self.contexto[Viaje]:
            try:
                impacto = viaje.impacto_ambiental()
                total += impacto
                lineas.append(f"Viaje {viaje.getter_id()}: {impacto:.2f}{Transporte.UNIDAD_IMPACTO}")
            except FlotaError as e:
                lineas.append(f"Viaje {viaje.getter_id()}: no se pudo calcular ({e})")
        lineas.append(f"\nEl impacto ambiental total de los viajes es de {total:.2f}{Transporte.UNIDAD_IMPACTO}")
        return lineas

    def es_lugar_conocido(self, lugar):
        return self.contexto[MatrizDistancia].lugar_conocido(lugar)

    def lugares_conocidos(self):
        lugares = self.contexto[MatrizDistancia].getter_lugares()
        if not lugares:
            raise DatoInvalidoError("La matriz está vacía. Agregá distancias antes de continuar.")
        return sorted(lugares)

    # Administrador

    def opciones_transportes(self):
        transportes = self.contexto[Transporte]
        if not transportes:
            raise DatoInvalidoError("Todavia no hay ningun transporte registrado. Registra uno primero.")
        return list(map(lambda i: f"{i}) {transportes[i]}", range(len(transportes))))

    def tipos_transporte(self):
        return list(Sistema.NOMBRES_TRANSPORTE)

    def registrar_transporte(self, opcion):
        clase = self.elegir_de(Sistema.CLASES_TRANSPORTE, opcion)
        transporte = self.getter_usuario().crear_transporte(clase)
        self.contexto[Transporte].append(transporte)
        return f"TRANSPORTE REGISTRADO: {transporte}"

    def crear_viaje(self, indice_transporte, deposito, horario):
        transporte = self.elegir_de(self.contexto[Transporte], indice_transporte)
        matriz = self.contexto[MatrizDistancia]
        self.lugares_conocidos()
        if not matriz.lugar_conocido(deposito):
            raise DatoInvalidoError(f"'{deposito}' no es un lugar de la matriz.")
        viaje = self.getter_usuario().crear_viaje(transporte, deposito, horario, matriz)
        self.contexto[Viaje].append(viaje)
        return f"VIAJE CREADO: {viaje}"

    def detalle_viaje(self, indice):
        viaje = self.obtener_viaje(indice)
        lineas = [f"\n{viaje}", "Solicitudes (en orden):"]
        lineas.extend(map(lambda s: f"  {s}", viaje.getter_solicitudes()))
        if viaje.getter_paradas():
            lineas.append("Paradas:")
            lineas.extend(map(lambda p: f"  {p}", viaje.getter_paradas()))
        lineas.append(f"Distancia total (con regreso al deposito): {viaje.distancia_total()} km")
        lineas.append(f"Costo total: ${viaje.costo_total()}")
        return lineas

    def iniciar_viaje(self, indice):
        viaje = self.obtener_viaje(indice, "PLANIFICADO")
        self.getter_usuario().iniciar_viaje(viaje)
        self.contexto[Parada].extend(viaje.getter_paradas())
        lineas = [f"VIAJE INICIADO. Estado: {viaje.getter_estado()}"]
        lineas.extend(map(lambda p: f"  {p}", viaje.getter_paradas()))
        return lineas

    def registrar_entrega(self, indice, hora_real, receptor, monto):
        viaje = self.obtener_viaje(indice, "EN_CURSO")
        comprobante = self.getter_usuario().registrar_entrega(viaje, hora_real, receptor, monto)
        self.contexto[Comprobante].append(comprobante)
        return f"Comprobante generado: {comprobante}" + self.aviso_si_finalizo(viaje)

    def registrar_incidente(self, indice, opcion_tipo, fecha, descripcion, opcion_alcance):
        viaje = self.obtener_viaje(indice, "EN_CURSO")
        tipo = self.elegir_de(Sistema.TIPOS_INCIDENTE, opcion_tipo)
        alcance = self.elegir_de(Sistema.ALCANCES_INCIDENTE, opcion_alcance)
        incidente = self.getter_usuario().registrar_incidente(viaje, tipo, fecha, descripcion, alcance)
        self.contexto[Incidente].append(incidente)
        return f"Incidente registrado: {incidente}" + self.aviso_si_finalizo(viaje)

    def tipos_incidente(self):
        return list(Sistema.TIPOS_INCIDENTE)

    def descripciones_alcance(self):
        return list(Sistema.DESCRIPCIONES_ALCANCE)

    def ver_matriz(self):
        distancias = self.contexto[MatrizDistancia].getter_distancias()
        return list(map(lambda par: f"{par[0][0]} -> {par[0][1]}: {par[1]}km", distancias.items()))

    def agregar_distancia(self, origen, destino, km):
        self.getter_usuario().agregar_distancia(self.contexto[MatrizDistancia], origen, destino, km)

    def deshacer_ultima_solicitud(self, indice):
        viaje = self.obtener_viaje(indice, "PLANIFICADO")
        solicitud = self.getter_usuario().deshacer_ultima_solicitud(viaje)
        self.setter_solicitud_deshecha(solicitud)
        return f"Solicitud sacada: {solicitud}"

    def reasignar_solicitud_deshecha(self, indice):
        solicitud = self.getter_solicitud_deshecha()
        if solicitud is None:
            raise DatoInvalidoError("No hay ninguna solicitud deshecha para reasignar.")
        viaje = self.obtener_viaje(indice, "PLANIFICADO")
        self.setter_solicitud_deshecha(None)
        try:
            self.getter_usuario().asignar_solicitud(viaje, solicitud)
        except Exception as e:
            return f"Error al agregar al nuevo viaje ({e}): La solicitud quedará pendiente de asignación."
        return f"Solicitud agregada al viaje: {solicitud}"

    def descartar_solicitud_deshecha(self):
        self.setter_solicitud_deshecha(None)
        return "La solicitud quedará pendiente de asignación"

    def opciones_pendientes(self):
        pendientes = list(filter(lambda s: s.esta_pendiente(), self.contexto[Solicitud]))
        if not pendientes:
            raise DatoInvalidoError("No hay solicitudes pendientes de asignación.")
        return list(map(lambda i: f"{i}) {pendientes[i]}", range(len(pendientes))))

    def asignar_solicitud_pendiente(self, indice_pendiente, indice_viaje):
        pendientes = list(filter(lambda s: s.esta_pendiente(), self.contexto[Solicitud]))
        solicitud = self.elegir_de(pendientes, indice_pendiente)
        viaje = self.obtener_viaje(indice_viaje, "PLANIFICADO")
        self.getter_usuario().asignar_solicitud(viaje, solicitud)
        return f"Solicitud agregada al viaje: {solicitud}"

    def buscar_persona(self, dni):
        persona, saltos = Persona.buscar_persona(dni)
        if persona is None:
            return [f"No hay ninguna persona registrada con el DNI {dni}.", f"Saltos entre nodos hasta llegar a un lugar vacío: {saltos}"]
        return [f"\nPERSONA ENCONTRADA: {persona}", f"Teléfono: {persona.getter_telefono()}", f"Saltos entre nodos desde la raíz: {saltos}"]

    # Solicitante

    def alcanzables_desde_viaje(self, indice):
        viaje = self.obtener_viaje(indice, "PLANIFICADO")
        lugar = viaje.ultimo_lugar()
        opciones = self.contexto[MatrizDistancia].alcanzables(lugar)
        if not opciones:
            raise DatoInvalidoError(f"Todavia no hay ninguna distancia cargada desde '{lugar}'. Pedile a un administrador que la agregue.")
        return lugar, opciones

    def crear_solicitud(self, indice, destino, ventana_inicio, ventana_fin, datos_articulos):
        viaje = self.obtener_viaje(indice, "PLANIFICADO")
        articulos = list(map(lambda d: Articulo(*d), datos_articulos))
        solicitud = self.getter_usuario().crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, *articulos)
        self.contexto[Solicitud].append(solicitud)
        self.contexto[Articulo].extend(articulos)
        return f"Solicitud agregada: {solicitud}"
