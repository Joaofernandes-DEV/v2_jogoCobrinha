"""Pausa (J2): menu por cima do jogo congelado, com a música em pausa."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.audio import Som
from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.base import EstadoDePartida
    from cobrinha.jogo import Jogo

TECLAS_CONTINUAR = (pygame.K_ESCAPE, pygame.K_p)
OPACIDADE_VEU = 170


class EstadoPausa(Estado):
    def __init__(self, jogo: Jogo, jogando: EstadoDePartida) -> None:
        super().__init__(jogo)
        self.jogando = jogando
        self.veu = criar_veu(OPACIDADE_VEU)
        self.menu = Menu(
            [
                ItemMenu("CONTINUAR", acao=self._continuar),
                ItemMenu("REINICIAR", acao=self._reiniciar),
                ItemMenu("MENU PRINCIPAL", acao=self._ir_para_menu),
                ItemMenu("SAIR DO JOGO", acao=self._sair),
            ],
            tocar=jogo.audio.tocar,
        )
        jogo.audio.tocar(Som.PAUSA)
        jogo.audio.pausar_musica()

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key in TECLAS_CONTINUAR:
            self._continuar()
        else:
            self.menu.tratar_evento(evento)

    def _deixar_pausa(self) -> None:
        self.jogo.audio.retomar_musica()

    def _continuar(self) -> None:
        self._deixar_pausa()
        navegacao.retomar(self.jogo, self.jogando)

    def _reiniciar(self) -> None:
        self._deixar_pausa()
        self.jogando.reiniciar()

    def _ir_para_menu(self) -> None:
        self._deixar_pausa()
        self.jogando.abandonar()

    def _sair(self) -> None:
        self.jogando.antes_de_sair_do_jogo()
        self.jogo.sair()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(
            superficie,
            [("PAUSADO", TamanhoFonte.ENORME, Paleta.BRANCO)],
            ALTURA_JANELA // 2 - 170,
        )
        self.menu.desenhar(superficie, topo=y + 20)
        desenhar_linhas(
            superficie,
            [("ESC ou P: continuar    M: som", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO)],
            ALTURA_JANELA - 50,
        )
