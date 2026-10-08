import random

import pytest

from cobrinha.config import COMIDAS_NO_DUELO, MAX_PASSOS_POR_QUADRO, PONTOS_FRUTA_DOURADA
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.duelo import NASCIMENTOS, EventoDuelo, PartidaDuelo
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada

P = Posicao
NIVEL_TESTE = Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=100)


def duelo(*cobras: Cobra, **kwargs) -> PartidaDuelo:
    """Duelo numa grade 10 × 10, com as maçãs longe (cantos de baixo), a 10 passos/s."""
    kwargs.setdefault("grade", Grade(10, 10))
    kwargs.setdefault("comidas", [P(0, 9), P(9, 9)])
    kwargs.setdefault("nivel", NIVEL_TESTE)
    kwargs.setdefault("rng", random.Random(0))
    return PartidaDuelo(cobras=cobras, **kwargs)


def reta(cabeca: Posicao, direcao: Direcao, tamanho: int = 3) -> Cobra:
    return Cobra.nova(cabeca, direcao, tamanho)


def eliminados(eventos: list[EventoDuelo]) -> set[int]:
    return {e.jogador for e in eventos if e.evento is Evento.BATEU}


# --- Começo da partida ---


def test_duelo_padrao_tem_2_cobras_nas_posicoes_de_nascimento():
    partida = PartidaDuelo(rng=random.Random(0))
    assert [j.nome for j in partida.jogadores] == ["J1", "J2"]
    for jogador, nascimento in zip(partida.jogadores, NASCIMENTOS, strict=False):
        assert jogador.cobra.cabeca == nascimento.cabeca
        assert jogador.cobra.direcao is nascimento.direcao
        assert jogador.vivo and jogador.pontos == 0
    assert len(partida.comidas) == COMIDAS_NO_DUELO
    for comida in partida.comidas:
        assert all(comida not in jogador.cobra for jogador in partida.jogadores)
    assert partida.em_andamento and not partida.empate


@pytest.mark.parametrize("quantidade", [0, 1, 5])
def test_quantidade_de_jogadores_fora_de_2_a_4_e_recusada(quantidade):
    with pytest.raises(ValueError):
        PartidaDuelo(quantidade=quantidade)


@pytest.mark.parametrize("quantidade", [2, 3, 4])
@pytest.mark.parametrize("nivel", NIVEIS, ids=lambda nivel: nivel.nome)
def test_nascimentos_ficam_livres_e_nao_se_cruzam_logo_no_comeco(nivel, quantidade):
    """Em todos os mapas, cada cobra nasce fora das pedras e tem 6 células livres à frente,
    sem cruzar o caminho das outras."""
    caminhos = []
    for nascimento in NASCIMENTOS[:quantidade]:
        cobra = reta(nascimento.cabeca, nascimento.direcao)
        frente = [nascimento.cabeca]
        for _ in range(6):
            frente.append(frente[-1].vizinha(nascimento.direcao))
        celulas = set(cobra.segmentos) | set(frente)
        assert all(GRADE_PADRAO.contem(celula) for celula in celulas)
        assert not celulas & nivel.obstaculos
        caminhos.append(celulas)
    for i, caminho in enumerate(caminhos):
        for outro in caminhos[i + 1 :]:
            assert not caminho & outro


# --- Colisões ---


def test_cobras_andam_juntas_no_mesmo_passo():
    partida = duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    assert partida.passo() == []
    assert partida.jogadores[0].cobra.cabeca == P(4, 2)
    assert partida.jogadores[1].cobra.cabeca == P(5, 6)


def test_cada_jogador_vira_so_a_propria_cobra():
    partida = duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    partida.virar(0, Direcao.BAIXO)
    partida.passo()
    assert partida.jogadores[0].cobra.cabeca == P(3, 3)
    assert partida.jogadores[1].cobra.cabeca == P(5, 6)


def test_bater_na_parede_elimina_e_o_outro_vence():
    partida = duelo(reta(P(9, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    eventos = partida.passo()
    assert EventoDuelo(Evento.BATEU, 0) in eventos
    assert EventoDuelo(Evento.VENCEU, 1) in eventos
    assert not partida.jogadores[0].vivo
    assert partida.encerrada and partida.vencedor == 1 and not partida.empate


def test_bater_numa_pedra_elimina():
    nivel = Nivel(
        nome="Pedra",
        numero=1,
        passos_por_segundo=10,
        meta_comidas=100,
        obstaculos=frozenset({P(4, 2)}),
    )
    partida = duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA), nivel=nivel)
    assert eliminados(partida.passo()) == {0}


def test_bater_no_proprio_corpo_elimina():
    cobra = Cobra([P(5, 5), P(4, 5), P(4, 6), P(5, 6), P(6, 6)], Direcao.DIREITA)
    partida = duelo(cobra, reta(P(2, 1), Direcao.DIREITA))
    partida.virar(0, Direcao.BAIXO)
    assert eliminados(partida.passo()) == {0}


def test_bater_no_corpo_de_outra_cobra_elimina_so_quem_bateu():
    # J1 desce e entra no meio do corpo horizontal do J2.
    partida = duelo(reta(P(5, 3), Direcao.BAIXO), reta(P(7, 4), Direcao.DIREITA, 4))
    eventos = partida.passo()
    assert eliminados(eventos) == {0}
    assert partida.vencedor == 1


def test_entrar_onde_estava_a_cabeca_do_outro_elimina():
    """A cabeça de antes do passo vira pescoço: entrar nela é bater no corpo."""
    # J2 desce de (5, 5) para (5, 6); J1 entra em (5, 5) no mesmo passo.
    partida = duelo(reta(P(4, 5), Direcao.DIREITA), reta(P(5, 5), Direcao.BAIXO))
    assert eliminados(partida.passo()) == {0}
    assert partida.vencedor == 1


def test_entrar_na_celula_da_cauda_que_sai_nao_elimina():
    # J2 anda para cima; a cauda dele sai de (5, 6) no mesmo passo em que J1 entra ali.
    partida = duelo(reta(P(4, 6), Direcao.DIREITA), reta(P(5, 4), Direcao.CIMA))
    eventos = partida.passo()
    assert eliminados(eventos) == set()
    assert partida.jogadores[0].cobra.cabeca == P(5, 6)
    assert partida.em_andamento


def test_entrar_na_cauda_de_quem_esta_crescendo_elimina():
    cauda_presa = reta(P(5, 4), Direcao.CIMA)
    cauda_presa.crescer()  # a cauda fica parada em (5, 6) neste passo
    partida = duelo(reta(P(4, 6), Direcao.DIREITA), cauda_presa)
    assert eliminados(partida.passo()) == {0}


def test_cabecas_na_mesma_celula_eliminam_as_duas_e_e_empate():
    partida = duelo(reta(P(3, 5), Direcao.DIREITA), reta(P(5, 5), Direcao.ESQUERDA))
    eventos = partida.passo()
    assert eliminados(eventos) == {0, 1}
    assert EventoDuelo(Evento.EMPATOU) in eventos
    assert partida.encerrada and partida.empate and partida.vencedor is None


def test_cabecas_que_trocam_de_lugar_eliminam_as_duas():
    partida = duelo(reta(P(4, 5), Direcao.DIREITA), reta(P(5, 5), Direcao.ESQUERDA))
    eventos = partida.passo()
    assert eliminados(eventos) == {0, 1}
    assert partida.empate


def test_tres_cabecas_na_mesma_celula_e_o_quarto_vence():
    partida = duelo(
        reta(P(3, 5), Direcao.DIREITA),
        reta(P(5, 5), Direcao.ESQUERDA),
        reta(P(4, 6), Direcao.CIMA),
        reta(P(1, 1), Direcao.DIREITA),
    )
    eventos = partida.passo()
    assert eliminados(eventos) == {0, 1, 2}
    assert partida.vencedor == 3


def test_todos_eliminados_no_mesmo_passo_por_motivos_diferentes_e_empate():
    # J1 bate na parede; J2 entra no corpo do J1, que conta mesmo ele saindo no passo.
    partida = duelo(reta(P(9, 4), Direcao.DIREITA, 5), reta(P(6, 3), Direcao.BAIXO))
    eventos = partida.passo()
    assert eliminados(eventos) == {0, 1}
    assert partida.empate


def test_cobra_eliminada_some_do_campo_e_libera_o_caminho():
    """Com 3 cobras, J1 bate; J2 passa depois por onde o corpo dele estava."""
    partida = duelo(
        reta(P(9, 4), Direcao.DIREITA),  # bate na parede no primeiro passo
        reta(P(8, 2), Direcao.BAIXO),  # desce pela coluna 8, onde estava o meio do J1
        reta(P(1, 8), Direcao.DIREITA),
    )
    assert eliminados(partida.passo()) == {0}
    assert partida.em_andamento and len(partida.vivos) == 2
    partida.passo()  # J2 entra em (8, 4), antes ocupada pelo J1
    assert partida.jogadores[1].vivo
    assert partida.jogadores[1].cobra.cabeca == P(8, 4)


def test_quem_e_eliminado_nao_vira_mais_e_a_partida_encerrada_para():
    partida = duelo(reta(P(9, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    partida.passo()
    cabeca = partida.jogadores[1].cobra.cabeca
    partida.virar(1, Direcao.CIMA)
    assert partida.atualizar(1.0) == []
    assert partida.jogadores[1].cobra.cabeca == cabeca


# --- Comida e tempo ---


def test_comer_da_ponto_so_a_quem_comeu_cresce_e_repoe_a_maca():
    partida = duelo(
        reta(P(3, 2), Direcao.DIREITA),
        reta(P(6, 6), Direcao.ESQUERDA),
        comidas=[P(4, 2), P(0, 9)],
    )
    eventos = partida.passo()
    assert eventos == [EventoDuelo(Evento.COMEU, 0)]
    assert [j.pontos for j in partida.jogadores] == [1, 0]
    assert partida.total_comidas == 1
    assert len(partida.comidas) == COMIDAS_NO_DUELO
    assert P(4, 2) not in partida.comidas
    partida.passo()
    assert len(partida.jogadores[0].cobra) == 4


def test_maca_dourada_vale_mais_para_quem_pegar():
    partida = duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    partida.fruta_dourada = FrutaDourada(P(5, 6))
    assert partida.passo() == [EventoDuelo(Evento.COMEU_DOURADA, 1)]
    assert partida.jogadores[1].pontos == PONTOS_FRUTA_DOURADA
    assert partida.fruta_dourada is None


def test_maca_dourada_some_com_o_tempo():
    partida = duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    partida.fruta_dourada = FrutaDourada(P(0, 0), tempo_restante=0.05)
    partida.atualizar(0.06)
    assert partida.fruta_dourada is None


def test_velocidade_e_uma_so_e_cresce_com_as_macas_de_todos():
    partida = duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 6), Direcao.ESQUERDA))
    inicial = partida.passos_por_segundo
    partida.total_comidas = 4
    assert partida.passos_por_segundo == pytest.approx(
        inicial + 4 * NIVEL_TESTE.aceleracao_por_comida
    )


def test_passo_fixo_independe_do_fps():
    partida = duelo(reta(P(1, 2), Direcao.DIREITA), reta(P(8, 6), Direcao.ESQUERDA))
    partida.atualizar(0.05)
    assert partida.jogadores[0].cobra.cabeca == P(1, 2)
    partida.atualizar(0.05)  # 0,1 s a 10 passos/s = 1 passo
    assert partida.jogadores[0].cobra.cabeca == P(2, 2)


def test_atualizar_nao_teleporta_depois_de_travamento():
    partida = duelo(reta(P(1, 2), Direcao.DIREITA), reta(P(8, 6), Direcao.ESQUERDA))
    partida.atualizar(5.0)
    assert partida.jogadores[0].cobra.cabeca == P(1 + MAX_PASSOS_POR_QUADRO, 2)


# --- Partidas aleatórias ---


@pytest.mark.parametrize("quantidade", [2, 3, 4])
@pytest.mark.parametrize("nivel", NIVEIS, ids=lambda nivel: nivel.nome)
def test_duelos_aleatorios_nunca_quebram_as_regras(nivel, quantidade):
    """Comandos aleatórios; a cada passo, as cobras vivas não se sobrepõem nem invadem nada."""
    rng = random.Random(quantidade * 10 + nivel.numero)
    partida = PartidaDuelo(quantidade, nivel=nivel, rng=random.Random(7))
    for _ in range(600):
        if partida.encerrada:
            break
        for jogador in partida.vivos:
            partida.virar(jogador.indice, rng.choice(list(Direcao)))
        partida.passo()
        ocupadas: list[Posicao] = []
        for jogador in partida.vivos:
            ocupadas.extend(jogador.cobra.segmentos)
        assert len(set(ocupadas)) == len(ocupadas)
        assert not set(ocupadas) & nivel.obstaculos
        assert all(GRADE_PADRAO.contem(celula) for celula in ocupadas)
        assert not set(partida.comidas) & (set(ocupadas) | nivel.obstaculos)
        assert len(partida.vivos) >= 2 or partida.encerrada
    if partida.encerrada:
        assert partida.empate or partida.jogadores[partida.vencedor].vivo
