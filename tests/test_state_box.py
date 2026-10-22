"""Testes da caixa de estado (fase 1): correr, pausa, turbo e quantos ticks avançar.

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import pytest

import config
from state_box import State


def test_estado_inicial():
    s = State()
    assert s.correr is True
    assert s.pausa is False
    assert s.turbo is False


def test_estados_independentes():
    a, b = State(), State()
    a.pausa = True
    assert b.pausa is False


@pytest.mark.parametrize("pausa, turbo, esperado", [
    (False, False, config.TICK_AVANCO),
    (False, True, config.TICK_AVANCO_TURBO),
    (True, False, config.TICK_PARADO),
    (True, True, config.TICK_PARADO),  # a pausa ganha ao turbo
])
def test_avanco_de_ticks(pausa, turbo, esperado):
    assert State(pausa=pausa, turbo=turbo).get_avanco_ticks() == esperado


def test_config_pausa_e_zero():
    assert config.TICK_PARADO == 0


def test_config_turbo_mais_rapido_que_normal():
    assert config.TICK_AVANCO_TURBO > config.TICK_AVANCO >= 1


def test_avanco_e_inteiro():
    """É usado num range(), por isso tem de ser inteiro."""
    for pausa in (False, True):
        for turbo in (False, True):
            assert isinstance(State(pausa=pausa, turbo=turbo).get_avanco_ticks(), int)
