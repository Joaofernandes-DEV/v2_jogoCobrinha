"""Créditos: autores da V1 e da V2 e recursos de terceiros (a licença OFL pede atribuição)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import Paleta, TamanhoFonte
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.menu import BOTAO_ESQUERDO, TECLAS_CONFIRMAR
from cobrinha.ui.painel import Linha, criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 200
TECLAS_VOLTAR = (*TECLAS_CONFIRMAR, pygame.K_ESCAPE)

SECAO = (TamanhoFonte.PEQUENO, Paleta.AMARELO)
NOME = (TamanhoFonte.PEQUENO, Paleta.BRANCO)
DETALHE = (TamanhoFonte.MINIMO, Paleta.CINZA_CLARO)

CONTEUDO: list[Linha] = [
    ("V2", *SECAO),
    ("João Vitor Fernandes", *NOME),
    ("V1 (2025) - Computação Gráfica", *SECAO),
    ("João Vitor Fernandes", *NOME),
    ("João Pedro Sinhorini Silva", *NOME),
    ("Vitor Barssoti de Souza", *NOME),
    ("Alex Barbosa Lourenço", *NOME),
    ("Recursos", *SECAO),
    ("Fonte VT323 - Peter Hull", *NOME),
    ("SIL Open Font License 1.1", *DETALHE),
    ("Sprites e sons gerados por código", *NOME),
    ("Python + pygame-ce", *DETALHE),
]


class EstadoCreditos(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.veu = criar_veu(OPACIDADE_VEU)

    def tratar_evento(self, evento: pygame.Event) -> None:
        if (evento.type == pygame.KEYDOWN and evento.key in TECLAS_VOLTAR) or (
            evento.type == pygame.MOUSEBUTTONDOWN and evento.button == BOTAO_ESQUERDO
        ):
            navegacao.abrir_menu(self.jogo)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.fundo_campo, (0, 0))
        superficie.blit(self.fundo_campo, (0, self.fundo_campo.get_height()))
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(superficie, [("CRÉDITOS", TamanhoFonte.TITULO, Paleta.VERDE_CLARO)], 30)
        y = desenhar_linhas(superficie, CONTEUDO, y + 6, espaco=12)
        desenhar_linhas(
            superficie,
            [("ENTER, ESC ou clique: voltar", TamanhoFonte.MINIMO, Paleta.CINZA_CLARO)],
            y + 10,
        )
