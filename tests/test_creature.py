"""Testes da criatura: virar, andar, energia (fases 3 e 5), comer, morrer e reproduzir (fase 4).

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import math
import random

import numpy as np
import pytest

import config
from creature import Creature
from conftest import faz_genoma, faz_criatura, custo, cerebro_zero

MUNDO = (1000, 700)
LIMIAR = config.REPRODUCAO_LIMIAR
PCT = config.REPRODUCAO_PERCENTAGEM
CUSTO_REP = config.REPRODUCAO_CUSTO
MAX_TURN = config.CREATURE_MAX_TURN


def aprox(v, tol=1e-9):
    return pytest.approx(v, abs=tol)


def diferenca_angular(a, b):
    return (b - a + math.pi) % (2 * math.pi) - math.pi


def a_andar(pos=(500.0, 350.0), velocidade=2.0, angulo=0.0, **kw):
    """Uma criatura já com velocidade real definida, pronta para andar."""
    c = faz_criatura(pos, velocity=max(velocidade, config.CREATURE_MIN_VELOCITY), **kw)
    c.velocidade_real = velocidade
    c.angle = angulo
    return c


# ================================================================ construtor

def test_construtor_guarda_valores():
    g = faz_genoma(7.5, 1.8)
    c = Creature((10.0, 20.0), g, 33.0)
    assert c.pos == (10.0, 20.0)
    assert c.genoma is g
    assert c.energy == 33.0


def test_energia_por_omissao_e_a_base():
    assert Creature((0.0, 0.0), faz_genoma()).energy == config.CREATURE_BASE_ENERGY


def test_nasce_parada():
    assert faz_criatura().velocidade_real == 0


def test_angulo_inicial_dentro_de_uma_volta():
    for _ in range(500):
        assert 0 <= faz_criatura().angle < 2 * math.pi


def test_angulos_iniciais_variam():
    assert len({round(faz_criatura().angle, 6) for _ in range(50)}) > 40


def test_criaturas_com_o_mesmo_genoma_nao_se_afetam():
    g = faz_genoma()
    a, b = Creature((0.0, 0.0), g), Creature((10.0, 10.0), g)
    a.gastar_energia()
    assert b.energy == config.CREATURE_BASE_ENERGY


# ================================================================ virar (fase 5: pelo cérebro)

@pytest.mark.parametrize("saida", [-1.0, -0.5, 0.0, 0.3, 1.0])
def test_virar_proporcional_a_saida(saida):
    c = faz_criatura()
    c.angle = 2.0
    c.virar(saida)
    assert diferenca_angular(2.0, c.angle) == aprox(saida * MAX_TURN)


def test_virar_zero_nao_muda_o_angulo():
    c = faz_criatura()
    c.angle = 1.234
    c.virar(0.0)
    assert c.angle == aprox(1.234)


def test_virar_positivo_e_no_sentido_dos_ponteiros():
    """No pygame (y para baixo), somar ao ângulo vira para a direita do ecrã a partir de 'para a direita'."""
    c = a_andar(angulo=0.0, velocidade=10.0)
    for _ in range(5):
        c.virar(1.0)
    c.andar(MUNDO)
    assert c.pos[1] > 350.0


def test_virar_mantem_o_angulo_numa_volta():
    c = faz_criatura()
    for i in range(5000):
        c.virar(1.0 if i % 7 else -1.0)
        assert 0 <= c.angle < 2 * math.pi


def test_virar_atravessa_o_zero():
    c = faz_criatura()
    c.angle = 0.05
    c.virar(-1.0)
    assert c.angle == aprox(2 * math.pi + 0.05 - MAX_TURN)


def test_virar_sempre_para_o_mesmo_lado_da_a_volta():
    c = faz_criatura()
    c.angle = 0.0
    passos = round(2 * math.pi / MAX_TURN)
    for _ in range(passos):
        c.virar(1.0)
    assert abs(diferenca_angular(0.0, c.angle)) < MAX_TURN


# ================================================================ velocidade real (fase 5)

@pytest.mark.parametrize("saida, fracao", [(-1.0, 0.0), (0.0, 0.5), (1.0, 1.0), (0.5, 0.75), (-0.5, 0.25)])
def test_velocidade_real_entre_zero_e_o_maximo(saida, fracao):
    c = faz_criatura(velocity=4.0)
    c.calcula_velocidade_real(saida)
    assert c.velocidade_real == aprox(fracao * 4.0)


def test_velocidade_real_nunca_passa_do_gene():
    c = faz_criatura(velocity=3.0)
    for s in np.linspace(-1, 1, 101):
        c.calcula_velocidade_real(s)
        assert 0 <= c.velocidade_real <= 3.0 + 1e-12


def test_velocidade_real_nao_muda_o_gene():
    c = faz_criatura(velocity=3.0)
    c.calcula_velocidade_real(-1.0)
    assert c.genoma.velocity == 3.0


# ================================================================ agir (fase 5)

def test_agir_usa_a_saida_0_para_virar_e_a_1_para_acelerar():
    c = faz_criatura(velocity=4.0)
    c.angle = 1.0
    c.agir(np.array([0.5, 1.0]))
    assert diferenca_angular(1.0, c.angle) == aprox(0.5 * MAX_TURN)
    assert c.velocidade_real == aprox(4.0)


def test_agir_com_saidas_zero():
    c = faz_criatura(velocity=4.0)
    c.angle = 1.0
    c.agir(np.array([0.0, 0.0]))
    assert c.angle == aprox(1.0)
    assert c.velocidade_real == aprox(2.0)


def test_agir_nao_mexe_a_criatura():
    """Agir só decide; quem mexe é o andar."""
    c = faz_criatura()
    c.agir(np.array([1.0, 1.0]))
    assert c.pos == (500.0, 350.0)


def test_agir_nao_gasta_energia():
    c = faz_criatura()
    antes = c.energy
    c.agir(np.array([1.0, 1.0]))
    assert c.energy == antes


def test_agir_aceita_tuplos():
    c = faz_criatura(velocity=4.0)
    c.agir((0.0, 1.0))
    assert c.velocidade_real == aprox(4.0)


# ================================================================ andar

@pytest.mark.parametrize("angulo, esperado", [
    (0.0, (502.0, 350.0)),
    (math.pi / 2, (500.0, 352.0)),
    (math.pi, (498.0, 350.0)),
    (3 * math.pi / 2, (500.0, 348.0)),
])
def test_andar_na_direcao_do_angulo(angulo, esperado):
    c = a_andar(velocidade=2.0, angulo=angulo)
    c.andar(MUNDO)
    assert c.pos == aprox(esperado)


def test_andar_usa_a_velocidade_real_e_nao_o_gene():
    c = faz_criatura(velocity=5.0)
    c.angle = 0.0
    c.velocidade_real = 1.5
    c.andar(MUNDO)
    assert c.pos == aprox((501.5, 350.0))


def test_parada_nao_anda():
    c = faz_criatura()
    c.andar(MUNDO)
    assert c.pos == (500.0, 350.0)


def test_andar_percorre_a_velocidade_real():
    rng = random.Random(6)
    for _ in range(200):
        v = rng.uniform(0.0, 10.0)
        c = a_andar(velocidade=v, angulo=rng.uniform(0, 2 * math.pi))
        c.andar(MUNDO)
        assert math.hypot(c.pos[0] - 500.0, c.pos[1] - 350.0) == aprox(v)


def test_andar_atravessa_a_borda_direita():
    c = a_andar((999.0, 100.0), velocidade=3.0, angulo=0.0)
    c.andar(MUNDO)
    assert c.pos == aprox((2.0, 100.0))


def test_andar_atravessa_a_borda_de_cima():
    c = a_andar((100.0, 1.0), velocidade=3.0, angulo=3 * math.pi / 2)
    c.andar(MUNDO)
    assert c.pos == aprox((100.0, 698.0))


def test_andar_fica_sempre_dentro_do_mundo():
    rng = random.Random(7)
    c = a_andar((5.0, 5.0), velocidade=3.0)
    for _ in range(20_000):
        c.virar(rng.uniform(-1, 1))
        c.andar(MUNDO)
        assert 0 <= c.pos[0] < MUNDO[0] and 0 <= c.pos[1] < MUNDO[1]


def test_andar_respeita_o_tamanho_do_mundo_recebido():
    c = a_andar((95.0, 10.0), velocidade=10.0, angulo=0.0)
    c.andar((100, 50))
    assert c.pos == aprox((5.0, 10.0))


def test_andar_nao_gasta_energia():
    c = a_andar()
    antes = c.energy
    c.andar(MUNDO)
    assert c.energy == antes


# ================================================================ energia (fase 5: velocidade real + manutenção)

@pytest.mark.parametrize("size, vmax, vreal", [
    (8.0, 2.0, 2.0), (8.0, 2.0, 0.0), (6.4, 3.6, 1.8), (25.0, 10.0, 10.0), (3.0, 0.3, 0.0),
])
def test_gastar_energia_segue_a_formula(size, vmax, vreal):
    c = faz_criatura(size=size, velocity=vmax, energy=100.0)
    c.velocidade_real = vreal
    c.gastar_energia()
    assert 100.0 - c.energy == aprox(custo(size, vmax, vreal))


def test_abrandar_poupa_energia():
    rapida, lenta = faz_criatura(velocity=4.0, energy=100.0), faz_criatura(velocity=4.0, energy=100.0)
    rapida.velocidade_real, lenta.velocidade_real = 4.0, 1.0
    rapida.gastar_energia()
    lenta.gastar_energia()
    assert lenta.energy > rapida.energy


def test_velocidade_real_conta_ao_quadrado():
    a, b = faz_criatura(velocity=4.0, energy=100.0), faz_criatura(velocity=4.0, energy=100.0)
    a.velocidade_real, b.velocidade_real = 1.5, 3.0
    a.gastar_energia()
    b.gastar_energia()
    fixo = custo(8.0, 4.0, 0.0)
    assert (100.0 - b.energy - fixo) == aprox(4 * (100.0 - a.energy - fixo))


def test_ter_velocidade_maxima_alta_custa_mesmo_parada():
    """A manutenção: músculos custam energia mesmo sem os usar."""
    pequena, grande = faz_criatura(velocity=1.0, energy=100.0), faz_criatura(velocity=8.0, energy=100.0)
    pequena.gastar_energia()
    grande.gastar_energia()
    assert grande.energy < pequena.energy


def test_manutencao_mais_barata_que_andar():
    assert config.CREATURE_K3 < config.CREATURE_K2


def test_maior_gasta_mais():
    pequena, grande = faz_criatura(size=6.0), faz_criatura(size=10.0)
    pequena.gastar_energia()
    grande.gastar_energia()
    assert grande.energy < pequena.energy


def test_custo_sempre_positivo():
    c = faz_criatura(size=config.CREATURE_MIN_RADIUS, velocity=config.CREATURE_MIN_VELOCITY)
    antes = c.energy
    c.gastar_energia()
    assert c.energy < antes


def test_custo_da_criatura_media_e_razoavel():
    v = config.CREATURE_BASE_VELOCITY
    ticks = config.CREATURE_BASE_ENERGY / custo(config.CREATURE_BASE_RADIUS, v, v)
    assert 100 <= ticks <= 5000


# ================================================================ energia normalizada (fase 5)

@pytest.mark.parametrize("energia, esperado", [
    (0.0, -1.0),
    (LIMIAR / 2, 0.0),
    (LIMIAR, 1.0),
    (LIMIAR / 4, -0.5),
])
def test_energia_normalizada(energia, esperado):
    assert faz_criatura(energy=energia).energia_normalizada() == aprox(esperado)


@pytest.mark.parametrize("energia", [LIMIAR + 1, LIMIAR * 2, 1e6])
def test_energia_normalizada_presa_a_1(energia):
    assert faz_criatura(energy=energia).energia_normalizada() == 1


def test_energia_normalizada_sempre_entre_menos_1_e_1_enquanto_viva():
    for e in np.linspace(0.001, LIMIAR * 3, 300):
        assert -1 <= faz_criatura(energy=float(e)).energia_normalizada() <= 1


def test_energia_normalizada_nao_muda_a_energia():
    c = faz_criatura(energy=70.0)
    c.energia_normalizada()
    assert c.energy == 70.0


# ================================================================ comer e morrer

def test_comer_da_a_energia_da_comida():
    c = faz_criatura(energy=50.0)
    c.comer()
    assert c.energy == aprox(50.0 + config.FOOD_ENERGY)


def test_regenerar_soma_a_quantidade():
    c = faz_criatura(energy=10.0)
    c.regenerar_energia(12.5)
    assert c.energy == aprox(22.5)


def test_comer_pode_passar_a_energia_base():
    c = faz_criatura(energy=config.CREATURE_BASE_ENERGY)
    c.comer()
    assert c.energy > config.CREATURE_BASE_ENERGY


@pytest.mark.parametrize("energia, viva", [(100.0, True), (0.001, True), (0.0, False), (-3.0, False)])
def test_esta_viva(energia, viva):
    assert faz_criatura(energy=energia).esta_viva() is viva


def test_morre_de_fome_no_tick_certo():
    c = faz_criatura(size=8.0, velocity=2.0, energy=10.0)
    c.velocidade_real = 2.0
    esperado = math.ceil(10.0 / custo(8.0, 2.0, 2.0))
    ticks = 0
    while c.esta_viva():
        c.gastar_energia()
        ticks += 1
        assert ticks < 100_000
    assert ticks in (esperado, esperado + 1)


# ================================================================ reprodução

@pytest.mark.parametrize("energia, pode", [
    (LIMIAR + 50, True), (LIMIAR + 0.001, True), (LIMIAR - 0.001, False),
    (config.CREATURE_BASE_ENERGY, False), (0.0, False),
])
def test_pode_reproduzir(energia, pode):
    assert faz_criatura(energy=energia).pode_reproduzir() is pode


def test_pode_reproduzir_nao_muda_nada():
    c = faz_criatura(energy=LIMIAR + 10)
    c.pode_reproduzir()
    assert c.energy == LIMIAR + 10


def test_criatura_acabada_de_nascer_nao_se_reproduz_logo():
    assert not Creature((0.0, 0.0), faz_genoma()).pode_reproduzir()


def test_gera_filho_devolve_uma_criatura():
    assert isinstance(faz_criatura(energy=LIMIAR + 10).gera_filho(), Creature)


def test_filho_nasce_onde_esta_o_pai():
    assert faz_criatura((123.0, 456.0), energy=LIMIAR + 10).gera_filho().pos == (123.0, 456.0)


def test_filho_nasce_parado():
    pai = faz_criatura(energy=LIMIAR + 10)
    pai.velocidade_real = 2.0
    assert pai.gera_filho().velocidade_real == 0


def test_filho_tem_a_percentagem_da_energia():
    assert faz_criatura(energy=200.0).gera_filho().energy == aprox(200.0 * PCT)


def test_pai_fica_com_o_resto_menos_o_custo():
    pai = faz_criatura(energy=200.0)
    pai.gera_filho()
    assert pai.energy == aprox(200.0 * (1 - PCT) - CUSTO_REP)


def test_energia_conservada_menos_o_custo():
    for antes in (LIMIAR + 0.5, 180.0, 300.0, 1000.0):
        pai = faz_criatura(energy=antes)
        filho = pai.gera_filho()
        assert pai.energy + filho.energy == aprox(antes - CUSTO_REP)


@pytest.mark.parametrize("pct", [0.3, 0.5, 0.7])
def test_divisao_funciona_com_outras_percentagens(monkeypatch, pct):
    monkeypatch.setattr(config, "REPRODUCAO_PERCENTAGEM", pct)
    pai = faz_criatura(energy=200.0)
    filho = pai.gera_filho()
    assert filho.energy == aprox(200.0 * pct)
    assert pai.energy + filho.energy == aprox(200.0 - CUSTO_REP)


def test_pai_sobrevive_a_reproducao_no_limiar():
    pai = faz_criatura(energy=LIMIAR + 0.001)
    filho = pai.gera_filho()
    assert pai.esta_viva() and filho.esta_viva()


def test_depois_de_reproduzir_ja_nao_pode_logo_outra_vez():
    pai = faz_criatura(energy=LIMIAR + 1)
    filho = pai.gera_filho()
    assert not pai.pode_reproduzir() and not filho.pode_reproduzir()


def test_filho_tem_genoma_novo():
    pai = faz_criatura(energy=LIMIAR + 10)
    assert pai.gera_filho().genoma is not pai.genoma


def test_genoma_do_pai_fica_igual():
    pai = faz_criatura(size=8.0, velocity=2.0, cor=(10, 20, 30), geracao=3, energy=LIMIAR + 10)
    pai.gera_filho()
    g = pai.genoma
    assert (g.size, g.velocity, g.cor, g.geracao) == (8.0, 2.0, (10, 20, 30), 3)


def test_filho_e_da_geracao_seguinte():
    assert faz_criatura(geracao=7, energy=LIMIAR + 10).gera_filho().genoma.geracao == 8


def test_filho_herda_a_fundadora():
    assert faz_criatura(fundador=23, energy=LIMIAR + 10).gera_filho().genoma.id_fundador == 23


def test_filho_tem_cerebro_proprio():
    pai = faz_criatura(energy=LIMIAR + 10)
    assert pai.gera_filho().genoma.brain is not pai.genoma.brain


def test_filho_e_independente_do_pai():
    pai = faz_criatura(energy=LIMIAR + 10)
    filho = pai.gera_filho()
    filho.angle = 0.0
    filho.velocidade_real = 2.0
    filho.andar(MUNDO)
    filho.gastar_energia()
    assert pai.pos == (500.0, 350.0)
    assert pai.energy == aprox((LIMIAR + 10) * (1 - PCT) - CUSTO_REP)


def test_sem_mutacao_filho_igual_ao_pai(sem_mutacao):
    pai = faz_criatura(size=9.0, velocity=2.5, cor=(1, 2, 3), energy=LIMIAR + 10)
    g = pai.gera_filho().genoma
    assert (g.size, g.velocity, g.cor) == (pytest.approx(9.0), pytest.approx(2.5), (1, 2, 3))
    assert np.array_equal(g.brain.w1, pai.genoma.brain.w1)
