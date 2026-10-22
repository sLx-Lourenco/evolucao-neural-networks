"""Testes do mundo: ticks, comida (fase 2) e criaturas (fase 3).

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import math
import random

import pytest

import config
from creature import Creature
from food import Food
from world import World

TAMANHO = (1000, 700)
LARGURA, ALTURA = TAMANHO


def mundo_vazio():
    """Um mundo sem comida nem criaturas, para montar cada cenário à mão."""
    w = World(TAMANHO)
    w.foods.clear()
    w.creatures.clear()
    return w


def mundo_so_comida():
    """Um mundo normal, mas sem criaturas a comer (para testar só a comida)."""
    w = World(TAMANHO)
    w.creatures.clear()
    return w


# ================================================================ configuração

def test_config_comida_inicial_nao_passa_do_maximo():
    assert config.INICIAL_AMOUNT_FOOD <= config.MAX_FOOD, (
        "A comida inicial é maior do que o máximo: o mundo começa acima do limite."
    )


# ================================================================ ticks

def test_mundo_comeca_no_tick_zero():
    assert World(TAMANHO).n_ticks == 0


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


# ================================================================ comida

def test_comida_inicial():
    assert len(World(TAMANHO).foods) == config.INICIAL_AMOUNT_FOOD


def test_comida_tem_posicao_em_tuplo():
    for f in World(TAMANHO).foods:
        assert len(f.pos) == 2


def test_comida_nunca_passa_do_maximo():
    random.seed(1)
    w = mundo_so_comida()
    for _ in range(20_000):
        w.advance_tick()
        assert len(w.foods) <= max(config.MAX_FOOD, config.INICIAL_AMOUNT_FOOD)


def test_comida_chega_ao_maximo():
    random.seed(2)
    w = mundo_so_comida()
    for _ in range(int(50 * config.MAX_FOOD / config.TAXA_FOOD_PER_TICK) + 1000):
        w.advance_tick()
    assert len(w.foods) == max(config.MAX_FOOD, config.INICIAL_AMOUNT_FOOD)


def test_comida_nasce_dentro_do_mundo():
    random.seed(3)
    w = mundo_so_comida()
    for _ in range(5000):
        w.advance_tick()
    for f in w.foods:
        x, y = f.pos
        assert 0 <= x <= LARGURA and 0 <= y <= ALTURA


def test_comida_usa_o_tamanho_do_proprio_mundo():
    w = World((100, 50))
    w.gerar_comida(500)
    for f in w.foods:
        x, y = f.pos
        assert 0 <= x <= 100 and 0 <= y <= 50


def test_taxa_de_comida_aproximada():
    random.seed(4)
    w = mundo_vazio()
    ticks = min(2000, int(config.MAX_FOOD / max(config.TAXA_FOOD_PER_TICK, 1e-9) * 0.5))
    for _ in range(ticks):
        w.advance_tick()
    esperado = ticks * config.TAXA_FOOD_PER_TICK
    assert abs(len(w.foods) - esperado) <= max(5, 0.25 * esperado)


# ================================================================ criaturas: criação

def test_criaturas_iniciais():
    assert len(World(TAMANHO).creatures) == config.INICIAL_AMOUNT_CREATURES


def test_criaturas_sao_objetos_diferentes():
    w = World(TAMANHO)
    assert len({id(c) for c in w.creatures}) == len(w.creatures)


def test_criaturas_nascem_dentro_do_mundo():
    random.seed(10)
    for c in World(TAMANHO).creatures:
        assert 0 <= c.pos[0] <= LARGURA and 0 <= c.pos[1] <= ALTURA


def test_criaturas_nascem_no_mundo_pequeno():
    random.seed(11)
    w = mundo_vazio()
    w.size = (100, 50)
    w.gerar_criatura(300)
    for c in w.creatures:
        assert 0 <= c.pos[0] <= 100 and 0 <= c.pos[1] <= 50


def test_tamanho_dentro_da_variacao():
    random.seed(12)
    w = mundo_vazio()
    w.gerar_criatura(500)
    lo = config.CREATURE_BASE_RADIUS * (1 - config.CREATURE_VARIATION)
    hi = config.CREATURE_BASE_RADIUS * (1 + config.CREATURE_VARIATION)
    for c in w.creatures:
        assert lo <= c.size <= hi


def test_velocidade_dentro_da_variacao():
    """Apanha o erro de sortear a velocidade à volta do raio."""
    random.seed(13)
    w = mundo_vazio()
    w.gerar_criatura(500)
    lo = config.CREATURE_BASE_VELOCITY * (1 - config.CREATURE_VARIATION)
    hi = config.CREATURE_BASE_VELOCITY * (1 + config.CREATURE_VARIATION)
    for c in w.creatures:
        assert lo <= c.velocity <= hi


def test_criaturas_nascem_diferentes():
    random.seed(14)
    w = mundo_vazio()
    w.gerar_criatura(100)
    assert len({round(c.size, 6) for c in w.creatures}) > 90
    assert len({round(c.velocity, 6) for c in w.creatures}) > 90


def test_criaturas_nascem_com_energia_base():
    for c in World(TAMANHO).creatures:
        assert c.energy == config.CREATURE_BASE_ENERGY


# ================================================================ criaturas: comer

def criatura_em(pos, size=8.0, velocity=2.0, energy=50.0):
    return Creature(pos, size, velocity, energy)


def test_come_comida_em_cima():
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0))
    w.creatures.append(c)
    w.foods.append(Food((500.0, 350.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []
    assert c.energy == pytest.approx(50.0 + config.FOOD_ENERGY)


def test_come_quando_os_circulos_se_tocam():
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0), size=8.0)
    alcance = 8.0 + config.FOOD_RADIUS
    w.foods.append(Food((500.0 + alcance - 0.5, 350.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []


def test_nao_come_comida_longe():
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0), size=8.0)
    alcance = 8.0 + config.FOOD_RADIUS
    f = Food((500.0 + alcance + 0.5, 350.0))
    w.foods.append(f)
    w.verificar_alimentacao(c)
    assert w.foods == [f]
    assert c.energy == 50.0


def test_nao_come_comida_longe_na_diagonal():
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0), size=8.0)
    alcance = 8.0 + config.FOOD_RADIUS
    d = (alcance + 0.5) / math.sqrt(2)
    f = Food((500.0 + d, 350.0 + d))
    w.foods.append(f)
    w.verificar_alimentacao(c)
    assert w.foods == [f]


def test_criatura_maior_chega_mais_longe():
    w = mundo_vazio()
    pequena = criatura_em((200.0, 350.0), size=6.0)
    grande = criatura_em((600.0, 350.0), size=10.0)
    distancia = 8.0 + config.FOOD_RADIUS
    fp = Food((200.0 + distancia, 350.0))
    fg = Food((600.0 + distancia, 350.0))
    w.foods.extend([fp, fg])
    w.verificar_alimentacao(pequena)
    w.verificar_alimentacao(grande)
    assert fp in w.foods
    assert fg not in w.foods


def test_come_atraves_da_borda():
    """A criatura em x=2 e a comida em x=998 estão a 4 pixéis uma da outra."""
    w = mundo_vazio()
    c = criatura_em((2.0, 350.0))
    w.foods.append(Food((998.0, 350.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []


def test_come_atraves_do_canto():
    w = mundo_vazio()
    c = criatura_em((1.0, 1.0))
    w.foods.append(Food((998.0, 698.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []


def test_so_come_uma_comida_por_tick():
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0))
    w.foods.extend([Food((500.0, 350.0)) for _ in range(3)])
    w.verificar_alimentacao(c)
    assert len(w.foods) == 2
    assert c.energy == pytest.approx(50.0 + config.FOOD_ENERGY)


def test_comer_nao_mexe_na_outra_comida():
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0))
    longe1, perto, longe2 = Food((100.0, 100.0)), Food((500.0, 350.0)), Food((900.0, 600.0))
    w.foods.extend([longe1, perto, longe2])
    w.verificar_alimentacao(c)
    assert w.foods == [longe1, longe2]


def test_duas_criaturas_nao_comem_a_mesma_comida():
    w = mundo_vazio()
    a, b = criatura_em((500.0, 350.0)), criatura_em((501.0, 350.0))
    w.foods.append(Food((500.5, 350.0)))
    w.verificar_alimentacao(a)
    w.verificar_alimentacao(b)
    assert a.energy + b.energy == pytest.approx(100.0 + config.FOOD_ENERGY)


# ================================================================ criaturas: o tick

def test_tick_mexe_as_criaturas(monkeypatch):
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0), velocity=2.0)
    w.creatures.append(c)
    w.advance_tick()
    assert math.hypot(c.pos[0] - 500.0, c.pos[1] - 350.0) == pytest.approx(2.0)


def test_tick_cobra_energia(monkeypatch):
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0), size=8.0, velocity=2.0, energy=50.0)
    w.creatures.append(c)
    w.advance_tick()
    custo = config.CREATURE_K_BASE + config.CREATURE_K1 * 8.0 + config.CREATURE_K2 * 4.0
    assert c.energy == pytest.approx(50.0 - custo)


def test_tick_remove_as_mortas(monkeypatch):
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    w = mundo_vazio()
    quase_morta = criatura_em((100.0, 100.0), energy=0.01)
    viva = criatura_em((800.0, 500.0), energy=50.0)
    w.creatures.extend([quase_morta, viva])
    w.advance_tick()
    assert w.creatures == [viva]


def test_tick_remove_varias_mortas_seguidas(monkeypatch):
    """Apanha o erro de remover enquanto se percorre a lista (saltar elementos)."""
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    w = mundo_vazio()
    mortas = [criatura_em((50.0 * i + 25, 100.0), energy=0.01) for i in range(10)]
    vivas = [criatura_em((50.0 * i + 25, 500.0), energy=50.0) for i in range(5)]
    w.creatures.extend(mortas[:5] + vivas + mortas[5:])
    w.advance_tick()
    assert w.creatures == vivas


def test_comer_no_ultimo_tick_salva(monkeypatch):
    """Pagar primeiro e só depois ver se morreu: comer no mesmo tick salva a criatura."""
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    monkeypatch.setattr(config, "CREATURE_MAX_TURN", 0.0)
    w = mundo_vazio()
    c = criatura_em((500.0, 350.0), velocity=2.0, energy=0.01)
    c.angle = 0.0
    w.creatures.append(c)
    w.foods.append(Food((502.0, 350.0)))
    w.advance_tick()
    assert w.creatures == [c]
    assert c.energy > 0


def test_sem_comida_morrem_todas(monkeypatch):
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    random.seed(20)
    w = World(TAMANHO)
    w.foods.clear()
    pior_caso = config.CREATURE_BASE_ENERGY / config.CREATURE_K_BASE
    for _ in range(int(pior_caso) + 10):
        w.advance_tick()
        if not w.creatures:
            break
    assert w.creatures == []


def test_criaturas_ficam_dentro_do_mundo():
    random.seed(21)
    w = World(TAMANHO)
    for _ in range(3000):
        w.advance_tick()
        for c in w.creatures:
            assert 0 <= c.pos[0] < LARGURA and 0 <= c.pos[1] < ALTURA


def test_comida_comida_desaparece_do_mundo(monkeypatch):
    """A comida total só diminui pelo que foi comido (sem comida nova)."""
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)
    random.seed(22)
    w = World(TAMANHO)
    comida_antes = len(w.foods)
    energia_antes = sum(c.energy for c in w.creatures)
    gasto = 0.0
    for c in w.creatures:
        gasto += config.CREATURE_K_BASE + config.CREATURE_K1 * c.size + config.CREATURE_K2 * c.velocity ** 2
    w.advance_tick()
    comidas_comidas = comida_antes - len(w.foods)
    energia_depois = sum(c.energy for c in w.creatures)
    if len(w.creatures) == config.INICIAL_AMOUNT_CREATURES:
        assert energia_depois == pytest.approx(energia_antes - gasto + comidas_comidas * config.FOOD_ENERGY)
