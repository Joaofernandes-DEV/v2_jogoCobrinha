from cobrinha.config import ALTURA_HUD, ALTURA_JANELA, COLUNAS, LARGURA_JANELA, LINHAS
from cobrinha.dominio.grade import Posicao, todas_as_posicoes
from cobrinha.ui.campo import celula_para_pixel


def test_grade_preenche_a_janela_sem_sobras():
    assert (LARGURA_JANELA, ALTURA_JANELA) == (800, 600)
    assert (COLUNAS, LINHAS, ALTURA_HUD) == (32, 22, 50)


def test_posicao_dentro_da_grade():
    assert Posicao(0, 0).dentro_da_grade()
    assert Posicao(COLUNAS - 1, LINHAS - 1).dentro_da_grade()


def test_posicao_fora_da_grade():
    assert not Posicao(-1, 0).dentro_da_grade()
    assert not Posicao(0, -1).dentro_da_grade()
    assert not Posicao(COLUNAS, 0).dentro_da_grade()
    assert not Posicao(0, LINHAS).dentro_da_grade()


def test_todas_as_posicoes_cobre_a_grade_uma_vez():
    posicoes = todas_as_posicoes()
    assert len(posicoes) == COLUNAS * LINHAS
    assert len(set(posicoes)) == len(posicoes)


def test_celula_para_pixel_desconta_o_hud():
    assert celula_para_pixel(Posicao(0, 0)) == (0, 50)
    assert celula_para_pixel(Posicao(1, 2)) == (25, 100)
    assert celula_para_pixel(Posicao(31, 21)) == (775, 575)
