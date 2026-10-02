"""Grade lógica do jogo: posições e direções medidas em células, nunca em pixels."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import cached_property
from typing import NamedTuple

from cobrinha.config import COLUNAS, LINHAS


class Direcao(Enum):
    """Direções de movimento; o valor é o deslocamento (colunas, linhas)."""

    CIMA = (0, -1)
    BAIXO = (0, 1)
    ESQUERDA = (-1, 0)
    DIREITA = (1, 0)

    @property
    def oposta(self) -> Direcao:
        dx, dy = self.value
        return Direcao((-dx, -dy))


class Posicao(NamedTuple):
    """Uma célula da grade: (0, 0) é o canto superior esquerdo do campo."""

    coluna: int
    linha: int

    def vizinha(self, direcao: Direcao) -> Posicao:
        dx, dy = direcao.value
        return Posicao(self.coluna + dx, self.linha + dy)


@dataclass(frozen=True)
class Grade:
    """Dimensões do campo. Os testes usam grades pequenas; o jogo usa `GRADE_PADRAO`."""

    colunas: int
    linhas: int

    @property
    def total_celulas(self) -> int:
        return self.colunas * self.linhas

    def contem(self, posicao: Posicao) -> bool:
        return 0 <= posicao.coluna < self.colunas and 0 <= posicao.linha < self.linhas

    def envolver(self, posicao: Posicao) -> Posicao:
        """Leva uma posição de fora do campo para o lado oposto (modo sem bordas)."""
        return Posicao(posicao.coluna % self.colunas, posicao.linha % self.linhas)

    @cached_property
    def todas(self) -> tuple[Posicao, ...]:
        """Todas as células, linha por linha (calculado uma vez por grade)."""
        return tuple(
            Posicao(coluna, linha) for linha in range(self.linhas) for coluna in range(self.colunas)
        )


GRADE_PADRAO = Grade(COLUNAS, LINHAS)
