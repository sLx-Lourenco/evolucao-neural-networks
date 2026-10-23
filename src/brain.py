import numpy as np
import config

rng = np.random.default_rng()

class Brain():
    def __init__(self, w1: np.ndarray,b1: np.ndarray
                 ,w2: np.ndarray,b2: np.ndarray):
        self.w1 = w1
        self.b1=b1
        self.w2=w2
        self.b2=b2

    @classmethod
    def create_random(cls):
        r_w1= rng.normal(0, config.NEURO_DESVIO_DE_PESOS, 
                         size=(config.NEURO_ESCONDIDA, config.NEURO_ENTRADAS))

        r_b1= rng.normal(0, config.NEURO_DESVIO_DE_PESOS, 
                         size=config.NEURO_ESCONDIDA)

        r_w2= rng.normal(0, config.NEURO_DESVIO_DE_PESOS, 
                         size=(config.NEURO_SAIDA, config.NEURO_ESCONDIDA))
        
        r_b2= rng.normal(0, config.NEURO_DESVIO_DE_PESOS, 
                         size=config.NEURO_SAIDA)

        return cls(r_w1,r_b1,r_w2,r_b2)
        
        
    def pensar(self, vect_entrada:np.ndarray):
        vect_entrada = np.asarray(vect_entrada, dtype=float)

        escondida = np.tanh((self.w1 @ vect_entrada) + self.b1)
        saidas = np.tanh((self.w2 @ escondida) + self.b2)

        return saidas

    def copia_mutada(self):
    
            desvio = config.NEURO_DESVIO_MUTACAO

            n_w1 = rng.normal(self.w1, desvio, self.w1.shape)
            n_b1 = rng.normal(self.b1, desvio, self.b1.shape)
            n_w2 = rng.normal(self.w2, desvio, self.w2.shape)
            n_b2 = rng.normal(self.b2, desvio, self.b2.shape)

            return Brain(n_w1,n_b1,n_w2,n_b2)


    


