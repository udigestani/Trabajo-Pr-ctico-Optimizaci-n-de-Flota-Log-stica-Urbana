from datetime import datetime

class Comprobante:
    curr_id = 0
    def __init__(self,solicitud, fecha_Hora, receptor,monto):
        self.solicitud = self.validar_solicitud(solicitud)
        self.receptor = self.validar_receptor(receptor)
        self.fecha_Hora = self.validar_fecha_hora(fecha_Hora)
        self.monto=self.validar_monto(monto)
        Comprobante.curr_id += 1
        self.id = Comprobante.curr_id

    @staticmethod
    def validar_receptor(receptor):
        if not isinstance(receptor, str):
            raise TypeError(f"El receptor {receptor} debe ser una cadena str")
        if receptor and receptor.strip():
            return receptor
        raise ValueError(f"El receptor no puede ser vacio")

    @staticmethod
    def validar_fecha_hora(fecha_hora):
        if not isinstance(fecha_hora, datetime):
            raise TypeError("La fecha_hora del comprobante debe ser un objeto datetime")
        return fecha_hora

    @staticmethod
    def validar_solicitud(solicitud):
        from solicitud import Solicitud    #El import esta aca xq sino no abre el archivo
        if not isinstance(solicitud, Solicitud):
            raise TypeError("La solicitud debe ser un objeto de la clase Solicitud")
        return solicitud
    
    @staticmethod
    def validar_monto(monto):
        if not isinstance(monto, (int, float)):
            raise TypeError("El monto debe ser un número")
        if monto < 0:
            raise ValueError("El monto no puede ser negativo")
        return monto
comp1=Comprobante("solicitud1", datetime(2023, 6, 1, 10, 0), "Juan Perez", 1500)
print(comp1.id, comp1.solicitud, comp1.fecha_Hora, comp1.receptor, comp1.monto)
