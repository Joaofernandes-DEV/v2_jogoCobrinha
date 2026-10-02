"""Contagem 3-2-1 antes de a cobra andar (J10), por cima do jogo congelado."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.audio import Som
from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.menu import BOTAO_ESQUERDO, TECLAS_CONFIRMAR
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo

SEQUENCIA = ("3", "2", "1", "JÁ!")
DURACAO_ETAPA = 0.6  # segundos por número
OPACIDADE_VEU = 150


class EstadoContagem(Estado):
    def __init__(
        self,
        jogo: Jogo,
        jogando: EstadoJogando,
        titulo: str | None = None,
        subtitulo: str | None = None,
    ) -> None:
        super().__init__(jogo)
        self.jogando = jogando
        self.titulo = titulo
        self.subtitulo = subtitulo
        self.tempo = 0.0
        self.veu = criar_veu(OPACIDADE_VEU)
        self._ultima_etapa_tocada = -1
        self._tocar_etapa()

    @property
    def indice_etapa(self) -> int:
        return min(int(self.tempo / DURACAO_ETAPA), len(SEQUENCIA) - 1)

    @property
    def etapa_atual(self) -> str:
        return SEQUENCIA[self.indice_etapa]

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.WINDOWFOCUSLOST:
            # Sem foco, a contagem não pode terminar e soltar a cobra: vira pausa.
            self.jogo.desempilhar()
            navegacao.pausar(self.jogo, self.jogando)
        elif (evento.type == pygame.KEYDOWN and evento.key in TECLAS_CONFIRMAR) or (
            evento.type == pygame.MOUSEBUTTONDOWN and evento.button == BOTAO_ESQUERDO
        ):
            self._terminar()

    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        if self.tempo >= DURACAO_ETAPA * len(SEQUENCIA):
            self._terminar()
        else:
            self._tocar_etapa()

    def _tocar_etapa(self) -> None:
        """Um bipe por número e um mais agudo no "JÁ!"."""
        if self.indice_etapa != self._ultima_etapa_tocada:
            self._ultima_etapa_tocada = self.indice_etapa
            ultimo = self.indice_etapa == len(SEQUENCIA) - 1
            self.jogo.audio.tocar(Som.CONTAGEM_JA if ultimo else Som.CONTAGEM)

    def _terminar(self) -> None:
        self.jogo.desempilhar()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        linhas = []
        if self.titulo:
            linhas.append((self.titulo, TamanhoFonte.TITULO, Paleta.BRANCO))
        if self.subtitulo:
            linhas.append((self.subtitulo, TamanhoFonte.MEDIO, Paleta.VERDE_CLARO))
        linhas.append((self.etapa_atual, TamanhoFonte.GIGANTE, Paleta.AMARELO))
        linhas.append(("ENTER: começar já", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO))
        desenhar_linhas(superficie, linhas, topo=ALTURA_JANELA // 2 - 150, espaco=20)
