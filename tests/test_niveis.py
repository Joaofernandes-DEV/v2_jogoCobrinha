import pytest

from cobrinha.dominio.niveis import NIVEIS, obter_nivel, proximo_nivel
from cobrinha.dominio.progresso import Progresso


def test_niveis_numerados_em_ordem_e_cada_vez_mais_rapidos():
    assert [nivel.numero for nivel in NIVEIS] == list(range(1, len(NIVEIS) + 1))
    velocidades = [nivel.passos_por_segundo for nivel in NIVEIS]
    assert velocidades == sorted(velocidades)
    assert len(set(velocidades)) == len(velocidades)
    assert all(nivel.meta_comidas > 0 for nivel in NIVEIS)


def test_obter_nivel():
    assert obter_nivel(1) is NIVEIS[0]
    assert obter_nivel(len(NIVEIS)) is NIVEIS[-1]
    for invalido in (0, len(NIVEIS) + 1):
        with pytest.raises(ValueError):
            obter_nivel(invalido)


def test_proximo_nivel():
    assert proximo_nivel(NIVEIS[0]) is NIVEIS[1]
    assert proximo_nivel(NIVEIS[-1]) is None


def test_progresso_registra_apenas_recordes_novos():
    progresso = Progresso()
    assert not progresso.registrar_pontuacao(0)
    assert progresso.registrar_pontuacao(5)
    assert not progresso.registrar_pontuacao(5)
    assert not progresso.registrar_pontuacao(3)
    assert progresso.recorde == 5


def test_progresso_libera_niveis_sem_regredir_nem_passar_do_ultimo():
    progresso = Progresso()
    assert progresso.maior_nivel_liberado == 1
    progresso.liberar_nivel(2)
    progresso.liberar_nivel(1)
    assert progresso.maior_nivel_liberado == 2
    progresso.liberar_nivel(99)
    assert progresso.maior_nivel_liberado == len(NIVEIS)
