"""Testes da criatura (fase 3): movimento, energia, comer e morrer.

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import math
import random

import pytest

import config
from creature import Creature

MUNDO = (1000, 700)


def aprox(v, tol=1e-9):
    return pytest.approx(v, abs=tol)


def diferenca_angular(a, b):
    """Menor diferença entre dois ângulos, em radianos (entre -pi e pi)."""
    return (b - a + math.pi) % (2 * math.pi) - math.pi


def nova(pos=(500.0, 350.0), size=8.0, velocity=2.0, **kw):
    return Creature(pos, size, velocity, **kw)


# ---------------------------------------------------------------- construtor

def test_construtor_guarda_valores():
    c = nova((10.0, 20.0), 7.5, 1.8)
    assert c.pos == (10.0, 20.0)
    assert c.size == 7.5
    assert c.velocity == 1.8


def test_energia_por_omissao_e_a_base():
    assert nova().energy == config.CREATURE_BASE_ENERGY


def test_energia_pode_ser_dada():
    """Na fase 4 os filhos nascem com parte da energia do pai."""
    assert nova(energy=37.5).energy == 37.5


def test_angulo_inicial_dentro_de_uma_volta():
    random.seed(0)
    for _ in range(500):
        assert 0 <= nova().angle < 2 * math.pi


def test_angulos_iniciais_variam():
    random.seed(1)
    angulos = {round(nova().angle, 6) for _ in range(50)}
    assert len(angulos) > 40


# ---------------------------------------------------------------- virar

def test_virar_nunca_passa_da_viragem_maxima():
    random.seed(2)
    c = nova()
    for _ in range(5000):
        antes = c.angle
        c.virar_acaso()
        assert abs(diferenca_angular(antes, c.angle)) <= config.CREATURE_MAX_TURN + 1e-12


def test_virar_mantem_angulo_dentro_de_uma_volta():
    random.seed(3)
    c = nova()
    for _ in range(20_000):
        c.virar_acaso()
        assert 0 <= c.angle < 2 * math.pi


def test_virar_e_igual_para_os_dois_lados():
    """Em média não deve haver tendência para virar só para um lado."""
    random.seed(4)
    c = nova()
    total = 0.0
    n = 20_000
    for _ in range(n):
        antes = c.angle
        c.virar_acaso()
        total += diferenca_angular(antes, c.angle)
    assert abs(total / n) < config.CREATURE_MAX_TURN * 0.05


def test_virar_nao_depende_da_direcao_atual():
    """A viragem é somada, não multiplicada: perto de 0 vira tanto como perto de 2*pi."""
    random.seed(5)
    maiores = []
    for inicio in (0.05, 3.0, 6.2):
        c = nova()
        maior = 0.0
        for _ in range(3000):
            c.angle = inicio
            c.virar_acaso()
            maior = max(maior, abs(diferenca_angular(inicio, c.angle)))
        maiores.append(maior)
    for m in maiores:
        assert m > config.CREATURE_MAX_TURN * 0.9


# ---------------------------------------------------------------- andar

@pytest.mark.parametrize("angulo, esperado", [
    (0.0, (502.0, 350.0)),               # para a direita
    (math.pi / 2, (500.0, 352.0)),       # para baixo (no pygame o y cresce para baixo)
    (math.pi, (498.0, 350.0)),           # para a esquerda
    (3 * math.pi / 2, (500.0, 348.0)),   # para cima
])
def test_andar_na_direcao_do_angulo(angulo, esperado):
    c = nova((500.0, 350.0), velocity=2.0)
    c.angle = angulo
    c.andar(MUNDO)
    assert c.pos == aprox(esperado)


def test_andar_percorre_a_velocidade():
    random.seed(6)
    for _ in range(200):
        v = random.uniform(0.5, 4.0)
        c = nova((500.0, 350.0), velocity=v)
        c.angle = random.uniform(0, 2 * math.pi)
        c.andar(MUNDO)
        dx, dy = c.pos[0] - 500.0, c.pos[1] - 350.0
        assert math.hypot(dx, dy) == aprox(v)


def test_andar_atravessa_a_borda_direita():
    c = nova((999.0, 100.0), velocity=3.0)
    c.angle = 0.0
    c.andar(MUNDO)
    assert c.pos == aprox((2.0, 100.0))


def test_andar_atravessa_a_borda_de_cima():
    c = nova((100.0, 1.0), velocity=3.0)
    c.angle = 3 * math.pi / 2
    c.andar(MUNDO)
    assert c.pos == aprox((100.0, 698.0))


def test_andar_fica_sempre_dentro_do_mundo():
    random.seed(7)
    c = nova((5.0, 5.0), velocity=3.0)
    for _ in range(20_000):
        c.virar_acaso()
        c.andar(MUNDO)
        assert 0 <= c.pos[0] < MUNDO[0]
        assert 0 <= c.pos[1] < MUNDO[1]


def test_andar_nao_gasta_energia():
    c = nova()
    antes = c.energy
    c.andar(MUNDO)
    assert c.energy == antes


# ---------------------------------------------------------------- energia

def custo_esperado(size, velocity):
    return config.CREATURE_K_BASE + config.CREATURE_K1 * size + config.CREATURE_K2 * velocity ** 2


@pytest.mark.parametrize("size, velocity", [(8.0, 2.0), (6.4, 3.6), (9.6, 1.0), (8.0, 0.0)])
def test_gastar_energia_segue_a_formula(size, velocity):
    c = nova(size=size, velocity=velocity)
    antes = c.energy
    c.gastar_energia()
    assert antes - c.energy == aprox(custo_esperado(size, velocity))


def test_velocidade_conta_ao_quadrado():
    """Duplicar a velocidade quadruplica a parte do custo que vem dela."""
    lenta, rapida = nova(velocity=1.5), nova(velocity=3.0)
    lenta.gastar_energia()
    rapida.gastar_energia()
    parte_lenta = config.CREATURE_BASE_ENERGY - lenta.energy - config.CREATURE_K_BASE - config.CREATURE_K1 * 8.0
    parte_rapida = config.CREATURE_BASE_ENERGY - rapida.energy - config.CREATURE_K_BASE - config.CREATURE_K1 * 8.0
    assert parte_rapida == aprox(4 * parte_lenta)


def test_maior_gasta_mais():
    pequena, grande = nova(size=6.0), nova(size=10.0)
    pequena.gastar_energia()
    grande.gastar_energia()
    assert grande.energy < pequena.energy


def test_custo_sempre_positivo():
    """Mesmo parada e minúscula, existir custa alguma coisa."""
    c = nova(size=0.0, velocity=0.0)
    antes = c.energy
    c.gastar_energia()
    assert c.energy < antes


def test_custo_da_criatura_media_e_razoavel():
    """Uma criatura média deve sobreviver entre 100 e 5000 ticks sem comer."""
    custo = custo_esperado(config.CREATURE_BASE_RADIUS, config.CREATURE_BASE_VELOCITY)
    ticks = config.CREATURE_BASE_ENERGY / custo
    assert 100 <= ticks <= 5000


# ---------------------------------------------------------------- comer e morrer

def test_comer_da_a_energia_da_comida():
    c = nova(energy=50.0)
    c.comer()
    assert c.energy == aprox(50.0 + config.FOOD_ENERGY)


def test_regenerar_soma_a_quantidade():
    c = nova(energy=10.0)
    c.regenerar_energia(12.5)
    assert c.energy == aprox(22.5)


@pytest.mark.parametrize("energia, viva", [(100.0, True), (0.001, True), (0.0, False), (-3.0, False)])
def test_esta_viva(energia, viva):
    assert nova(energy=energia).esta_viva() is viva


def test_morre_de_fome_no_tick_certo():
    """Sem comer, morre exatamente quando a energia acumulada gasta passa a inicial."""
    c = nova(size=8.0, velocity=2.0, energy=10.0)
    custo = custo_esperado(8.0, 2.0)
    ticks_esperados = math.ceil(10.0 / custo)
    ticks = 0
    while c.esta_viva():
        c.gastar_energia()
        ticks += 1
        assert ticks < 100_000
    assert ticks in (ticks_esperados, ticks_esperados + 1)
