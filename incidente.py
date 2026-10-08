from validaciones import Validaciones
from solicitud import Solicitud


class Incidente:
    curr_id = 0
    def __init__(self, tipo, fecha, descripcion, afectado, **detalles):
        self.tipo = Validaciones.validar_en(tipo, opciones = "DAÑO, AUSENTE, RETRASO", nombre = "tipo del incidente")
        self.fecha = Validaciones.validar_fecha(fecha, nombre = "fecha del incidente")
        self.descripcion = Validaciones.validar_str(descripcion, nombre = "descripción").strip()
        self.afectado = Validaciones.validar_instancia(afectado, clase = Solicitud, nombre = "afectado")
        self.detalles = self.validar_detalles(detalles)
        Incidente.curr_id += 1
        self.id = Incidente.curr_id

    @staticmethod
    def validar_detalles(detalles):
        for clave, valor in detalles.items():
            if isinstance(valor, str):
                Validaciones.validar_str(valor, nombre = f"detalle {clave}")
        return detalles
    def getter_tipo(self):
        return self.tipo
    def getter_afectado(self):
        return self.afectado
    def getter_detalles(self):
        return self.detalles.copy()

    def __str__(self):
        fecha_str = self.fecha.strftime('%H:%M')
        base = f"Incidente {self.id} [{self.tipo}] a las {fecha_str}: {self.descripcion}"
        for clave, valor in self.detalles.items():
            base += f", {clave}={valor}"
        return base
    def __repr__(self):
        return f"Incidente({self.tipo}, {self.fecha}, {self.descripcion}, {self.afectado}, **{self.detalles})"