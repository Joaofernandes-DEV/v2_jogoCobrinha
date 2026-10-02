"""Tela de recordes (J6): top 5 de cada modo de jogo, salvo entre sessões."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, TAMANHO_RANKING, Paleta, TamanhoFonte
from cobrinha.dominio.partida import Modo
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.menu import (
    BOTAO_ESQUERDO,
    TECLAS_CONFIRMAR,
    TECLAS_DIREITA,
    TECLAS_ESQUERDA,
)
from cobrinha.ui.painel import Linha, criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 200
TECLAS_VOLTAR = (*TECLAS_CONFIRMAR, pygame.K_ESCAPE)
CORES_PODIO = (Paleta.AMARELO, Paleta.CINZA_CLARO, Paleta.LARANJA)


class EstadoRecordes(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.veu = criar_veu(OPACIDADE_VEU)
        # Começa mostrando o modo escolhido no menu.
        self.modo = jogo.opcoes.modo_de_jogo

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN:
            if evento.key in (*TECLAS_ESQUERDA, *TECLAS_DIREITA):
                self._trocar_modo()
            elif evento.key in TECLAS_VOLTAR:
                navegacao.abrir_menu(self.jogo)
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == BOTAO_ESQUERDO:
            navegacao.abrir_menu(self.jogo)

    def _trocar_modo(self) -> None:
        modos = list(Modo)
        self.modo = modos[(modos.index(self.modo) + 1) % len(modos)]

    def linhas_do_ranking(self) -> list[Linha]:
        ranking = self.jogo.progresso.ranking(self.modo.name)
        if not ranking:
            return [("Nenhum recorde ainda. Bora jogar!", TamanhoFonte.PEQUENO, Paleta.BRANCO)]
        linhas: list[Linha] = []
        for posicao, recorde in enumerate(ranking, start=1):
            cor = CORES_PODIO[posicao - 1] if posicao <= len(CORES_PODIO) else Paleta.BRANCO
            dia, mes, ano = recorde.data[8:10], recorde.data[5:7], recorde.data[:4]
            linhas.append(
                (
                    f"{posicao}º   {recorde.pontos:04d} pts   nível {recorde.nivel}"
                    f"   {dia}/{mes}/{ano}",
                    TamanhoFonte.MEDIO,
                    cor,
                )
            )
        return linhas

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.fundo_campo, (0, 0))
        superficie.blit(self.fundo_campo, (0, self.fundo_campo.get_height()))
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(
            superficie,
            [
                ("RECORDES", TamanhoFonte.TITULO, Paleta.VERDE_CLARO),
                (f"<  {self.modo.value.upper()}  >", TamanhoFonte.MEDIO, Paleta.AZUL_CLARO),
            ],
            40,
            espaco=12,
        )
        desenhar_linhas(superficie, self.linhas_do_ranking(), y + 20, espaco=14)
        desenhar_linhas(
            superficie,
            [
                (
                    f"Top {TAMANHO_RANKING} de cada modo   SETAS: trocar modo   ENTER/ESC: voltar",
                    TamanhoFonte.MINIMO,
                    Paleta.CINZA_CLARO,
                )
            ],
            ALTURA_JANELA - 40,
        )
