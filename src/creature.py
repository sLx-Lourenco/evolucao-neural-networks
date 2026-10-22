import math
import random
import config
import geometria
import genome as gen

class Creature():
    def __init__(self, pos: tuple[float, float], 
                 genoma: gen.Genoma,
                 energy:float = config.CREATURE_BASE_ENERGY):
        
        self.pos=pos
        self.angle = random.uniform(0, 2 * math.pi)
        self.genoma=genoma
        self.energy = energy

    def virar_acaso(self):
        temp= self.angle + random.uniform(-config.CREATURE_MAX_TURN, config.CREATURE_MAX_TURN)
        self.angle = temp % (2 * math.pi)

    def andar(self, worldSize):
        #vetor direcao * velocidade
        deslocamento: tuple[float,float]=(math.cos(self.angle) * self.genoma.velocity,
                                       math.sin(self.angle)* self.genoma.velocity)

        temp_pos= (self.pos[0]+deslocamento[0], self.pos[1]+deslocamento[1])

        self.pos = geometria.wrap(temp_pos, worldSize)

    
    
    def gastar_energia(self):
        custo = config.CREATURE_K_BASE + (config.CREATURE_K1 * self.genoma.size) + (config.CREATURE_K2 * (self.genoma.velocity**2))
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