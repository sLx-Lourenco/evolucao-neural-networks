"""Testes da simulação completa (checkpoint da fase 4).

São os testes mais lentos: correm o mundo durante milhares de ticks com o teu config.
Se falharem, normalmente não é um bug, é o equilíbrio de parâmetros do config
(energia da comida, taxa de comida, custos, limiar de reprodução).

Correr só estes:  python -m pytest tests/test_simulacao.py -v
"""
import random
import statistics

import pytest

import config
from world import World

TICKS = 6_000
LIMITE_POPULACAO = 2000
SEMENTES = [0, 1, 2]


def corre(seed, ticks=TICKS):
    random.seed(seed)
    w = World(config.WORLD_SIZE)
    historico = []
    for _ in range(ticks):
        w.advance_tick()
        historico.append(len(w.creatures))
        if not w.creatures or len(w.creatures) > LIMITE_POPULACAO:
            break
    return w, historico


@pytest.fixture(scope="module")
def corridas():
    return {s: corre(s) for s in SEMENTES}


@pytest.mark.parametrize("seed", SEMENTES)
def test_populacao_nao_se_extingue(corridas, seed):
    w, _ = corridas[seed]
    assert w.creatures, (
        f"Com a semente {seed}, a população extinguiu-se no tick {w.n_ticks}. "
        "As criaturas não conseguem chegar ao limiar de reprodução: experimenta "
        "mais energia por comida, mais comida, ou um limiar mais baixo."
    )


@pytest.mark.parametrize("seed", SEMENTES)
def test_populacao_nao_explode(corridas, seed):
    w, _ = corridas[seed]
    assert len(w.creatures) <= LIMITE_POPULACAO, (
        f"Com a semente {seed}, a população passou de {LIMITE_POPULACAO}. "
        "Há energia a mais a entrar no mundo, ou reproduzir é barato demais."
    )


@pytest.mark.parametrize("seed", SEMENTES)
def test_ha_varias_geracoes(corridas, seed):
    w, _ = corridas[seed]
    if not w.creatures:
        pytest.skip("a população extinguiu-se (ver test_populacao_nao_se_extingue)")
    assert max(c.genoma.geracao for c in w.creatures) >= 5


@pytest.mark.parametrize("seed", SEMENTES)
def test_populacao_oscila_e_nao_fica_parada(corridas, seed):
    """No checkpoint da fase 4 a população sobe e desce."""
    w, historico = corridas[seed]
    if not w.creatures:
        pytest.skip("a população extinguiu-se")
    ultimos = historico[len(historico) // 2:]
    assert max(ultimos) > min(ultimos)


@pytest.mark.parametrize("seed", SEMENTES)
def test_comida_nunca_passa_do_maximo(corridas, seed):
    w, _ = corridas[seed]
    assert len(w.foods) <= max(config.MAX_FOOD, config.INICIAL_AMOUNT_FOOD)


@pytest.mark.parametrize("seed", SEMENTES)
def test_genes_continuam_nos_limites(corridas, seed):
    w, _ = corridas[seed]
    for c in w.creatures:
        assert config.CREATURE_MIN_RADIUS <= c.genoma.size <= config.CREATURE_MAX_RADIUS
        assert config.CREATURE_MIN_VELOCITY <= c.genoma.velocity <= config.CREATURE_MAX_VELOCITY
        assert all(0 <= canal <= 255 for canal in c.genoma.cor)


@pytest.mark.parametrize("seed", SEMENTES)
def test_todas_vivas_no_fim_do_tick(corridas, seed):
    w, _ = corridas[seed]
    assert all(c.esta_viva() for c in w.creatures)


def test_mesma_semente_mesmo_resultado():
    """Reprodutibilidade: a mesma semente dá exatamente a mesma simulação."""
    w1, h1 = corre(123, ticks=2000)
    w2, h2 = corre(123, ticks=2000)
    assert h1 == h2
    assert [c.pos for c in w1.creatures] == [c.pos for c in w2.creatures]
    assert [c.genoma.cor for c in w1.creatures] == [c.genoma.cor for c in w2.creatures]


def test_sementes_diferentes_resultados_diferentes():
    _, h1 = corre(1, ticks=2000)
    _, h2 = corre(2, ticks=2000)
    assert h1 != h2


def test_mutacao_cria_variedade(corridas):
    """Ao fim de muitas gerações há criaturas com genes diferentes entre si."""
    vivos = [c for s in SEMENTES for c in corridas[s][0].creatures]
    if len(vivos) < 5:
        pytest.skip("população demasiado pequena")
    assert statistics.pstdev(c.genoma.size for c in vivos) > 0
    assert len({c.genoma.cor for c in vivos}) > 1
