import random

import pytest

from cobrinha.config import MAX_PASSOS_POR_QUADRO
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada, Partida, Situacao

P = Posicao


def partida_controlada(**kwargs) -> Partida:
    """Cobra de 3 em (5,5) andando para a direita, comida longe, 10 passos/s, meta alta."""
    kwargs.setdefault("grade", Grade(10, 10))
    kwargs.setdefault("cobra", Cobra.nova(P(5, 5), Direcao.DIREITA, 3))
    kwargs.setdefault("comida", P(0, 9))
    kwargs.setdefault(
        "nivel", Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=100)
    )
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


def test_comidas_no_nivel_e_pontos_somam_juntos():
    partida = partida_controlada(comida=P(6, 5), pontos=7)
    partida.passo()
    assert (partida.pontos, partida.comidas_no_nivel) == (8, 1)


def test_bater_a_meta_conclui_o_nivel():
    nivel = Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=1)
    partida = partida_controlada(nivel=nivel, comida=P(6, 5))
    assert partida.passo() is Evento.CONCLUIU_NIVEL
    assert partida.situacao is Situacao.NIVEL_CONCLUIDO
    assert partida.comida is None
    assert partida.atualizar(1.0) == []


def test_bater_a_meta_do_ultimo_nivel_e_vitoria():
    ultimo = NIVEIS[-1]
    nivel = Nivel(nome="Teste", numero=ultimo.numero, passos_por_segundo=10, meta_comidas=1)
    partida = partida_controlada(nivel=nivel, comida=P(6, 5))
    assert partida.passo() is Evento.VENCEU
    assert partida.situacao is Situacao.VITORIA


def test_proxima_fase_leva_os_pontos_e_reinicia_a_cobra():
    nivel = Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=1)
    partida = partida_controlada(grade=GRADE_PADRAO, nivel=nivel, comida=P(6, 5), pontos=4)
    partida.passo()
    seguinte = partida.proxima_fase()
    assert seguinte.nivel == NIVEIS[1]
    assert seguinte.passos_por_segundo == NIVEIS[1].passos_por_segundo
    assert (seguinte.pontos, seguinte.comidas_no_nivel) == (5, 0)
    assert len(seguinte.cobra) == 3
    assert seguinte.em_andamento
    assert seguinte.comida is not None


def test_proxima_fase_exige_nivel_concluido():
    with pytest.raises(RuntimeError):
        partida_controlada().proxima_fase()


# Fase 4: obstáculos, modos, aceleração e fruta dourada

from cobrinha.config import (  # noqa: E402
    DURACAO_FRUTA_DOURADA,
    PONTOS_FRUTA_DOURADA,
)
from cobrinha.dominio.partida import Modo  # noqa: E402


def nivel_teste(**kwargs) -> Nivel:
    kwargs.setdefault("nome", "Teste")
    kwargs.setdefault("numero", 1)
    kwargs.setdefault("passos_por_segundo", 10)
    kwargs.setdefault("meta_comidas", 100)
    return Nivel(**kwargs)


def test_bater_em_pedra_encerra_a_partida():
    partida = partida_controlada(nivel=nivel_teste(obstaculos=frozenset({P(6, 5)})))
    assert partida.passo() is Evento.BATEU
    assert partida.situacao is Situacao.DERROTA


def test_comida_nunca_nasce_em_pedra():
    for semente in range(30):
        partida = Partida(nivel=NIVEIS[2], rng=random.Random(semente))
        assert partida.comida not in partida.obstaculos


def test_modo_classico_morre_na_borda_e_sem_bordas_atravessa():
    for modo, esperado in ((Modo.CLASSICO, Evento.BATEU), (Modo.SEM_BORDAS, Evento.MOVEU)):
        cobra = Cobra.nova(P(9, 5), Direcao.DIREITA, 3)
        partida = partida_controlada(cobra=cobra, modo=modo)
        assert partida.passo() is esperado
    assert partida.cobra.cabeca == P(0, 5)


def test_sem_bordas_atravessa_por_cima_e_por_baixo():
    cobra = Cobra.nova(P(4, 0), Direcao.CIMA, 3)
    partida = partida_controlada(cobra=cobra, modo=Modo.SEM_BORDAS)
    partida.passo()
    assert partida.cobra.cabeca == P(4, 9)


def test_cobra_acelera_a_cada_comida():
    nivel = nivel_teste(aceleracao_por_comida=0.5)
    partida = partida_controlada(nivel=nivel, comida=P(6, 5))
    assert partida.passos_por_segundo == 10
    partida.passo()
    assert partida.passos_por_segundo == 10.5


def test_vitoria_conta_so_as_celulas_sem_pedra():
    nivel = nivel_teste(obstaculos=frozenset({P(0, 0)}))
    cobra = Cobra.nova(P(3, 0), Direcao.DIREITA, 3)
    partida = partida_controlada(grade=Grade(5, 1), nivel=nivel, cobra=cobra, comida=P(4, 0))
    assert partida.passo() is Evento.VENCEU


def forcar_fruta_dourada(partida: Partida) -> None:
    partida.rng.random = lambda: 0.0  # a chance de 10% sempre acontece


def test_fruta_dourada_aparece_numa_celula_livre():
    partida = partida_controlada(comida=P(6, 5))
    forcar_fruta_dourada(partida)
    partida.passo()
    dourada = partida.fruta_dourada
    assert dourada is not None
    assert dourada.posicao != partida.comida
    assert dourada.posicao not in partida.cobra
    assert dourada.tempo_restante == DURACAO_FRUTA_DOURADA


def test_comer_fruta_dourada_vale_mais_e_nao_conta_para_a_meta():
    partida = partida_controlada()
    partida.fruta_dourada = FrutaDourada(P(6, 5))
    assert partida.passo() is Evento.COMEU_DOURADA
    assert partida.pontos == PONTOS_FRUTA_DOURADA
    assert partida.comidas_no_nivel == 0
    assert partida.fruta_dourada is None
    partida.passo()
    assert len(partida.cobra) == 4  # também faz crescer


def test_fruta_dourada_some_com_o_tempo():
    partida = partida_controlada()
    partida.fruta_dourada = FrutaDourada(P(0, 0), tempo_restante=0.05)
    partida.atualizar(0.06)
    assert partida.fruta_dourada is None


def test_proxima_fase_mantem_o_modo():
    nivel = nivel_teste(meta_comidas=1)
    partida = partida_controlada(
        grade=GRADE_PADRAO, nivel=nivel, comida=P(6, 5), modo=Modo.SEM_BORDAS
    )
    partida.passo()
    assert partida.proxima_fase().modo is Modo.SEM_BORDAS


@pytest.mark.parametrize("modo", list(Modo))
@pytest.mark.parametrize("numero_nivel", [1, 2, 3])
def test_partidas_aleatorias_respeitam_pedras_e_modos(modo, numero_nivel):
    rng = random.Random(numero_nivel)
    partida = Partida(nivel=NIVEIS[numero_nivel - 1], rng=random.Random(7), modo=modo)
    forcar_fruta_dourada(partida)
    for _ in range(400):
        if not partida.em_andamento:
            break
        partida.virar(rng.choice(list(Direcao)))
        partida.passo()
        segmentos = list(partida.cobra.segmentos)
        assert len(set(segmentos)) == len(segmentos)
        assert not set(segmentos) & partida.obstaculos
        assert all(GRADE_PADRAO.contem(segmento) for segmento in segmentos)
        if partida.comida is not None:
            assert partida.comida not in partida.cobra
            assert partida.comida not in partida.obstaculos


def test_progresso_do_passo_acompanha_o_tempo():
    partida = partida_controlada()  # 10 passos por segundo: 0,1 s por passo
    assert partida.progresso_passo == 0
    partida.atualizar(0.04)
    assert partida.progresso_passo == pytest.approx(0.4)
    partida.atualizar(0.07)  # completa um passo (0,11 s) e sobra 0,01 s
    assert partida.cobra.cabeca == P(6, 5)
    assert partida.progresso_passo == pytest.approx(0.1)


def test_progresso_do_passo_fica_em_1_com_a_partida_encerrada():
    partida = partida_controlada(
        grade=Grade(10, 10), cobra=Cobra.nova(P(2, 5), Direcao.ESQUERDA, 3)
    )
    partida.atualizar(0.5)
    assert partida.situacao is Situacao.DERROTA
    assert partida.progresso_passo == 1.0
