from datetime import datetime
from articulo import Articulo
from transporte import Transporte, Furgoneta, Motocicleta, Camion
from persona import Persona, Administrador, Solicitante
from matrizdistancia import MatrizDistancia
from politicaordenamiento import Vecinos, VentanasTiempo
from solicitud import Solicitud
from gestorarchivos import GestorArchivos
from viaje import Viaje
from comprobante import Comprobante
from incidente import Incidente
from parada import Parada


def pedir_texto(mensaje, mensajeUnico = None):
    if mensajeUnico:
        print(mensajeUnico)
    ingresado = input(mensaje).strip()
    if ingresado:
        return ingresado
    else:
        print(f"DatoInvalidoError: Se esperaba un texto no vacío")
        return pedir_texto(mensaje)


def pedir_entero(mensaje, mensajeUnico = None):
    if mensajeUnico:
        print(mensajeUnico)
    entero = input(mensaje).strip()
    try:
        return int(entero)
    except ValueError:
        print(f"ValueError: Se espera un entero, en lugar de {entero}")
        return pedir_entero(mensaje)

def pedir_numero(mensaje, mensajeUnico = None):
    if mensajeUnico:
        print(mensajeUnico)
    numero = input(mensaje).strip()
    try:
        return float(numero)
    except ValueError:
        print(f"ValueError: Se espera un número, en lugar de {numero}")
        return pedir_numero(mensaje)


def pedir_fecha_hora(mensaje):
    valor = input(mensaje + " (formato DD/MM/AAAA HH:MM): ").strip()
    try:
        return datetime.strptime(valor, "%d/%m/%Y %H:%M")
    except ValueError:
        print("Formato invalido. Ejemplo: 01/06/2024 09:30")
        return pedir_fecha_hora(mensaje)


def elegir_transporte(mostrar_opciones = False):
    OPCIONES_TRANSPORTE = {"1": Furgoneta, "2": Motocicleta, "3": Camion}
    if mostrar_opciones:
        print("1) Furgoneta\n2) Motocicleta\n3) Camión")
    opcion = input("Opcion: ").strip()
    if opcion in OPCIONES_TRANSPORTE:
        return OPCIONES_TRANSPORTE[opcion]()  
    print("Opcion invalida, elegi 1, 2 o 3.")
    return elegir_transporte()


def alcanzables(lugar, matriz):
    distancias = matriz.getter_distancias().items()
    distancias = filter(lambda item: item[0][0] == lugar, distancias)
    return list(map(lambda x: x[0][1], distancias))


def crear_solicitante(personas):
    nombre = pedir_texto("Nombre: ")
    dni = pedir_entero("DNI (7 u 8 digitos): ")
    telefono = pedir_entero("Telefono (10 digitos): ")
    solicitante = Solicitante(nombre, dni, telefono)
    print(f"\nSOLICITANTE CREADO: {solicitante}")
    personas.append(solicitante)


def crear_administrador(personas):
    nombre = pedir_texto("Nombre: ")
    dni = pedir_entero("DNI (7 u 8 digitos): ")
    telefono = pedir_entero("Telefono (10 digitos): ")
    administrador = Administrador(nombre, dni, telefono)
    print(f"\nADMINISTRADOR CREADO: {administrador}")
    personas.append(administrador)


def pedir_articulos(articulos = None):
    if articulos is None:
        articulos = []
    descripcion = pedir_texto("Descripcion del articulo: ")
    peso = pedir_numero("Peso (kg): ")
    volumen = pedir_numero("Volumen (m3): ")
    articulos.append(Articulo(descripcion, peso, volumen))
    otro = input("Agregar otro articulo? (s/n): ").strip().lower()
    if otro != "s":
        return articulos
    return pedir_articulos(articulos = articulos)



def ver_registrados(personas):
    print("\nLISTA DE REGISTRADOS: ")
    for persona in personas:
        print(persona)


def iniciar_sesion(personas, contexto):
    print("\nINICIANDO SESION")
    dni = pedir_entero("Ingrese su número de DNI: ")
    while dni not in Persona.getter_dnis_registrados():
        dni = pedir_entero("Ingrese su número de DNI: ", mensajeUnico = "DNI Incorrecto: Volver a intentar o probar creando una cuenta")
    persona = next(filter(lambda p: p.getter_dni() == dni, personas), None)
    if isinstance(persona, Administrador):
        menu_administrador(persona, contexto)
    elif isinstance(persona, Solicitante):
        menu_solicitante(persona, contexto)
    else:
        print("LA PERSONA NO ES NI SOLICITANTE NI ADMINISTRADOR, NO TIENES ACCESO A NINGÚN MENÚ")


def elegir_viaje(viajes, estados = None):
    if estados is None:
        estados = {"PLANIFICADO", "EN_CURSO", "FINALIZADO"}
    if not viajes:
        print("Todavia no hay ningun viaje creado.")
        return None
    print("Elegi el viaje:")
    opciones = set()
    for i in range(len(viajes)):
        if viajes[i].getter_estado() in estados:
            opciones.add(i)
            print(f"{i}) {viajes[i]}")
    opcion = pedir_entero("Numero: ")
    if opcion in opciones:
        return viajes[opcion]
    print("Numero invalido.")
    return None


def salir(contexto):
    GestorArchivos.guardar_todos(contexto)
    print("\nSALIENDO...")


def crear_viaje(admin, viajes, matriz, transportes):
    transporte = elegir_transporte(mostrar_opciones = True)
    deposito = pedir_texto("Nombre del deposito: ")
    horario = pedir_fecha_hora("Horario de salida")
    viaje = admin.crear_viaje(transporte, deposito, horario, matriz)
    transportes.append(transporte)
    viajes.append(viaje)
    print(f"VIAJE CREADO: {viaje}")


def ver_viajes(viajes):
    print("\nLISTA DE VIAJES: ")
    for viaje in viajes:
        print(viaje)

def ver_impacto_ambiental(viajes):
    print("\nIMPACTO AMBIENTAL DE CADA VIAJE: ")
    total = 0
    for viaje in viajes:
        print(f"Viaje {viaje.getter_id()}: {viaje.impacto_ambiental():.2f}{Transporte.UNIDAD_IMPACTO}")
        total += viaje.impacto_ambiental()
    print(f"\nEl impacto ambiental total de los viajes es de {total:.2f}{Transporte.UNIDAD_IMPACTO}")

def deshacer_ultima_solicitud(viajes):
    viaje = elegir_viaje(viajes, estados = {"PLANIFICADO"})
    if viaje is not None:
        solicitud = viaje.deshacer_ultima_solicitud()
        otro = input(f"Solicitud sacada: {solicitud}. Agregar a otro viaje? (s/n): ").strip().lower()
        if otro != "s":
            print("La solicitud quedará pendiente de asignación")
            return None
        nuevo_viaje = elegir_viaje(viajes, estados = {"PLANIFICADO"})
        if nuevo_viaje is not None:
            try:
                nuevo_viaje.agregar_solicitud(solicitud)
            except Exception as e:
                print(f"Error al agregar al nuevo viaje ({e}): La solicitud quedará pendiente de asignación.")

def iniciar_viaje(viajes, paradas):
    viaje = elegir_viaje(viajes, estados = {"PLANIFICADO"})
    if viaje is not None:
        viaje.iniciar_viaje()
        print(f"VIAJE INICIADO. Estado: {viaje.getter_estado()}")
        for parada in viaje.getter_paradas():
            print(f"  {parada}")
            paradas.append(parada)


def registrar_entrega(viajes, comprobantes):
    viaje = elegir_viaje(viajes, estados = {"EN_CURSO"})
    if viaje is not None:
        hora_real = pedir_fecha_hora("Hora real de entrega")
        receptor = pedir_texto("Nombre de quien recibe: ")
        monto = pedir_numero("Monto: ")
        comprobante = viaje.registrar_entrega(hora_real, receptor, monto)
        comprobantes.append(comprobante)
        print(f"Comprobante generado: {comprobante}")


def registrar_incidente(viajes, incidentes):
    OPCIONES_INCIDENTES = {"1": "DAÑO", "2": "AUSENTE", "3": "RETRASO"}
    OPCIONES_ALCANCE = {"1": "FALLA", "2": "SOLICITUD", "3": "TRANSPORTE"}
    viaje = elegir_viaje(viajes, estados = {"EN_CURSO"})
    if viaje is not None:
        print("Tipo de incidente:\n1) DAÑO\n2) AUSENTE\n3) RETRASO")
        opcion = input("Opcion: ").strip()
        tipo = OPCIONES_INCIDENTES.get(opcion, "DAÑO")
        fecha = pedir_fecha_hora("Fecha y hora del incidente")
        descripcion = pedir_texto("Descripcion: ")
        print("Alcance del incidente:\n1) Falla la entrega de la parada actual\n2) Afecta a la solicitud actual, pero se puede entregar\n3) Afecta al transporte")
        opcion_alcance = input("Opcion: ").strip()
        alcance = OPCIONES_ALCANCE.get(opcion_alcance, "FALLA")
        incidente = viaje.registrar_incidente(tipo, fecha, descripcion, alcance)
        incidentes.append(incidente)
        print(f"Incidente registrado: {incidente}")


def ver_matriz(matriz):
    print("\nMATRIZ: ")
    for (partida, llegada), valor in matriz.getter_distancias().items():
        print(f"{partida} -> {llegada}: {valor}km")


def agregar_distancias(matriz):
    origen = pedir_texto("Origen: ")
    destino = pedir_texto("Destino: ")
    km = pedir_numero("Distancia en km: ")
    matriz.agregar_distancia(origen, destino, km)
    vuelta = input("Cargar la vuelta también? (s/n): ").strip().lower()
    if vuelta == "s":
        km = pedir_numero(f"Distancia {destino} -> {origen} en km: ")
        matriz.agregar_distancia(destino, origen, km)

    otro = input("Agregar otro tramo? (s/n): ").strip().lower()
    if otro != "s":
        return matriz
    return agregar_distancias(matriz)


def cerrar_sesion(contexto):
    GestorArchivos.guardar_todos(contexto)
    print("\nCERRANDO SESIÓN...")


def crear_solicitud(solicitante, viajes, matriz, solicitudes, lista_articulos):
    viaje = elegir_viaje(viajes, estados = {"PLANIFICADO"})
    if viaje is None:
        return None
    # Después veamos si esto lo sacamos, no es muy necesario lo de alcanzables porque el sistema valida e intenta con Vecinos y VentanaTiempo
    lugar = viaje.getter_deposito()
    if viaje.getter_solicitudes():
        lugar = viaje.getter_solicitudes()[-1].getter_destino()
    opciones = alcanzables(lugar, matriz)
    if opciones:
        print(f"Desde '{lugar}' hay distancia cargada hacia: {opciones}")
    else:
        print(f"Todavia no hay ninguna distancia cargada desde '{lugar}'.")
        print("Pedile a un administrador que la agregue.")
        return None
    destino = pedir_texto("Destino de la solicitud (tiene que ser uno de los de arriba): ")
    ventana_inicio = pedir_fecha_hora("Inicio de la ventana")
    ventana_fin = pedir_fecha_hora("Fin de la ventana")
    articulos = pedir_articulos()
    solicitud = solicitante.crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, *articulos)
    solicitudes.append(solicitud)
    lista_articulos.extend(articulos)
    print(f"Solicitud agregada: {solicitud}")


def correr_menu(mensaje_menu, opciones, opcion_salida):
    while True:
        print(mensaje_menu)
        valor = input("Elegi una opción: ").strip()
        while valor not in opciones:
            valor = input("Opción inválida. Elegir un número del menú: ")
        try:
            opciones[valor][0](*opciones[valor][1:])
            if valor == opcion_salida:
                break
        except Exception as e:
            print(f"\n{type(e)}: {e}")


def menu_administrador(admin, contexto):
    viajes = contexto[Viaje]
    matriz = contexto[MatrizDistancia]
    transportes = contexto[Transporte]
    paradas = contexto[Parada]
    comprobantes = contexto[Comprobante]
    incidentes = contexto[Incidente]

    MENSAJE_ADMIN = f"MENU ADMINISTRADOR: {admin}"
    MENSAJE_MENU_ADMIN = "\n1) Crear viaje\n2) Ver viajes\n3) Iniciar viaje\n4) Registrar entrega\n5) Registrar incidente\n6) Ver matriz\n7) Agregar distancias\n8) Ver impacto ambiental\n9) Deshacer ultima solicitud de un viaje\n10) Cerrar sesión"
    OPCIONES_ADMIN = {"1": (crear_viaje, admin, viajes, matriz, transportes), "2": (ver_viajes, viajes),"3": (iniciar_viaje, viajes, paradas),"4": (registrar_entrega, viajes, comprobantes), "5": (registrar_incidente, viajes, incidentes),"6": (ver_matriz, matriz),"7": (agregar_distancias, matriz), "8": (ver_impacto_ambiental, viajes), "9": (deshacer_ultima_solicitud, viajes), "10": (cerrar_sesion, contexto)}

    print(MENSAJE_ADMIN)
    correr_menu(MENSAJE_MENU_ADMIN, OPCIONES_ADMIN, "10")


def menu_solicitante(solicitante, contexto):
    viajes = contexto[Viaje]
    matriz = contexto[MatrizDistancia]
    solicitudes = contexto[Solicitud]
    lista_articulos = contexto[Articulo]

    MENSAJE_SOLIC = f"MENU SOLICITANTE: {solicitante}"
    MENSAJE_MENU_SOLIC = "\n1) Crear Solicitud\n2) Ver viajes\n3) Ver matriz\n4) Ver impacto ambiental\n5) Cerrar sesión"
    OPCIONES_SOLIC = {"1": (crear_solicitud, solicitante, viajes, matriz, solicitudes, lista_articulos), "2": (ver_viajes, viajes),"3": (ver_matriz, matriz), "4": (ver_impacto_ambiental, viajes), "5": (cerrar_sesion, contexto)}

    print(MENSAJE_SOLIC)
    correr_menu(MENSAJE_MENU_SOLIC, OPCIONES_SOLIC, "5")


def main():
    contexto = GestorArchivos.leer_todos()
    personas = contexto[Persona]

    MENSAJE_INICIO = "\n" + "=" *50 + "\nSISTEMA LISASA - Planificación de entregas urbanas\n" + "=" *50
    MENSAJE_MENU_INICIO = "\n1) Iniciar sesión\n2) Crear un Administrador\n3) Crear un Solicitante\n4) Ver personas registradas\n5) Salir"
    OPCIONES_INICIO = {"1": (iniciar_sesion, personas, contexto), "2": (crear_administrador, personas),"3": (crear_solicitante, personas),"4": (ver_registrados, personas), "5": (salir, contexto)}

    print(MENSAJE_INICIO)
    correr_menu(MENSAJE_MENU_INICIO, OPCIONES_INICIO, "5")


if __name__ == "__main__":
    main()