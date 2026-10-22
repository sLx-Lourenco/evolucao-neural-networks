"""Testes da criatura: movimento, energia, comer, morrer (fase 3) e reproduzir (fase 4).

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import math
import random

import pytest

import config
from creature import Creature
from genome import Genoma
from conftest import faz_genoma, faz_criatura, custo

MUNDO = (1000, 700)
LIMIAR = config.REPRODUCAO_LIMIAR
PCT = config.REPRODUCAO_PERCENTAGEM
CUSTO_REP = config.REPRODUCAO_CUSTO


def aprox(v, tol=1e-9):
    return pytest.approx(v, abs=tol)


def diferenca_angular(a, b):
    return (b - a + math.pi) % (2 * math.pi) - math.pi


# ================================================================ construtor

def test_construtor_guarda_valores():
    g = faz_genoma(7.5, 1.8)
    c = Creature((10.0, 20.0), g, 33.0)
    assert c.pos == (10.0, 20.0)
    assert c.genoma is g
    assert c.energy == 33.0


def test_energia_por_omissao_e_a_base():
    assert Creature((0.0, 0.0), faz_genoma()).energy == config.CREATURE_BASE_ENERGY


def test_angulo_inicial_dentro_de_uma_volta():
    random.seed(0)
    for _ in range(500):
        assert 0 <= faz_criatura().angle < 2 * math.pi


def test_angulos_iniciais_variam():
    random.seed(1)
    assert len({round(faz_criatura().angle, 6) for _ in range(50)}) > 40


def test_criaturas_com_o_mesmo_genoma_nao_se_afetam():
    """Duas criaturas podem partilhar o objeto genoma sem problemas, porque ninguém o altera."""
    g = faz_genoma()
    a, b = Creature((0.0, 0.0), g), Creature((10.0, 10.0), g)
    a.gastar_energia()
    assert b.energy == config.CREATURE_BASE_ENERGY


# ================================================================ virar

def test_virar_nunca_passa_da_viragem_maxima():
    random.seed(2)
    c = faz_criatura()
    for _ in range(5000):
        antes = c.angle
        c.virar_acaso()
        assert abs(diferenca_angular(antes, c.angle)) <= config.CREATURE_MAX_TURN + 1e-12


def test_virar_mantem_angulo_dentro_de_uma_volta():
    random.seed(3)
    c = faz_criatura()
    for _ in range(20_000):
        c.virar_acaso()
        assert 0 <= c.angle < 2 * math.pi


def test_virar_e_igual_para_os_dois_lados():
    random.seed(4)
    c = faz_criatura()
    total, n = 0.0, 20_000
    for _ in range(n):
        antes = c.angle
        c.virar_acaso()
        total += diferenca_angular(antes, c.angle)
    assert abs(total / n) < config.CREATURE_MAX_TURN * 0.05


def test_virar_nao_depende_da_direcao_atual():
    random.seed(5)
    for inicio in (0.05, 3.0, 6.2):
        c = faz_criatura()
        maior = 0.0
        for _ in range(3000):
            c.angle = inicio
            c.virar_acaso()
            maior = max(maior, abs(diferenca_angular(inicio, c.angle)))
        assert maior > config.CREATURE_MAX_TURN * 0.9


def test_sem_viragem_anda_a_direito(sem_viragem):
    c = faz_criatura(velocity=2.0)
    c.angle = 0.0
    for _ in range(10):
        c.virar_acaso()
        c.andar(MUNDO)
    assert c.pos == aprox((520.0, 350.0))


# ================================================================ andar

@pytest.mark.parametrize("angulo, esperado", [
    (0.0, (502.0, 350.0)),
    (math.pi / 2, (500.0, 352.0)),
    (math.pi, (498.0, 350.0)),
    (3 * math.pi / 2, (500.0, 348.0)),
])
def test_andar_na_direcao_do_angulo(angulo, esperado):
    c = faz_criatura((500.0, 350.0), velocity=2.0)
    c.angle = angulo
    c.andar(MUNDO)
    assert c.pos == aprox(esperado)


def test_andar_usa_a_velocidade_do_genoma():
    random.seed(6)
    for _ in range(200):
        v = random.uniform(0.3, 10.0)
        c = faz_criatura((500.0, 350.0), velocity=v)
        c.angle = random.uniform(0, 2 * math.pi)
        c.andar(MUNDO)
        assert math.hypot(c.pos[0] - 500.0, c.pos[1] - 350.0) == aprox(v)


def test_andar_atravessa_a_borda_direita():
    c = faz_criatura((999.0, 100.0), velocity=3.0)
    c.angle = 0.0
    c.andar(MUNDO)
    assert c.pos == aprox((2.0, 100.0))


def test_andar_atravessa_a_borda_de_cima():
    c = faz_criatura((100.0, 1.0), velocity=3.0)
    c.angle = 3 * math.pi / 2
    c.andar(MUNDO)
    assert c.pos == aprox((100.0, 698.0))


def test_andar_fica_sempre_dentro_do_mundo():
    random.seed(7)
    c = faz_criatura((5.0, 5.0), velocity=3.0)
    for _ in range(20_000):
        c.virar_acaso()
        c.andar(MUNDO)
        assert 0 <= c.pos[0] < MUNDO[0] and 0 <= c.pos[1] < MUNDO[1]


def test_andar_respeita_o_tamanho_do_mundo_recebido():
    c = faz_criatura((95.0, 10.0), velocity=10.0)
    c.angle = 0.0
    c.andar((100, 50))
    assert c.pos == aprox((5.0, 10.0))


def test_andar_nao_gasta_energia():
    c = faz_criatura()
    antes = c.energy
    c.andar(MUNDO)
    assert c.energy == antes


# ================================================================ energia

@pytest.mark.parametrize("size, velocity", [(8.0, 2.0), (6.4, 3.6), (9.6, 1.0), (8.0, 0.3), (25.0, 10.0)])
def test_gastar_energia_segue_a_formula(size, velocity):
    c = faz_criatura(size=size, velocity=velocity, energy=100.0)
    c.gastar_energia()
    assert 100.0 - c.energy == aprox(custo(size, velocity))


def test_velocidade_conta_ao_quadrado():
    lenta, rapida = faz_criatura(velocity=1.5, energy=100.0), faz_criatura(velocity=3.0, energy=100.0)
    lenta.gastar_energia()
    rapida.gastar_energia()
    fixo = config.CREATURE_K_BASE + config.CREATURE_K1 * 8.0
    assert (100.0 - rapida.energy - fixo) == aprox(4 * (100.0 - lenta.energy - fixo))


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
    ticks = config.CREATURE_BASE_ENERGY / custo(config.CREATURE_BASE_RADIUS, config.CREATURE_BASE_VELOCITY)
    assert 100 <= ticks <= 5000


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
    """Sem teto: é assim que se chega ao limiar de reprodução."""
    c = faz_criatura(energy=config.CREATURE_BASE_ENERGY)
    c.comer()
    assert c.energy > config.CREATURE_BASE_ENERGY


@pytest.mark.parametrize("energia, viva", [(100.0, True), (0.001, True), (0.0, False), (-3.0, False)])
def test_esta_viva(energia, viva):
    assert faz_criatura(energy=energia).esta_viva() is viva


def test_morre_de_fome_no_tick_certo():
    c = faz_criatura(size=8.0, velocity=2.0, energy=10.0)
    esperado = math.ceil(10.0 / custo(8.0, 2.0))
    ticks = 0
    while c.esta_viva():
        c.gastar_energia()
        ticks += 1
        assert ticks < 100_000
    assert ticks in (esperado, esperado + 1)


# ================================================================ reprodução: pode_reproduzir

@pytest.mark.parametrize("energia, pode", [
    (LIMIAR + 50, True),
    (LIMIAR + 0.001, True),
    (LIMIAR - 0.001, False),
    (config.CREATURE_BASE_ENERGY, False),
    (0.0, False),
])
def test_pode_reproduzir(energia, pode):
    assert faz_criatura(energy=energia).pode_reproduzir() is pode


def test_pode_reproduzir_nao_muda_nada():
    c = faz_criatura(energy=LIMIAR + 10)
    c.pode_reproduzir()
    assert c.energy == LIMIAR + 10


def test_criatura_acabada_de_nascer_nao_se_reproduz_logo():
    """A primeira geração nasce abaixo do limiar."""
    assert not Creature((0.0, 0.0), faz_genoma()).pode_reproduzir()


# ================================================================ reprodução: gera_filho

def test_gera_filho_devolve_uma_criatura():
    random.seed(20)
    filho = faz_criatura(energy=LIMIAR + 10).gera_filho()
    assert isinstance(filho, Creature)


def test_filho_nasce_onde_esta_o_pai():
    random.seed(21)
    pai = faz_criatura((123.0, 456.0), energy=LIMIAR + 10)
    assert pai.gera_filho().pos == (123.0, 456.0)


def test_filho_tem_a_percentagem_da_energia():
    random.seed(22)
    pai = faz_criatura(energy=200.0)
    filho = pai.gera_filho()
    assert filho.energy == aprox(200.0 * PCT)


def test_pai_fica_com_o_resto_menos_o_custo():
    random.seed(23)
    pai = faz_criatura(energy=200.0)
    pai.gera_filho()
    assert pai.energy == aprox(200.0 * (1 - PCT) - CUSTO_REP)


def test_energia_conservada_menos_o_custo():
    """Pai + filho = energia de antes menos o custo de reprodução (nada se cria nem se perde)."""
    random.seed(24)
    for antes in (LIMIAR + 0.5, 180.0, 300.0, 1000.0):
        pai = faz_criatura(energy=antes)
        filho = pai.gera_filho()
        assert pai.energy + filho.energy == aprox(antes - CUSTO_REP)


@pytest.mark.parametrize("pct", [0.3, 0.5, 0.7])
def test_divisao_funciona_com_outras_percentagens(monkeypatch, pct):
    """Apanha o erro de o pai ficar com a mesma fração que o filho."""
    monkeypatch.setattr(config, "REPRODUCAO_PERCENTAGEM", pct)
    random.seed(25)
    pai = faz_criatura(energy=200.0)
    filho = pai.gera_filho()
    assert filho.energy == aprox(200.0 * pct)
    assert pai.energy + filho.energy == aprox(200.0 - CUSTO_REP)


def test_pai_sobrevive_a_reproducao_no_limiar():
    random.seed(26)
    pai = faz_criatura(energy=LIMIAR + 0.001)
    filho = pai.gera_filho()
    assert pai.esta_viva()
    assert filho.esta_viva()


def test_depois_de_reproduzir_ja_nao_pode_logo_outra_vez():
    random.seed(27)
    pai = faz_criatura(energy=LIMIAR + 1)
    filho = pai.gera_filho()
    assert not pai.pode_reproduzir()
    assert not filho.pode_reproduzir()


def test_filho_tem_genoma_novo():
    random.seed(28)
    pai = faz_criatura(energy=LIMIAR + 10)
    filho = pai.gera_filho()
    assert filho.genoma is not pai.genoma


def test_genoma_do_pai_fica_igual():
    random.seed(29)
    pai = faz_criatura(size=8.0, velocity=2.0, cor=(10, 20, 30), geracao=3, energy=LIMIAR + 10)
    pai.gera_filho()
    g = pai.genoma
    assert (g.size, g.velocity, g.cor, g.geracao) == (8.0, 2.0, (10, 20, 30), 3)


def test_filho_e_da_geracao_seguinte():
    random.seed(30)
    pai = faz_criatura(geracao=7, energy=LIMIAR + 10)
    assert pai.gera_filho().genoma.geracao == 8


def test_filho_parecido_com_o_pai():
    random.seed(31)
    pai = faz_criatura(size=8.0, velocity=2.0, energy=LIMIAR + 10)
    filho = pai.gera_filho()
    assert abs(filho.genoma.size - 8.0) < 5 * config.REPRODUCAO_DESVIO_PADRAO * config.CREATURE_BASE_RADIUS
    assert abs(filho.genoma.velocity - 2.0) < 5 * config.REPRODUCAO_DESVIO_PADRAO * config.CREATURE_BASE_VELOCITY


def test_filho_e_independente_do_pai():
    random.seed(32)
    pai = faz_criatura(energy=LIMIAR + 10)
    filho = pai.gera_filho()
    filho.angle = 0.0
    filho.andar(MUNDO)
    filho.gastar_energia()
    assert pai.pos == (500.0, 350.0)
    assert pai.energy == aprox((LIMIAR + 10) * (1 - PCT) - CUSTO_REP)


def test_sem_mutacao_filho_igual_ao_pai(sem_mutacao):
    pai = faz_criatura(size=9.0, velocity=2.5, cor=(1, 2, 3), energy=LIMIAR + 10)
    g = pai.gera_filho().genoma
    assert (g.size, g.velocity, g.cor) == (pytest.approx(9.0), pytest.approx(2.5), (1, 2, 3))
