"""Fim de uma rodada do Duelo: quem venceu (ou empate), os pontos e o placar de vitórias.

Quando alguém chega a 3 vitórias, a tela anuncia o campeão e "Jogar de novo" começa outra
disputa com os mesmos jogadores; antes disso, "Próxima rodada" continua o placar.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha import recursos
from cobrinha.config import (
    ALTURA_JANELA,
    LARGURA_JANELA,
    VITORIAS_PARA_VENCER,
    Paleta,
    TamanhoFonte,
)
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.estados.duelo import nome_do_jogador, pele_do_jogador
from cobrinha.ui import texto
from cobrinha.ui.hud import desenhar_vitorias
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import Linha, criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.duelo import EstadoDuelo
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 170
LADO_MARCADOR = 18  # quadradinhos das vitórias, maiores que os do HUD
DESLOCAMENTO_PLACAR = 40  # as linhas do placar vão um pouco à esquerda, para caber os quadradinhos


class EstadoFimDoDuelo(Estado):
    def __init__(self, jogo: Jogo, duelo: EstadoDuelo) -> None:
        super().__init__(jogo)
        self.duelo = duelo
        partida = duelo.partida
        self.placar = duelo.placar
        self.numero_nivel = duelo.numero_nivel
        self.entradas = tuple(duelo.entradas)  # jogar de novo com a mesma formação
        self.vencedor = partida.vencedor  # None = empate
        self.campeao = self.placar.campeao
        self.tem_relogio = partida.tem_relogio
        self.tempo_esgotado = partida.tempo_esgotado
        self.pontos = [jogador.pontos for jogador in partida.jogadores]
        self.veu = criar_veu(OPACIDADE_VEU)
        if self.campeao is None:
            continuar = ItemMenu("PRÓXIMA RODADA", acao=self._proxima_rodada)
        else:
            continuar = ItemMenu("JOGAR DE NOVO", acao=self._jogar_de_novo)
        self.menu = Menu(
            [
                continuar,
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

    def _proxima_rodada(self) -> None:
        navegacao.proxima_rodada(self.jogo, self.duelo)

    def _jogar_de_novo(self) -> None:
        """Outra disputa, com o placar zerado e os mesmos jogadores, mapa e modo."""
        navegacao.iniciar_duelo(
            self.jogo, self.numero_nivel, self.entradas, self.duelo.partida.modo
        )

    def _titulo(self) -> list[Linha]:
        rodada = f"rodada {self.placar.rodada}"
        if self.tempo_esgotado:
            rodada += "   tempo esgotado"
        if self.campeao is not None:
            pele = pele_do_jogador(self.campeao)
            return [
                (
                    f"{nome_do_jogador(self.campeao)} É O CAMPEÃO!",
                    TamanhoFonte.TITULO,
                    pele.destaque,
                ),
                (
                    f"{VITORIAS_PARA_VENCER} vitórias   cobra {pele.nome.lower()}",
                    TamanhoFonte.PEQUENO,
                    Paleta.CINZA_CLARO,
                ),
            ]
        if self.vencedor is None:
            motivo = "pontos iguais" if self.tem_relogio else "todos bateram ao mesmo tempo"
            return [
                ("EMPATE!", TamanhoFonte.TITULO, Paleta.BRANCO),
                (f"{rodada}   {motivo}", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO),
            ]
        pele = pele_do_jogador(self.vencedor)
        return [
            (
                f"{nome_do_jogador(self.vencedor)} VENCEU A RODADA!",
                TamanhoFonte.TITULO,
                pele.destaque,
            ),
            (rodada, TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO),
        ]

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(superficie, self._titulo(), ALTURA_JANELA // 2 - 200, espaco=10)
        y += 10
        centro_x = LARGURA_JANELA // 2 - DESLOCAMENTO_PLACAR
        altura_linha = recursos.fonte(TamanhoFonte.MEDIO).get_linesize() + 8
        for indice, pontos in enumerate(self.pontos):
            cor = pele_do_jogador(indice).destaque
            rotulo = "PONTO" if pontos == 1 else "PONTOS"
            area = texto.desenhar_centralizado(
                superficie,
                f"{nome_do_jogador(indice)}   {pontos} {rotulo}",
                TamanhoFonte.MEDIO,
                cor,
                centro_x,
                y,
            )
            vitorias = self.placar.vitorias[indice]
            desenhar_vitorias(
                superficie, vitorias, cor, area.right + 20, area.centery, True, LADO_MARCADOR
            )
            y += altura_linha
        self.menu.desenhar(superficie, topo=y + 16)
