"""Duelo, etapa 3: power-ups disputados, cobra lenta, modos, relógio e placar de rodadas."""

import random

import pytest

from cobrinha.config import (
    PONTOS_FRUTA_DOURADA,
    SEGMENTOS_ENCOLHER,
    TAMANHO_INICIAL_COBRA,
    TEMPO_DUELO_COM_RELOGIO,
    VITORIAS_PARA_VENCER,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.duelo import POWER_UPS_SEM_RELOGIO, EventoDuelo, PartidaDuelo, Placar
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada, Modo
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp

P = Posicao
NIVEL_TESTE = Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=100)
LENTA = TipoPowerUp.CAMERA_LENTA
DOBRO = TipoPowerUp.PONTOS_EM_DOBRO
ENCOLHER = TipoPowerUp.ENCOLHER


def duelo(*cobras: Cobra, **kwargs) -> PartidaDuelo:
    """Duelo numa grade 12 × 12, com as maçãs longe, a 10 passos/s."""
    kwargs.setdefault("grade", Grade(12, 12))
    kwargs.setdefault("comidas", [P(0, 11), P(11, 11)])
    kwargs.setdefault("nivel", NIVEL_TESTE)
    kwargs.setdefault("rng", random.Random(0))
    return PartidaDuelo(cobras=cobras, **kwargs)


def reta(cabeca: Posicao, direcao: Direcao, tamanho: int = 3) -> Cobra:
    return Cobra.nova(cabeca, direcao, tamanho)


def tres_cobras(**kwargs) -> PartidaDuelo:
    """J1 pega o que estiver em (4, 2); J2 e J3 andam longe dele."""
    return duelo(
        reta(P(3, 2), Direcao.DIREITA, 3),
        reta(P(3, 6), Direcao.DIREITA, 6),
        reta(P(3, 9), Direcao.DIREITA, 6),
        **kwargs,
    )


# --- Power-ups disputados ---


def test_camera_lenta_deixa_os_adversarios_lentos_e_quem_pegou_normal():
    partida = tres_cobras()
    partida.power_up = PowerUpNoCampo(LENTA, P(4, 2))
    eventos = partida.passo()
    assert eventos == [EventoDuelo(Evento.PEGOU_POWER_UP, 0, LENTA, (1, 2))]
    j1, j2, j3 = partida.jogadores
    assert not j1.lento and j2.lento and j3.lento
    assert j2.efeitos[LENTA] == LENTA.duracao
    assert partida.power_up is None
    assert j1.pontos == 0 and len(j1.cobra) == 3  # não dá pontos nem faz crescer


def test_pegar_a_camera_lenta_estando_lento_inverte_o_efeito():
    partida = tres_cobras()
    partida.jogadores[0].efeitos[LENTA] = 3.0
    partida.passo()  # passo 1: J1 lento fica parado
    partida.power_up = PowerUpNoCampo(LENTA, P(4, 2))
    partida.passo()  # passo 2: J1 anda e pega
    j1, j2, _ = partida.jogadores
    assert not j1.lento and j2.lento


def test_cobra_lenta_anda_um_passo_sim_um_nao():
    partida = tres_cobras()
    partida.jogadores[1].efeitos[LENTA] = 5.0
    cabecas = []
    for _ in range(4):
        partida.passo()
        cabecas.append(partida.jogadores[1].cobra.cabeca)
    assert cabecas == [P(3, 6), P(4, 6), P(4, 6), P(5, 6)]
    assert partida.jogadores[0].cobra.cabeca == P(7, 2)  # quem não está lento anda sempre


def test_cobra_lenta_guarda_a_curva_ate_andar():
    partida = tres_cobras()
    partida.jogadores[1].efeitos[LENTA] = 5.0
    partida.virar(1, Direcao.CIMA)
    partida.passo()  # parada
    assert partida.jogadores[1].cobra.tem_comandos_pendentes
    partida.passo()
    assert partida.jogadores[1].cobra.cabeca == P(3, 5)


def test_cauda_da_cobra_parada_e_obstaculo():
    # J2, lento e parado, tem a cauda em (5, 6); J1 desce exatamente nela.
    parada = reta(P(5, 4), Direcao.CIMA)
    partida = duelo(reta(P(4, 6), Direcao.DIREITA), parada)
    partida.jogadores[1].efeitos[LENTA] = 5.0
    eventos = partida.passo()
    assert EventoDuelo(Evento.BATEU, 0) in eventos
    assert partida.vencedor == 1


def test_bater_de_frente_em_cobra_parada_elimina_so_quem_andou():
    partida = duelo(reta(P(3, 5), Direcao.DIREITA), reta(P(4, 5), Direcao.ESQUERDA, 1))
    partida.jogadores[1].efeitos[LENTA] = 5.0
    eventos = partida.passo()
    assert {e.jogador for e in eventos if e.evento is Evento.BATEU} == {0}


def test_encolher_corta_a_cauda_dos_adversarios_sem_passar_do_minimo():
    partida = tres_cobras()
    partida.jogadores[2].cobra = reta(P(3, 9), Direcao.DIREITA, 4)
    partida.power_up = PowerUpNoCampo(ENCOLHER, P(4, 2))
    eventos = partida.passo()
    assert eventos == [EventoDuelo(Evento.PEGOU_POWER_UP, 0, ENCOLHER, (1, 2))]
    j1, j2, j3 = partida.jogadores
    assert len(j1.cobra) == 3  # quem pegou não muda
    assert len(j2.cobra) == 6 - SEGMENTOS_ENCOLHER
    assert len(j3.cobra) == TAMANHO_INICIAL_COBRA  # 4 - 3 daria 1: para no mínimo


def test_power_up_nao_atinge_quem_ja_foi_eliminado():
    partida = tres_cobras()
    partida.jogadores[2].vivo = False
    partida.power_up = PowerUpNoCampo(LENTA, P(4, 2))
    (evento,) = partida.passo()
    assert evento.alvos == (1,)
    assert not partida.jogadores[2].lento


def test_pontos_em_dobro_valem_so_para_quem_pegou():
    partida = tres_cobras(modo=Modo.CONTRA_O_TEMPO, comidas=[P(5, 2), P(5, 6)])
    partida.power_up = PowerUpNoCampo(DOBRO, P(4, 2))
    partida.passo()  # J1 pega o x2
    partida.passo()  # J1 come (5, 2) e J2 come (5, 6)
    assert partida.jogadores[0].pontos == 2
    assert partida.jogadores[1].pontos == 1
    partida.fruta_dourada = FrutaDourada(P(6, 2))
    partida.passo()
    assert partida.jogadores[0].pontos == 2 + 2 * PONTOS_FRUTA_DOURADA


def test_efeitos_acabam_com_o_tempo_e_power_up_some_do_campo():
    partida = tres_cobras()
    partida.jogadores[1].efeitos[LENTA] = 0.05
    partida.power_up = PowerUpNoCampo(ENCOLHER, P(0, 0), tempo_restante=0.05)
    partida.atualizar(0.06)
    assert not partida.jogadores[1].lento
    assert partida.power_up is None


@pytest.mark.parametrize("modo", list(Modo))
def test_power_up_sorteado_depende_do_relogio(modo):
    partida = tres_cobras(modo=modo)
    partida.rng.random = lambda: 0.0  # as chances sempre acontecem
    j1 = partida.jogadores[0]
    sorteados = set()
    for semente in range(30):
        partida.rng.choice = random.Random(semente).choice
        partida.power_up = None
        partida.comidas = [j1.cobra.cabeca]  # J1 está comendo uma maçã
        partida._comer_se_houver(j1)
        sorteados.add(partida.power_up.tipo)
    esperado = set(TipoPowerUp) if modo is Modo.CONTRA_O_TEMPO else set(POWER_UPS_SEM_RELOGIO)
    assert sorteados == esperado


# --- Modos ---


def test_sem_bordas_a_cobra_atravessa_e_sai_do_outro_lado():
    partida = duelo(
        reta(P(11, 2), Direcao.DIREITA), reta(P(6, 8), Direcao.ESQUERDA), modo=Modo.SEM_BORDAS
    )
    assert partida.passo() == []
    assert partida.jogadores[0].cobra.cabeca == P(0, 2)


def test_no_classico_a_borda_continua_eliminando():
    partida = duelo(reta(P(11, 2), Direcao.DIREITA), reta(P(6, 8), Direcao.ESQUERDA))
    assert partida.passo()[0] == EventoDuelo(Evento.BATEU, 0)


# --- Relógio (Contra o tempo) ---


def com_relogio(*cobras: Cobra, **kwargs) -> PartidaDuelo:
    return duelo(*cobras, modo=Modo.CONTRA_O_TEMPO, **kwargs)


def test_so_o_contra_o_tempo_tem_relogio_e_ele_nao_ganha_tempo_com_macas():
    partida = com_relogio(
        reta(P(3, 2), Direcao.DIREITA), reta(P(6, 8), Direcao.ESQUERDA), comidas=[P(4, 2)]
    )
    assert partida.tem_relogio and partida.tempo_restante == TEMPO_DUELO_COM_RELOGIO
    partida.passo()
    assert partida.jogadores[0].pontos == 1
    assert partida.tempo_restante == TEMPO_DUELO_COM_RELOGIO
    assert not duelo(reta(P(3, 2), Direcao.DIREITA), reta(P(6, 8), Direcao.ESQUERDA)).tem_relogio


def test_tempo_esgotado_da_a_vitoria_a_quem_tem_mais_pontos():
    partida = com_relogio(reta(P(1, 2), Direcao.DIREITA), reta(P(10, 8), Direcao.ESQUERDA))
    partida.jogadores[1].pontos = 4
    partida.tempo_restante = 0.05
    eventos = partida.atualizar(0.06)
    assert eventos[-2:] == [EventoDuelo(Evento.TEMPO_ESGOTADO), EventoDuelo(Evento.VENCEU, 1)]
    assert partida.encerrada and partida.tempo_esgotado and partida.vencedor == 1


def test_tempo_esgotado_com_pontos_iguais_e_empate():
    partida = com_relogio(reta(P(1, 2), Direcao.DIREITA), reta(P(10, 8), Direcao.ESQUERDA))
    partida.tempo_restante = 0.01
    eventos = partida.atualizar(0.02)
    assert eventos[-1] == EventoDuelo(Evento.EMPATOU)
    assert partida.empate


def test_com_relogio_quem_e_eliminado_sai_mas_os_pontos_valem():
    partida = com_relogio(
        reta(P(11, 2), Direcao.DIREITA),  # bate na borda
        reta(P(6, 8), Direcao.ESQUERDA),
        reta(P(6, 10), Direcao.ESQUERDA),
    )
    partida.jogadores[0].pontos = 9
    partida.passo()
    assert not partida.jogadores[0].vivo
    assert partida.em_andamento  # ainda há 2 vivos e o relógio corre
    partida.tempo_restante = 0.01
    partida.atualizar(0.02)
    assert partida.vencedor == 0  # mesmo fora do campo, tinha mais pontos


def test_ultimo_vivo_na_frente_vence_na_hora():
    partida = com_relogio(reta(P(11, 2), Direcao.DIREITA), reta(P(6, 8), Direcao.ESQUERDA))
    partida.jogadores[1].pontos = 2
    eventos = partida.passo()
    assert eventos[-1] == EventoDuelo(Evento.VENCEU, 1)
    assert not partida.tempo_esgotado


def test_ultimo_vivo_atras_continua_ate_passar_a_frente():
    partida = com_relogio(
        reta(P(11, 2), Direcao.DIREITA),
        reta(P(6, 8), Direcao.ESQUERDA),
        comidas=[P(4, 8), P(0, 0)],
    )
    partida.jogadores[0].pontos = 1
    partida.passo()  # J1 sai; J2 está atrás (0 a 1): a rodada segue
    assert partida.em_andamento
    partida.passo()  # J2 come (4, 8): empata em 1, ainda não passou
    assert partida.em_andamento and partida.jogadores[1].pontos == 1
    partida.jogadores[1].pontos = 2  # passa à frente com a próxima maçã
    partida.comidas = [partida.jogadores[1].cobra.cabeca.vizinha(Direcao.ESQUERDA)]
    eventos = partida.passo()
    assert eventos[-1] == EventoDuelo(Evento.VENCEU, 1)


def test_com_relogio_ninguem_sobra_e_os_pontos_decidem():
    partida = com_relogio(reta(P(3, 5), Direcao.DIREITA), reta(P(5, 5), Direcao.ESQUERDA))
    partida.jogadores[0].pontos = 3
    eventos = partida.passo()
    assert eventos[-1] == EventoDuelo(Evento.VENCEU, 0)


# --- Partidas aleatórias com power-ups e modos ---


@pytest.mark.parametrize("modo", list(Modo))
@pytest.mark.parametrize("quantidade", [2, 4])
def test_duelos_aleatorios_com_power_ups_nunca_quebram_as_regras(modo, quantidade):
    rng = random.Random(quantidade)
    partida = PartidaDuelo(quantidade, nivel=NIVEIS[1], rng=random.Random(3), modo=modo)
    partida.rng.random = lambda: 0.0 if rng.random() < 0.3 else 0.99  # muitos itens
    for _ in range(800):
        if partida.encerrada:
            break
        for jogador in partida.vivos:
            partida.virar(jogador.indice, rng.choice(list(Direcao)))
        partida.atualizar(partida.intervalo_passo)
        ocupadas: list[Posicao] = []
        for jogador in partida.vivos:
            ocupadas.extend(jogador.cobra.segmentos)
            assert len(jogador.cobra) >= 1
        assert len(set(ocupadas)) == len(ocupadas)
        assert not set(ocupadas) & partida.obstaculos
        assert all(GRADE_PADRAO.contem(celula) for celula in ocupadas)
        if partida.power_up is not None:
            assert partida.power_up.posicao not in ocupadas
            if not partida.tem_relogio:
                assert partida.power_up.tipo in POWER_UPS_SEM_RELOGIO


# --- Placar ---


def test_placar_conta_vitorias_ate_o_campeao():
    placar = Placar(3)
    assert placar.vitorias == [0, 0, 0] and placar.rodada == 1
    placar.registrar(1)
    placar.registrar(None)  # empate não conta
    assert placar.vitorias == [0, 1, 0] and placar.campeao is None
    for _ in range(VITORIAS_PARA_VENCER - 1):
        placar.nova_rodada()
        placar.registrar(1)
    assert placar.campeao == 1
    assert placar.rodada == VITORIAS_PARA_VENCER


def test_placar_com_campeao_nao_aceita_mais_rodadas():
    placar = Placar(2, vitorias=[VITORIAS_PARA_VENCER, 0])
    with pytest.raises(RuntimeError):
        placar.nova_rodada()
    with pytest.raises(RuntimeError):
        placar.registrar(1)
