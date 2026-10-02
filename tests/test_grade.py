from cobrinha.config import ALTURA_HUD, ALTURA_JANELA, COLUNAS, LARGURA_JANELA, LINHAS
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.ui.campo import celula_para_pixel


def test_grade_preenche_a_janela_sem_sobras():
    assert (LARGURA_JANELA, ALTURA_JANELA) == (800, 600)
    assert (COLUNAS, LINHAS, ALTURA_HUD) == (32, 22, 50)
    assert (GRADE_PADRAO.colunas, GRADE_PADRAO.linhas) == (32, 22)


def test_direcoes_opostas():
    assert Direcao.CIMA.oposta is Direcao.BAIXO
    assert Direcao.BAIXO.oposta is Direcao.CIMA
    assert Direcao.ESQUERDA.oposta is Direcao.DIREITA
    assert Direcao.DIREITA.oposta is Direcao.ESQUERDA


def test_vizinha_em_cada_direcao():
    centro = Posicao(5, 5)
    assert centro.vizinha(Direcao.CIMA) == Posicao(5, 4)
    assert centro.vizinha(Direcao.BAIXO) == Posicao(5, 6)
    assert centro.vizinha(Direcao.ESQUERDA) == Posicao(4, 5)
    assert centro.vizinha(Direcao.DIREITA) == Posicao(6, 5)


def test_grade_contem_os_cantos():
    assert GRADE_PADRAO.contem(Posicao(0, 0))
    assert GRADE_PADRAO.contem(Posicao(COLUNAS - 1, LINHAS - 1))


def test_grade_nao_contem_posicoes_de_fora():
    assert not GRADE_PADRAO.contem(Posicao(-1, 0))
    assert not GRADE_PADRAO.contem(Posicao(0, -1))
    assert not GRADE_PADRAO.contem(Posicao(COLUNAS, 0))
    assert not GRADE_PADRAO.contem(Posicao(0, LINHAS))


def test_todas_as_posicoes_cobre_a_grade_uma_vez():
    grade = Grade(4, 3)
    assert len(grade.todas) == 12
    assert len(set(grade.todas)) == 12
    assert all(grade.contem(posicao) for posicao in grade.todas)


def test_celula_para_pixel_desconta_o_hud():
    assert celula_para_pixel(Posicao(0, 0)) == (0, 50)
    assert celula_para_pixel(Posicao(1, 2)) == (25, 100)
    assert celula_para_pixel(Posicao(31, 21)) == (775, 575)
