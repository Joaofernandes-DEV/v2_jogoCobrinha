"""Tela "Quem joga?": entrar pelo teclado ou pelo controle, sair, começar e luzes."""

import pygame
from auxiliares import botao, conectar_controles, desenhar_tudo, enviar, postar

from cobrinha.config import PELES, Paleta
from cobrinha.entradas import TECLADO_DIREITO, TECLADO_ESQUERDO, Entrada
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.duelo import EstadoDuelo
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.quem_joga import EstadoQuemJoga

X = pygame.CONTROLLER_BUTTON_A  # ✕
BOLA = pygame.CONTROLLER_BUTTON_B  # ◯


def quem_joga(jogo, nivel: int = 1) -> EstadoQuemJoga:
    navegacao.abrir_quem_joga(jogo, nivel)
    assert isinstance(jogo.estado_atual, EstadoQuemJoga)
    return jogo.estado_atual


def test_comeca_sem_ninguem_e_nao_deixa_comecar_sozinho(jogo):
    tela = quem_joga(jogo)
    desenhar_tudo(jogo)
    assert tela.entradas == []
    enviar(jogo, pygame.K_RETURN)
    assert jogo.estado_atual is tela
    enviar(jogo, pygame.K_w, pygame.K_RETURN)
    assert jogo.estado_atual is tela  # 1 jogador ainda não basta
    desenhar_tudo(jogo)


def test_cada_lado_do_teclado_entra_uma_vez_so(jogo):
    tela = quem_joga(jogo)
    enviar(jogo, pygame.K_UP, pygame.K_a, pygame.K_DOWN, pygame.K_s)
    assert tela.entradas == [TECLADO_DIREITO, TECLADO_ESQUERDO]  # ordem de chegada


def test_controles_entram_com_x_e_saem_com_bola(jogo):
    conectar_controles(jogo, 5, 6)
    tela = quem_joga(jogo)
    postar(jogo, botao(X, 5), botao(X, 6))
    assert tela.entradas == [Entrada.controle(5), Entrada.controle(6)]
    postar(jogo, botao(BOLA, 5))
    assert tela.entradas == [Entrada.controle(6)]  # o J2 sobe para J1


def test_bola_de_quem_nao_entrou_volta_ao_menu(jogo):
    conectar_controles(jogo, 5)
    quem_joga(jogo)
    postar(jogo, botao(BOLA, 5))
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_esc_volta_ao_menu(jogo):
    quem_joga(jogo)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_direcional_do_controle_nao_entra_como_teclado(jogo):
    conectar_controles(jogo, 5)
    tela = quem_joga(jogo)
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_DPAD_UP, 5))
    assert tela.entradas == []


def test_no_maximo_4_jogadores(jogo):
    conectar_controles(jogo, 5, 6, 7)
    tela = quem_joga(jogo)
    enviar(jogo, pygame.K_w, pygame.K_UP)
    postar(jogo, botao(X, 5), botao(X, 6), botao(X, 7))
    assert len(tela.entradas) == 4
    assert Entrada.controle(7) not in tela.entradas
    desenhar_tudo(jogo)


def test_enter_comeca_o_duelo_com_a_formacao_e_o_mapa(jogo):
    jogo.progresso.liberar_nivel(2)
    conectar_controles(jogo, 5)
    quem_joga(jogo, nivel=2)
    enviar(jogo, pygame.K_UP)
    postar(jogo, botao(X, 5))
    enviar(jogo, pygame.K_d, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoContagem)
    assert jogo.estado_atual.dica == "J1: SETAS   J2: CONTROLE   J3: WASD"
    duelo = jogo.pilha[0]
    assert isinstance(duelo, EstadoDuelo)
    assert duelo.entradas == [TECLADO_DIREITO, Entrada.controle(5), TECLADO_ESQUERDO]
    assert len(duelo.partida.jogadores) == 3
    assert duelo.numero_nivel == 2


def test_x_de_quem_ja_entrou_comeca(jogo):
    conectar_controles(jogo, 5)
    quem_joga(jogo)
    postar(jogo, botao(X, 5))
    enviar(jogo, pygame.K_w)
    postar(jogo, botao(X, 5))
    assert isinstance(jogo.pilha[0], EstadoDuelo)


def test_controle_que_entra_acende_na_cor_da_vaga(jogo):
    falsos = conectar_controles(jogo, 5, 6)
    tela = quem_joga(jogo)
    enviar(jogo, pygame.K_w)
    postar(jogo, botao(X, 6))
    assert tela.luzes_dos_controles == {6: PELES[1].destaque}
    jogo._atualizar_quadro(0.01)
    assert falsos[6].cores[-1] == PELES[1].destaque
    assert falsos[5].cores[-1] == Paleta.BRANCO  # quem não entrou: branco
