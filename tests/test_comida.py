import random

from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import Grade, Posicao


def test_nunca_sorteia_celula_ocupada():
    grade = Grade(3, 3)
    ocupadas = set(grade.todas) - {Posicao(2, 2)}
    rng = random.Random(0)
    for _ in range(20):
        assert sortear_posicao_livre(grade, ocupadas, rng) == Posicao(2, 2)


def test_campo_cheio_devolve_none_sem_travar():
    """Bug B7 da V1: com o campo cheio, o sorteio entrava em laço infinito."""
    grade = Grade(3, 3)
    assert sortear_posicao_livre(grade, set(grade.todas), random.Random(0)) is None


def test_mesma_semente_gera_mesma_sequencia():
    grade = Grade(10, 10)
    a, b = random.Random(42), random.Random(42)
    sequencia_a = [sortear_posicao_livre(grade, set(), a) for _ in range(10)]
    sequencia_b = [sortear_posicao_livre(grade, set(), b) for _ in range(10)]
    assert sequencia_a == sequencia_b
