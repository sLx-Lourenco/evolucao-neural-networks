import config

class State:
    def __init__(self, correr:bool = True, pausa:bool = False, turbo:bool = False):
        self.correr = correr
        self.pausa=pausa
        self.turbo=turbo


    def get_avanco_ticks(self):
        if(self.pausa):
            return config.TICK_PARADO
        elif(self.turbo):
            return config.TICK_AVANCO_TURBO
        else:
            return config.TICK_AVANCO
    
