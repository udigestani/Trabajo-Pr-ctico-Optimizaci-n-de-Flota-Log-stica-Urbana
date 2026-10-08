from excepciones import DatoInvalidoError, DNIInvalidoError, VentanaInvalidaError
from math import isfinite
from datetime import datetime

class Validaciones:
    @staticmethod
    def _resultado(valores):
        if not valores:
            raise TypeError("Se debe pasar al menos un valor para validar")
        return valores[0] if len(valores) == 1 else valores

    @staticmethod
    def validar_str(*valores, nombre = "valor"):
        Validaciones._resultado(valores)
        for valor in valores:
            if not isinstance(valor, str):
                raise TypeError(f"El {nombre} {valor} debe ser una cadena str")
            if not valor.strip():
                raise DatoInvalidoError(f"El {nombre} no debe estar vacío")
        return Validaciones._resultado(valores)

    @staticmethod
    def validar_numero(*valores, cero = False, entero = False, nombre = "valor"):
        Validaciones._resultado(valores)
        if entero:
            tipo = int
        else:
            tipo = (int, float)
        for valor in valores:
            if not isinstance(valor, tipo) or isinstance(valor, bool):
                raise TypeError(f"El {nombre} {valor} debe ser un {'entero' if entero else 'número'}")
            if not isfinite(valor) or valor < 0 or (valor == 0 and not cero):
                raise DatoInvalidoError(f"El {nombre} {valor} debe ser finito y {'no negativo' if cero else 'mayor a 0'}")
        return Validaciones._resultado(valores)

    @staticmethod
    def validar_fecha(*fechas, vacio = False, nombre = "fecha"):
        Validaciones._resultado(fechas)
        for fecha in fechas:
            if not (fecha is None and vacio) and not isinstance(fecha, datetime):
                raise TypeError(f"La {nombre} {fecha} debe ser un objeto datetime")
        return Validaciones._resultado(fechas)

    @staticmethod
    def validar_ventana(inicio, fin):
        Validaciones.validar_fecha(inicio, fin, nombre = "fecha de la ventana")
        if inicio > fin:
            raise VentanaInvalidaError(inicio, fin)
        return inicio, fin

    @staticmethod
    def validar_digitos(valor, cantidades, nombre = "valor"):
        if isinstance(cantidades, int):
            cantidades = (cantidades,)
        if isinstance(valor, int) and not isinstance(valor, bool) and valor > 0 and len(str(valor)) in cantidades:
            return valor
        opciones = " o ".join(str(c) for c in cantidades)
        raise DatoInvalidoError(f"El {nombre} {valor} debe ser un número entero positivo de {opciones} dígitos")

    @staticmethod
    def validar_dni(dni, registrados = ()):
        Validaciones.validar_digitos(dni, (7, 8), "DNI")
        if registrados is None:
            registrados = ()
        if dni in registrados:
            raise DNIInvalidoError(dni)
        return dni

    @staticmethod
    def validar_en(*valores, opciones, nombre = "valor"):
        Validaciones._resultado(valores)
        if isinstance(opciones, str):
            opciones = tuple(opcion.strip() for opcion in opciones.split(","))
        for valor in valores:
            if not isinstance(valor, str):
                raise TypeError(f"El {nombre} {valor} debe ser una cadena str")
            if valor not in opciones:
                raise DatoInvalidoError(f"El {nombre} {valor} debe ser uno de: {', '.join(str(opcion) for opcion in opciones)}")
        return Validaciones._resultado(valores)

    @staticmethod
    def validar_instancia(*valores, clase, nombre = "valor"):
        Validaciones._resultado(valores)
        for valor in valores:
            if not isinstance(valor, clase):
                raise TypeError(f"El {nombre} {valor} debe ser un objeto de clase {clase.__name__}")
        return Validaciones._resultado(valores)

    @staticmethod
    def validar_coleccion(coleccion, tipo = None, clase = None, vacia = False, nombre = "colección"):
        if tipo is not None and not isinstance(coleccion, tipo):
            raise TypeError(f"La {nombre} {coleccion} debe ser de tipo {tipo.__name__}")
        if not vacia:
            if hasattr(coleccion, "esVacia"):
                esta_vacia = coleccion.esVacia()
            elif hasattr(coleccion, "__len__"):
                esta_vacia = len(coleccion) == 0
            else:
                raise TypeError(f"La {nombre} {coleccion} debe ser una colección")
            if esta_vacia:
                raise DatoInvalidoError(f"La {nombre} no debe estar vacía")
        if clase is not None:
            for elemento in coleccion:
                if not isinstance(elemento, clase):
                    raise TypeError(f"La {nombre} contiene {elemento}, que no es un objeto de clase {clase.__name__}")
        return coleccion
