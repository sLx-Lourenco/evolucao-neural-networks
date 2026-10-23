"""Testes da geometria toroidal (wrap e delta).

Correr a partir da pasta do projeto:  python -m pytest -v
Se o teu ficheiro de geometria tiver outro nome, muda o import abaixo.
"""
import pytest
from geometria import wrap, delta

MUNDO = (1000, 700)


def aprox(v):
    return pytest.approx(v, abs=1e-9)


# ---------------------------------------------------------------- wrap

@pytest.mark.parametrize("pos, esperado", [
    ((500, 300), (500, 300)),     # dentro: não muda
    ((0, 0), (0, 0)),             # canto de origem
    ((1003, 300), (3, 300)),      # saiu pela direita
    ((-2, 300), (998, 300)),      # saiu pela esquerda
    ((500, 705), (500, 5)),       # saiu por baixo
    ((500, -10), (500, 690)),     # saiu por cima
    ((1000, 700), (0, 0)),        # exatamente na borda: já está fora
    ((-1500, 1450), (500, 50)),   # mais de uma volta
    ((12.5, 699.75), (12.5, 699.75)),  # decimais
])
def test_wrap(pos, esperado):
    assert wrap(pos, MUNDO) == aprox(esperado)


def test_wrap_resultado_sempre_dentro():
    for x in range(-3000, 3000, 37):
        for y in range(-2000, 2000, 41):
            wx, wy = wrap((x + 0.5, y + 0.25), MUNDO)
            assert 0 <= wx < MUNDO[0]
            assert 0 <= wy < MUNDO[1]


# ---------------------------------------------------------------- delta

@pytest.mark.parametrize("a, b, esperado", [
    ((500, 300), (520, 330), (20, 30)),      # perto, no meio
    ((500, 300), (480, 300), (-20, 0)),      # para a esquerda, sem borda
    ((5, 300), (995, 320), (-10, 20)),       # x atravessa a borda esquerda
    ((995, 300), (5, 300), (10, 0)),         # x atravessa a borda direita
    ((500, 5), (500, 695), (0, -10)),        # y atravessa a borda de cima
    ((500, 695), (500, 5), (0, 10)),         # y atravessa a borda de baixo
    ((990, 690), (10, 15), (20, 25)),        # cantos opostos
    ((0, 0), (0, 300), (0, 300)),            # y abaixo de metade da altura
    ((0, 0), (400, 0), (400, 0)),            # x abaixo de metade da largura
    ((123.4, 56.7), (123.4, 56.7), (0, 0)),  # o mesmo ponto
])
def test_delta(a, b, esperado):
    assert delta(a, b, MUNDO) == aprox(esperado)


def test_delta_nunca_maior_que_metade():
    pontos = [(x + 0.3, y + 0.7) for x in range(0, 1000, 97) for y in range(0, 700, 83)]
    for a in pontos:
        for b in pontos:
            dx, dy = delta(a, b, MUNDO)
            assert abs(dx) <= MUNDO[0] / 2
            assert abs(dy) <= MUNDO[1] / 2


def test_delta_leva_de_a_ate_b():
    """Andar o vetor delta a partir de a (e dar a volta) tem de chegar a b."""
    pontos = [(x + 0.3, y + 0.7) for x in range(0, 1000, 131) for y in range(0, 700, 109)]
    for a in pontos:
        for b in pontos:
            dx, dy = delta(a, b, MUNDO)
            chegada = wrap((a[0] + dx, a[1] + dy), MUNDO)
            assert chegada == aprox(b)


def test_delta_antissimetrico():
    """O caminho de b para a é o de a para b ao contrário (fora do empate a meio caminho)."""
    a, b = (5, 300), (995, 320)
    dx1, dy1 = delta(a, b, MUNDO)
    dx2, dy2 = delta(b, a, MUNDO)
    assert (dx1, dy1) == aprox((-dx2, -dy2))


# ---------------------------------------------------------------- angulo_relativo (fase 5)

import math
from geometria import angulo_relativo, pitagoras


@pytest.mark.parametrize("angulo_criatura, vetor, esperado", [
    (0.0, (10, 0), 0.0),                       # mesmo à frente
    (0.0, (0, 10), math.pi / 2),               # abaixo = à direita (y cresce para baixo)
    (0.0, (0, -10), -math.pi / 2),             # acima = à esquerda
    (math.pi / 2, (10, 0), -math.pi / 2),      # a olhar para baixo, a comida à direita do ecrã fica à esquerda
    (math.pi / 2, (0, 10), 0.0),               # a olhar para baixo, comida em baixo: à frente
    (math.pi, (-10, 0), 0.0),                  # a olhar para a esquerda, comida à esquerda
    (3 * math.pi / 2, (0, -10), 0.0),          # a olhar para cima, comida em cima
    (0.0, (10, 10), math.pi / 4),              # na diagonal
    (6.0, (10, 0), 2 * math.pi - 6.0),         # ângulo da criatura perto de uma volta
    (0.1, (math.cos(6.2), math.sin(6.2)), 6.2 - 0.1 - 2 * math.pi),  # caminho curto pelo outro lado
])
def test_angulo_relativo(angulo_criatura, vetor, esperado):
    assert angulo_relativo(angulo_criatura, vetor) == pytest.approx(esperado, abs=1e-9)


def test_angulo_relativo_comida_atras():
    v = angulo_relativo(0.0, (-10, 0))
    assert abs(v) == pytest.approx(math.pi)


def test_angulo_relativo_sempre_entre_menos_pi_e_pi():
    for i in range(200):
        a = i * 0.137 - 10
        for vx, vy in [(1, 0), (0, 1), (-1, 0), (0, -1), (3, -7), (-2, -5)]:
            v = angulo_relativo(a, (vx, vy))
            assert -math.pi <= v < math.pi + 1e-12


def test_angulo_relativo_nao_depende_da_distancia():
    assert angulo_relativo(1.0, (3, 4)) == pytest.approx(angulo_relativo(1.0, (300, 400)))


def test_angulo_relativo_invariante_a_voltas_completas():
    assert angulo_relativo(0.5, (2, 7)) == pytest.approx(angulo_relativo(0.5 + 2 * math.pi, (2, 7)))
    assert angulo_relativo(0.5, (2, 7)) == pytest.approx(angulo_relativo(0.5 - 4 * math.pi, (2, 7)))


def test_virar_pelo_angulo_relativo_aponta_para_a_comida():
    """Somar o ângulo relativo ao ângulo da criatura deixa-a virada para a comida."""
    for a in (0.0, 1.0, 2.5, 4.0, 6.0):
        for vetor in [(5, 1), (-3, 4), (-2, -2), (0.5, -6)]:
            novo = a + angulo_relativo(a, vetor)
            assert angulo_relativo(novo, vetor) == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("v, esperado", [((3, 4), 5.0), ((0, 0), 0.0), ((-6, 8), 10.0), ((1.5, 2.0), 2.5)])
def test_pitagoras(v, esperado):
    assert pitagoras(v) == pytest.approx(esperado)
