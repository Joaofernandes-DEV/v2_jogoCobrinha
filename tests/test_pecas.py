import pygame
import pytest

from cobrinha.config import TAMANHO_CELULA
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.ui.pecas import (
    Sprites,
    TipoPeca,
    angulo_da_curva,
    classificar_pecas,
    direcao_entre,
)

P = Posicao
D = Direcao


def test_direcao_entre_vizinhas():
    assert direcao_entre(P(5, 5), P(6, 5)) is D.DIREITA
    assert direcao_entre(P(5, 5), P(4, 5)) is D.ESQUERDA
    assert direcao_entre(P(5, 5), P(5, 4)) is D.CIMA
    assert direcao_entre(P(5, 5), P(5, 6)) is D.BAIXO


def test_direcao_entre_atravessando_a_borda():
    # Modo sem bordas: da última coluna para a primeira é um passo para a direita.
    assert direcao_entre(P(31, 5), P(0, 5)) is D.DIREITA
    assert direcao_entre(P(0, 5), P(31, 5)) is D.ESQUERDA
    assert direcao_entre(P(3, 0), P(3, 21)) is D.CIMA


@pytest.mark.parametrize(
    ("lados", "angulo"),
    [
        ({D.ESQUERDA, D.BAIXO}, 0),
        ({D.BAIXO, D.DIREITA}, 90),
        ({D.DIREITA, D.CIMA}, 180),
        ({D.CIMA, D.ESQUERDA}, 270),
    ],
)
def test_angulo_da_curva(lados, angulo):
    assert angulo_da_curva(frozenset(lados)) == angulo


def test_lados_opostos_nao_formam_curva():
    with pytest.raises(ValueError):
        angulo_da_curva(frozenset({D.ESQUERDA, D.DIREITA}))


def test_classificar_cobra_em_l():
    # Cabeça em cima, descendo para a curva e seguindo para a esquerda até a cauda.
    segmentos = [P(5, 3), P(5, 4), P(5, 5), P(4, 5), P(3, 5)]
    pecas = classificar_pecas(segmentos, D.CIMA)
    assert [(p.tipo, p.angulo) for p in pecas] == [
        (TipoPeca.CABECA, 90),  # olhando para cima
        (TipoPeca.RETO, 90),  # vertical
        (TipoPeca.CURVA, 270),  # liga cima e esquerda
        (TipoPeca.RETO, 0),  # horizontal
        (TipoPeca.CAUDA, 0),  # liga à direita
    ]
    assert [p.posicao for p in pecas] == segmentos


def test_cobra_de_um_segmento_usa_a_direcao_atual():
    pecas = classificar_pecas([P(1, 1)], D.ESQUERDA)
    assert [(p.tipo, p.angulo) for p in pecas] == [(TipoPeca.CABECA, 180)]


def test_cabeca_aponta_para_onde_andou_e_nao_para_a_fila_de_comandos():
    cobra = Cobra.nova(P(5, 5), D.DIREITA, 3)
    cobra.virar(D.CIMA)  # ainda na fila: a cabeça continua virada para a direita
    pecas = classificar_pecas(cobra.segmentos, cobra.direcao)
    assert pecas[0].angulo == 0


def test_sprites_tem_todas_as_rotacoes_e_desenham(jogo):
    sprites = Sprites()
    superficie = pygame.Surface(jogo.tela.get_size())
    sprites.desenhar_cobra(superficie, Cobra.nova(P(5, 5), D.DIREITA, 4))
    sprites.desenhar_comida(superficie, P(10, 10), tempo=1.0)
    for tipo in TipoPeca:
        for angulo in (0, 90, 180, 270):
            peca = sprites._pecas[tipo, angulo]
            assert peca.get_size() == (TAMANHO_CELULA, TAMANHO_CELULA)
