from validaciones import Validaciones

class Comprobante:
    curr_id = 0
    def __init__(self,solicitud, fecha_Hora, receptor,monto):
        self.solicitud = self.validar_solicitud(solicitud)
        self.receptor = Validaciones.validar_str(receptor, nombre = "receptor")
        self.fecha_Hora = Validaciones.validar_fecha(fecha_Hora, nombre = "fecha y hora del comprobante")
        self.monto=Validaciones.validar_numero(monto, cero = True, nombre = "monto")
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    @staticmethod
    def validar_solicitud(solicitud):
        from solicitud import Solicitud
        return Validaciones.validar_instancia(solicitud, clase = Solicitud, nombre = "solicitud")

    
    def getter_solicitud(self):
        return self.solicitud
    def getter_receptor(self):
        return self.receptor
    def getter_monto(self):
        return self.monto

    def __str__(self):
        fecha_str = self.fecha_Hora.strftime('%Y-%m-%d %H:%M')
        return f"Comprobante {self.id} | Solicitud {self.solicitud.getter_id()} | Recibió: {self.receptor} el {fecha_str} | Monto: ${self.monto}"
