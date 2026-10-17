from datetime import datetime
from validaciones import Validaciones

class Comprobante:
    curr_id = 0
    def __init__(self,solicitud, fecha_Hora, receptor,monto):
        self.solicitud = self.validar_solicitud(solicitud)
        self.receptor = Validaciones.validar_str(receptor, nombre = "receptor")
        self.fecha_hora = Validaciones.validar_fecha(fecha_Hora, nombre = "fecha y hora del comprobante")
        self.monto=Validaciones.validar_numero(monto, cero = True, nombre = "monto")
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    @staticmethod
    def validar_solicitud(solicitud):
        from solicitud import Solicitud
        return Validaciones.validar_instancia(solicitud, clase = Solicitud, nombre = "solicitud")

    def getter_id(self):
        return self.id
    def getter_fecha_hora(self):
        return self.fecha_hora
    def getter_solicitud(self):
        return self.solicitud
    def getter_receptor(self):
        return self.receptor
    def getter_monto(self):
        return self.monto

    def serializar(self):
        return [self.id, self.solicitud.getter_id(), self.fecha_hora, self.receptor, self.monto]

    @classmethod
    def deserializar(cls, archivo, contexto):
        # Dicc {id: sol}
        from solicitud import Solicitud
        dicc_solicitudes = dict(map(lambda sol: (sol.id, sol), contexto[Solicitud]))
        # Deserializamos los comprobantes
        comprobantes = []
        for fila in archivo[1:]:
            if fila:
                solicitud = dicc_solicitudes[int(fila[1])]
                comprobante = cls(solicitud, datetime.fromisoformat(fila[2]), fila[3], float(fila[4]))
                comprobante.id = int(fila[0])
                solicitud.setter_comprobante(comprobante)
                comprobantes.append(comprobante)
        cls.curr_id = max(cls.curr_id, 0, *map(lambda comp: comp.id, comprobantes))
        return comprobantes

    def __str__(self):
        fecha_str = self.fecha_hora.strftime('%Y-%m-%d %H:%M')
        return f"Comprobante {self.id} | Solicitud {self.solicitud.getter_id()} | Recibió: {self.receptor} el {fecha_str} | Monto: ${self.monto}"
