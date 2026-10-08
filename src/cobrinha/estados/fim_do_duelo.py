"""Fim do Duelo: quem venceu (ou empate) e os pontos de cada um, por cima do campo congelado."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.estados.duelo import nome_do_jogador, pele_do_jogador
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import Linha, criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.duelo import EstadoDuelo
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 170


class EstadoFimDoDuelo(Estado):
    def __init__(self, jogo: Jogo, duelo: EstadoDuelo) -> None:
        super().__init__(jogo)
        partida = duelo.partida
        self.numero_nivel = duelo.numero_nivel
        self.vencedor = partida.vencedor  # None = empate
        self.pontos = [jogador.pontos for jogador in partida.jogadores]
        self.veu = criar_veu(OPACIDADE_VEU)
        self.menu = Menu(
            [
                ItemMenu("JOGAR DE NOVO", acao=self._jogar_de_novo),
                ItemMenu("MENU PRINCIPAL", acao=lambda: navegacao.abrir_menu(jogo)),
                ItemMenu("SAIR DO JOGO", acao=jogo.sair),
            ],
            tocar=jogo.audio.tocar,
        )

    @property
    def empate(self) -> bool:
        return self.vencedor is None

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            navegacao.abrir_menu(self.jogo)
        else:
            self.menu.tratar_evento(evento)

    def _jogar_de_novo(self) -> None:
        navegacao.iniciar_duelo(self.jogo, self.numero_nivel)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        linhas: list[Linha]
        if self.vencedor is None:
            linhas = [
                ("EMPATE!", TamanhoFonte.TITULO, Paleta.BRANCO),
                ("todos bateram ao mesmo tempo", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO),
            ]
        else:
            pele = pele_do_jogador(self.vencedor)
            linhas = [
                (f"{nome_do_jogador(self.vencedor)} VENCEU!", TamanhoFonte.TITULO, pele.destaque),
                (f"cobra {pele.nome.lower()}", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO),
            ]
        for indice, pontos in enumerate(self.pontos):
            cor = pele_do_jogador(indice).destaque
            rotulo = "PONTO" if pontos == 1 else "PONTOS"
            linhas.append(
                (f"{nome_do_jogador(indice)}   {pontos} {rotulo}", TamanhoFonte.MEDIO, cor)
            )
        y = desenhar_linhas(superficie, linhas, ALTURA_JANELA // 2 - 190, espaco=14)
        self.menu.desenhar(superficie, topo=y + 20)
