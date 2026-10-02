"""Loop principal e gerenciador de estados (telas) do jogo."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, FPS, LARGURA_JANELA, TITULO, Paleta

if TYPE_CHECKING:
    from cobrinha.estados.base import Estado


class Jogo:
    """Dono da janela e do único loop do jogo.

    As telas ficam numa pilha: só a do topo recebe eventos e é atualizada,
    mas todas são desenhadas de baixo para cima (assim a pausa aparece
    por cima do jogo congelado).
    """

    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(TITULO)
        # SCALED permite ampliar a janela e usar tela cheia sem borrar a pixel art.
        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA), pygame.SCALED)
        self.relogio = pygame.time.Clock()
        self.pilha: list[Estado] = []
        self.rodando = False

    @property
    def estado_atual(self) -> Estado | None:
        return self.pilha[-1] if self.pilha else None

    def trocar_estado(self, estado: Estado) -> None:
        """Substitui a pilha inteira por uma nova tela."""
        self.pilha = [estado]

    def empilhar(self, estado: Estado) -> None:
        """Abre uma tela por cima da atual (ex.: pausa)."""
        self.pilha.append(estado)

    def desempilhar(self) -> None:
        """Fecha a tela do topo e volta para a de baixo."""
        if self.pilha:
            self.pilha.pop()

    def sair(self) -> None:
        """Pede o fim do loop. O pygame é encerrado só em `executar`."""
        self.rodando = False

    def executar(self) -> None:
        self.rodando = True
        try:
            while self.rodando and self.estado_atual is not None:
                dt = self.relogio.tick(FPS) / 1000
                self._processar_eventos()
                if not self.rodando:
                    break
                self.estado_atual.atualizar(dt)
                self._desenhar()
        finally:
            # Único ponto de encerramento do pygame (corrige B1 e B5 da V1).
            pygame.quit()

    def _processar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.sair()
                return
            if self.estado_atual is not None:
                self.estado_atual.tratar_evento(evento)

    def _desenhar(self) -> None:
        self.tela.fill(Paleta.PRETO)
        for estado in self.pilha:
            estado.desenhar(self.tela)
        pygame.display.flip()
