"""Testes do mundo: ticks, comida (fase 2), criaturas (fase 3) e reprodução (fase 4).

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import math
import random

import pytest

import config
from creature import Creature
from food import Food
from genome import Genoma
from world import World
from conftest import faz_criatura, custo

TAMANHO = (1000, 700)
LARGURA, ALTURA = TAMANHO
LIMIAR = config.REPRODUCAO_LIMIAR


def mundo_vazio():
    """Um mundo sem comida nem criaturas, para montar cada cenário à mão."""
    w = World(TAMANHO)
    w.foods.clear()
    w.creatures.clear()
    return w


def mundo_so_comida():
    w = World(TAMANHO)
    w.creatures.clear()
    return w


# ================================================================ configuração

def test_config_comida_inicial_nao_passa_do_maximo():
    assert config.INICIAL_AMOUNT_FOOD <= config.MAX_FOOD


def test_config_limiar_acima_da_energia_inicial():
    """Senão a primeira geração reproduz-se logo no primeiro tick."""
    assert config.REPRODUCAO_LIMIAR > config.CREATURE_BASE_ENERGY


def test_config_percentagem_entre_0_e_1():
    assert 0 < config.REPRODUCAO_PERCENTAGEM < 1


def test_config_pai_sobrevive_a_reproduzir():
    """No limiar, depois de dar a parte do filho e pagar o custo, o pai tem de ficar vivo."""
    resto = config.REPRODUCAO_LIMIAR * (1 - config.REPRODUCAO_PERCENTAGEM) - config.REPRODUCAO_CUSTO
    assert resto > 0


def test_config_variacao_inicial_dentro_dos_limites():
    v = config.CREATURE_VARIATION
    assert config.CREATURE_BASE_RADIUS * (1 - v) >= config.CREATURE_MIN_RADIUS
    assert config.CREATURE_BASE_RADIUS * (1 + v) <= config.CREATURE_MAX_RADIUS
    assert config.CREATURE_BASE_VELOCITY * (1 - v) >= config.CREATURE_MIN_VELOCITY
    assert config.CREATURE_BASE_VELOCITY * (1 + v) <= config.CREATURE_MAX_VELOCITY


def test_config_cores_base_validas():
    assert len(config.RANGE_COR_BASE) == 3
    for canal in config.RANGE_COR_BASE:
        assert 0 <= canal <= 255


# ================================================================ ticks

def test_mundo_comeca_no_tick_zero():
    assert World(TAMANHO).n_ticks == 0


def test_ticks_avancam_um_a_um():
    w = World(TAMANHO)
    for _ in range(250):
        w.advance_tick()
    assert w.n_ticks == 250


def test_mundos_nao_partilham_listas():
    w1, w2 = World(TAMANHO), World(TAMANHO)
    assert w1.foods is not w2.foods
    assert w1.creatures is not w2.creatures
    antes = len(w2.foods)
    w1.gerar_comida(5)
    assert len(w2.foods) == antes


def test_mundo_vazio_avanca_sem_erros():
    w = mundo_vazio()
    for _ in range(100):
        w.advance_tick()
    assert w.creatures == []


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


def test_comida_volta_ao_maximo():
    random.seed(2)
    w = mundo_so_comida()
    del w.foods[: len(w.foods) // 2]
    for _ in range(int(50 * config.MAX_FOOD / config.TAXA_FOOD_PER_TICK) + 1000):
        w.advance_tick()
    assert len(w.foods) == config.MAX_FOOD


def test_comida_nasce_dentro_do_mundo():
    random.seed(3)
    w = mundo_vazio()
    w.gerar_comida(2000)
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


# ================================================================ primeira geração

def test_criaturas_iniciais():
    assert len(World(TAMANHO).creatures) == config.INICIAL_AMOUNT_CREATURES


def test_criaturas_sao_objetos_diferentes():
    w = World(TAMANHO)
    assert len({id(c) for c in w.creatures}) == len(w.creatures)


def test_cada_criatura_tem_o_seu_genoma():
    w = World(TAMANHO)
    assert len({id(c.genoma) for c in w.creatures}) == len(w.creatures)
    for c in w.creatures:
        assert isinstance(c.genoma, Genoma)


def test_primeira_geracao_e_a_1():
    for c in World(TAMANHO).creatures:
        assert c.genoma.geracao == 1


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


def test_tamanho_inicial_dentro_da_variacao():
    random.seed(12)
    w = mundo_vazio()
    w.gerar_criatura(500)
    lo = config.CREATURE_BASE_RADIUS * (1 - config.CREATURE_VARIATION)
    hi = config.CREATURE_BASE_RADIUS * (1 + config.CREATURE_VARIATION)
    for c in w.creatures:
        assert lo <= c.genoma.size <= hi


def test_velocidade_inicial_dentro_da_variacao():
    random.seed(13)
    w = mundo_vazio()
    w.gerar_criatura(500)
    lo = config.CREATURE_BASE_VELOCITY * (1 - config.CREATURE_VARIATION)
    hi = config.CREATURE_BASE_VELOCITY * (1 + config.CREATURE_VARIATION)
    for c in w.creatures:
        assert lo <= c.genoma.velocity <= hi


def test_cor_inicial_valida():
    random.seed(14)
    w = mundo_vazio()
    w.gerar_criatura(500)
    for c in w.creatures:
        assert isinstance(c.genoma.cor, tuple) and len(c.genoma.cor) == 3
        for canal, maximo in zip(c.genoma.cor, config.RANGE_COR_BASE):
            assert isinstance(canal, int)
            assert 0 <= canal <= maximo


def test_criaturas_nascem_diferentes():
    random.seed(15)
    w = mundo_vazio()
    w.gerar_criatura(100)
    assert len({round(c.genoma.size, 6) for c in w.creatures}) > 90
    assert len({round(c.genoma.velocity, 6) for c in w.creatures}) > 90
    assert len({c.genoma.cor for c in w.creatures}) > 90


def test_criaturas_nascem_com_energia_base():
    for c in World(TAMANHO).creatures:
        assert c.energy == config.CREATURE_BASE_ENERGY


# ================================================================ comer

def test_come_comida_em_cima():
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0))
    w.creatures.append(c)
    w.foods.append(Food((500.0, 350.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []
    assert c.energy == pytest.approx(50.0 + config.FOOD_ENERGY)


def test_come_quando_os_circulos_se_tocam():
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0), size=8.0)
    w.foods.append(Food((500.0 + 8.0 + config.FOOD_RADIUS - 0.5, 350.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []


def test_nao_come_comida_longe():
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0), size=8.0)
    f = Food((500.0 + 8.0 + config.FOOD_RADIUS + 0.5, 350.0))
    w.foods.append(f)
    w.verificar_alimentacao(c)
    assert w.foods == [f]
    assert c.energy == 50.0


def test_nao_come_comida_longe_na_diagonal():
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0), size=8.0)
    d = (8.0 + config.FOOD_RADIUS + 0.5) / math.sqrt(2)
    f = Food((500.0 + d, 350.0 + d))
    w.foods.append(f)
    w.verificar_alimentacao(c)
    assert w.foods == [f]


def test_alcance_usa_o_tamanho_do_genoma():
    w = mundo_vazio()
    pequena = faz_criatura((200.0, 350.0), size=6.0)
    grande = faz_criatura((600.0, 350.0), size=10.0)
    d = 8.0 + config.FOOD_RADIUS
    fp, fg = Food((200.0 + d, 350.0)), Food((600.0 + d, 350.0))
    w.foods.extend([fp, fg])
    w.verificar_alimentacao(pequena)
    w.verificar_alimentacao(grande)
    assert fp in w.foods
    assert fg not in w.foods


def test_come_atraves_da_borda():
    w = mundo_vazio()
    c = faz_criatura((2.0, 350.0))
    w.foods.append(Food((998.0, 350.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []


def test_come_atraves_do_canto():
    w = mundo_vazio()
    c = faz_criatura((1.0, 1.0))
    w.foods.append(Food((998.0, 698.0)))
    w.verificar_alimentacao(c)
    assert w.foods == []


def test_so_come_uma_comida_por_tick():
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0))
    w.foods.extend([Food((500.0, 350.0)) for _ in range(3)])
    w.verificar_alimentacao(c)
    assert len(w.foods) == 2
    assert c.energy == pytest.approx(50.0 + config.FOOD_ENERGY)


def test_comer_nao_mexe_na_outra_comida():
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0))
    longe1, perto, longe2 = Food((100.0, 100.0)), Food((500.0, 350.0)), Food((900.0, 600.0))
    w.foods.extend([longe1, perto, longe2])
    w.verificar_alimentacao(c)
    assert w.foods == [longe1, longe2]


def test_duas_criaturas_nao_comem_a_mesma_comida():
    w = mundo_vazio()
    a, b = faz_criatura((500.0, 350.0)), faz_criatura((501.0, 350.0))
    w.foods.append(Food((500.5, 350.0)))
    w.verificar_alimentacao(a)
    w.verificar_alimentacao(b)
    assert a.energy + b.energy == pytest.approx(100.0 + config.FOOD_ENERGY)


# ================================================================ o tick (fase 3)

def test_tick_mexe_as_criaturas(sem_comida_nova):
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0), velocity=2.0)
    w.creatures.append(c)
    w.advance_tick()
    assert math.hypot(c.pos[0] - 500.0, c.pos[1] - 350.0) == pytest.approx(2.0)


def test_tick_cobra_energia(sem_comida_nova):
    w = mundo_vazio()
    c = faz_criatura(size=8.0, velocity=2.0, energy=50.0)
    w.creatures.append(c)
    w.advance_tick()
    assert c.energy == pytest.approx(50.0 - custo(8.0, 2.0))


def test_tick_remove_as_mortas(sem_comida_nova):
    w = mundo_vazio()
    quase_morta = faz_criatura((100.0, 100.0), energy=0.01)
    viva = faz_criatura((800.0, 500.0), energy=50.0)
    w.creatures.extend([quase_morta, viva])
    w.advance_tick()
    assert w.creatures == [viva]


def test_tick_remove_varias_mortas_seguidas(sem_comida_nova):
    w = mundo_vazio()
    mortas = [faz_criatura((50.0 * i + 25, 100.0), energy=0.01) for i in range(10)]
    vivas = [faz_criatura((50.0 * i + 25, 500.0), energy=50.0) for i in range(5)]
    w.creatures.extend(mortas[:5] + vivas + mortas[5:])
    w.advance_tick()
    assert w.creatures == vivas


def test_comer_no_ultimo_tick_salva(sem_comida_nova, sem_viragem):
    w = mundo_vazio()
    c = faz_criatura((500.0, 350.0), velocity=2.0, energy=0.01)
    c.angle = 0.0
    w.creatures.append(c)
    w.foods.append(Food((502.0, 350.0)))
    w.advance_tick()
    assert w.creatures == [c]


def test_sem_comida_morrem_todas(sem_comida_nova):
    random.seed(20)
    w = World(TAMANHO)
    w.foods.clear()
    for _ in range(int(config.CREATURE_BASE_ENERGY / config.CREATURE_K_BASE) + 10):
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


# ================================================================ reprodução no tick (fase 4)

def test_criatura_acima_do_limiar_tem_filho(sem_comida_nova):
    random.seed(30)
    w = mundo_vazio()
    pai = faz_criatura(energy=LIMIAR + 50)
    w.creatures.append(pai)
    w.advance_tick()
    assert len(w.creatures) == 2
    assert w.creatures[0] is pai


def test_criatura_abaixo_do_limiar_nao_tem_filho(sem_comida_nova):
    w = mundo_vazio()
    w.creatures.append(faz_criatura(energy=LIMIAR - 5))
    w.advance_tick()
    assert len(w.creatures) == 1


def test_filho_entra_no_fim_da_lista(sem_comida_nova):
    random.seed(31)
    w = mundo_vazio()
    a = faz_criatura((100.0, 100.0), energy=LIMIAR + 50)
    b = faz_criatura((800.0, 500.0), energy=50.0)
    w.creatures.extend([a, b])
    w.advance_tick()
    assert w.creatures[:2] == [a, b]
    assert len(w.creatures) == 3


def test_filho_nao_e_processado_no_tick_em_que_nasce(sem_comida_nova):
    """O filho não anda nem paga energia no tick em que nasceu."""
    random.seed(32)
    w = mundo_vazio()
    pai = faz_criatura((500.0, 350.0), energy=LIMIAR + 50)
    w.creatures.append(pai)
    w.advance_tick()
    filho = w.creatures[1]
    energia_pai_antes = LIMIAR + 50 - custo(8.0, 2.0)
    assert filho.energy == pytest.approx(energia_pai_antes * config.REPRODUCAO_PERCENTAGEM)
    assert filho.pos == pai.pos


def test_so_um_filho_por_tick_mesmo_com_muita_energia(sem_comida_nova):
    random.seed(33)
    w = mundo_vazio()
    w.creatures.append(faz_criatura(energy=LIMIAR * 20))
    w.advance_tick()
    assert len(w.creatures) == 2


def test_filho_no_tick_seguinte_ja_e_processado(sem_comida_nova):
    random.seed(34)
    w = mundo_vazio()
    w.creatures.append(faz_criatura(energy=LIMIAR + 50))
    w.advance_tick()
    filho = w.creatures[1]
    energia, pos = filho.energy, filho.pos
    w.advance_tick()
    assert filho.energy < energia
    assert filho.pos != pos


def test_comer_ate_ao_limiar_reproduz_no_mesmo_tick(sem_comida_nova, sem_viragem):
    random.seed(35)
    w = mundo_vazio()
    energia = LIMIAR - config.FOOD_ENERGY + 5
    c = faz_criatura((500.0, 350.0), velocity=2.0, energy=energia)
    c.angle = 0.0
    w.creatures.append(c)
    w.foods.append(Food((502.0, 350.0)))
    w.advance_tick()
    assert len(w.creatures) == 2


def test_energia_total_conservada_na_reproducao(sem_comida_nova):
    random.seed(36)
    w = mundo_vazio()
    antes = LIMIAR + 40
    pai = faz_criatura(size=8.0, velocity=2.0, energy=antes)
    w.creatures.append(pai)
    w.advance_tick()
    total = sum(c.energy for c in w.creatures)
    assert total == pytest.approx(antes - custo(8.0, 2.0) - config.REPRODUCAO_CUSTO)


def test_filho_tem_geracao_seguinte(sem_comida_nova):
    random.seed(37)
    w = mundo_vazio()
    w.creatures.append(faz_criatura(energy=LIMIAR + 50, geracao=4))
    w.advance_tick()
    assert w.creatures[1].genoma.geracao == 5


def test_varias_criaturas_reproduzem_no_mesmo_tick(sem_comida_nova):
    random.seed(38)
    w = mundo_vazio()
    pais = [faz_criatura((100.0 * i + 50, 300.0), energy=LIMIAR + 30) for i in range(6)]
    normais = [faz_criatura((100.0 * i + 50, 600.0), energy=60.0) for i in range(4)]
    w.creatures.extend(pais + normais)
    w.advance_tick()
    assert len(w.creatures) == 16
    assert w.creatures[:10] == pais + normais


def test_sem_comida_nem_reproducao_a_linhagem_acaba(sem_comida_nova):
    """Mesmo uma criatura rica acaba por morrer, com os descendentes, se não houver comida."""
    random.seed(39)
    w = mundo_vazio()
    w.creatures.append(faz_criatura(energy=LIMIAR * 3))
    for _ in range(20_000):
        w.advance_tick()
        if not w.creatures:
            break
    assert w.creatures == []
