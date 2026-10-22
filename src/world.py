import food
import random
import config
import creature
import geometria
import genome as gen

class World:
    def __init__(self, size: tuple[float, float]):
        self.size=size
        self.n_ticks:int = 0
        self.foods:list[food.Food] = []
        self.creatures:list[creature.Creature]= []

        self.gerar_comida(config.INICIAL_AMOUNT_FOOD)
        self.gerar_criatura(config.INICIAL_AMOUNT_CREATURES)


    def advance_tick(self):
            self.n_ticks += 1
            filhos:list[creature.Creature] = []

            if(random.uniform(0.0,1.0) < config.TAXA_FOOD_PER_TICK
               and len(self.foods) < config.MAX_FOOD):
                self.gerar_comida()


            for c in self.creatures:
                 c.virar_acaso()
                 c.andar(self.size)
                 c.gastar_energia()

                 self.verificar_alimentacao(c)

                 if c.pode_reproduzir():
                     filhos.append(c.gera_filho())
                     

            
            self.creatures = [c for c in self.creatures if c.esta_viva()]
            self.creatures.extend(filhos)
                 




    def gerar_comida(self, num_comida:int = 1):
         for _ in range(num_comida):
            f = food.Food(
                (random.uniform(0, self.size[0]), random.uniform(0, self.size[1]))
                )
            self.foods.append(f)


    def gerar_criatura(self, num_criaturas:int = 1):
         for _ in range(num_criaturas):

            c_size = random.uniform(config.CREATURE_BASE_RADIUS * (1- config.CREATURE_VARIATION),
                                    config.CREATURE_BASE_RADIUS * (1+ config.CREATURE_VARIATION))

            c_velocity = random.uniform(config.CREATURE_BASE_VELOCITY * (1- config.CREATURE_VARIATION), 
                                        config.CREATURE_BASE_VELOCITY * (1+ config.CREATURE_VARIATION))

            cor:list[int] = []
            for i in range(3):
                cor.append(round(random.uniform(0,config.RANGE_COR_BASE[i])))



            c_cor = (cor[0],cor[1],cor[2])

            genoma = gen.Genoma(c_size, c_velocity, c_cor, 1)


            c = creature.Creature(
                 (random.uniform(0, self.size[0]), random.uniform(0, self.size[1])),
                 genoma
                )
            self.creatures.append(c)


    def verificar_alimentacao(self, c: creature.Creature):


        for f in self.foods:
            vetor= geometria.delta(c.pos, f.pos, self.size)
            h = vetor[0]**2 + vetor[1]**2

            if((c.genoma.size + config.FOOD_RADIUS)**2 > h):
                c.comer()
                self.foods.remove(f)
                break

             
         