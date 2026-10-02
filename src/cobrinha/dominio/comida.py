"""Sorteio da posição da comida."""

import random
from collections.abc import Container

from cobrinha.dominio.grade import Grade, Posicao


def sortear_posicao_livre(
    grade: Grade, ocupadas: Container[Posicao], rng: random.Random
) -> Posicao | None:
    """Sorteia uma célula livre, ou devolve None se o campo estiver cheio.

    Sorteia direto entre as células livres, em vez de tentar ao acaso até acertar.
    Isso evita o laço infinito da V1 com o campo cheio (B7) e não fica mais lento
    quando a cobra é grande (D5).
    """
    livres = [posicao for posicao in grade.todas if posicao not in ocupadas]
    return rng.choice(livres) if livres else None
