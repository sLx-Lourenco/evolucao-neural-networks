"""Configuração comum a todos os testes.

- Põe o pygame em modo "sem ecrã", para os testes do main correrem em qualquer lado.
- Fornece funções auxiliares para criar cérebros, genomas e criaturas com valores escolhidos.
- Fixa as sementes dos DOIS geradores (random e numpy) antes de cada teste.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import random  # noqa: E402

import numpy as np  # noqa: E402
import pytest  # noqa: E402

import brain  # noqa: E402
import config  # noqa: E402
from brain import Brain  # noqa: E402
from creature import Creature  # noqa: E402
from genome import Genoma  # noqa: E402

TAMANHO = (1000, 700)
E, H, S = config.NEURO_ENTRADAS, config.NEURO_ESCONDIDA, config.NEURO_SAIDA


def semear(seed):
    """Fixa os dois geradores do projeto: o random (corpo) e o numpy (cérebros)."""
    random.seed(seed)
    brain.rng = np.random.default_rng(seed)


@pytest.fixture(autouse=True)
def sementes_fixas():
    semear(12345)


def cerebro_zero():
    """Um cérebro com tudo a zero: devolve sempre (0, 0) -> não vira, anda a meia velocidade."""
    return Brain(np.zeros((H, E)), np.zeros(H), np.zeros((S, H)), np.zeros(S))


def cerebro_fixo(virar=0.0, acelerar=0.0):
    """Um cérebro que ignora as entradas e devolve sempre as mesmas saídas (via os biases)."""
    b2 = np.zeros(S)
    b2[0] = np.arctanh(np.clip(virar, -0.999999, 0.999999))
    b2[1] = np.arctanh(np.clip(acelerar, -0.999999, 0.999999))
    return Brain(np.zeros((H, E)), np.zeros(H), np.zeros((S, H)), b2)


def cerebro_cacador():
    """Um cérebro feito à mão que vira para a comida e anda sempre no máximo.

    Entrada 0 (ângulo) -> neurónio escondido 0 -> saída 0 (virar), tudo com pesos positivos grandes.
    Bias da saída 1 grande -> acelerar perto de 1.
    """
    w1 = np.zeros((H, E))
    w1[0, 0] = 5.0
    w2 = np.zeros((S, H))
    w2[0, 0] = 5.0
    b2 = np.zeros(S)
    b2[1] = 5.0
    return Brain(w1, np.zeros(H), w2, b2)


def faz_genoma(size=8.0, velocity=2.0, cor=(120, 120, 120), geracao=1, cerebro=None, fundador=0):
    return Genoma(size, velocity, cor, geracao, cerebro if cerebro is not None else cerebro_zero(), fundador)


def faz_criatura(pos=(500.0, 350.0), size=8.0, velocity=2.0, energy=50.0,
                 cor=(120, 120, 120), geracao=1, cerebro=None, fundador=0):
    return Creature(pos, faz_genoma(size, velocity, cor, geracao, cerebro, fundador), energy)


def custo(size, vel_max, vel_real):
    return (config.CREATURE_K_BASE + config.CREATURE_K1 * size
            + config.CREATURE_K2 * vel_real ** 2 + config.CREATURE_K3 * vel_max ** 2)


@pytest.fixture
def sem_comida_nova(monkeypatch):
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)


@pytest.fixture
def sem_mutacao(monkeypatch):
    """Os filhos são cópias exatas dos pais (corpo e cérebro)."""
    monkeypatch.setattr(config, "REPRODUCAO_DESVIO_PADRAO", 0.0)
    monkeypatch.setattr(config, "NEURO_DESVIO_MUTACAO", 0.0)
