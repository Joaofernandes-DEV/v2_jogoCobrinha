"""Pausa (J2): menu por cima do jogo congelado."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo

TECLAS_CONTINUAR = (pygame.K_ESCAPE, pygame.K_p)
OPACIDADE_VEU = 170


class EstadoPausa(Estado):
    def __init__(self, jogo: Jogo, jogando: EstadoJogando) -> None:
        super().__init__(jogo)
        self.jogando = jogando
        self.veu = criar_veu(OPACIDADE_VEU)
        self.menu = Menu(
            [
                ItemMenu("CONTINUAR", acao=self._continuar),
                ItemMenu("REINICIAR", acao=self._reiniciar),
                ItemMenu("MENU PRINCIPAL", acao=self._ir_para_menu),
                ItemMenu("SAIR DO JOGO", acao=self._sair),
            ]
        )

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key in TECLAS_CONTINUAR:
            self._continuar()
        else:
            self.menu.tratar_evento(evento)

    def _continuar(self) -> None:
        navegacao.retomar(self.jogo, self.jogando)

    def _reiniciar(self) -> None:
        self.jogo.progresso.registrar_pontuacao(self.jogando.partida.pontos)
        navegacao.iniciar_campanha(self.jogo, self.jogando.nivel_inicial)

    def _ir_para_menu(self) -> None:
        navegacao.abandonar_partida(self.jogo, self.jogando)

    def _sair(self) -> None:
        self.jogo.progresso.registrar_pontuacao(self.jogando.partida.pontos)
        self.jogo.sair()

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(superficie, [("PAUSADO", 64, Paleta.BRANCO)], ALTURA_JANELA // 2 - 150)
        self.menu.desenhar(superficie, topo=y + 10)
        desenhar_linhas(
            superficie,
            [("ESC ou P: continuar", 22, Paleta.CINZA_CLARO)],
            ALTURA_JANELA - 60,
        )
