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


def crear_persona():
    print("Que persona queres crear?")
    print("  1) Administrador")
    print("  2) Solicitante")
    tipo = input("Opcion: ").strip()
    nombre = pedir_texto("Nombre: ")
    dni = pedir_entero("DNI (7 u 8 digitos): ")
    telefono = pedir_entero("Telefono (10 digitos): ")
    if tipo == "1":
        return Administrador(nombre, dni, telefono)
    return Solicitante(nombre, dni, telefono)


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


def mostrar_menu():
    print("\n" + "=" * 50)
    print("SISTEMA LISASA - Planificacion de entregas urbanas")
    print("=" * 50)
    print("1) Crear persona (Administrador o Solicitante)")
    print("2) Crear un viaje nuevo")
    print("3) Agregar una solicitud al viaje actual")
    print("4) Ver estado del viaje actual")
    print("5) Iniciar el viaje actual")
    print("6) Registrar una entrega")
    print("7) Registrar un incidente")
    print("8) Comparar politicas de ordenamiento")
    print("9) Salir")
    print("0) Ver ubicaciones cargadas / agregar una distancia nueva")
    print("10) Deshacer la ultima solicitud agregada al viaje actual")


def main():
    # Permite correr el programa varias veces en la misma sesion sin
    # chocar con DNIs de una corrida anterior.
    Persona.limpiar_dnis_registrados()

    print("Antes de arrancar, vamos a cargar la matriz de distancias.")
    matriz = pedir_matriz_manual()
    print("Matriz cargada.")

    personas = []
    viaje_actual = None

    while True:
        mostrar_menu()
        opcion = input("Elegi una opcion: ").strip()

        try:
            if opcion == "1":
                persona = crear_persona()
                personas.append(persona)
                print(f"Creado: {persona}")

            elif opcion == "2":
                admins = [p for p in personas if isinstance(p, Administrador)]
                if not admins:
                    print("Primero teness que crear un Administrador (opcion 1).")
                    continue
                print("Elegi el administrador:")
                for i, a in enumerate(admins):
                    print(f"  {i + 1}) {a}")
                idx = pedir_entero("Numero: ") - 1
                admin = admins[idx]
                transporte = elegir_transporte()
                deposito = pedir_texto("Nombre del deposito: ")
                horario = pedir_fecha_hora("Horario de salida")
                viaje_actual = admin.crear_viaje(transporte, deposito, horario, matriz)
                print(f"Viaje creado: {viaje_actual}")

            elif opcion == "3":
                if viaje_actual is None:
                    print("Primero crea un viaje (opcion 2).")
                    continue
                alcanzables = destinos_alcanzables_desde(matriz, viaje_actual.deposito)
                if alcanzables:
                    print(f"Desde '{viaje_actual.deposito}' hay distancia cargada hacia: {alcanzables}")
                else:
                    print(f"Todavia no hay ninguna distancia cargada desde '{viaje_actual.deposito}'.")
                    print("Usa la opcion 0 del menu para agregar una antes de continuar.")
                    continue
                destino = pedir_texto("Destino de la solicitud (tiene que ser uno de los de arriba): ")
                ventana_inicio = pedir_fecha_hora("Inicio de la ventana")
                ventana_fin = pedir_fecha_hora("Fin de la ventana")
                articulos = pedir_articulos()
                solicitud = viaje_actual.crear_solicitud(destino, ventana_inicio, ventana_fin, *articulos)
                print(f"Solicitud agregada: {solicitud}")

            elif opcion == "4":
                if viaje_actual is None:
                    print("Todavia no hay ningun viaje creado.")
                    continue
                mostrar_estado_viaje(viaje_actual)

            elif opcion == "5":
                if viaje_actual is None:
                    print("Todavia no hay ningun viaje creado.")
                    continue
                viaje_actual.iniciar_viaje()
                print(f"Viaje iniciado. Estado: {viaje_actual.getter_estado()}")
                for parada in viaje_actual.getter_paradas():
                    print(f"  {parada}")

            elif opcion == "6":
                if viaje_actual is None:
                    print("Todavia no hay ningun viaje creado.")
                    continue
                hora_real = pedir_fecha_hora("Hora real de entrega")
                receptor = pedir_texto("Nombre de quien recibe: ")
                monto = pedir_numero("Monto: ")
                comprobante = viaje_actual.registrar_entrega(hora_real, receptor, monto)
                print(f"Comprobante generado: {comprobante}")

            elif opcion == "7":
                if viaje_actual is None:
                    print("Todavia no hay ningun viaje creado.")
                    continue
                print("Tipo de incidente: 1) DAÑO  2) AUSENTE  3) RETRASO")
                tipo_op = input("Opcion: ").strip()
                tipo = {"1": "DAÑO", "2": "AUSENTE", "3": "RETRASO"}.get(tipo_op, "DAÑO")
                fecha = pedir_fecha_hora("Fecha y hora del incidente")
                descripcion = pedir_texto("Descripcion: ")
                incidente = viaje_actual.registrar_incidente(tipo, fecha, descripcion)
                print(f"Incidente registrado: {incidente}")

            elif opcion == "8":
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
                orden_vecinos = Vecinos.sugerir_orden(deposito_ref, solicitudes, matriz)
                orden_ventanas = VentanasTiempo.sugerir_orden(deposito_ref, solicitudes, matriz)
                print("Orden por Vecinos (mas cercano primero):", [s.getter_destino() for s in orden_vecinos])
                print("Orden por VentanasTiempo (ventana mas temprana primero):", [s.getter_destino() for s in orden_ventanas])

            elif opcion == "9":
                print("Listo, saliendo.")
                break

            elif opcion == "0":
                print("Ubicaciones conocidas por la matriz:", ubicaciones_conocidas(matriz))
                agregar = input("Queres agregar una distancia nueva? (s/n): ").strip().lower()
                if agregar == "s":
                    agregar_tramo_interactivo(matriz)

            elif opcion == "10":
                if viaje_actual is None:
                    print("Todavia no hay ningun viaje creado.")
                    continue
                solicitud = viaje_actual.deshacer_ultima_solicitud()
                print(f"Solicitud deshecha: {solicitud}")

            else:
                print("Opcion invalida, elegi un numero del menu.")

        except Exception as e:
            print(f"\n>>> ERROR: {type(e).__name__}: {e}\n")


if __name__ == "__main__":
    main()