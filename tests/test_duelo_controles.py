"""Duelo com controles: cada controle move a sua cobra, vibra e acende só por ela, e a
partida espera o controle de um jogador que desconectou."""

import random

import pygame
from auxiliares import (
    botao,
    conectar_controles,
    desconectar,
    desenhar_tudo,
    encerrar,
    enviar,
    postar,
)

from cobrinha.config import PELES, Paleta
from cobrinha.controle import Vibracao
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.duelo import PartidaDuelo
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.entradas import TECLADO_DIREITO, TECLADO_ESQUERDO, Entrada
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.controle_desconectado import EstadoControleDesconectado
from cobrinha.estados.duelo import COR_ELIMINADO, COR_FORA_DO_DUELO, EstadoDuelo
from cobrinha.estados.pausa import EstadoPausa

P = Posicao
CIMA = pygame.CONTROLLER_BUTTON_DPAD_UP
X = pygame.CONTROLLER_BUTTON_A
OPTIONS = pygame.CONTROLLER_BUTTON_START


def duelo_com(jogo, *entradas: Entrada) -> EstadoDuelo:
    """Duelo com as entradas pedidas, já sem a contagem."""
    navegacao.iniciar_duelo(jogo, 1, entradas)
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoDuelo)
    return jogo.estado_atual


def com_cobras(duelo: EstadoDuelo, *cobras: Cobra) -> PartidaDuelo:
    duelo.partida = PartidaDuelo(cobras=cobras, comidas=[P(0, 21)], rng=random.Random(0))
    return duelo.partida


def um_passo(duelo: EstadoDuelo) -> None:
    duelo.atualizar(duelo.partida.intervalo_passo)


# --- Comandos ---


def test_cada_controle_move_so_a_propria_cobra(jogo):
    conectar_controles(jogo, 5, 6)
    duelo = duelo_com(jogo, Entrada.controle(5), Entrada.controle(6))
    j1, j2 = (jogador.cobra for jogador in duelo.partida.jogadores)
    postar(jogo, botao(CIMA, 6))
    assert j2.tem_comandos_pendentes and not j1.tem_comandos_pendentes


def test_controle_e_teclado_no_mesmo_duelo_nao_se_misturam(jogo):
    conectar_controles(jogo, 5)
    duelo = duelo_com(jogo, Entrada.controle(5), TECLADO_DIREITO, TECLADO_ESQUERDO)
    j1, j2, j3 = (jogador.cobra for jogador in duelo.partida.jogadores)
    postar(jogo, botao(CIMA, 5))  # direcional do controle: só o J1
    assert j1.tem_comandos_pendentes and not j2.tem_comandos_pendentes
    enviar(jogo, pygame.K_DOWN)  # seta do teclado: só o J2
    assert j2.tem_comandos_pendentes and not j3.tem_comandos_pendentes
    enviar(jogo, pygame.K_s)
    assert j3.tem_comandos_pendentes


def test_controle_de_fora_nao_move_ninguem_mas_pode_pausar(jogo):
    conectar_controles(jogo, 5, 9)
    duelo = duelo_com(jogo, Entrada.controle(5), TECLADO_DIREITO)
    postar(jogo, botao(CIMA, 9))
    assert not any(j.cobra.tem_comandos_pendentes for j in duelo.partida.jogadores)
    postar(jogo, botao(OPTIONS, 9))
    assert isinstance(jogo.estado_atual, EstadoPausa)


def test_duelo_de_4_com_2_controles_e_o_teclado(jogo):
    conectar_controles(jogo, 5, 6)
    entradas = (TECLADO_ESQUERDO, TECLADO_DIREITO, Entrada.controle(5), Entrada.controle(6))
    duelo = duelo_com(jogo, *entradas)
    assert len(duelo.partida.jogadores) == 4
    for _ in range(10):
        duelo.atualizar(1 / 60)
    desenhar_tudo(jogo)


# --- Vibração e luz ---


def test_so_vibra_o_controle_de_quem_comeu(jogo):
    falsos = conectar_controles(jogo, 5, 6)
    duelo = duelo_com(jogo, Entrada.controle(5), Entrada.controle(6))
    partida = com_cobras(
        duelo,
        Cobra.nova(P(5, 5), Direcao.DIREITA, 3),
        Cobra.nova(P(20, 15), Direcao.ESQUERDA, 3),
    )
    partida.comidas = [P(19, 15)]
    um_passo(duelo)
    assert falsos[5].vibracoes == []
    assert falsos[6].vibracoes == [Vibracao.FRACA.value]


def test_eliminado_vibra_forte_e_vencedor_vibra_medio(jogo):
    falsos = conectar_controles(jogo, 5, 6)
    duelo = duelo_com(jogo, Entrada.controle(5), Entrada.controle(6))
    com_cobras(
        duelo,
        Cobra.nova(P(31, 5), Direcao.DIREITA, 3),
        Cobra.nova(P(10, 15), Direcao.ESQUERDA, 3),
    )
    um_passo(duelo)
    assert falsos[5].vibracoes == [Vibracao.FORTE.value]
    assert falsos[6].vibracoes == [Vibracao.MEDIA.value]


def test_jogador_no_teclado_nao_faz_vibrar_controle_nenhum(jogo):
    falsos = conectar_controles(jogo, 5)
    duelo = duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5))
    com_cobras(
        duelo,
        Cobra.nova(P(31, 5), Direcao.DIREITA, 3),  # J1 (teclado) bate
        Cobra.nova(P(10, 15), Direcao.ESQUERDA, 3),
    )
    um_passo(duelo)
    assert falsos[5].vibracoes == [Vibracao.MEDIA.value]  # só a vitória do J2


def test_luz_de_cada_controle_na_cor_da_cobra_e_cinza_ao_ser_eliminado(jogo):
    falsos = conectar_controles(jogo, 5, 6, 9)
    duelo = duelo_com(jogo, Entrada.controle(5), TECLADO_DIREITO, Entrada.controle(6))
    jogo._atualizar_quadro(0.0)
    assert falsos[5].cores[-1] == PELES[0].destaque
    assert falsos[6].cores[-1] == PELES[2].destaque
    assert falsos[9].cores[-1] == COR_FORA_DO_DUELO == Paleta.BRANCO  # controle de fora
    duelo.partida.jogadores[0].vivo = False
    jogo._atualizar_quadro(0.0)
    assert falsos[5].cores[-1] == COR_ELIMINADO == Paleta.CINZA


def test_luzes_continuam_por_baixo_da_pausa(jogo):
    falsos = conectar_controles(jogo, 5)
    duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5))
    enviar(jogo, pygame.K_p)
    assert isinstance(jogo.estado_atual, EstadoPausa)
    jogo._atualizar_quadro(0.0)
    assert falsos[5].cores[-1] == PELES[1].destaque


# --- Controle desconectado ---


def test_controle_de_um_jogador_desconecta_e_o_duelo_espera(jogo):
    conectar_controles(jogo, 5)
    duelo = duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5))
    postar(jogo, desconectar(5))
    aviso = jogo.estado_atual
    assert isinstance(aviso, EstadoControleDesconectado)
    assert duelo.jogadores_sem_controle == [1]
    desenhar_tudo(jogo)
    cabecas = [j.cobra.cabeca for j in duelo.partida.jogadores]
    jogo._atualizar_quadro(1.0)  # o duelo, por baixo, não anda
    assert [j.cobra.cabeca for j in duelo.partida.jogadores] == cabecas


def test_controle_reconectado_aperta_x_e_volta_a_ser_do_jogador(jogo):
    conectar_controles(jogo, 5, 6)
    duelo = duelo_com(jogo, Entrada.controle(6), Entrada.controle(5))
    postar(jogo, desconectar(5))
    postar(jogo, botao(X, 6))  # o ✕ de quem já joga não rouba a vaga
    assert isinstance(jogo.estado_atual, EstadoControleDesconectado)
    conectar_controles(jogo, 8)  # o SDL dá um id novo ao controle que volta
    postar(jogo, botao(X, 8))
    assert duelo.entradas == [Entrada.controle(6), Entrada.controle(8)]
    assert isinstance(jogo.estado_atual, EstadoContagem)
    enviar(jogo, pygame.K_RETURN)
    assert jogo.estado_atual is duelo
    postar(jogo, botao(CIMA, 8))
    assert duelo.partida.jogadores[1].cobra.tem_comandos_pendentes


def test_esc_no_aviso_abre_a_pausa(jogo):
    conectar_controles(jogo, 5)
    duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5))
    postar(jogo, desconectar(5))
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoPausa)
    enviar(jogo, pygame.K_DOWN, pygame.K_DOWN, pygame.K_RETURN)  # MENU PRINCIPAL
    from cobrinha.estados.menu_principal import EstadoMenuPrincipal

    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_controle_de_fora_desconecta_e_o_duelo_segue(jogo):
    conectar_controles(jogo, 5, 9)
    duelo = duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5))
    postar(jogo, desconectar(9))
    assert jogo.estado_atual is duelo


def test_controle_que_sai_durante_a_pausa_e_pedido_ao_voltar(jogo):
    conectar_controles(jogo, 5)
    duelo = duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5))
    enviar(jogo, pygame.K_p)
    postar(jogo, desconectar(5))
    assert isinstance(jogo.estado_atual, EstadoPausa)
    enviar(jogo, pygame.K_RETURN)  # CONTINUAR → contagem
    enviar(jogo, pygame.K_RETURN)  # pula a contagem
    assert jogo.estado_atual is duelo
    duelo.atualizar(0.01)
    assert isinstance(jogo.estado_atual, EstadoControleDesconectado)


def test_controle_de_quem_ja_foi_eliminado_pode_sair(jogo):
    conectar_controles(jogo, 5, 6)
    duelo = duelo_com(jogo, TECLADO_ESQUERDO, Entrada.controle(5), Entrada.controle(6))
    duelo.partida.jogadores[1].vivo = False
    postar(jogo, desconectar(5))
    assert jogo.estado_atual is duelo


# --- Mesma formação ---


def test_reiniciar_e_jogar_de_novo_mantem_quem_joga_com_o_que(jogo):
    conectar_controles(jogo, 5)
    entradas = [Entrada.controle(5), TECLADO_ESQUERDO]
    duelo_com(jogo, *entradas)
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_RETURN)  # REINICIAR
    assert jogo.pilha[0].entradas == entradas
    enviar(jogo, pygame.K_RETURN)
    duelo = jogo.estado_atual
    com_cobras(
        duelo,
        Cobra.nova(P(31, 5), Direcao.DIREITA, 3),
        Cobra.nova(P(10, 15), Direcao.ESQUERDA, 3),
    )
    um_passo(duelo)
    encerrar(duelo)
    enviar(jogo, pygame.K_RETURN)  # JOGAR DE NOVO
    assert jogo.pilha[0] is not duelo
    assert jogo.pilha[0].entradas == entradas
