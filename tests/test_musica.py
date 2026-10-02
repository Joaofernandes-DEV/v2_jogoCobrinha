"""Qual música toca em cada momento do jogo."""

import pygame
from auxiliares import desenhar_tudo, encerrar, enviar, jogo_em_andamento

from cobrinha.audio import Musica
from cobrinha.dominio.partida import Situacao
from cobrinha.estados import navegacao


def musica(jogo) -> Musica | None:
    return jogo.audio.musica_atual


def test_menu_toca_a_musica_do_menu(jogo):
    navegacao.abrir_menu(jogo)
    assert musica(jogo) is Musica.MENU


def test_telas_do_menu_mantem_a_musica_do_menu(jogo):
    navegacao.abrir_menu(jogo)
    for abrir in (navegacao.abrir_recordes, navegacao.abrir_opcoes, navegacao.abrir_creditos):
        abrir(jogo)
        assert musica(jogo) is Musica.MENU


def test_musica_muda_quando_o_jogo_comeca(jogo):
    navegacao.abrir_menu(jogo)
    enviar(jogo, pygame.K_RETURN)  # JOGAR
    assert musica(jogo) is Musica.FASE_1


def test_musica_alterna_a_cada_troca_de_fase(jogo):
    jogando = jogo_em_andamento(jogo)
    tocadas = [musica(jogo)]
    for _ in range(2):
        jogando.partida.situacao = Situacao.NIVEL_CONCLUIDO
        encerrar(jogando)
        enviar(jogo, pygame.K_RETURN, pygame.K_RETURN)  # próximo nível e pula a contagem
        jogando = jogo.estado_atual
        tocadas.append(musica(jogo))
    assert tocadas == [Musica.FASE_1, Musica.FASE_2, Musica.FASE_3]


def test_comecar_direto_numa_fase_toca_a_musica_dela(jogo):
    jogo_em_andamento(jogo, nivel=3)
    assert musica(jogo) is Musica.FASE_3


def test_ao_bater_a_musica_para_na_hora_e_so_volta_no_menu(jogo):
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    # Pedra imaginária logo à frente: o próximo passo é uma batida de verdade.
    partida.obstaculos = frozenset({partida.cobra.cabeca.vizinha(partida.cobra.direcao)})
    jogando.atualizar(partida.intervalo_passo)
    assert partida.situacao is Situacao.DERROTA
    assert musica(jogo) is None  # parou já na batida, antes da tela de fim
    assert not pygame.mixer.music.get_busy()

    encerrar(jogando)
    desenhar_tudo(jogo)
    assert musica(jogo) is None  # continua em silêncio na tela de fim

    enviar(jogo, pygame.K_ESCAPE)  # volta ao menu
    assert musica(jogo) is Musica.MENU


def test_jogar_de_novo_depois_de_bater_comeca_a_musica_da_fase(jogo):
    jogando = jogo_em_andamento(jogo, nivel=2)
    jogando.partida.situacao = Situacao.DERROTA
    jogo.audio.parar_musica()
    encerrar(jogando)
    enviar(jogo, pygame.K_RETURN)  # JOGAR DE NOVO
    assert musica(jogo) is Musica.FASE_2


def test_vitoria_tambem_para_a_musica(jogo):
    jogando = jogo_em_andamento(jogo, nivel=3)
    partida = jogando.partida
    partida.comidas_no_nivel = partida.nivel.meta_comidas - 1
    partida.comida = partida.cobra.cabeca.vizinha(partida.cobra.direcao)
    jogando.atualizar(partida.intervalo_passo)
    assert partida.situacao is Situacao.VITORIA
    assert musica(jogo) is None


def test_pausa_pausa_e_retoma_a_mesma_musica(jogo):
    jogo_em_andamento(jogo)
    enviar(jogo, pygame.K_p)
    assert not pygame.mixer.music.get_busy()
    assert musica(jogo) is Musica.FASE_1
    enviar(jogo, pygame.K_p)
    assert pygame.mixer.music.get_busy()
    assert musica(jogo) is Musica.FASE_1


def test_sair_pela_pausa_volta_para_a_musica_do_menu(jogo):
    jogo_em_andamento(jogo, nivel=2)
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_DOWN, pygame.K_RETURN)  # MENU PRINCIPAL
    assert musica(jogo) is Musica.MENU
    assert pygame.mixer.music.get_busy()
