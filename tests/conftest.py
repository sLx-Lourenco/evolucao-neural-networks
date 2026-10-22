"""Configuração comum a todos os testes.

- Põe o pygame em modo "sem ecrã", para os testes do main correrem em qualquer lado
  (no teu PC e no GitHub Actions).
- Fornece funções auxiliares para criar genomas e criaturas com valores escolhidos.
"""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pytest  # noqa: E402

import config  # noqa: E402
from creature import Creature  # noqa: E402
from genome import Genoma  # noqa: E402

TAMANHO = (1000, 700)


def faz_genoma(size=8.0, velocity=2.0, cor=(120, 120, 120), geracao=1):
    return Genoma(size, velocity, cor, geracao)


def faz_criatura(pos=(500.0, 350.0), size=8.0, velocity=2.0, energy=50.0,
                 cor=(120, 120, 120), geracao=1):
    return Creature(pos, faz_genoma(size, velocity, cor, geracao), energy)


def custo(size, velocity):
    return config.CREATURE_K_BASE + config.CREATURE_K1 * size + config.CREATURE_K2 * velocity ** 2


@pytest.fixture
def sem_comida_nova(monkeypatch):
    """Durante o teste não nasce comida nova."""
    monkeypatch.setattr(config, "TAXA_FOOD_PER_TICK", 0.0)


@pytest.fixture
def sem_viragem(monkeypatch):
    """Durante o teste as criaturas andam sempre a direito."""
    monkeypatch.setattr(config, "CREATURE_MAX_TURN", 0.0)


@pytest.fixture
def sem_mutacao(monkeypatch):
    """Durante o teste os filhos são cópias exatas dos pais."""
    monkeypatch.setattr(config, "REPRODUCAO_DESVIO_PADRAO", 0.0)
