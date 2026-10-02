"""Tela de jogo. Na Fase 0 ela só desenha o HUD e o campo vazio."""

import pygame

from cobrinha.config import ALTURA_HUD
from cobrinha.estados.base import Estado
from cobrinha.jogo import Jogo
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.hud import desenhar_hud


class EstadoJogando(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.pontos = 0
        self.nivel = 1
        self.recorde = 0

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.jogo.sair()

    def desenhar(self, superficie: pygame.Surface) -> None:
        desenhar_hud(superficie, self.pontos, self.nivel, self.recorde)
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
