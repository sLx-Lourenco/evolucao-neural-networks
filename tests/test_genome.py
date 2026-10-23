"""Testes do genoma (fases 4 e 5): genes, cérebro, fundadora, cópia mutada, limites e hereditariedade.

Correr a partir da pasta do projeto:  python -m pytest -v
"""
import random
import statistics

import numpy as np
import pytest

import config
from brain import Brain
from genome import Genoma
from conftest import faz_genoma, cerebro_zero

TAXA = config.REPRODUCAO_DESVIO_PADRAO


# ================================================================ construtor

def test_construtor_guarda_os_genes():
    cerebro = cerebro_zero()
    g = Genoma(7.5, 2.25, (10, 200, 30), 4, cerebro, 17)
    assert g.size == 7.5
    assert g.velocity == 2.25
    assert g.cor == (10, 200, 30)
    assert g.geracao == 4
    assert g.brain is cerebro
    assert g.id_fundador == 17


# ================================================================ cópia mutada: básico

def test_copia_e_um_objeto_novo():
    g = faz_genoma()
    assert g.copia_mutada() is not g


def test_copia_nao_altera_o_original():
    random.seed(0)
    g = faz_genoma(8.0, 2.0, (100, 150, 200), 3)
    for _ in range(200):
        g.copia_mutada()
    assert (g.size, g.velocity, g.cor, g.geracao) == (8.0, 2.0, (100, 150, 200), 3)


def test_copia_e_do_tipo_genoma():
    assert isinstance(faz_genoma().copia_mutada(), Genoma)


def test_geracao_aumenta_um():
    assert faz_genoma(geracao=1).copia_mutada().geracao == 2
    assert faz_genoma(geracao=41).copia_mutada().geracao == 42


def test_geracao_acumula_ao_longo_de_linhagens():
    random.seed(1)
    g = faz_genoma(geracao=1)
    for _ in range(100):
        g = g.copia_mutada()
    assert g.geracao == 101


# ================================================================ cópia mutada: a cor

def test_cor_e_um_tuplo_de_tres():
    random.seed(2)
    for _ in range(200):
        c = faz_genoma().copia_mutada().cor
        assert isinstance(c, tuple)
        assert len(c) == 3


def test_cor_tem_inteiros():
    random.seed(3)
    for _ in range(200):
        for canal in faz_genoma().copia_mutada().cor:
            assert isinstance(canal, int)


@pytest.mark.parametrize("cor", [(0, 0, 0), (255, 255, 255), (0, 255, 3), (128, 128, 128)])
def test_cor_fica_entre_0_e_255(cor):
    random.seed(4)
    g = faz_genoma(cor=cor)
    for _ in range(2000):
        g = g.copia_mutada()
        for canal in g.cor:
            assert 0 <= canal <= 255


def test_cor_dos_filhos_parecida_com_a_do_pai():
    """A cor muta pouco: a média dos filhos fica perto da do pai."""
    random.seed(5)
    pai = faz_genoma(cor=(100, 150, 200))
    filhos = [pai.copia_mutada().cor for _ in range(3000)]
    for i, canal_pai in enumerate(pai.cor):
        media = statistics.mean(f[i] for f in filhos)
        assert abs(media - canal_pai) < 2


def test_cor_muta_canal_a_canal():
    """Os três canais mudam de forma independente (não somam todos o mesmo)."""
    random.seed(6)
    pai = faz_genoma(cor=(128, 128, 128))
    diferentes = 0
    for _ in range(500):
        r, g, b = pai.copia_mutada().cor
        if not (r == g == b):
            diferentes += 1
    assert diferentes > 400


def test_cor_presa_nas_pontas_nao_fica_presa_para_sempre():
    """Um canal a 0 pode voltar a subir."""
    random.seed(7)
    g = faz_genoma(cor=(0, 0, 0))
    maximo = 0
    for _ in range(500):
        g = g.copia_mutada()
        maximo = max(maximo, *g.cor)
    assert maximo > 20


# ================================================================ cópia mutada: tamanho e velocidade

def test_filhos_nao_sao_todos_iguais():
    random.seed(8)
    pai = faz_genoma()
    filhos = [pai.copia_mutada() for _ in range(100)]
    assert len({round(f.size, 9) for f in filhos}) > 90
    assert len({round(f.velocity, 9) for f in filhos}) > 90


def test_tamanho_dos_filhos_centrado_no_pai():
    random.seed(9)
    pai = faz_genoma(size=10.0)
    tamanhos = [pai.copia_mutada().size for _ in range(5000)]
    assert statistics.mean(tamanhos) == pytest.approx(10.0, abs=0.05)


def test_velocidade_dos_filhos_centrada_no_pai():
    """Apanha o erro de sortear a velocidade à volta do tamanho."""
    random.seed(10)
    pai = faz_genoma(size=8.0, velocity=2.5)
    velocidades = [pai.copia_mutada().velocity for _ in range(5000)]
    assert statistics.mean(velocidades) == pytest.approx(2.5, abs=0.03)


def test_desvio_do_tamanho_segue_o_config():
    random.seed(11)
    pai = faz_genoma(size=10.0)
    tamanhos = [pai.copia_mutada().size for _ in range(8000)]
    esperado = TAXA * config.CREATURE_BASE_RADIUS
    assert statistics.stdev(tamanhos) == pytest.approx(esperado, rel=0.08)


def test_desvio_da_velocidade_segue_o_config():
    random.seed(12)
    pai = faz_genoma(velocity=3.0)
    velocidades = [pai.copia_mutada().velocity for _ in range(8000)]
    esperado = TAXA * config.CREATURE_BASE_VELOCITY
    assert statistics.stdev(velocidades) == pytest.approx(esperado, rel=0.08)


def test_tamanho_e_velocidade_mutam_independentes():
    """O tamanho do filho não deve decidir a velocidade (e vice-versa)."""
    random.seed(13)
    pai = faz_genoma(size=8.0, velocity=3.0)
    filhos = [pai.copia_mutada() for _ in range(3000)]
    r = statistics.correlation([f.size for f in filhos], [f.velocity for f in filhos])
    assert abs(r) < 0.1


# ================================================================ limites

def test_tamanho_nunca_sai_dos_limites():
    random.seed(14)
    for inicio in (config.CREATURE_MIN_RADIUS, config.CREATURE_MAX_RADIUS, 8.0):
        g = faz_genoma(size=inicio)
        for _ in range(3000):
            g = g.copia_mutada()
            assert config.CREATURE_MIN_RADIUS <= g.size <= config.CREATURE_MAX_RADIUS


def test_velocidade_nunca_sai_dos_limites():
    """Apanha o erro de prender a velocidade usando o tamanho."""
    random.seed(15)
    for inicio in (config.CREATURE_MIN_VELOCITY, config.CREATURE_MAX_VELOCITY, 3.0):
        g = faz_genoma(velocity=inicio)
        for _ in range(3000):
            g = g.copia_mutada()
            assert config.CREATURE_MIN_VELOCITY <= g.velocity <= config.CREATURE_MAX_VELOCITY


def test_velocidade_nao_copia_o_tamanho():
    random.seed(16)
    g = faz_genoma(size=6.0, velocity=1.0)
    filho = g.copia_mutada()
    assert abs(filho.velocity - 1.0) < 1.0


def test_valores_fora_dos_limites_sao_puxados_para_dentro():
    g = faz_genoma(size=1000.0, velocity=-5.0)
    filho = g.copia_mutada()
    assert filho.size == config.CREATURE_MAX_RADIUS
    assert filho.velocity == config.CREATURE_MIN_VELOCITY


def test_limites_do_config_fazem_sentido():
    assert 0 < config.CREATURE_MIN_RADIUS < config.CREATURE_BASE_RADIUS < config.CREATURE_MAX_RADIUS
    assert 0 < config.CREATURE_MIN_VELOCITY < config.CREATURE_BASE_VELOCITY < config.CREATURE_MAX_VELOCITY


# ================================================================ sem mutação

def test_sem_mutacao_os_filhos_sao_copias(sem_mutacao):
    g = faz_genoma(8.3, 2.7, (10, 20, 30), 5, cerebro=Brain.create_random(), fundador=9)
    filho = g.copia_mutada()
    assert filho.size == pytest.approx(8.3)
    assert filho.velocity == pytest.approx(2.7)
    assert filho.cor == (10, 20, 30)
    assert filho.geracao == 6
    assert filho.id_fundador == 9
    assert np.array_equal(filho.brain.w1, g.brain.w1)


# ================================================================ hereditariedade

def test_netos_parecem_mais_com_os_avos_do_que_com_estranhos():
    """Hereditariedade: ao fim de poucas gerações a linhagem ainda se reconhece."""
    random.seed(17)
    avo = faz_genoma(size=5.0, velocity=1.5, cor=(250, 10, 10))
    neto = avo.copia_mutada().copia_mutada().copia_mutada()
    estranho = faz_genoma(size=12.0, velocity=4.0, cor=(10, 10, 250))
    dist_avo = abs(neto.size - avo.size) + abs(neto.velocity - avo.velocity)
    dist_estranho = abs(neto.size - estranho.size) + abs(neto.velocity - estranho.velocity)
    assert dist_avo < dist_estranho
    assert neto.cor[0] > neto.cor[2]


def test_linhagens_afastam_se_com_o_tempo():
    """Variação: muitas gerações de mutação afastam a linhagem do ponto de partida."""
    random.seed(18)
    distancias = []
    for _ in range(50):
        g = faz_genoma(size=8.0)
        for _ in range(200):
            g = g.copia_mutada()
        distancias.append(abs(g.size - 8.0))
    assert statistics.mean(distancias) > TAXA * config.CREATURE_BASE_RADIUS * 3


# ================================================================ cérebro no genoma (fase 5)

def test_filho_tem_cerebro_novo():
    g = faz_genoma(cerebro=Brain.create_random())
    filho = g.copia_mutada()
    assert isinstance(filho.brain, Brain)
    assert filho.brain is not g.brain


def test_cerebro_do_filho_e_mutado():
    g = faz_genoma(cerebro=Brain.create_random())
    filho = g.copia_mutada()
    assert not np.array_equal(filho.brain.w1, g.brain.w1)


def test_cerebro_do_filho_parecido_com_o_do_pai():
    g = faz_genoma(cerebro=Brain.create_random())
    filho = g.copia_mutada()
    assert np.abs(filho.brain.w1 - g.brain.w1).max() < 6 * config.NEURO_DESVIO_MUTACAO


def test_cerebro_do_pai_fica_igual():
    g = faz_genoma(cerebro=Brain.create_random())
    antes = g.brain.w1.copy()
    for _ in range(20):
        g.copia_mutada()
    assert np.array_equal(g.brain.w1, antes)


def test_cor_nao_e_estragada_pela_variavel_do_cerebro():
    """O canal azul e o cérebro não se misturam (os dois chegam a usar o nome b)."""
    g = faz_genoma(cor=(10, 20, 250), cerebro=Brain.create_random())
    filho = g.copia_mutada()
    assert isinstance(filho.cor, tuple) and len(filho.cor) == 3
    assert isinstance(filho.brain, Brain)
    assert filho.cor[2] > 150


def test_mutacao_do_corpo_e_do_cerebro_sao_independentes(monkeypatch):
    """Desligar a mutação do corpo não desliga a do cérebro, e vice-versa."""
    monkeypatch.setattr(config, "REPRODUCAO_DESVIO_PADRAO", 0.0)
    g = faz_genoma(cerebro=Brain.create_random())
    f = g.copia_mutada()
    assert f.size == pytest.approx(g.size)
    assert not np.array_equal(f.brain.w1, g.brain.w1)

    monkeypatch.setattr(config, "REPRODUCAO_DESVIO_PADRAO", 0.05)
    monkeypatch.setattr(config, "NEURO_DESVIO_MUTACAO", 0.0)
    f = g.copia_mutada()
    assert np.array_equal(f.brain.w1, g.brain.w1)


# ================================================================ fundadora

@pytest.mark.parametrize("fundador", [0, 7, 49])
def test_fundadora_passa_igual_aos_filhos(fundador):
    g = faz_genoma(fundador=fundador)
    for _ in range(100):
        g = g.copia_mutada()
        assert g.id_fundador == fundador
