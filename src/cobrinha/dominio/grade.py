"""Posições na grade lógica do jogo, medidas em células e não em pixels."""

from typing import NamedTuple

from cobrinha.config import COLUNAS, LINHAS


class Posicao(NamedTuple):
    """Uma célula da grade: (0, 0) é o canto superior esquerdo do campo."""

    coluna: int
    linha: int

    def dentro_da_grade(self) -> bool:
        return 0 <= self.coluna < COLUNAS and 0 <= self.linha < LINHAS


def todas_as_posicoes() -> list[Posicao]:
    """Todas as células do campo, linha por linha."""
    return [Posicao(coluna, linha) for linha in range(LINHAS) for coluna in range(COLUNAS)]
