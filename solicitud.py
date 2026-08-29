from comprobante import Comprobante
from viaje import Viaje

class Solicitud:
    curr_id = 0
    def __init__(self, articulos, ubi_ini , ubi_desti, horario, estado):
        self.articulos = articulos
        self.ubi_ini = ubi_ini
        self.ubi_desti = ubi_desti
        self.horario = horario
        self.estado = estado
        Solicitud.curr_id += 1
        self.id = Solicitud.curr_id

    def generar_comprobante(self, fecha_Hora, monto, receptor):
        self.comprobante = Comprobante(fecha_Hora, monto, receptor)
        return self.comprobante

    def setter_generar_viaje(self, transporte, deposito, horario, estado):
        if self.estado == "pendiente":
            self.viaje = Viaje(transporte, deposito,horario, estado)
            self.estado = "realizada"
            return self.viaje    
    def calcular_peso_total(self):
        total = 0
        for articulo in self.articulos:
            total += articulo.peso
        return total




solicitud1 = Solicitud(["articulo1", "articulo2"], "ubicacion1", "ubicacion2", "10:00", "pendiente")
solicitud1.generar_comprobante("2023-06-01 10:00", 100.0, "receptor1")
print(solicitud1.comprobante.id)
print(solicitud1.horario) 
