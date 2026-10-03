"""Modo contra o tempo: relógio, bônus de segundos, fim por tempo, ranking e telas."""

import random

import pygame
import pytest
from auxiliares import desenhar_tudo, encerrar, enviar, jogo_em_andamento

from cobrinha.audio import Som
from cobrinha.config import (
    TEMPO_INICIAL,
    TEMPO_MAXIMO,
    TEMPO_POR_COMIDA,
    TEMPO_POR_FRUTA_DOURADA,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import Direcao, Grade, Posicao
from cobrinha.dominio.niveis import Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada, Modo, Partida, Situacao
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.fim_de_partida import EstadoFimDePartida
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.recordes import EstadoRecordes
from cobrinha.ui.hud import DadosHud, desenhar_hud

P = Posicao


def partida_com_relogio(**kwargs) -> Partida:
    """Cobra de 3 em (5,5) andando para a direita, comida logo à frente, meta de 2 comidas."""
    kwargs.setdefault("grade", Grade(10, 10))
    kwargs.setdefault("cobra", Cobra.nova(P(5, 5), Direcao.DIREITA, 3))
    kwargs.setdefault("comida", P(6, 5))
    kwargs.setdefault("nivel", Nivel(nome="Teste", numero=1, passos_por_segundo=10, meta_comidas=2))
    kwargs.setdefault("rng", random.Random(0))
    kwargs.setdefault("modo", Modo.CONTRA_O_TEMPO)
    return Partida(**kwargs)


# Regras da partida


def test_so_o_contra_o_tempo_tem_relogio():
    assert partida_com_relogio().tempo_restante == TEMPO_INICIAL
    for modo in (Modo.CLASSICO, Modo.SEM_BORDAS):
        assert partida_com_relogio(modo=modo).tempo_restante is None


def test_relogio_corre_com_o_tempo_da_partida():
    partida = partida_com_relogio(comida=P(0, 9))
    partida.atualizar(0.25)
    assert partida.tempo_restante == pytest.approx(TEMPO_INICIAL - 0.25)


def test_comer_devolve_segundos():
    partida = partida_com_relogio()
    partida.tempo_restante = 20.0
    assert partida.passo() is Evento.COMEU
    assert partida.tempo_restante == pytest.approx(20.0 + TEMPO_POR_COMIDA)


def test_fruta_dourada_devolve_mais_segundos():
    partida = partida_com_relogio(comida=P(0, 9))
    partida.fruta_dourada = FrutaDourada(P(6, 5))
    partida.tempo_restante = 20.0
    assert partida.passo() is Evento.COMEU_DOURADA
    assert partida.tempo_restante == pytest.approx(20.0 + TEMPO_POR_FRUTA_DOURADA)


def test_relogio_tem_teto():
    partida = partida_com_relogio()
    partida.tempo_restante = TEMPO_MAXIMO - 1
    partida.passo()
    assert partida.tempo_restante == TEMPO_MAXIMO


def test_acabar_o_tempo_encerra_a_partida():
    partida = partida_com_relogio(comida=P(0, 9))
    partida.tempo_restante = 0.05
    eventos = partida.atualizar(0.1)  # a cobra ainda dá um passo antes do relógio zerar
    assert eventos == [Evento.MOVEU, Evento.TEMPO_ESGOTADO]
    assert partida.situacao is Situacao.TEMPO_ESGOTADO
    assert not partida.em_andamento
    assert partida.tempo_restante == 0
    assert partida.comida is None
    assert partida.atualizar(1.0) == []  # nada mais acontece depois do fim


def test_acabar_o_tempo_tira_o_power_up_do_campo():
    partida = partida_com_relogio(comida=P(0, 9))
    partida.power_up = PowerUpNoCampo(TipoPowerUp.ENCOLHER, P(0, 0))
    partida.tempo_restante = 0.01
    partida.atualizar(0.05)
    assert partida.situacao is Situacao.TEMPO_ESGOTADO
    assert partida.power_up is None


def test_power_ups_valem_no_contra_o_tempo():
    """Pontos em dobro dobra os pontos, mas não os segundos ganhos."""
    partida = partida_com_relogio()
    partida.efeitos_ativos[TipoPowerUp.PONTOS_EM_DOBRO] = 5.0
    partida.tempo_restante = 20.0
    assert partida.passo() is Evento.COMEU
    assert partida.pontos == 2
    assert partida.tempo_restante == pytest.approx(20.0 + TEMPO_POR_COMIDA)


def test_relogio_nao_anda_mais_que_a_cobra_depois_de_um_travamento():
    partida = partida_com_relogio(comida=P(0, 9))
    partida.atualizar(30.0)  # janela arrastada por 30 s
    assert partida.em_andamento
    assert partida.tempo_restante > TEMPO_INICIAL - 1


def test_nao_ha_meta_de_comidas_no_contra_o_tempo():
    """Comer além da meta do nível não conclui o nível: a corrida continua."""
    partida = partida_com_relogio()
    for _ in range(3):
        partida.comida = partida.cobra.cabeca.vizinha(Direcao.DIREITA)
        assert partida.passo() is Evento.COMEU
    assert partida.comidas_no_nivel == 3 > partida.nivel.meta_comidas
    assert partida.em_andamento
    assert not partida.tem_meta


def test_nos_outros_modos_a_meta_continua_valendo():
    partida = partida_com_relogio(modo=Modo.CLASSICO)
    partida.passo()
    partida.comida = partida.cobra.cabeca.vizinha(Direcao.DIREITA)
    assert partida.passo() is Evento.CONCLUIU_NIVEL
    assert partida.situacao is Situacao.NIVEL_CONCLUIDO


def test_bater_continua_encerrando_a_partida():
    partida = partida_com_relogio(cobra=Cobra.nova(P(9, 5), Direcao.DIREITA, 3))
    assert partida.passo() is Evento.BATEU
    assert partida.situacao is Situacao.DERROTA


# HUD


def test_hud_desenha_o_relogio_normal_e_em_alerta(jogo):
    superficie = pygame.Surface(jogo.tela.get_size())
    base = dict(pontos=3, recorde=10, nivel=1, comidas=3, meta=10)
    desenhar_hud(superficie, DadosHud(**base, tempo=42.3))
    desenhar_hud(superficie, DadosHud(**base, tempo=0.2))
    desenhar_hud(superficie, DadosHud(**base))  # sem relógio: barra de progresso


# Telas


def escolher_contra_o_tempo(jogo) -> None:
    navegacao.abrir_menu(jogo)
    menu = jogo.estado_atual.menu
    menu.selecionado = next(i for i, item in enumerate(menu.itens) if item.texto.startswith("MODO"))
    enviar(jogo, pygame.K_RIGHT, pygame.K_RIGHT)
    assert jogo.opcoes.modo == "CONTRA_O_TEMPO"


def test_menu_escolhe_o_modo_para_frente_e_para_tras(jogo):
    navegacao.abrir_menu(jogo)
    menu = jogo.estado_atual.menu
    menu.selecionado = next(i for i, item in enumerate(menu.itens) if item.texto.startswith("MODO"))
    enviar(jogo, pygame.K_LEFT)
    assert jogo.opcoes.modo == "CONTRA_O_TEMPO"
    assert "CONTRA O TEMPO" in menu.itens[menu.selecionado].texto
    enviar(jogo, pygame.K_RIGHT)
    assert jogo.opcoes.modo == "CLASSICO"
    desenhar_tudo(jogo)


def test_contagem_explica_as_regras_do_modo(jogo):
    escolher_contra_o_tempo(jogo)
    navegacao.iniciar_campanha(jogo, 1)
    contagem = jogo.estado_atual if isinstance(jogo.estado_atual, EstadoContagem) else None
    assert contagem is not None
    assert contagem.dica and "+3 s" in contagem.dica and "+5 s" in contagem.dica
    desenhar_tudo(jogo)


def test_contagem_dos_outros_modos_nao_tem_dica(jogo):
    navegacao.iniciar_campanha(jogo, 1)
    assert jogo.estado_atual.dica is None


def test_partida_contra_o_tempo_desenha_e_o_relogio_corre(jogo):
    jogo.opcoes.modo = "CONTRA_O_TEMPO"
    jogando = jogo_em_andamento(jogo)
    antes = jogando.partida.tempo_restante
    jogando.atualizar(0.1)
    assert jogando.partida.tempo_restante < antes
    desenhar_tudo(jogo)


def test_comer_mostra_pontos_e_segundos(jogo):
    jogo.opcoes.modo = "CONTRA_O_TEMPO"
    jogando = jogo_em_andamento(jogo)
    assert jogando._texto_do_bonus(1, 3) == "+1  +3s"
    assert jogando._texto_do_bonus(2, 3) == "+2  +3s"  # com pontos em dobro
    jogo.opcoes.modo = "CLASSICO"
    assert jogo_em_andamento(jogo)._texto_do_bonus(1, 3) == "+1"


def test_tempo_esgotado_abre_a_tela_de_fim_e_salva_o_recorde(jogo):
    jogo.opcoes.modo = "CONTRA_O_TEMPO"
    jogando = jogo_em_andamento(jogo)
    jogando.partida.pontos = 17
    jogando.partida.tempo_restante = 0.01
    jogando.atualizar(0.1)
    fim = jogo.estado_atual
    assert isinstance(fim, EstadoFimDePartida)
    assert fim.tempo_esgotado and not fim.vitoria
    assert fim.novo_recorde
    assert jogo.progresso.recorde("CONTRA_O_TEMPO") == 17
    assert jogo.progresso.recorde("CLASSICO") == 0
    desenhar_tudo(jogo)


def test_tempo_esgotado_toca_som_e_para_a_musica(jogo, monkeypatch):
    tocados, paradas = [], []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    monkeypatch.setattr(jogo.audio, "parar_musica", lambda: paradas.append(True))
    jogo.opcoes.modo = "CONTRA_O_TEMPO"
    jogando = jogo_em_andamento(jogo)
    jogando.partida.tempo_restante = 0.01
    jogando.atualizar(0.1)
    assert Som.NIVEL in tocados
    assert paradas


def test_jogar_de_novo_recomeca_com_o_relogio_cheio(jogo):
    jogo.opcoes.modo = "CONTRA_O_TEMPO"
    jogando = jogo_em_andamento(jogo)
    jogando.partida.situacao = Situacao.TEMPO_ESGOTADO
    encerrar(jogando)
    fim = jogo.estado_atual
    fim.menu.selecionado = 0  # JOGAR DE NOVO
    enviar(jogo, pygame.K_RETURN)
    novo = jogo.pilha[0]
    assert novo.partida.modo is Modo.CONTRA_O_TEMPO
    assert novo.partida.tempo_restante == TEMPO_INICIAL


def test_bater_no_contra_o_tempo_abre_a_tela_de_derrota(jogo):
    jogo.opcoes.modo = "CONTRA_O_TEMPO"
    jogando = jogo_em_andamento(jogo)
    jogando.partida.situacao = Situacao.DERROTA
    encerrar(jogando)
    assert isinstance(jogo.estado_atual, EstadoFimDePartida)
    assert not jogo.estado_atual.tempo_esgotado


def test_recordes_circulam_pelos_tres_modos_nos_dois_sentidos(jogo):
    jogo.progresso.registrar_pontuacao("CONTRA_O_TEMPO", 25, 1, "2026-10-02")
    navegacao.abrir_menu(jogo)
    navegacao.abrir_recordes(jogo)
    recordes = jogo.estado_atual
    assert isinstance(recordes, EstadoRecordes)
    assert recordes.modo is Modo.CLASSICO
    enviar(jogo, pygame.K_LEFT)
    assert recordes.modo is Modo.CONTRA_O_TEMPO
    assert "0025" in recordes.linhas_do_ranking()[0][0]
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_RIGHT)
    assert recordes.modo is Modo.CLASSICO
    enviar(jogo, pygame.K_RIGHT, pygame.K_RIGHT)
    assert recordes.modo is Modo.CONTRA_O_TEMPO
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)
