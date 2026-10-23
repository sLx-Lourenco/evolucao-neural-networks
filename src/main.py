import pygame
import state_box as sb
import config as config
import world as w
import food as food
import math



def eventos(state:sb.State):

    for evento in pygame.event.get():
         match(evento.type):
            
            case pygame.QUIT: 
                     state.correr = False

            case pygame.KEYDOWN: 
                     match (evento.key):

                        case pygame.K_ESCAPE:
                               state.correr = False

                        case pygame.K_SPACE:
                               state.pausa = not state.pausa

                        case pygame.K_t : 
                               state.turbo= not state.turbo


def update(world:w.World):
    world.advance_tick()


def draw(clock, world: w.World, state:sb.State, surface, fonte):
    ids_f:list[int]=[]

    surface.fill(config.COR_DE_FUNDO)

    text_fps = fonte.render(f"Fps: {round(clock.get_fps())}", True, config.COR_DE_TEXT)
    text_ticks = fonte.render(f"Ticks: {world.n_ticks}", True, config.COR_DE_TEXT)

    text_pausa = fonte.render(f"PAUSA: {state.pausa}", True, config.COR_DE_TEXT)
    text_turbo = fonte.render(f"TURBO: {state.turbo}", True, config.COR_DE_TEXT)

    surface.blit(text_fps, (0,0))

    surface.blit(text_pausa, (100,0))

    surface.blit(text_ticks, (0,20))

    surface.blit(text_turbo, (100,20))

    #FOOD
    for f in world.foods:
         pygame.draw.circle(
              surface, 
              config.FOOD_COLOR,
              f.pos,
              config.FOOD_RADIUS)


    for c in world.creatures:
         if c.genoma.id_fundador not in ids_f:
            ids_f.append(c.genoma.id_fundador)

        
         text_vida = fonte.render(f"{round(c.energy)} : {c.genoma.geracao}", True, config.COR_DE_TEXT)
         surface.blit(text_vida, (c.pos[0]-10,c.pos[1]-25))

         
         pygame.draw.circle(
                surface,
                c.genoma.cor,
                c.pos,
                c.genoma.size)

         fim = (c.pos[0] + math.cos(c.angle) * c.genoma.size,
                c.pos[1] + math.sin(c.angle) * c.genoma.size)
    
         pygame.draw.line(
                surface, 
                config.CREATURE_DIRECTION_COLOR, 
                c.pos, 
                fim, 
                config.CREATURE_DIRECTION_LARGURA)
         
    texto = "Fundadores: " + " | ".join(str(i) for i in sorted(ids_f))
    text_fundadores = fonte.render(texto, True, config.COR_DE_TEXT)
    surface.blit(text_fundadores, (0, 40))     
    pygame.display.flip()





def main():
    pygame.init()
    pygame.display.set_caption("Evolucao")

    caixa_de_estado = sb.State()
    world= w.World(config.WORLD_SIZE)
    clock = pygame.time.Clock()
    

    fonte= pygame.font.SysFont(config.TEXT_FONT,config.TEXT_SIZE)


    surface = pygame.display.set_mode(config.TAMANHO_JANELA)

    while(caixa_de_estado.correr):
        eventos(caixa_de_estado)

        
        for _ in range(caixa_de_estado.get_avanco_ticks()):         
            update(world)


        draw(clock, world, caixa_de_estado, surface, fonte)
        

        clock.tick(config.FPS)


    pygame.quit()

    
if __name__ == "__main__":
    main()