class Transporte:
    curr_id = 0
    # aca tenemos que ver como lo hacmos. lo que estoy pensando es que la velocidad, el costo de viaje y el factor hambiental son cosas que dependen de que se uso para el viaje. Todas esas cosas se caclulan dependiendo el tipo de auto qeu usamos. Entonces tendrian que empezar como cero? y dsp las cambiamos? o directamente no se pasan como parametros?    
    def __init__(self, peso_max, volumen, velocidad, costo_km, costo_parada, factor_ambiental):
        self.peso_max = peso_max
        self.costo_km = costo_km
        self.factor_ambiental = factor_ambiental
        self.volumen = volumen
        self.velocidad = velocidad
        self.costo_parada = costo_parada

        Transporte.curr_id += 1      
        self.id = Transporte.curr_id

class Furgoneta(Transporte):
    PESO_MAX = 500
    VOLUMEN = 8
    VELOCIDAD = 30
    COSTO_KM = 2
    COSTO_PARADA = 5
    FACTOR_AMBIENTAL = 0.27

    def __init__(self):
        super().__init__(
            self.PESO_MAX, 
            self.VOLUMEN, 
            self.VELOCIDAD, 
            self.COSTO_KM, 
            self.COSTO_PARADA, 
            self.FACTOR_AMBIENTAL
        )

class Motocicleta(Transporte):
    PESO_MAX = 40
    VOLUMEN = 1
    VELOCIDAD = 45
    COSTO_KM = 1
    COSTO_PARADA = 3
    FACTOR_AMBIENTAL = 0.27

    def __init__(self):
        super().__init__(
            self.PESO_MAX, 
            self.VOLUMEN, 
            self.VELOCIDAD, 
            self.COSTO_KM, 
            self.COSTO_PARADA, 
            self.FACTOR_AMBIENTAL
        )

class Camion(Transporte):
    PESO_MAX = 1500
    VOLUMEN = 20
    VELOCIDAD = 25
    COSTO_KM = 3.5
    COSTO_PARADA = 10
    FACTOR_AMBIENTAL = 1

    def __init__(self):
        super().__init__(
            self.PESO_MAX, 
            self.VOLUMEN, 
            self.VELOCIDAD, 
            self.COSTO_KM, 
            self.COSTO_PARADA, 
            self.FACTOR_AMBIENTAL
        )

