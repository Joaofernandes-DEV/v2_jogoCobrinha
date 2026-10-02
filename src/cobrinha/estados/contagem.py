"""Contagem 3-2-1 antes de a cobra andar (J10), por cima do jogo congelado."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.menu import TECLAS_CONFIRMAR
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo

SEQUENCIA = ("3", "2", "1", "JÁ!")
DURACAO_ETAPA = 0.6  # segundos por número
OPACIDADE_VEU = 110


class EstadoContagem(Estado):
    def __init__(self, jogo: Jogo, jogando: EstadoJogando, titulo: str | None = None) -> None:
        super().__init__(jogo)
        self.jogando = jogando
        self.titulo = titulo
        self.tempo = 0.0
        self.veu = criar_veu(OPACIDADE_VEU)

    @property
    def etapa_atual(self) -> str:
        indice = min(int(self.tempo / DURACAO_ETAPA), len(SEQUENCIA) - 1)
        return SEQUENCIA[indice]

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.WINDOWFOCUSLOST:
            # Sem foco, a contagem não pode terminar e soltar a cobra: vira pausa.
            self.jogo.desempilhar()
            navegacao.pausar(self.jogo, self.jogando)
        elif evento.type == pygame.KEYDOWN and evento.key in TECLAS_CONFIRMAR:
            self._terminar()

    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        if self.tempo >= DURACAO_ETAPA * len(SEQUENCIA):
            self._terminar()

    def _terminar(self) -> None:
        self.jogo.desempilhar()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        linhas = []
        if self.titulo:
            linhas.append((self.titulo, 48, Paleta.BRANCO))
        linhas.append((self.etapa_atual, 120, Paleta.AMARELO))
        linhas.append(("ENTER: começar já", 22, Paleta.CINZA_CLARO))
        desenhar_linhas(superficie, linhas, topo=ALTURA_JANELA // 2 - 130)
