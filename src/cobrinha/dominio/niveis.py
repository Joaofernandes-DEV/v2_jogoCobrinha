"""Definição dos níveis como dados: adicionar um nível é acrescentar uma linha."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Nivel:
    numero: int
    passos_por_segundo: float
    meta_comidas: int  # comidas para concluir o nível


NIVEIS: tuple[Nivel, ...] = (
    Nivel(numero=1, passos_por_segundo=8.0, meta_comidas=10),
    Nivel(numero=2, passos_por_segundo=11.0, meta_comidas=12),
    Nivel(numero=3, passos_por_segundo=14.0, meta_comidas=15),
)


def obter_nivel(numero: int) -> Nivel:
    if not 1 <= numero <= len(NIVEIS):
        raise ValueError(f"Nível {numero} não existe (1 a {len(NIVEIS)}).")
    return NIVEIS[numero - 1]


def proximo_nivel(nivel: Nivel) -> Nivel | None:
    """Nível seguinte, ou None se `nivel` for o último."""
    return NIVEIS[nivel.numero] if nivel.numero < len(NIVEIS) else None
