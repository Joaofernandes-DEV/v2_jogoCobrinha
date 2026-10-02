import pytest

from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import Direcao, Posicao

P = Posicao


def cobra_para_direita(tamanho: int = 3) -> Cobra:
    return Cobra.nova(P(5, 5), Direcao.DIREITA, tamanho)


def test_nova_cobra_fica_reta_atras_da_cabeca():
    cobra = cobra_para_direita()
    assert list(cobra.segmentos) == [P(5, 5), P(4, 5), P(3, 5)]
    assert cobra.cabeca == P(5, 5)
    assert cobra.cauda == P(3, 5)
    assert len(cobra) == 3


def test_cobra_sabe_quais_celulas_ocupa():
    cobra = cobra_para_direita()
    assert P(4, 5) in cobra
    assert P(6, 5) not in cobra


def test_segmentos_invalidos_sao_recusados():
    with pytest.raises(ValueError):
        Cobra([], Direcao.DIREITA)
    with pytest.raises(ValueError):
        Cobra([P(1, 1), P(1, 1)], Direcao.DIREITA)


def test_avancar_move_cabeca_e_libera_cauda():
    cobra = cobra_para_direita()
    cobra.avancar(P(6, 5))
    assert list(cobra.segmentos) == [P(6, 5), P(5, 5), P(4, 5)]
    assert P(3, 5) not in cobra


def test_crescer_segura_a_cauda_por_um_passo():
    cobra = cobra_para_direita()
    cobra.crescer()
    cobra.avancar(P(6, 5))
    assert len(cobra) == 4
    assert cobra.cauda == P(3, 5)
    cobra.avancar(P(7, 5))
    assert len(cobra) == 4


def test_tamanho_final_conta_o_crescimento_pendente():
    cobra = cobra_para_direita()
    cobra.crescer(2)
    assert len(cobra) == 3
    assert cobra.tamanho_final == 5


def test_virar_ignora_mesma_direcao_e_meia_volta():
    cobra = cobra_para_direita()
    assert not cobra.virar(Direcao.DIREITA)
    assert not cobra.virar(Direcao.ESQUERDA)
    assert cobra.aplicar_proxima_direcao() is Direcao.DIREITA


def test_dois_toques_rapidos_viram_duas_curvas_e_nao_meia_volta():
    """Bug B3 da V1: andando para a →, ↑ e ← no mesmo tick matavam a cobra."""
    cobra = cobra_para_direita()
    assert cobra.virar(Direcao.CIMA)
    assert cobra.virar(Direcao.ESQUERDA)
    assert cobra.aplicar_proxima_direcao() is Direcao.CIMA
    assert cobra.aplicar_proxima_direcao() is Direcao.ESQUERDA


def test_fila_de_direcoes_tem_limite():
    cobra = cobra_para_direita()
    assert cobra.virar(Direcao.CIMA)
    assert cobra.virar(Direcao.ESQUERDA)
    assert not cobra.virar(Direcao.BAIXO)


def test_comando_e_validado_contra_o_ultimo_da_fila():
    cobra = cobra_para_direita()
    assert cobra.virar(Direcao.CIMA)
    # BAIXO seria meia-volta em relação ao CIMA já enfileirado.
    assert not cobra.virar(Direcao.BAIXO)


def test_sem_comandos_mantem_a_direcao():
    cobra = cobra_para_direita()
    assert cobra.aplicar_proxima_direcao() is Direcao.DIREITA


def test_celula_da_cauda_e_segura_quando_nao_esta_crescendo():
    cobra = cobra_para_direita()
    assert not cobra.colidiria(P(3, 5))
    assert cobra.colidiria(P(4, 5))


def test_celula_da_cauda_mata_quando_esta_crescendo():
    cobra = cobra_para_direita()
    cobra.crescer()
    assert cobra.colidiria(P(3, 5))


def test_avancar_para_a_celula_da_cauda_mantem_a_ocupacao():
    # Cobra em "U": a cabeça entra exatamente onde a cauda estava.
    cobra = Cobra([P(1, 0), P(1, 1), P(0, 1), P(0, 0)], Direcao.ESQUERDA)
    cobra.avancar(P(0, 0))
    assert P(0, 0) in cobra
    assert len(cobra) == 4
