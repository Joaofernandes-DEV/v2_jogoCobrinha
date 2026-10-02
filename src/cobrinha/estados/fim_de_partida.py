"""Tela de fim de partida, desenhada por cima do campo congelado.

Versão simples da Fase 1; ganha o visual definitivo na Fase 3.
"""

import pygame

from cobrinha.config import ALTURA_JANELA, LARGURA_JANELA, Paleta
from cobrinha.dominio.partida import Partida, Situacao
from cobrinha.estados.base import Estado
from cobrinha.jogo import Jogo
from cobrinha.ui import texto

OPACIDADE_VEU = 170
TECLAS_JOGAR_DE_NOVO = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


class EstadoFimDePartida(Estado):
    def __init__(self, jogo: Jogo, partida: Partida, recorde_anterior: int) -> None:
        super().__init__(jogo)
        self.vitoria = partida.situacao is Situacao.VITORIA
        self.pontos = partida.pontos
        self.novo_recorde = self.pontos > recorde_anterior
        self.recorde = max(recorde_anterior, self.pontos)
        self.veu = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA), pygame.SRCALPHA)
        self.veu.fill((*Paleta.PRETO, OPACIDADE_VEU))

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in TECLAS_JOGAR_DE_NOVO:
            # Import local: jogando.py também importa este módulo.
            from cobrinha.estados.jogando import EstadoJogando

            self.jogo.trocar_estado(EstadoJogando(self.jogo, self.recorde))
        elif evento.key == pygame.K_ESCAPE:
            self.jogo.sair()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        titulo = "VOCÊ VENCEU!" if self.vitoria else "FIM DE JOGO"
        linhas = [
            (titulo, 64, Paleta.AMARELO if self.vitoria else Paleta.VERMELHO),
            (f"PONTOS {self.pontos}", 36, Paleta.BRANCO),
        ]
        if self.novo_recorde:
            linhas.append(("NOVO RECORDE!", 32, Paleta.AMARELO))
        linhas.append(("ENTER: jogar de novo    ESC: sair", 26, Paleta.CINZA_CLARO))

        y = ALTURA_JANELA // 2 - 90
        for conteudo, tamanho, cor in linhas:
            imagem = texto.renderizar(conteudo, tamanho, cor)
            superficie.blit(imagem, imagem.get_rect(midtop=(LARGURA_JANELA // 2, y)))
            y += imagem.get_height() + 18
