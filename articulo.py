from validaciones import Validaciones

class Articulo:
    curr_id = 0
    def __init__(self, descripcion, peso, volumen):
        self.descripcion = Validaciones.validar_str(descripcion, nombre = "descripción")
        self.peso = Validaciones.validar_numero(peso, nombre = "peso")
        self.volumen = Validaciones.validar_numero(volumen, nombre = "volumen")
        Articulo.curr_id += 1
        self.id = Articulo.curr_id

    def getter_peso(self):
        return self.peso
    def getter_volumen(self):
        return self.volumen
    def getter_id(self):
        return self.id

    def __str__(self):
        return f"Artículo {self.id}: {self.descripcion} ({self.peso}kg, {self.volumen}m³)"
    def __repr__(self):
        return f"<Articulo {self.id} '{self.descripcion}'>"
    def __eq__(self, otro):
        if isinstance(otro, Articulo):
            return self.id == otro.getter_id()
        return False
    def __hash__(self):
        return hash(self.id)
