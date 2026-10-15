from datetime import datetime
from articulo import Articulo
from transporte import Furgoneta, Motocicleta, Camion
from persona import Persona, Administrador, Solicitante
from matrizdistancia import MatrizDistancia
from politicaordenamiento import Vecinos, VentanasTiempo
from solicitud import Solicitud


def pedir_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("No puede quedar vacio, intenta de nuevo.")


def pedir_entero(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            return int(valor)
        except ValueError:
            print("Tiene que ser un numero entero. Intenta de nuevo.")


def pedir_numero(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            return float(valor)
        except ValueError:
            print("Tiene que ser un numero. Intenta de nuevo.")


def pedir_fecha_hora(mensaje):
    while True:
        valor = input(mensaje + " (formato DD/MM/AAAA HH:MM): ").strip()
        try:
            return datetime.strptime(valor, "%d/%m/%Y %H:%M")
        except ValueError:
            print("Formato invalido. Ejemplo: 01/06/2024 09:30")


def elegir_transporte():
    print("Elegi el transporte:")
    print("  1) Furgoneta")
    print("  2) Motocicleta")
    print("  3) Camion")
    while True:
        opcion = input("Opcion: ").strip()
        if opcion == "1":
            return Furgoneta()
        if opcion == "2":
            return Motocicleta()
        if opcion == "3":
            return Camion()
        print("Opcion invalida, elegi 1, 2 o 3.")


def ubicaciones_conocidas(matriz):
    ubicaciones = set()
    for origen, destino in matriz.getter_distancias().keys():
        ubicaciones.add(origen)
        ubicaciones.add(destino)
    return sorted(ubicaciones)


def destinos_alcanzables_desde(matriz, origen):
    return sorted(d for (o, d) in matriz.getter_distancias().keys() if o == origen)


def agregar_tramo_interactivo(matriz):
    origen = pedir_texto("Origen: ")
    destino = pedir_texto("Destino: ")
    km = pedir_numero("Distancia en km: ")
    matriz.agregar_distancia(origen, destino, km)
    print(f"Cargado: {origen} -> {destino} = {km} km")
    vuelta = input(f"Cargar tambien la vuelta ({destino} -> {origen})? (s/n): ").strip().lower()
    if vuelta == "s":
        km_vuelta = pedir_numero(f"Distancia {destino} -> {origen} en km: ")
        matriz.agregar_distancia(destino, origen, km_vuelta)
        print(f"Cargado: {destino} -> {origen} = {km_vuelta} km")


def pedir_matriz_manual():
    matriz = MatrizDistancia()
    print("Vamos a cargar la matriz tramo por tramo.")
    print("(Necesitas al menos un tramo para poder crear solicitudes despues.)")
    while True:
        agregar_tramo_interactivo(matriz)
        otro = input("Agregar otro tramo? (s/n): ").strip().lower()
        if otro != "s":
            break
    return matriz


def hay_administradores(personas):
    return any(isinstance(p, Administrador) for p in personas)


def crear_solicitante_interactivo():
    print("Vamos a crear un Solicitante.")
    nombre = pedir_texto("Nombre: ")
    dni = pedir_entero("DNI (7 u 8 digitos): ")
    telefono = pedir_entero("Telefono (10 digitos): ")
    return Solicitante(nombre, dni, telefono)


def crear_administrador_interactivo():
    print("Vamos a crear un Administrador.")
    nombre = pedir_texto("Nombre: ")
    dni = pedir_entero("DNI (7 u 8 digitos): ")
    telefono = pedir_entero("Telefono (10 digitos): ")
    return Administrador(nombre, dni, telefono)


def pedir_articulos():
    articulos = []
    while True:
        descripcion = pedir_texto("Descripcion del articulo: ")
        peso = pedir_numero("Peso (kg): ")
        volumen = pedir_numero("Volumen (m3): ")
        articulos.append(Articulo(descripcion, peso, volumen))
        otro = input("Agregar otro articulo? (s/n): ").strip().lower()
        if otro != "s":
            break
    return articulos


def mostrar_estado_viaje(viaje):
    print(f"\n{viaje}")
    print(f"  Estado: {viaje.getter_estado()}")
    print(f"  Carga: {viaje.getter_peso()} kg / {viaje.getter_volumen()} m3  (max {viaje.getter_peso_max()} kg / {viaje.getter_volumen_max()} m3)")
    print(f"  Distancia total: {viaje.distancia_total()} km")
    if viaje.getter_estado() != "PLANIFICADO":
        for parada in viaje.getter_paradas():
            print(f"  {parada}")


def listar_personas(personas):
    if not personas:
        print("Todavia no hay ninguna persona registrada.")
        return
    print("Personas registradas:")
    for persona in personas:
        tipo = "Administrador" if isinstance(persona, Administrador) else "Solicitante"
        print(f"  {persona.getter_nombre()} - DNI {persona.getter_dni()} - {tipo}")


def login(personas):
    dni = pedir_entero("Tu DNI: ")
    for persona in personas:
        if persona.getter_dni() == dni:
            return persona
    print("No hay ninguna persona registrada con ese DNI. Creala primero con la opcion 1.")
    return None


def elegir_viaje(viajes):
    if not viajes:
        print("Todavia no hay ningun viaje creado.")
        return None
    print("Elegi el viaje:")
    for i, viaje in enumerate(viajes):
        print(f"  {i + 1}) {viaje}  [{viaje.getter_estado()}]")
    indice = pedir_entero("Numero: ") - 1
    if 0 <= indice < len(viajes):
        return viajes[indice]
    print("Numero invalido.")
    return None


def mostrar_menu_principal():
    print("\n" + "=" * 50)
    print("SISTEMA LISASA - Planificacion de entregas urbanas")
    print("=" * 50)
    print("1) Crear un Solicitante")
    print("2) Crear un Administrador (solo funciona si todavia no hay ninguno)")
    print("3) Iniciar sesion con DNI")
    print("4) Listar personas registradas")
    print("5) Salir")


def mostrar_menu_admin(admin):
    print("\n" + "-" * 50)
    print(f"Sesion de Administrador: {admin}")
    print("-" * 50)
    print("1) Crear un viaje nuevo")
    print("2) Ver estado de un viaje")
    print("3) Iniciar un viaje")
    print("4) Registrar una entrega")
    print("5) Registrar un incidente")
    print("6) Comparar politicas de ordenamiento")
    print("7) Crear un nuevo Administrador")
    print("8) Ver ubicaciones cargadas / agregar una distancia nueva")
    print("9) Cerrar sesion")


def mostrar_menu_solicitante(solicitante):
    print("\n" + "-" * 50)
    print(f"Sesion de Solicitante: {solicitante}")
    print("-" * 50)
    print("1) Crear una solicitud")
    print("2) Cerrar sesion")


def sesion_admin(admin, viajes, matriz, personas):
    while True:
        mostrar_menu_admin(admin)
        opcion = input("Elegi una opcion: ").strip()

        try:
            if opcion == "1":
                transporte = elegir_transporte()
                deposito = pedir_texto("Nombre del deposito: ")
                horario = pedir_fecha_hora("Horario de salida")
                viaje = admin.crear_viaje(transporte, deposito, horario, matriz)
                viajes.append(viaje)
                print(f"Viaje creado: {viaje}")

            elif opcion == "2":
                viaje = elegir_viaje(viajes)
                if viaje is not None:
                    mostrar_estado_viaje(viaje)

            elif opcion == "3":
                viaje = elegir_viaje(viajes)
                if viaje is not None:
                    viaje.iniciar_viaje()
                    print(f"Viaje iniciado. Estado: {viaje.getter_estado()}")
                    for parada in viaje.getter_paradas():
                        print(f"  {parada}")

            elif opcion == "4":
                viaje = elegir_viaje(viajes)
                if viaje is not None:
                    hora_real = pedir_fecha_hora("Hora real de entrega")
                    receptor = pedir_texto("Nombre de quien recibe: ")
                    monto = pedir_numero("Monto: ")
                    comprobante = viaje.registrar_entrega(hora_real, receptor, monto)
                    print(f"Comprobante generado: {comprobante}")

            elif opcion == "5":
                viaje = elegir_viaje(viajes)
                if viaje is not None:
                    print("Tipo de incidente: 1) DAÑO  2) AUSENTE  3) RETRASO")
                    tipo_op = input("Opcion: ").strip()
                    tipo = {"1": "DAÑO", "2": "AUSENTE", "3": "RETRASO"}.get(tipo_op, "DAÑO")
                    fecha = pedir_fecha_hora("Fecha y hora del incidente")
                    descripcion = pedir_texto("Descripcion: ")
                    incidente = viaje.registrar_incidente(tipo, fecha, descripcion)
                    print(f"Incidente registrado: {incidente}")

            elif opcion == "6":
                print("Vas a armar una lista de solicitudes SUELTAS, solo para comparar el orden sugerido.")
                print("(Esto no crea ni modifica ningun viaje.)")
                solicitudes = []
                while True:
                    destino = pedir_texto("Destino: ")
                    ventana_inicio = pedir_fecha_hora("Inicio de ventana")
                    ventana_fin = pedir_fecha_hora("Fin de ventana")
                    solicitudes.append(Solicitud(destino, ventana_inicio, ventana_fin, Articulo("Generico", 1, 1)))
                    otra = input("Agregar otra solicitud? (s/n): ").strip().lower()
                    if otra != "s":
                        break
                deposito_ref = pedir_texto("Deposito de referencia: ")
                orden_vecinos = Vecinos().sugerir_orden(deposito_ref, solicitudes, matriz)
                orden_ventanas = VentanasTiempo().sugerir_orden(deposito_ref, solicitudes, matriz)
                print("Orden por Vecinos (mas cercano primero):", [s.getter_destino() for s in orden_vecinos])
                print("Orden por VentanasTiempo (ventana mas temprana primero):", [s.getter_destino() for s in orden_ventanas])

            elif opcion == "7":
                nuevo_admin = crear_administrador_interactivo()
                personas.append(nuevo_admin)
                print(f"Creado: {nuevo_admin}")

            elif opcion == "8":
                print("Ubicaciones conocidas por la matriz:", ubicaciones_conocidas(matriz))
                agregar = input("Queres agregar una distancia nueva? (s/n): ").strip().lower()
                if agregar == "s":
                    agregar_tramo_interactivo(matriz)

            elif opcion == "9":
                print("Cerrando sesion.")
                break

            else:
                print("Opcion invalida, elegi un numero del menu.")

        except Exception as e:
            print(f"\n>>> ERROR: {type(e).__name__}: {e}\n")


def sesion_solicitante(solicitante, viajes, matriz):
    while True:
        mostrar_menu_solicitante(solicitante)
        opcion = input("Elegi una opcion: ").strip()

        try:
            if opcion == "1":
                disponibles = [v for v in viajes if v.getter_estado() == "PLANIFICADO"]
                if not disponibles:
                    print("No hay ningun viaje planificado disponible por ahora. Pedile a un administrador que cree uno.")
                    continue
                viaje = elegir_viaje(disponibles)
                if viaje is None:
                    continue
                alcanzables = destinos_alcanzables_desde(matriz, viaje.deposito)
                if alcanzables:
                    print(f"Desde '{viaje.deposito}' hay distancia cargada hacia: {alcanzables}")
                else:
                    print(f"Todavia no hay ninguna distancia cargada desde '{viaje.deposito}'.")
                    print("Pedile a un administrador que la agregue (opcion 3 del menu principal).")
                    continue
                destino = pedir_texto("Destino de la solicitud (tiene que ser uno de los de arriba): ")
                ventana_inicio = pedir_fecha_hora("Inicio de la ventana")
                ventana_fin = pedir_fecha_hora("Fin de la ventana")
                articulos = pedir_articulos()
                solicitud = solicitante.crear_solicitud(viaje, destino, ventana_inicio, ventana_fin, *articulos)
                print(f"Solicitud agregada: {solicitud}")

            elif opcion == "2":
                print("Cerrando sesion.")
                break

            else:
                print("Opcion invalida, elegi un numero del menu.")

        except Exception as e:
            print(f"\n>>> ERROR: {type(e).__name__}: {e}\n")


def main():
    # Permite correr el programa varias veces en la misma sesion sin
    # chocar con DNIs de una corrida anterior.
    Persona.limpiar_dnis_registrados()

    print("Antes de arrancar, vamos a cargar la matriz de distancias.")
    matriz = pedir_matriz_manual()
    print("Matriz cargada.")

    personas = []
    viajes = []

    while True:
        mostrar_menu_principal()
        opcion = input("Elegi una opcion: ").strip()

        try:
            if opcion == "1":
                persona = crear_solicitante_interactivo()
                personas.append(persona)
                print(f"Creado: {persona}")

            elif opcion == "2":
                if hay_administradores(personas):
                    print("Ya existe un Administrador registrado.")
                    print("Para crear otro, logueate como administrador (opcion 3) y usa su menu.")
                    continue
                persona = crear_administrador_interactivo()
                personas.append(persona)
                print(f"Creado: {persona}")

            elif opcion == "3":
                persona = login(personas)
                if persona is None:
                    continue
                print(f"Sesion iniciada como: {persona}")
                if isinstance(persona, Administrador):
                    sesion_admin(persona, viajes, matriz, personas)
                else:
                    sesion_solicitante(persona, viajes, matriz)

            elif opcion == "4":
                listar_personas(personas)

            elif opcion == "5":
                print("Listo, saliendo.")
                break

            else:
                print("Opcion invalida, elegi un numero del menu.")

        except Exception as e:
            print(f"\n>>> ERROR: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()