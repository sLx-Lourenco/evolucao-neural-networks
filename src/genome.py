import random
import config
import brain
import math

class Genoma:
    def __init__(self, size:float, velocity: float, cor: tuple[int,int,int], geracao:int, 
                 brain:brain.Brain, id_fundador:int):
            self.size = size
            self.velocity = velocity
            self.cor=cor
            self.geracao=geracao
            self.brain = brain
            self.id_fundador = id_fundador


    def copia_mutada(self):

          taxa = config.REPRODUCAO_DESVIO_PADRAO

          s = random.gauss(self.size, taxa * config.CREATURE_BASE_RADIUS)
          s = max(config.CREATURE_MIN_RADIUS, min(config.CREATURE_MAX_RADIUS, s))

          v = random.gauss(self.velocity, taxa * config.CREATURE_BASE_VELOCITY)
          v = max(config.CREATURE_MIN_VELOCITY, min(config.CREATURE_MAX_VELOCITY, v))

          desvio_cor = taxa * 255
          r, g, b = (
            int(max(0, min(255, random.gauss(canal, desvio_cor))))
            for canal in self.cor
          )

          c = (r,g,b)
          ger = self.geracao+1

          b = self.brain.copia_mutada()

          return Genoma(s,v,c,ger, b, self.id_fundador)

