import random

import pytest

from cobrinha.config import MAX_PASSOS_POR_QUADRO
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.partida import Evento, Partida, Situacao

P = Posicao


def partida_controlada(**kwargs) -> Partida:
    """Cobra de 3 em (5,5) andando para a direita, comida longe, 10 passos/s."""
    kwargs.setdefault("grade", Grade(10, 10))
    kwargs.setdefault("cobra", Cobra.nova(P(5, 5), Direcao.DIREITA, 3))
    kwargs.setdefault("comida", P(0, 9))
    kwargs.setdefault("passos_por_segundo", 10)
    kwargs.setdefault("rng", random.Random(0))
    return Partida(**kwargs)


def test_partida_padrao_comeca_alinhada_a_grade():
    """Bug B2 da V1: a cobra nascia fora do alinhamento da comida."""
    partida = Partida(rng=random.Random(0))
    assert partida.em_andamento
    assert all(GRADE_PADRAO.contem(segmento) for segmento in partida.cobra.segmentos)
    assert partida.comida is not None
    assert partida.comida not in partida.cobra


def test_passo_move_a_cobra():
    partida = partida_controlada()
    assert partida.passo() is Evento.MOVEU
    assert partida.cobra.cabeca == P(6, 5)


def test_comer_soma_ponto_cresce_e_sorteia_nova_comida():
    partida = partida_controlada(comida=P(6, 5))
    assert partida.passo() is Evento.COMEU
    assert partida.pontos == 1
    assert partida.comida is not None
    assert partida.comida not in partida.cobra
    partida.passo()
    assert len(partida.cobra) == 4


def test_bater_na_parede_encerra_a_partida():
    partida = partida_controlada(cobra=Cobra.nova(P(9, 5), Direcao.DIREITA, 3))
    assert partida.passo() is Evento.BATEU
    assert partida.situacao is Situacao.DERROTA


def test_bater_no_proprio_corpo_encerra_a_partida():
    # Cobra de 5 em "C": virar para baixo leva a cabeça para dentro do corpo.
    cobra = Cobra([P(5, 5), P(4, 5), P(4, 6), P(5, 6), P(6, 6)], Direcao.DIREITA)
    partida = partida_controlada(cobra=cobra)
    partida.virar(Direcao.BAIXO)
    assert partida.passo() is Evento.BATEU
    assert partida.situacao is Situacao.DERROTA


def test_seguir_a_propria_cauda_nao_mata():
    # Cobra de 4 em quadrado: a cabeça entra na célula que a cauda está deixando.
    cobra = Cobra([P(5, 5), P(5, 6), P(4, 6), P(4, 5)], Direcao.CIMA)
    partida = partida_controlada(cobra=cobra)
    partida.virar(Direcao.ESQUERDA)
    assert partida.passo() is Evento.MOVEU
    assert partida.em_andamento


def test_curva_rapida_nao_mata_a_cobra():
    """Bug B3 da V1, de ponta a ponta: ↑ e ← no mesmo tick fazem um "U" seguro."""
    partida = partida_controlada(cobra=Cobra.nova(P(5, 5), Direcao.DIREITA, 5))
    partida.virar(Direcao.CIMA)
    partida.virar(Direcao.ESQUERDA)
    assert partida.passo() is Evento.MOVEU
    assert partida.passo() is Evento.MOVEU
    assert partida.cobra.cabeca == P(4, 4)
    assert partida.em_andamento


def test_encher_o_campo_e_vitoria():
    # 4 células: a cobra de 3 come a última comida e vai ter tamanho 4.
    grade = Grade(4, 1)
    cobra = Cobra.nova(P(2, 0), Direcao.DIREITA, 3)
    partida = partida_controlada(grade=grade, cobra=cobra, comida=P(3, 0))
    assert partida.passo() is Evento.VENCEU
    assert partida.situacao is Situacao.VITORIA
    assert partida.comida is None


def test_atualizar_executa_passos_em_ritmo_fixo():
    partida = partida_controlada()  # 10 passos/s → 1 passo a cada 0,1 s
    assert partida.atualizar(0.06) == []
    assert partida.atualizar(0.06) == [Evento.MOVEU]
    assert partida.cobra.cabeca == P(6, 5)


def test_atualizar_nao_teleporta_depois_de_travamento():
    partida = partida_controlada()
    eventos = partida.atualizar(5.0)
    assert len(eventos) == MAX_PASSOS_POR_QUADRO


def test_partida_encerrada_nao_avanca_nem_vira():
    partida = partida_controlada(cobra=Cobra.nova(P(9, 5), Direcao.DIREITA, 3))
    partida.passo()
    cabeca = partida.cobra.cabeca
    partida.virar(Direcao.CIMA)
    assert partida.atualizar(1.0) == []
    assert partida.cobra.cabeca == cabeca


@pytest.mark.parametrize("semente", range(5))
def test_partidas_aleatorias_nunca_quebram_as_regras(semente):
    """Joga partidas com comandos aleatórios e confere os invariantes a cada passo."""
    rng = random.Random(semente)
    partida = Partida(grade=Grade(8, 6), rng=random.Random(semente))
    for _ in range(500):
        if not partida.em_andamento:
            break
        partida.virar(rng.choice(list(Direcao)))
        partida.passo()
        segmentos = list(partida.cobra.segmentos)
        assert len(set(segmentos)) == len(segmentos)
        assert all(partida.grade.contem(segmento) for segmento in segmentos)
        assert partida.comida is None or partida.comida not in partida.cobra
