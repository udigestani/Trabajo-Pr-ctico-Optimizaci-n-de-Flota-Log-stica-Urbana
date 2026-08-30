from comprobante import Comprobante
from viaje import Viaje
from articulo import Articulo
from ubicacion import Ubicacion

class Solicitud:
    curr_id = 0
    # Me parece que ubi_ini no va, porque solicitud no va a saber si es la 1° del viaje (sale del deposito), u otra (sale del lugar de la anterior)
    def __init__(self, articulos, ubi_ini , ubi_destino, llegada_prevista, estado):
        self.articulos = articulos
        # self.ubi_ini = ubi_ini # ?? Va?
        self.ubi_destino = self.comprobar_ubicacion(ubi_destino)
        self.llegada_prevista = llegada_prevista
        self.estado = estado
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, monto, receptor):
        self.comprobante = Comprobante(fecha_Hora, monto, receptor)
        return self.comprobante

    @staticmethod
    def comprobar_ubicacion(ubicacion):
        if ubicacion.isinstance(Ubicacion):
            return ubicacion
        raise TypeError(f"La ubicacion debe ser de clase Ubicacion")

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
    




art1 = Articulo("Maquinaria", 200, 4)
art2 = Articulo("Maquinaria", 150, 3.5)

solicitud = Solicitud([art1, art2], "ubi1", "ubi2", "10:00", "")
print(solicitud.calcular_peso(), solicitud.calcular_volumen())
solicitud1 = Solicitud(["articulo1", "articulo2"], "ubicacion1", "ubicacion2", "10:00", "pendiente")
solicitud1.generar_comprobante("2023-06-01 10:00", 100.0, "receptor1")
print(solicitud1.comprobante.id)
print(solicitud1.horario) 