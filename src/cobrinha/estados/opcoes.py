"""Tela de opções (I9): volumes, tela cheia e efeitos visuais. Tudo é salvo ao sair."""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 200


def _porcentagem(volume: float) -> str:
    return f"{round(volume * 100):3d}%"


def _sim_nao(valor: bool) -> str:
    return "SIM" if valor else "NÃO"


class EstadoOpcoes(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.veu = criar_veu(OPACIDADE_VEU)
        opcoes = jogo.opcoes
        self.menu = Menu(
            [
                ItemMenu(
                    lambda: f"EFEITOS SONOROS: < {_porcentagem(opcoes.volume_efeitos)} >",
                    ajustar=self._ajustar(opcoes.ajustar_volume_efeitos),
                ),
                ItemMenu(
                    lambda: f"MÚSICA: < {_porcentagem(opcoes.volume_musica)} >",
                    ajustar=self._ajustar(opcoes.ajustar_volume_musica),
                ),
                ItemMenu(
                    lambda: f"TELA CHEIA: < {_sim_nao(opcoes.tela_cheia)} >",
                    acao=self._alternar_tela_cheia,
                    ajustar=lambda _delta: self._alternar_tela_cheia(),
                ),
                ItemMenu(
                    lambda: f"EFEITOS VISUAIS: < {_sim_nao(opcoes.efeitos_visuais)} >",
                    acao=self._alternar_efeitos_visuais,
                    ajustar=lambda _delta: self._alternar_efeitos_visuais(),
                ),
                ItemMenu("VOLTAR", acao=self._voltar),
            ],
            tocar=jogo.audio.tocar,
        )

    def _ajustar(self, ajuste: Callable[[int], None]) -> Callable[[int], None]:
        """Ajusta um volume e aplica na hora (o som do menu já sai no volume novo)."""

        def ajustar(delta: int) -> None:
            ajuste(delta)
            self.jogo.aplicar_opcoes()

        return ajustar

    def _alternar_tela_cheia(self) -> None:
        self.jogo.opcoes.tela_cheia = not self.jogo.opcoes.tela_cheia
        self.jogo.aplicar_opcoes()

    def _alternar_efeitos_visuais(self) -> None:
        self.jogo.opcoes.efeitos_visuais = not self.jogo.opcoes.efeitos_visuais

    def _voltar(self) -> None:
        self.jogo.salvar()
        navegacao.abrir_menu(self.jogo)

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self._voltar()
        else:
            self.menu.tratar_evento(evento)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.fundo_campo, (0, 0))
        superficie.blit(self.fundo_campo, (0, self.fundo_campo.get_height()))
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(
            superficie, [("OPÇÕES", TamanhoFonte.TITULO, Paleta.VERDE_CLARO)], 60, espaco=30
        )
        self.menu.desenhar(superficie, topo=y, espaco=16)
        desenhar_linhas(
            superficie,
            [
                (
                    "Efeitos visuais: textos de pontos e cobra piscando ao bater",
                    TamanhoFonte.MINIMO,
                    Paleta.CINZA_CLARO,
                ),
                (
                    "SETAS: ajustar   ENTER: alternar   ESC: voltar",
                    TamanhoFonte.MINIMO,
                    Paleta.CINZA_CLARO,
                ),
            ],
            ALTURA_JANELA - 70,
            espaco=6,
        )
