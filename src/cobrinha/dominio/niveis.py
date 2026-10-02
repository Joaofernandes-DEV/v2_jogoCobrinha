"""Definição dos níveis como dados (J4): adicionar um nível é acrescentar um bloco aqui.

Os obstáculos são desenhados como mapas de texto, 32 colunas × 22 linhas:
"#" é uma pedra e "." é célula livre. A cobra nasce na linha 11, colunas 6 a 8,
andando para a direita, então essa faixa fica sempre livre.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from cobrinha.config import COLUNAS, LINHAS
from cobrinha.dominio.grade import Posicao


def mapa(*linhas: str) -> frozenset[Posicao]:
    """Converte um mapa de texto nas posições das pedras."""
    if len(linhas) != LINHAS or any(len(linha) != COLUNAS for linha in linhas):
        raise ValueError(f"O mapa precisa ter {LINHAS} linhas de {COLUNAS} caracteres.")
    return frozenset(
        Posicao(coluna, numero_linha)
        for numero_linha, linha in enumerate(linhas)
        for coluna, caractere in enumerate(linha)
        if caractere == "#"
    )


@dataclass(frozen=True)
class Nivel:
    numero: int
    nome: str
    passos_por_segundo: float
    meta_comidas: int  # comidas para concluir o nível
    # Passos/s a mais a cada comida dentro do nível (J9): a tensão cresce aos poucos.
    aceleracao_por_comida: float = 0.15
    obstaculos: frozenset[Posicao] = field(default_factory=frozenset)


PEDRAS_NO_CAMINHO = mapa(
    "................................",
    "................................",
    "................................",
    ".....######..........######.....",
    "................................",
    "................................",
    "................................",
    "...............##...............",
    "...............##...............",
    "................................",
    "................................",
    "................................",
    "................................",
    "...............##...............",
    "...............##...............",
    "................................",
    "................................",
    "................................",
    ".....######..........######.....",
    "................................",
    "................................",
    "................................",
)

LABIRINTO = mapa(
    "................................",
    "................................",
    "..############....############..",
    "..#..........................#..",
    "..#..........................#..",
    "..#.....######....######.....#..",
    "........#..............#........",
    "........#..............#........",
    "........#..............#........",
    "................................",
    "................................",
    "................................",
    "................................",
    "........#..............#........",
    "........#..............#........",
    "........#..............#........",
    "..#.....######....######.....#..",
    "..#..........................#..",
    "..#..........................#..",
    "..############....############..",
    "................................",
    "................................",
)

NIVEIS: tuple[Nivel, ...] = (
    Nivel(numero=1, nome="Campo aberto", passos_por_segundo=8.0, meta_comidas=10),
    Nivel(
        numero=2,
        nome="Pedras no caminho",
        passos_por_segundo=10.0,
        meta_comidas=12,
        obstaculos=PEDRAS_NO_CAMINHO,
    ),
    Nivel(
        numero=3,
        nome="Labirinto",
        passos_por_segundo=12.0,
        meta_comidas=15,
        obstaculos=LABIRINTO,
    ),
)


def obter_nivel(numero: int) -> Nivel:
    if not 1 <= numero <= len(NIVEIS):
        raise ValueError(f"Nível {numero} não existe (1 a {len(NIVEIS)}).")
    return NIVEIS[numero - 1]


def proximo_nivel(nivel: Nivel) -> Nivel | None:
    """Nível seguinte, ou None se `nivel` for o último."""
    return NIVEIS[nivel.numero] if nivel.numero < len(NIVEIS) else None
