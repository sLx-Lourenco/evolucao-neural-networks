"""Testes do cérebro (fase 5): formas, criação ao acaso, pensar e mutação.

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import numpy as np
import pytest

import brain
import config
from brain import Brain
from conftest import cerebro_zero, cerebro_fixo, semear, E, H, S


# ================================================================ construtor e criação ao acaso

def test_construtor_guarda_os_arrays():
    w1, b1, w2, b2 = np.ones((H, E)), np.ones(H), np.ones((S, H)), np.ones(S)
    c = Brain(w1, b1, w2, b2)
    assert c.w1 is w1 and c.b1 is b1 and c.w2 is w2 and c.b2 is b2


def test_formas_dos_arrays():
    c = Brain.create_random()
    assert c.w1.shape == (H, E)
    assert c.b1.shape == (H,)
    assert c.w2.shape == (S, H)
    assert c.b2.shape == (S,)


def test_numero_de_genes_do_cerebro():
    c = Brain.create_random()
    total = c.w1.size + c.b1.size + c.w2.size + c.b2.size
    assert total == E * H + H + H * S + S


def test_create_random_devolve_um_brain():
    assert isinstance(Brain.create_random(), Brain)


def test_cerebros_ao_acaso_sao_diferentes():
    a, b = Brain.create_random(), Brain.create_random()
    assert not np.array_equal(a.w1, b.w1)
    assert not np.array_equal(a.w2, b.w2)


def test_pesos_iniciais_centrados_em_zero():
    pesos = np.concatenate([Brain.create_random().w1.ravel() for _ in range(500)])
    assert abs(pesos.mean()) < 0.05


def test_pesos_iniciais_com_o_desvio_do_config():
    pesos = np.concatenate([Brain.create_random().w1.ravel() for _ in range(800)])
    assert pesos.std() == pytest.approx(config.NEURO_DESVIO_DE_PESOS, rel=0.05)


def test_biases_tambem_sao_ao_acaso():
    biases = np.concatenate([Brain.create_random().b2 for _ in range(500)])
    assert biases.std() == pytest.approx(config.NEURO_DESVIO_DE_PESOS, rel=0.1)


def test_mesma_semente_mesmo_cerebro():
    semear(7)
    a = Brain.create_random()
    semear(7)
    b = Brain.create_random()
    assert np.array_equal(a.w1, b.w1) and np.array_equal(a.b2, b.b2)


# ================================================================ pensar

def test_pensar_devolve_duas_saidas():
    saidas = Brain.create_random().pensar(np.array([0.5, -0.2, 0.8]))
    assert np.shape(saidas) == (S,)


def test_saidas_sempre_entre_menos_1_e_1():
    rng = np.random.default_rng(1)
    for _ in range(200):
        c = Brain.create_random()
        x = rng.uniform(-1, 1, E)
        assert np.all(np.abs(c.pensar(x)) <= 1)


def test_saidas_ficam_limitadas_mesmo_com_pesos_enormes():
    c = Brain(np.full((H, E), 1e6), np.full(H, 1e6), np.full((S, H), -1e6), np.full(S, 1e6))
    saidas = c.pensar(np.array([1.0, 1.0, 1.0]))
    assert np.all(np.abs(saidas) <= 1)
    assert np.all(np.isfinite(saidas))


def test_pensar_e_deterministico():
    c = Brain.create_random()
    x = np.array([0.3, 0.7, -0.4])
    assert np.array_equal(c.pensar(x), c.pensar(x))


def test_pensar_nao_altera_o_cerebro():
    c = Brain.create_random()
    antes = [a.copy() for a in (c.w1, c.b1, c.w2, c.b2)]
    c.pensar(np.array([0.3, 0.7, -0.4]))
    for a, b in zip(antes, (c.w1, c.b1, c.w2, c.b2)):
        assert np.array_equal(a, b)


def test_pensar_nao_altera_as_entradas():
    x = np.array([0.3, 0.7, -0.4])
    copia = x.copy()
    Brain.create_random().pensar(x)
    assert np.array_equal(x, copia)


def test_cerebros_diferentes_pensam_diferente():
    x = np.array([0.3, 0.7, -0.4])
    assert not np.allclose(Brain.create_random().pensar(x), Brain.create_random().pensar(x))


@pytest.mark.parametrize("entrada", [[0.1, 0.2, 0.3], (0.1, 0.2, 0.3), [0, 1, 0]])
def test_pensar_aceita_listas_e_tuplos(entrada):
    c = Brain.create_random()
    assert np.allclose(c.pensar(entrada), c.pensar(np.array(entrada, dtype=float)))


def test_cerebro_zero_devolve_zeros():
    assert np.allclose(cerebro_zero().pensar(np.array([0.9, -0.3, 0.5])), 0)


def test_pensar_segue_a_formula():
    """saídas = tanh(W2 · tanh(W1 · x + b1) + b2)"""
    rng = np.random.default_rng(3)
    w1, b1, w2, b2 = rng.normal(size=(H, E)), rng.normal(size=H), rng.normal(size=(S, H)), rng.normal(size=S)
    x = rng.uniform(-1, 1, E)
    esperado = np.tanh(w2 @ np.tanh(w1 @ x + b1) + b2)
    assert np.allclose(Brain(w1, b1, w2, b2).pensar(x), esperado)


def test_pensar_a_mao_num_caso_simples():
    """Só a entrada 0 liga ao neurónio 0, que liga só à saída 0."""
    w1 = np.zeros((H, E)); w1[0, 0] = 1.0
    w2 = np.zeros((S, H)); w2[0, 0] = 2.0
    c = Brain(w1, np.zeros(H), w2, np.zeros(S))
    saidas = c.pensar(np.array([0.5, 0.0, 0.0]))
    assert saidas[0] == pytest.approx(np.tanh(2 * np.tanh(0.5)))
    assert saidas[1] == pytest.approx(0.0)


def test_bias_funciona_sem_entradas():
    c = cerebro_fixo(virar=0.3, acelerar=-0.6)
    assert np.allclose(c.pensar(np.zeros(E)), [0.3, -0.6], atol=1e-6)


def test_ordem_das_entradas_importa():
    w1 = np.zeros((H, E)); w1[0, 0] = 3.0
    w2 = np.zeros((S, H)); w2[0, 0] = 3.0
    c = Brain(w1, np.zeros(H), w2, np.zeros(S))
    assert c.pensar(np.array([0.5, 0.0, 0.0]))[0] != pytest.approx(c.pensar(np.array([0.0, 0.5, 0.0]))[0])


# ================================================================ cópia mutada

def test_copia_e_um_brain_novo():
    c = Brain.create_random()
    filho = c.copia_mutada()
    assert isinstance(filho, Brain)
    assert filho is not c


def test_copia_tem_arrays_novos():
    """Apanha o erro de pai e filho partilharem o mesmo array."""
    c = Brain.create_random()
    f = c.copia_mutada()
    for a, b in ((c.w1, f.w1), (c.b1, f.b1), (c.w2, f.w2), (c.b2, f.b2)):
        assert a is not b
        assert not np.shares_memory(a, b)


def test_copia_mantem_as_formas():
    f = Brain.create_random().copia_mutada()
    assert (f.w1.shape, f.b1.shape, f.w2.shape, f.b2.shape) == ((H, E), (H,), (S, H), (S,))


def test_copia_nao_altera_o_pai():
    c = Brain.create_random()
    antes = [a.copy() for a in (c.w1, c.b1, c.w2, c.b2)]
    for _ in range(50):
        c.copia_mutada()
    for a, b in zip(antes, (c.w1, c.b1, c.w2, c.b2)):
        assert np.array_equal(a, b)


def test_copia_muda_todos_os_arrays():
    c = Brain.create_random()
    f = c.copia_mutada()
    for a, b in ((c.w1, f.w1), (c.b1, f.b1), (c.w2, f.w2), (c.b2, f.b2)):
        assert not np.array_equal(a, b)


def test_mutacao_centrada_nos_pesos_do_pai():
    """Apanha o erro de o filho ficar só com ruído (sem herdar os pesos)."""
    c = Brain(np.full((H, E), 2.0), np.full(H, -1.0), np.full((S, H), 0.5), np.full(S, 3.0))
    filhos = [c.copia_mutada() for _ in range(2000)]
    assert np.mean([f.w1 for f in filhos]) == pytest.approx(2.0, abs=0.01)
    assert np.mean([f.b1 for f in filhos]) == pytest.approx(-1.0, abs=0.01)
    assert np.mean([f.w2 for f in filhos]) == pytest.approx(0.5, abs=0.01)
    assert np.mean([f.b2 for f in filhos]) == pytest.approx(3.0, abs=0.01)


def test_mutacao_com_o_desvio_do_config():
    c = Brain.create_random()
    difs = np.concatenate([(c.copia_mutada().w1 - c.w1).ravel() for _ in range(1500)])
    assert difs.std() == pytest.approx(config.NEURO_DESVIO_MUTACAO, rel=0.05)


def test_mutacao_independente_do_valor_do_peso():
    """O desvio é absoluto: um peso grande muta tanto como um peso pequeno."""
    grande = Brain(np.full((H, E), 4.0), np.zeros(H), np.zeros((S, H)), np.zeros(S))
    pequeno = Brain(np.full((H, E), 0.01), np.zeros(H), np.zeros((S, H)), np.zeros(S))
    dg = np.concatenate([(grande.copia_mutada().w1 - 4.0).ravel() for _ in range(1000)])
    dp = np.concatenate([(pequeno.copia_mutada().w1 - 0.01).ravel() for _ in range(1000)])
    assert dg.std() == pytest.approx(dp.std(), rel=0.08)


def test_filho_pensa_parecido_com_o_pai():
    c = Brain.create_random()
    x = np.array([0.4, 0.6, -0.1])
    difs = [np.abs(c.copia_mutada().pensar(x) - c.pensar(x)).max() for _ in range(200)]
    assert np.median(difs) < 0.3


def test_sem_mutacao_copia_exata(monkeypatch):
    monkeypatch.setattr(config, "NEURO_DESVIO_MUTACAO", 0.0)
    c = Brain.create_random()
    f = c.copia_mutada()
    assert np.array_equal(c.w1, f.w1) and np.array_equal(c.b2, f.b2)
    assert f.w1 is not c.w1


def test_linhagens_de_cerebros_afastam_se():
    c = Brain.create_random()
    f = c
    for _ in range(100):
        f = f.copia_mutada()
    assert np.abs(f.w1 - c.w1).mean() > config.NEURO_DESVIO_MUTACAO * 3


def test_mutacao_usa_o_gerador_do_modulo():
    """Reprodutibilidade: com a mesma semente, a mesma mutação."""
    c = Brain.create_random()
    brain.rng = np.random.default_rng(99)
    a = c.copia_mutada()
    brain.rng = np.random.default_rng(99)
    b = c.copia_mutada()
    assert np.array_equal(a.w1, b.w1)
