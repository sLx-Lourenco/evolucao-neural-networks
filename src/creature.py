import math
import random
import config
import geometria
import genome as gen
import numpy as np

class Creature():
    def __init__(self, pos: tuple[float, float], 
                 genoma: gen.Genoma,
                 energy:float = config.CREATURE_BASE_ENERGY):
        
        self.pos=pos
        self.angle = random.uniform(0, 2 * math.pi)
        self.genoma=genoma
        self.energy = energy
        self.velocidade_real = 0

    def virar(self, saida1: float):
        temp= self.angle + saida1 * config.CREATURE_MAX_TURN
        self.angle = temp % (2 * math.pi)

    def andar(self, worldSize):
        #vetor direcao * velocidade
        deslocamento: tuple[float,float]=(math.cos(self.angle) * self.velocidade_real,
                                       math.sin(self.angle)* self.velocidade_real)

        temp_pos= (self.pos[0]+deslocamento[0], self.pos[1]+deslocamento[1])

        self.pos = geometria.wrap(temp_pos, worldSize)

    
    
    def gastar_energia(self):
        custo = config.CREATURE_K_BASE + (config.CREATURE_K1 * self.genoma.size) + (config.CREATURE_K2 * (self.velocidade_real**2)) + (config.CREATURE_K3 * (self.genoma.velocity**2))
        self.energy-=custo


    def regenerar_energia(self, ammount:float):
        self.energy +=ammount

    def comer(self):
        self.regenerar_energia(config.FOOD_ENERGY)

    def esta_viva(self):
        return self.energy>0

    def pode_reproduzir(self):
        return self.energy>config.REPRODUCAO_LIMIAR

    def gera_filho(self):
        novo_genoma = self.genoma.copia_mutada()
        energia_dada = self.energy * config.REPRODUCAO_PERCENTAGEM
        filho = Creature(self.pos, novo_genoma, energia_dada)
        self.energy= self.energy - energia_dada - config.REPRODUCAO_CUSTO
        return filho

    def energia_normalizada(self):
        return min(((self.energy/config.REPRODUCAO_LIMIAR)*2)-1, 1)

    def calcula_velocidade_real(self, x:float):
        self.velocidade_real= (x+1)/2 * self.genoma.velocity

    def agir(self, saidas:np.ndarray):
        self.virar(saidas[0])
        self.calcula_velocidade_real(saidas[1])
        


