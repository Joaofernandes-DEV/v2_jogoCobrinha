"""Tela entre níveis (J3): a progressão não interrompe mais a partida no meio."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta
from cobrinha.dominio.niveis import proximo_nivel
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 170


class EstadoNivelConcluido(Estado):
    def __init__(self, jogo: Jogo, jogando: EstadoJogando) -> None:
        super().__init__(jogo)
        self.jogando = jogando
        partida = jogando.partida
        self.nivel = partida.nivel.numero
        self.pontos = partida.pontos
        seguinte = proximo_nivel(partida.nivel)
        assert seguinte is not None  # o último nível termina em vitória, não aqui
        self.proximo = seguinte
        jogo.progresso.liberar_nivel(seguinte.numero)
        self.veu = criar_veu(OPACIDADE_VEU)
        self.menu = Menu(
            [
                ItemMenu("PRÓXIMO NÍVEL", acao=self._avancar),
                ItemMenu("MENU PRINCIPAL", acao=self._ir_para_menu),
            ]
        )

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._ir_para_menu()
        else:
            self.menu.tratar_evento(evento)

    def _avancar(self) -> None:
        navegacao.avancar_nivel(self.jogo, self.jogando)

    def _ir_para_menu(self) -> None:
        navegacao.abandonar_partida(self.jogo, self.jogando)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(
            superficie,
            [
                (f"NÍVEL {self.nivel} CONCLUÍDO!", 56, Paleta.AMARELO),
                (f"PONTOS {self.pontos}", 36, Paleta.BRANCO),
                (
                    f"Próximo: nível {self.proximo.numero}, mais rápido "
                    f"e com meta de {self.proximo.meta_comidas} comidas",
                    22,
                    Paleta.CINZA_CLARO,
                ),
            ],
            ALTURA_JANELA // 2 - 150,
        )
        self.menu.desenhar(superficie, topo=y + 20)
