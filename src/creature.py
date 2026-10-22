import math
import random
import config
import geometria

class Creature():
    def __init__(self, pos: tuple[float, float], size:float, velocity: float, 
                 energy:float = config.CREATURE_BASE_ENERGY):
        self.pos=pos
        self.angle = random.uniform(0, 2 * math.pi)
        self.size = size
        self.velocity = velocity
        self.energy = energy

    def virar_acaso(self):
        temp= self.angle + random.uniform(-config.CREATURE_MAX_TURN, config.CREATURE_MAX_TURN)
        self.angle = temp % (2 * math.pi)

    def andar(self, worldSize):
        #vetor direcao * velocidade
        deslocamento: tuple[float,float]=(math.cos(self.angle) * self.velocity,
                                       math.sin(self.angle)* self.velocity)

        temp_pos= (self.pos[0]+deslocamento[0], self.pos[1]+deslocamento[1])

        self.pos = geometria.wrap(temp_pos, worldSize)

    
    
    def gastar_energia(self):
        custo = config.CREATURE_K_BASE + (config.CREATURE_K1 * self.size) + (config.CREATURE_K2 * (self.velocity**2))
        self.energy-=custo


    def regenerar_energia(self, ammount:float):
        
        #if self.energy+ammount>=config.CREATURE_MAX_ENERGY:
        #    self.energy = config.CREATURE_MAX_ENERGY
        #else:
        #    self.energy +=ammount
        self.energy +=ammount

    def comer(self):
        self.regenerar_energia(config.FOOD_ENERGY)

    def esta_viva(self):
        return self.energy>0