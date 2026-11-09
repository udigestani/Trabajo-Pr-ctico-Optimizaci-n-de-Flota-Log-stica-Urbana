from datetime import datetime

class Menu:
    MENSAJE_INICIO = "\n" + "=" * 50 + "\nSISTEMA LISASA - Planificación de entregas urbanas\n" + "=" * 50
    MENSAJE_MENU_INICIO = "\n1) Iniciar sesión\n2) Crear un Administrador\n3) Crear un Solicitante\n4) Ver personas registradas\n5) Salir"

    def __init__(self, sistema):
        self.sistema = sistema

    def getter_sistema(self):
        return self.sistema

    # Pedir datos

    def pedir_texto(self, mensaje, mensaje_unico = None):
        if mensaje_unico:
            print(mensaje_unico)
        ingresado = input(mensaje).strip()
        if ingresado:
            return ingresado
        print("DatoInvalidoError: Se esperaba un texto no vacío")
        return self.pedir_texto(mensaje)

    def pedir_entero(self, mensaje, mensaje_unico = None):
        if mensaje_unico:
            print(mensaje_unico)
        entero = input(mensaje).strip()
        try:
            return int(entero)
        except ValueError:
            print(f"ValueError: Se espera un entero, en lugar de {entero}")
            return self.pedir_entero(mensaje)

    def pedir_numero(self, mensaje, mensaje_unico = None):
        if mensaje_unico:
            print(mensaje_unico)
        numero = input(mensaje).strip()
        try:
            return float(numero)
        except ValueError:
            print(f"ValueError: Se espera un número, en lugar de {numero}")
            return self.pedir_numero(mensaje)

    def pedir_fecha_hora(self, mensaje):
        valor = input(mensaje + " (formato DD/MM/AAAA HH:MM): ").strip()
        try:
            return datetime.strptime(valor, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Formato invalido. Ejemplo: 01/06/2024 09:30")
            return self.pedir_fecha_hora(mensaje)

    def pedir_si_no(self, mensaje):
        return input(mensaje + " (s/n): ").strip().lower() == "s"

    def pedir_lugar(self, mensaje):
        lugar = self.pedir_texto(mensaje)
        if self.getter_sistema().es_lugar_conocido(lugar):
            return lugar
        print(f"DatoInvalidoError: '{lugar}' no es un lugar de la matriz. Lugares conocidos: {self.getter_sistema().lugares_conocidos()}")
        return self.pedir_lugar(mensaje)

    def pedir_persona(self):
        nombre = self.pedir_texto("Nombre: ")
        dni = self.pedir_entero("DNI (7 u 8 digitos): ")
        telefono = self.pedir_entero("Telefono (10 digitos): ")
        return nombre, dni, telefono

    def pedir_articulos(self, articulos = None):
        if articulos is None:
            articulos = []
        descripcion = self.pedir_texto("Descripcion del articulo: ")
        peso = self.pedir_numero("Peso (kg): ")
        volumen = self.pedir_numero("Volumen (m3): ")
        articulos.append((descripcion, peso, volumen))
        if not self.pedir_si_no("Agregar otro articulo?"):
            return articulos
        return self.pedir_articulos(articulos)

    def mostrar(self, lineas):
        for linea in lineas:
            print(linea)

    # Elegir

    def elegir_viaje(self, estado = None):
        print("Elegi el viaje:")
        self.mostrar(self.getter_sistema().opciones_viajes(estado))
        return self.pedir_entero("Numero: ")

    def correr_menu(self, mensaje_menu, opciones, opcion_salida):
        while True:
            print(mensaje_menu)
            valor = input("Elegi una opción: ").strip()
            while valor not in opciones:
                valor = input("Opción inválida. Elegir un número del menú: ")
            try:
                opciones[valor]()
                if valor == opcion_salida:
                    break
            except Exception as e:
                print(f"\n{type(e)}: {e}")

    # Opciones compartidas

    def ver_viajes(self):
        print("\nLISTA DE VIAJES: ")
        self.mostrar(self.getter_sistema().ver_viajes())

    def ver_impacto_ambiental(self):
        print("\nIMPACTO AMBIENTAL DE CADA VIAJE: ")
        self.mostrar(self.getter_sistema().ver_impacto_ambiental())

    def cerrar_sesion(self):
        self.getter_sistema().cerrar_sesion()
        print("\nCERRANDO SESIÓN...")

    # Menú de inicio

    def iniciar_sesion(self):
        print("\nINICIANDO SESION")
        sistema = self.getter_sistema()
        dni = self.pedir_entero("Ingrese su número de DNI: ")
        rol = sistema.iniciar_sesion(dni)
        while rol is None:
            dni = self.pedir_entero("Ingrese su número de DNI: ", mensaje_unico = "DNI Incorrecto: Volver a intentar o probar creando una cuenta")
            rol = sistema.iniciar_sesion(dni)
        if rol == sistema.ROL_ADMINISTRADOR:
            MenuAdmin(sistema).ejecutar()
        elif rol == sistema.ROL_SOLICITANTE:
            MenuSolic(sistema).ejecutar()
        else:
            print("LA PERSONA NO ES NI SOLICITANTE NI ADMINISTRADOR, NO TIENES ACCESO A NINGÚN MENÚ")

    def crear_administrador(self):
        nombre, dni, telefono = self.pedir_persona()
        print("\n" + self.getter_sistema().crear_administrador(nombre, dni, telefono))

    def crear_solicitante(self):
        nombre, dni, telefono = self.pedir_persona()
        print("\n" + self.getter_sistema().crear_solicitante(nombre, dni, telefono))

    def ver_registrados(self):
        print("\nLISTA DE REGISTRADOS: ")
        self.mostrar(self.getter_sistema().ver_registrados())

    def salir(self):
        self.getter_sistema().salir()
        print("\nSALIENDO...")

    def ejecutar(self):
        opciones = {"1": self.iniciar_sesion, "2": self.crear_administrador, "3": self.crear_solicitante, "4": self.ver_registrados, "5": self.salir}
        print(Menu.MENSAJE_INICIO)
        self.correr_menu(Menu.MENSAJE_MENU_INICIO, opciones, "5")


class MenuAdmin(Menu):
    MENSAJE_MENU = "\n1) Crear viaje\n2) Ver viajes\n3) Iniciar viaje\n4) Registrar entrega\n5) Registrar incidente\n6) Ver matriz\n7) Agregar distancias\n8) Ver impacto ambiental\n9) Deshacer ultima solicitud de un viaje\n10) Ver detalle de un viaje (distancia y costo)\n11) Registrar transporte\n12) Asignar solicitud pendiente a un viaje\n13) Buscar persona por DNI\n14) Cerrar sesión"

    def registrar_transporte(self):
        sistema = self.getter_sistema()
        print("Tipo de transporte:")
        self.mostrar(map(lambda t: f"{t[0]}) {t[1]}", enumerate(sistema.tipos_transporte())))
        opcion = self.pedir_entero("Opcion: ")
        print(sistema.registrar_transporte(opcion))

    def crear_viaje(self):
        sistema = self.getter_sistema()
        print("Elegi el transporte:")
        self.mostrar(sistema.opciones_transportes())
        transporte = self.pedir_entero("Numero: ")
        print(f"Lugares conocidos en la matriz: {sistema.lugares_conocidos()}")
        deposito = self.pedir_lugar("Nombre del deposito: ")
        horario = self.pedir_fecha_hora("Horario de salida")
        print(sistema.crear_viaje(transporte, deposito, horario))

    def ver_detalle_viaje(self):
        viaje = self.elegir_viaje()
        self.mostrar(self.getter_sistema().detalle_viaje(viaje))

    def iniciar_viaje(self):
        viaje = self.elegir_viaje("PLANIFICADO")
        self.mostrar(self.getter_sistema().iniciar_viaje(viaje))

    def registrar_entrega(self):
        viaje = self.elegir_viaje("EN_CURSO")
        hora_real = self.pedir_fecha_hora("Hora real de entrega")
        receptor = self.pedir_texto("Nombre de quien recibe: ")
        monto = self.pedir_numero("Monto: ")
        print(self.getter_sistema().registrar_entrega(viaje, hora_real, receptor, monto))

    def registrar_incidente(self):
        sistema = self.getter_sistema()
        viaje = self.elegir_viaje("EN_CURSO")
        print("Tipo de incidente:")
        self.mostrar(map(lambda t: f"{t[0]}) {t[1]}", enumerate(sistema.tipos_incidente())))
        tipo = self.pedir_entero("Opcion: ")
        fecha = self.pedir_fecha_hora("Fecha y hora del incidente")
        descripcion = self.pedir_texto("Descripcion: ")
        print("Alcance del incidente:")
        self.mostrar(map(lambda t: f"{t[0]}) {t[1]}", enumerate(sistema.descripciones_alcance())))
        alcance = self.pedir_entero("Opcion: ")
        print(sistema.registrar_incidente(viaje, tipo, fecha, descripcion, alcance))

    def ver_matriz(self):
        print("\nMATRIZ: ")
        self.mostrar(self.getter_sistema().ver_matriz())

    def agregar_distancias(self):
        sistema = self.getter_sistema()
        origen = self.pedir_texto("Origen: ")
        destino = self.pedir_texto("Destino: ")
        km = self.pedir_numero("Distancia en km: ")
        sistema.agregar_distancia(origen, destino, km)
        if self.pedir_si_no("Cargar la vuelta también?"):
            km = self.pedir_numero(f"Distancia {destino} -> {origen} en km: ")
            sistema.agregar_distancia(destino, origen, km)
        if self.pedir_si_no("Agregar otro tramo?"):
            self.agregar_distancias()

    def deshacer_ultima_solicitud(self):
        sistema = self.getter_sistema()
        viaje = self.elegir_viaje("PLANIFICADO")
        print(sistema.deshacer_ultima_solicitud(viaje))
        if not self.pedir_si_no("Agregar a otro viaje?"):
            print(sistema.descartar_solicitud_deshecha())
            return None
        nuevo_viaje = self.elegir_viaje("PLANIFICADO")
        print(sistema.reasignar_solicitud_deshecha(nuevo_viaje))

    def asignar_solicitud_pendiente(self):
        sistema = self.getter_sistema()
        print("Solicitudes pendientes de asignación:")
        self.mostrar(sistema.opciones_pendientes())
        pendiente = self.pedir_entero("Numero: ")
        viaje = self.elegir_viaje("PLANIFICADO")
        print(sistema.asignar_solicitud_pendiente(pendiente, viaje))

    def buscar_persona(self):
        dni = self.pedir_entero("DNI de la persona a buscar: ")
        self.mostrar(self.getter_sistema().buscar_persona(dni))

    def ejecutar(self):
        opciones = {"1": self.crear_viaje, "2": self.ver_viajes, "3": self.iniciar_viaje, "4": self.registrar_entrega, "5": self.registrar_incidente, "6": self.ver_matriz, "7": self.agregar_distancias, "8": self.ver_impacto_ambiental, "9": self.deshacer_ultima_solicitud, "10": self.ver_detalle_viaje, "11": self.registrar_transporte, "12": self.asignar_solicitud_pendiente, "13": self.buscar_persona, "14": self.cerrar_sesion}
        print(f"MENU ADMINISTRADOR: {self.getter_sistema().descripcion_usuario()}")
        self.correr_menu(MenuAdmin.MENSAJE_MENU, opciones, "14")


class MenuSolic(Menu):
    MENSAJE_MENU = "\n1) Crear Solicitud\n2) Ver viajes\n3) Ver impacto ambiental\n4) Cerrar sesión"

    def crear_solicitud(self):
        sistema = self.getter_sistema()
        viaje = self.elegir_viaje("PLANIFICADO")
        lugar, opciones = sistema.alcanzables_desde_viaje(viaje)
        print(f"Desde '{lugar}' hay distancia cargada hacia: {opciones}")
        destino = self.pedir_lugar("Destino de la solicitud (tiene que ser uno de los de arriba): ")
        ventana_inicio = self.pedir_fecha_hora("Inicio de la ventana")
        ventana_fin = self.pedir_fecha_hora("Fin de la ventana")
        articulos = self.pedir_articulos()
        print(sistema.crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, articulos))

    def ejecutar(self):
        opciones = {"1": self.crear_solicitud, "2": self.ver_viajes, "3": self.ver_impacto_ambiental, "4": self.cerrar_sesion}
        print(f"MENU SOLICITANTE: {self.getter_sistema().descripcion_usuario()}")
        self.correr_menu(MenuSolic.MENSAJE_MENU, opciones, "4")
