"""Efeitos visuais curtos (I10): textos de pontos que sobem e somem."""

from __future__ import annotations

from dataclasses import dataclass

import pygame

from cobrinha.config import Cor, TamanhoFonte
from cobrinha.ui import texto

DURACAO = 0.8  # segundos
SUBIDA = 30  # pixels percorridos até sumir


@dataclass
class TextoFlutuante:
    conteudo: str
    cor: Cor
    x: int
    y: int
    idade: float = 0.0


class Efeitos:
    def __init__(self) -> None:
        self.textos: list[TextoFlutuante] = []

    def texto_flutuante(self, conteudo: str, cor: Cor, centro: tuple[int, int]) -> None:
        self.textos.append(TextoFlutuante(conteudo, cor, *centro))

    def atualizar(self, dt: float) -> None:
        for efeito in self.textos:
            efeito.idade += dt
        self.textos = [efeito for efeito in self.textos if efeito.idade < DURACAO]

    def desenhar(self, superficie: pygame.Surface) -> None:
        for efeito in self.textos:
            progresso = efeito.idade / DURACAO
            imagem = texto.renderizar(efeito.conteudo, TamanhoFonte.MEDIO, efeito.cor).copy()
            imagem.set_alpha(round(255 * (1 - progresso**2)))
            centro = (efeito.x, round(efeito.y - SUBIDA * progresso))
            superficie.blit(imagem, imagem.get_rect(center=centro))
