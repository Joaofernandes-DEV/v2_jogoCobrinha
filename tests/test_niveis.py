import pytest

from cobrinha.dominio.niveis import NIVEIS, obter_nivel, proximo_nivel
from cobrinha.dominio.progresso import Progresso


def test_niveis_numerados_em_ordem_e_cada_vez_mais_rapidos():
    assert [nivel.numero for nivel in NIVEIS] == list(range(1, len(NIVEIS) + 1))
    velocidades = [nivel.passos_por_segundo for nivel in NIVEIS]
    assert velocidades == sorted(velocidades)
    assert len(set(velocidades)) == len(velocidades)
    assert all(nivel.meta_comidas > 0 for nivel in NIVEIS)


def test_obter_nivel():
    assert obter_nivel(1) is NIVEIS[0]
    assert obter_nivel(len(NIVEIS)) is NIVEIS[-1]
    for invalido in (0, len(NIVEIS) + 1):
        with pytest.raises(ValueError):
            obter_nivel(invalido)


def test_proximo_nivel():
    assert proximo_nivel(NIVEIS[0]) is NIVEIS[1]
    assert proximo_nivel(NIVEIS[-1]) is None


def test_ranking_guarda_os_5_melhores_em_ordem():
    progresso = Progresso()
    for pontos in (3, 9, 1, 7, 5, 8):
        progresso.registrar_pontuacao("CLASSICO", pontos, 1, "2026-10-02")
    assert [r.pontos for r in progresso.ranking("CLASSICO")] == [9, 8, 7, 5, 3]
    assert progresso.recorde("CLASSICO") == 9


def test_registrar_devolve_a_colocacao():
    progresso = Progresso()
    assert progresso.registrar_pontuacao("CLASSICO", 0, 1, "2026-10-02") is None
    assert progresso.registrar_pontuacao("CLASSICO", 10, 2, "2026-10-02") == 1
    assert progresso.registrar_pontuacao("CLASSICO", 4, 1, "2026-10-02") == 2
    # Empate: quem chegou antes fica na frente.
    assert progresso.registrar_pontuacao("CLASSICO", 10, 3, "2026-10-03") == 2
    for pontos in (8, 7, 6):
        progresso.registrar_pontuacao("CLASSICO", pontos, 1, "2026-10-02")
    assert progresso.registrar_pontuacao("CLASSICO", 2, 1, "2026-10-02") is None


def test_rankings_sao_separados_por_modo():
    progresso = Progresso()
    progresso.registrar_pontuacao("CLASSICO", 5, 1, "2026-10-02")
    progresso.registrar_pontuacao("SEM_BORDAS", 12, 2, "2026-10-02")
    assert progresso.recorde("CLASSICO") == 5
    assert progresso.recorde("SEM_BORDAS") == 12
    assert progresso.recorde("OUTRO") == 0


def test_progresso_libera_niveis_sem_regredir_nem_passar_do_ultimo():
    progresso = Progresso()
    assert progresso.maior_nivel_liberado == 1
    progresso.liberar_nivel(2)
    progresso.liberar_nivel(1)
    assert progresso.maior_nivel_liberado == 2
    progresso.liberar_nivel(99)
    assert progresso.maior_nivel_liberado == len(NIVEIS)


# Mapas dos níveis (J4)

from collections import deque  # noqa: E402

from cobrinha.config import COLUNAS, LINHAS, TAMANHO_INICIAL_COBRA  # noqa: E402
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Posicao  # noqa: E402
from cobrinha.dominio.niveis import mapa  # noqa: E402

LINHA_DE_PARTIDA = LINHAS // 2
COLUNA_DE_PARTIDA = COLUNAS // 4


def test_nomes_unicos_e_aceleracao_positiva():
    assert len({nivel.nome for nivel in NIVEIS}) == len(NIVEIS)
    assert all(nivel.aceleracao_por_comida > 0 for nivel in NIVEIS)


def test_dificuldade_cresce_com_pedras_a_partir_do_nivel_2():
    assert not NIVEIS[0].obstaculos
    assert 0 < len(NIVEIS[1].obstaculos) < len(NIVEIS[2].obstaculos)


def test_obstaculos_ficam_dentro_do_campo():
    for nivel in NIVEIS:
        assert all(GRADE_PADRAO.contem(pedra) for pedra in nivel.obstaculos)


def test_faixa_de_partida_da_cobra_esta_livre():
    """A cobra nasce na linha 11 e precisa de espaço à frente para reagir."""
    inicio = COLUNA_DE_PARTIDA - TAMANHO_INICIAL_COBRA + 1
    faixa = {Posicao(c, LINHA_DE_PARTIDA) for c in range(inicio, COLUNA_DE_PARTIDA + 10)}
    for nivel in NIVEIS:
        assert not faixa & nivel.obstaculos, nivel.nome


def test_todas_as_celulas_livres_sao_alcancaveis():
    """Sem áreas fechadas: a comida nunca nasce num lugar impossível de alcançar."""
    for nivel in NIVEIS:
        livres = set(GRADE_PADRAO.todas) - nivel.obstaculos
        inicio = Posicao(COLUNA_DE_PARTIDA, LINHA_DE_PARTIDA)
        visitadas, fila = {inicio}, deque([inicio])
        while fila:
            atual = fila.popleft()
            for direcao in Direcao:
                vizinha = atual.vizinha(direcao)
                if vizinha in livres and vizinha not in visitadas:
                    visitadas.add(vizinha)
                    fila.append(vizinha)
        assert visitadas == livres, nivel.nome


def test_mapa_com_tamanho_errado_e_recusado():
    with pytest.raises(ValueError):
        mapa("....")


def test_mapa_converte_cerquilhas_em_posicoes():
    linhas = ["." * COLUNAS] * LINHAS
    linhas[3] = "#" + "." * (COLUNAS - 2) + "#"
    assert mapa(*linhas) == {Posicao(0, 3), Posicao(COLUNAS - 1, 3)}
