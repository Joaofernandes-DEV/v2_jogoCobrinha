"""Tela de fim de partida (derrota ou vitória), por cima do campo congelado."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.dominio.partida import Situacao
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 170


class EstadoFimDePartida(Estado):
    def __init__(self, jogo: Jogo, jogando: EstadoJogando) -> None:
        super().__init__(jogo)
        self.nivel_inicial = jogando.nivel_inicial
        self.vitoria = jogando.partida.situacao is Situacao.VITORIA
        self.pontos = jogando.partida.pontos
        # Colocação no ranking do modo (1 = novo recorde; None = fora do top 5).
        self.colocacao = navegacao.registrar_resultado(jogo, jogando.partida)
        self.veu = criar_veu(OPACIDADE_VEU)
        self.menu = Menu(
            [
                ItemMenu("JOGAR DE NOVO", acao=self._jogar_de_novo),
                ItemMenu("MENU PRINCIPAL", acao=lambda: navegacao.abrir_menu(jogo)),
                ItemMenu("SAIR DO JOGO", acao=jogo.sair),
            ],
            tocar=jogo.audio.tocar,
        )

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            navegacao.abrir_menu(self.jogo)
        else:
            self.menu.tratar_evento(evento)

    @property
    def novo_recorde(self) -> bool:
        return self.colocacao == 1

    def _jogar_de_novo(self) -> None:
        navegacao.iniciar_campanha(self.jogo, self.nivel_inicial)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        if self.vitoria:
            linhas = [("VOCÊ VENCEU!", TamanhoFonte.TITULO, Paleta.AMARELO)]
        else:
            linhas = [("FIM DE JOGO", TamanhoFonte.TITULO, Paleta.VERMELHO)]
        linhas.append((f"PONTOS {self.pontos}", TamanhoFonte.MEDIO, Paleta.BRANCO))
        if self.novo_recorde:
            linhas.append(("NOVO RECORDE!", TamanhoFonte.MEDIO, Paleta.AMARELO))
        elif self.colocacao is not None:
            linhas.append(
                (f"TOP 5: {self.colocacao}º LUGAR", TamanhoFonte.MEDIO, Paleta.AZUL_CLARO)
            )
        y = desenhar_linhas(superficie, linhas, ALTURA_JANELA // 2 - 170, espaco=24)
        self.menu.desenhar(superficie, topo=y + 20)
