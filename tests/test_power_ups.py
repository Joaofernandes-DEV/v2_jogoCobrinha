"""Power-ups da V3: câmera lenta, pontos em dobro e encolher."""

import random

import pytest
from auxiliares import desenhar_tudo, jogo_em_andamento

from cobrinha.audio import Som
from cobrinha.config import (
    DURACAO_CAMERA_LENTA,
    DURACAO_PONTOS_EM_DOBRO,
    DURACAO_POWER_UP_NO_CAMPO,
    FATOR_CAMERA_LENTA,
    PONTOS_FRUTA_DOURADA,
    SEGMENTOS_ENCOLHER,
    TAMANHO_INICIAL_COBRA,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import Direcao, Grade, Posicao
from cobrinha.dominio.niveis import Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada, Partida, Situacao
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp

P = Posicao
D = Direcao


def partida_controlada(**kwargs) -> Partida:
    """Cobra andando para a direita a partir de (5,5), comida longe, 10 passos/s."""
    kwargs.setdefault("grade", Grade(12, 12))
    kwargs.setdefault("cobra", Cobra.nova(P(5, 5), D.DIREITA, 3))
    kwargs.setdefault("comida", P(0, 11))
    kwargs.setdefault(
        "nivel", Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=100)
    )
    kwargs.setdefault("rng", random.Random(0))
    return Partida(**kwargs)


def com_power_up_a_frente(partida: Partida, tipo: TipoPowerUp) -> Partida:
    partida.power_up = PowerUpNoCampo(tipo, partida.cobra.cabeca.vizinha(partida.cobra.direcao))
    return partida


# Cobra.encolher


def test_encolher_tira_segmentos_da_cauda():
    cobra = Cobra.nova(P(8, 5), D.DIREITA, 6)
    assert cobra.encolher(3) == 3
    assert list(cobra.segmentos) == [P(8, 5), P(7, 5), P(6, 5)]
    assert P(5, 5) not in cobra


def test_encolher_respeita_o_tamanho_minimo():
    cobra = Cobra.nova(P(8, 5), D.DIREITA, 4)
    assert cobra.encolher(3, minimo=3) == 1
    assert len(cobra) == 3


def test_encolher_cancela_primeiro_o_crescimento_pendente():
    cobra = Cobra.nova(P(8, 5), D.DIREITA, 5)
    cobra.crescer(2)
    assert cobra.encolher(3) == 3
    assert len(cobra) == 4
    assert cobra.tamanho_final == 4


# Partida


def test_power_up_aparece_numa_celula_livre_ao_comer():
    partida = partida_controlada(comida=P(6, 5))
    partida.rng.random = lambda: 0.0  # as chances sempre acontecem
    partida.passo()
    power_up = partida.power_up
    assert power_up is not None
    assert power_up.posicao not in partida.cobra
    assert power_up.posicao not in (partida.comida, partida.fruta_dourada.posicao)
    assert power_up.tempo_restante == DURACAO_POWER_UP_NO_CAMPO


def test_power_up_nao_aparece_sem_sorte():
    partida = partida_controlada(comida=P(6, 5))
    partida.rng.random = lambda: 0.99
    partida.passo()
    assert partida.power_up is None


def test_power_up_some_do_campo_com_o_tempo():
    partida = partida_controlada()
    partida.power_up = PowerUpNoCampo(TipoPowerUp.ENCOLHER, P(0, 0), tempo_restante=0.05)
    partida.atualizar(0.06)
    assert partida.power_up is None


def test_pegar_power_up_nao_da_pontos_nem_faz_crescer():
    partida = com_power_up_a_frente(partida_controlada(), TipoPowerUp.PONTOS_EM_DOBRO)
    assert partida.passo() is Evento.PEGOU_POWER_UP
    assert partida.power_up is None
    assert partida.pontos == 0
    partida.passo()
    assert len(partida.cobra) == 3


def test_camera_lenta_reduz_a_velocidade_ate_acabar():
    partida = com_power_up_a_frente(partida_controlada(), TipoPowerUp.CAMERA_LENTA)
    normal = partida.passos_por_segundo
    partida.passo()
    assert partida.passos_por_segundo == pytest.approx(normal * FATOR_CAMERA_LENTA)
    assert partida.efeitos_ativos[TipoPowerUp.CAMERA_LENTA] == DURACAO_CAMERA_LENTA
    # O efeito conta tempo de jogo: depois da duração, volta à velocidade normal.
    partida._envelhecer_power_ups(DURACAO_CAMERA_LENTA + 0.01)
    assert TipoPowerUp.CAMERA_LENTA not in partida.efeitos_ativos
    assert partida.passos_por_segundo == pytest.approx(normal)


def test_pontos_em_dobro_vale_para_comida_e_fruta_dourada():
    partida = com_power_up_a_frente(partida_controlada(), TipoPowerUp.PONTOS_EM_DOBRO)
    partida.passo()
    assert partida.efeitos_ativos[TipoPowerUp.PONTOS_EM_DOBRO] == DURACAO_PONTOS_EM_DOBRO
    partida.comida = P(7, 5)
    partida.passo()
    assert partida.pontos == 2
    assert partida.comidas_no_nivel == 1  # a meta continua contando 1 por comida
    partida.fruta_dourada = FrutaDourada(P(8, 5))
    partida.passo()
    assert partida.pontos == 2 + 2 * PONTOS_FRUTA_DOURADA


def test_pegar_de_novo_renova_a_duracao_sem_somar():
    partida = com_power_up_a_frente(partida_controlada(), TipoPowerUp.PONTOS_EM_DOBRO)
    partida.passo()
    partida._envelhecer_power_ups(3.0)
    com_power_up_a_frente(partida, TipoPowerUp.PONTOS_EM_DOBRO)
    partida.passo()
    assert partida.efeitos_ativos[TipoPowerUp.PONTOS_EM_DOBRO] == DURACAO_PONTOS_EM_DOBRO


def test_encolher_tira_segmentos_sem_passar_do_tamanho_inicial():
    cobra = Cobra.nova(P(8, 5), D.DIREITA, TAMANHO_INICIAL_COBRA + SEGMENTOS_ENCOLHER + 2)
    partida = com_power_up_a_frente(partida_controlada(cobra=cobra), TipoPowerUp.ENCOLHER)
    partida.passo()
    assert len(partida.cobra) == TAMANHO_INICIAL_COBRA + 2
    partida.power_up = PowerUpNoCampo(TipoPowerUp.ENCOLHER, P(10, 5))
    partida.passo()
    assert len(partida.cobra) == TAMANHO_INICIAL_COBRA
    assert TipoPowerUp.ENCOLHER not in partida.efeitos_ativos  # efeito instantâneo


def test_concluir_o_nivel_tira_o_power_up_do_campo():
    nivel = Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=1)
    partida = partida_controlada(nivel=nivel, comida=P(6, 5))
    partida.power_up = PowerUpNoCampo(TipoPowerUp.CAMERA_LENTA, P(0, 0))
    assert partida.passo() is Evento.CONCLUIU_NIVEL
    assert partida.situacao is Situacao.NIVEL_CONCLUIDO
    assert partida.power_up is None


def test_efeitos_nao_passam_para_o_proximo_nivel():
    nivel = Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=1)
    partida = partida_controlada(nivel=nivel, comida=P(7, 5))
    com_power_up_a_frente(partida, TipoPowerUp.CAMERA_LENTA)
    partida.passo()
    partida.passo()
    assert partida.situacao is Situacao.NIVEL_CONCLUIDO
    assert partida.proxima_fase().efeitos_ativos == {}


# Tela da partida


def test_pegar_power_up_toca_som_e_mostra_texto(jogo, monkeypatch):
    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    jogando = jogo_em_andamento(jogo)
    partida = com_power_up_a_frente(jogando.partida, TipoPowerUp.CAMERA_LENTA)
    desenhar_tudo(jogo)
    jogando.atualizar(partida.intervalo_passo)
    assert Som.POWER_UP in tocados
    assert [t.conteudo for t in jogando.efeitos.textos] == ["LENTO!"]
    desenhar_tudo(jogo)  # com o véu da câmera lenta e o HUD mostrando o efeito


def test_comida_em_dobro_mostra_mais_dois(jogo):
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    partida.efeitos_ativos[TipoPowerUp.PONTOS_EM_DOBRO] = DURACAO_PONTOS_EM_DOBRO
    partida.comida = partida.cobra.cabeca.vizinha(partida.cobra.direcao)
    jogando.atualizar(partida.intervalo_passo)
    assert [t.conteudo for t in jogando.efeitos.textos] == ["+2"]


@pytest.mark.parametrize("tipo", list(TipoPowerUp))
def test_todos_os_power_ups_sao_desenhados_e_piscam_ao_sumir(jogo, tipo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.power_up = PowerUpNoCampo(tipo, P(0, 0), tempo_restante=0.5)
    for _ in range(4):
        jogando.tempo += 0.07
        desenhar_tudo(jogo)
