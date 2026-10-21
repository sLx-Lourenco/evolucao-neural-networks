

class World:
    def __init__(self, width:int, height:int, n_ticks:int = 0, foods = [], creatures = []):
        self.width = width
        self.height = height
        self.n_ticks = n_ticks
        self.foods = foods
        self.creatures=creatures


    def add_tick(self):
            self.n_ticks += 1