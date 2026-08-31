from comprobante import Comprobante
from viaje import Viaje
from articulo import Articulo
from ubicacion import Ubicacion

class Solicitud:
    curr_id = 0
    # Me parece que ubi_ini no va, porque solicitud no va a saber si es la 1° del viaje (sale del deposito), u otra (sale del lugar de la anterior)
    def __init__(self, articulos, ubi_ini , destino, ventana_horaria, estado):
        self.articulos = self.validar_articulos(articulos)
        # self.ubi_ini = ubi_ini # ?? Va?
        self.destino = self.validar_ubicacion(destino)
        self.ventana_horaria = ventana_horaria
        # self.estado = estado       #Me fijé y estado es algo del viaje no de la solicitud. Asumo que es porque la solicitud está lista cuando se genera el comprobante
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, monto, receptor):
        self.comprobante = Comprobante(fecha_Hora, monto, receptor)
        return self.comprobante

    def getter_ubicacion(self):
        return self.ubi_destino

    def setter_generar_viaje(self, transporte, deposito, horario, estado):
        if self.estado == "pendiente":
            self.viaje = Viaje(transporte, deposito,horario, estado)
            self.estado = "realizada"
            return self.viaje
        
    def calcular_peso(self):
        total = 0
        for articulo in self.articulos:
            total += articulo.getter_peso()
        return total

    def calcular_volumen(self):
        total = 0
        for articulo in self.articulos:
            total += articulo.getter_volumen()
        return total
    
    @staticmethod
    def validar_ubicacion(ubicacion):
        if ubicacion.isinstance(Ubicacion):
            return ubicacion
        raise TypeError(f"La ubicacion debe ser de clase Ubicacion")

    @staticmethod
    def validar_articulos(articulos):
        if articulos.isinstance(list):
            for articulo in articulos:
                if not isinstance(articulo, Articulo):
                    raise TypeError(f"La lista de articulos {articulos} contiene un articulo {articulo} no válido")
            return articulos
        raise TypeError(f"La lista de articulos {articulos} debe ser una lista")

    # @staticmethod
    # def validar_ventana_horaria(ventana_horaria):      ???




# art1 = Articulo("Maquinaria", 200, 4)
# art2 = Articulo("Maquinaria", 150, 3.5)

# solicitud = Solicitud([art1, art2], "ubi1", "ubi2", "10:00", "")
# print(solicitud.calcular_peso(), solicitud.calcular_volumen())
# solicitud1 = Solicitud(["articulo1", "articulo2"], "ubicacion1", "ubicacion2", "10:00", "pendiente")
# solicitud1.generar_comprobante("2023-06-01 10:00", 100.0, "receptor1")
# print(solicitud1.comprobante.id)
# print(solicitud1.horario) 