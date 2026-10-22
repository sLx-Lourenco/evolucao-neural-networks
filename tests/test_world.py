"""Testes do mundo (fase 2): ticks e comida.

Correr a partir da pasta do projeto:  python -m pytest -v
Usa os valores do teu config.py. Assume que o World recebe o tamanho
como um tuplo e que cada Food guarda a posição em .pos.
"""
import random
import config as config
from world import World

TAMANHO = (1000, 700)
LARGURA, ALTURA = TAMANHO


def test_mundo_comeca_no_tick_zero():
    assert World(TAMANHO).n_ticks == 0


def test_comida_inicial():
    assert len(World(TAMANHO).foods) == config.INICIAL_AMOUNT_FOOD


def test_comeca_sem_criaturas():
    assert World(TAMANHO).creatures == []


def test_ticks_avancam_um_a_um():
    w = World(TAMANHO)
    for _ in range(250):
        w.advance_tick()
    assert w.n_ticks == 250


def test_mundos_nao_partilham_listas():
    """Apanha a armadilha das listas como valor por omissão."""
    w1, w2 = World(TAMANHO), World(TAMANHO)
    assert w1.foods is not w2.foods
    assert w1.creatures is not w2.creatures
    antes = len(w2.foods)
    w1.gerar_comida(5)
    assert len(w2.foods) == antes


def test_comida_nunca_passa_do_maximo():
    random.seed(1)
    w = World(TAMANHO)
    for _ in range(20_000):
        w.advance_tick()
        assert len(w.foods) <= max(config.MAX_FOOD, config.INICIAL_AMOUNT_FOOD)


def test_comida_chega_ao_maximo():
    random.seed(2)
    w = World(TAMANHO)
    for _ in range(int(50 * config.MAX_FOOD / config.TAXA_FOOD_PER_TICK) + 1000):
        w.advance_tick()
    assert len(w.foods) == max(config.MAX_FOOD, config.INICIAL_AMOUNT_FOOD)


def test_comida_tem_posicao_em_tuplo():
    w = World(TAMANHO)
    for f in w.foods:
        assert len(f.pos) == 2


def test_comida_nasce_dentro_do_mundo():
    random.seed(3)
    w = World(TAMANHO)
    for _ in range(5000):
        w.advance_tick()
    for f in w.foods:
        x, y = f.pos
        assert 0 <= x <= LARGURA and 0 <= y <= ALTURA


def test_comida_usa_o_tamanho_do_proprio_mundo():
    """Um mundo pequeno não pode ter comida fora dele."""
    w = World((100, 50))
    w.gerar_comida(500)
    for f in w.foods:
        x, y = f.pos
        assert 0 <= x <= 100 and 0 <= y <= 50


def test_taxa_de_comida_aproximada():
    """Em média nasce TAXA_FOOD_PER_TICK comida por tick (enquanto não chega ao máximo)."""
    random.seed(4)
    w = World(TAMANHO)
    w.foods.clear()
    ticks = min(2000, int(config.MAX_FOOD / max(config.TAXA_FOOD_PER_TICK, 1e-9) * 0.5))
    for _ in range(ticks):
        w.advance_tick()
    esperado = ticks * config.TAXA_FOOD_PER_TICK
    assert abs(len(w.foods) - esperado) <= max(5, 0.25 * esperado)
