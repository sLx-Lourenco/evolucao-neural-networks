import food as food
import random
import config as config

class World:
    def __init__(self, size: tuple[int, int]):
        self.size=size
        self.n_ticks:int = 0
        self.foods:list[food.Food] = []
        self.creatures:list= []

        self.gerar_comida(config.INICIAL_AMOUNT_FOOD)


    def advance_tick(self):
            self.n_ticks += 1

            if(random.uniform(0.0,1.0) < config.TAXA_FOOD_PER_TICK
               and len(self.foods) < config.MAX_FOOD):
                self.gerar_comida()

    def gerar_comida(self, num_comida:int = 1):
         for _ in range(num_comida):
            f = food.Food(
                (random.uniform(0, self.size[0]), random.uniform(0, self.size[1]))
                )
            self.foods.append(f)