"""Testes do main (fase 1): eventos de teclado, update e desenho (sem abrir janela).

Correr a partir da pasta do projeto:  python -m pytest -v
O pygame corre em modo "dummy" (ver conftest.py), por isso não aparece nenhuma janela.
"""
import random

import pygame
import pytest

import config
import main
from state_box import State
from world import World
from conftest import faz_criatura


@pytest.fixture(autouse=True)
def pygame_ligado():
    pygame.init()
    pygame.display.set_mode((10, 10))
    pygame.event.clear()
    yield
    pygame.quit()


def carrega(tecla):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=tecla))


def larga(tecla):
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=tecla))


# ================================================================ eventos

def test_sem_eventos_nada_muda():
    s = State()
    main.eventos(s)
    assert (s.correr, s.pausa, s.turbo) == (True, False, False)


def test_fechar_janela_para_o_programa():
    s = State()
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    main.eventos(s)
    assert s.correr is False


def test_escape_para_o_programa():
    s = State()
    carrega(pygame.K_ESCAPE)
    main.eventos(s)
    assert s.correr is False


def test_espaco_alterna_a_pausa():
    s = State()
    carrega(pygame.K_SPACE)
    main.eventos(s)
    assert s.pausa is True
    carrega(pygame.K_SPACE)
    main.eventos(s)
    assert s.pausa is False


def test_t_alterna_o_turbo():
    s = State()
    carrega(pygame.K_t)
    main.eventos(s)
    assert s.turbo is True
    carrega(pygame.K_t)
    main.eventos(s)
    assert s.turbo is False


def test_largar_tecla_nao_faz_nada():
    s = State()
    larga(pygame.K_SPACE)
    larga(pygame.K_t)
    larga(pygame.K_ESCAPE)
    main.eventos(s)
    assert (s.correr, s.pausa, s.turbo) == (True, False, False)


def test_outras_teclas_sao_ignoradas():
    s = State()
    for tecla in (pygame.K_a, pygame.K_RETURN, pygame.K_UP, pygame.K_1):
        carrega(tecla)
    main.eventos(s)
    assert (s.correr, s.pausa, s.turbo) == (True, False, False)


def test_varios_eventos_no_mesmo_tick():
    s = State()
    carrega(pygame.K_SPACE)
    carrega(pygame.K_t)
    carrega(pygame.K_SPACE)
    main.eventos(s)
    assert (s.correr, s.pausa, s.turbo) == (True, False, True)


def test_eventos_esvazia_a_fila():
    s = State()
    carrega(pygame.K_a)
    carrega(pygame.K_SPACE)
    main.eventos(s)
    assert pygame.event.get() == []


def test_espaco_e_t_mudam_o_avanco():
    s = State()
    carrega(pygame.K_t)
    main.eventos(s)
    assert s.get_avanco_ticks() == config.TICK_AVANCO_TURBO
    carrega(pygame.K_SPACE)
    main.eventos(s)
    assert s.get_avanco_ticks() == config.TICK_PARADO


# ================================================================ update

def test_update_avanca_um_tick():
    w = World(config.WORLD_SIZE)
    main.update(w)
    assert w.n_ticks == 1


# ================================================================ draw

@pytest.fixture
def ecra():
    surface = pygame.Surface(config.TAMANHO_JANELA)
    fonte = pygame.font.SysFont(config.TEXT_FONT, config.TEXT_SIZE)
    return surface, fonte, pygame.time.Clock()


def test_draw_nao_rebenta_com_o_mundo_inicial(ecra):
    surface, fonte, clock = ecra
    random.seed(1)
    main.draw(clock, World(config.WORLD_SIZE), State(), surface, fonte)


def test_draw_nao_rebenta_com_mundo_vazio(ecra):
    surface, fonte, clock = ecra
    w = World(config.WORLD_SIZE)
    w.foods.clear()
    w.creatures.clear()
    main.draw(clock, w, State(pausa=True, turbo=True), surface, fonte)


def test_draw_aguenta_valores_extremos(ecra):
    """Criaturas nas bordas, gigantes, minúsculas, com energia negativa ou enorme e cores nos limites."""
    surface, fonte, clock = ecra
    w = World(config.WORLD_SIZE)
    w.creatures = [
        faz_criatura((0.0, 0.0), size=config.CREATURE_MIN_RADIUS, energy=-5.0, cor=(0, 0, 0)),
        faz_criatura((999.99, 699.99), size=config.CREATURE_MAX_RADIUS, energy=1e6, cor=(255, 255, 255)),
        faz_criatura((500.5, 350.25), size=8.3, energy=0.0001, cor=(0, 255, 7), geracao=10_000),
    ]
    main.draw(clock, w, State(), surface, fonte)


def test_draw_pinta_o_fundo(ecra):
    surface, fonte, clock = ecra
    surface.fill((123, 45, 67))
    w = World(config.WORLD_SIZE)
    w.foods.clear()
    w.creatures.clear()
    main.draw(clock, w, State(), surface, fonte)
    canto = surface.get_at((config.TAMANHO_JANELA[0] - 1, config.TAMANHO_JANELA[1] - 1))
    assert tuple(canto)[:3] == tuple(config.COR_DE_FUNDO)


def test_draw_desenha_a_comida(ecra):
    surface, fonte, clock = ecra
    from food import Food
    w = World(config.WORLD_SIZE)
    w.creatures.clear()
    w.foods = [Food((600.0, 400.0))]
    main.draw(clock, w, State(), surface, fonte)
    assert tuple(surface.get_at((600, 400)))[:3] == tuple(config.FOOD_COLOR)


def test_draw_desenha_a_criatura_com_a_cor_do_genoma(ecra):
    surface, fonte, clock = ecra
    w = World(config.WORLD_SIZE)
    w.foods.clear()
    c = faz_criatura((600.0, 400.0), size=10.0, cor=(10, 200, 30))
    c.angle = 0.0
    w.creatures = [c]
    main.draw(clock, w, State(), surface, fonte)
    # um ponto dentro do círculo, do lado oposto à linha da direção
    assert tuple(surface.get_at((594, 400)))[:3] == (10, 200, 30)
