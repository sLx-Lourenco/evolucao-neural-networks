import random
import config

class Genoma:
    def __init__(self, size:float, velocity: float, cor: tuple[int,int,int], geracao:int):
            self.size = size
            self.velocity = velocity
            self.cor=cor
            self.geracao=geracao


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

          return Genoma(s,v,c,ger)