"""Fluxo entre as telas: menu, contagem, jogo, pausa, nível concluído e fim de partida."""

import pygame
from auxiliares import desenhar_tudo, encerrar, enviar, jogo_em_andamento

from cobrinha.dominio.partida import Situacao
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import DURACAO_ETAPA, SEQUENCIA, EstadoContagem
from cobrinha.estados.fim_de_partida import EstadoFimDePartida
from cobrinha.estados.jogando import EstadoJogando
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.nivel_concluido import EstadoNivelConcluido
from cobrinha.estados.pausa import EstadoPausa

# Menu principal


def test_menu_jogar_abre_contagem_do_nivel_1(jogo):
    navegacao.abrir_menu(jogo)
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoContagem)
    assert jogo.estado_atual.titulo == "NÍVEL 1"
    assert isinstance(jogo.pilha[0], EstadoJogando)
    assert jogo.pilha[0].partida.nivel.numero == 1


def test_menu_so_oferece_niveis_liberados(jogo):
    navegacao.abrir_menu(jogo)
    menu = jogo.estado_atual
    enviar(jogo, pygame.K_DOWN, pygame.K_RIGHT)
    assert menu.nivel_escolhido == 1  # só o nível 1 está liberado

    jogo.progresso.liberar_nivel(3)
    enviar(jogo, pygame.K_RIGHT, pygame.K_RIGHT)
    assert menu.nivel_escolhido == 3
    enviar(jogo, pygame.K_RIGHT)
    assert menu.nivel_escolhido == 1  # circula
    enviar(jogo, pygame.K_LEFT)
    assert menu.nivel_escolhido == 3

    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_RETURN)
    assert jogo.pilha[0].partida.nivel.numero == 3


# Contagem 3-2-1


def test_contagem_mostra_a_sequencia_e_libera_o_jogo(jogo):
    navegacao.iniciar_campanha(jogo)
    contagem = jogo.estado_atual
    jogando = jogo.pilha[0]
    vistos = []
    for _ in range(len(SEQUENCIA)):
        vistos.append(contagem.etapa_atual)
        desenhar_tudo(jogo)
        contagem.atualizar(DURACAO_ETAPA)
    assert vistos == list(SEQUENCIA)
    assert jogo.estado_atual is jogando


def test_jogo_fica_congelado_durante_a_contagem(jogo):
    navegacao.iniciar_campanha(jogo)
    jogando = jogo.pilha[0]
    cabeca = jogando.partida.cobra.cabeca
    jogo.estado_atual.atualizar(0.5)  # só o topo (a contagem) é atualizado
    assert jogando.partida.cobra.cabeca == cabeca


def test_perder_o_foco_na_contagem_vira_pausa(jogo):
    navegacao.iniciar_campanha(jogo)
    jogo.estado_atual.tratar_evento(pygame.Event(pygame.WINDOWFOCUSLOST))
    assert isinstance(jogo.estado_atual, EstadoPausa)
    assert len(jogo.pilha) == 2


# Jogo e pausa


def test_esc_e_p_pausam(jogo):
    for codigo in (pygame.K_ESCAPE, pygame.K_p):
        jogo_em_andamento(jogo)
        enviar(jogo, codigo)
        assert isinstance(jogo.estado_atual, EstadoPausa)


def test_perder_o_foco_pausa_automaticamente(jogo):
    jogo_em_andamento(jogo)
    jogo.estado_atual.tratar_evento(pygame.Event(pygame.WINDOWFOCUSLOST))
    assert isinstance(jogo.estado_atual, EstadoPausa)


def test_continuar_volta_com_contagem(jogo):
    jogando = jogo_em_andamento(jogo)
    enviar(jogo, pygame.K_ESCAPE)
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_ESCAPE)  # Esc de novo = continuar
    assert isinstance(jogo.estado_atual, EstadoContagem)
    assert jogo.estado_atual.titulo is None
    assert jogo.pilha == [jogando, jogo.estado_atual]


def test_reiniciar_na_pausa_recomeca_do_nivel_inicial(jogo):
    jogando = jogo_em_andamento(jogo, nivel=2)
    jogando.partida.pontos = 4
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_RETURN)
    novo = jogo.pilha[0]
    assert novo is not jogando
    assert (novo.partida.nivel.numero, novo.partida.pontos) == (2, 0)
    assert jogo.progresso.recorde("CLASSICO") == 4


def test_menu_principal_na_pausa_guarda_o_recorde(jogo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.pontos = 6
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_DOWN, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)
    assert jogo.progresso.recorde("CLASSICO") == 6


def test_sair_na_pausa_encerra(jogo):
    jogo_em_andamento(jogo)
    jogo.rodando = True
    enviar(jogo, pygame.K_p, pygame.K_UP, pygame.K_RETURN)
    assert not jogo.rodando


def test_setas_e_wasd_viram_a_cobra(jogo):
    jogando = jogo_em_andamento(jogo)
    enviar(jogo, pygame.K_w)
    assert jogando.partida.cobra.aplicar_proxima_direcao().name == "CIMA"
    enviar(jogo, pygame.K_LEFT)
    assert jogando.partida.cobra.aplicar_proxima_direcao().name == "ESQUERDA"


# Nível concluído (J3)


def test_concluir_nivel_abre_tela_e_libera_o_proximo(jogo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.pontos = 10
    jogando.partida.situacao = Situacao.NIVEL_CONCLUIDO
    encerrar(jogando)
    assert isinstance(jogo.estado_atual, EstadoNivelConcluido)
    assert jogo.progresso.maior_nivel_liberado == 2
    desenhar_tudo(jogo)

    enviar(jogo, pygame.K_RETURN)  # próximo nível
    assert isinstance(jogo.estado_atual, EstadoContagem)
    assert jogo.estado_atual.titulo == "NÍVEL 2"
    proximo = jogo.pilha[0]
    assert (proximo.partida.nivel.numero, proximo.partida.pontos) == (2, 10)
    assert proximo.nivel_inicial == 1


def test_esc_no_nivel_concluido_volta_ao_menu(jogo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.pontos = 10
    jogando.partida.situacao = Situacao.NIVEL_CONCLUIDO
    encerrar(jogando)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)
    assert jogo.progresso.recorde("CLASSICO") == 10


# Fim de partida


def test_derrota_registra_recorde_e_jogar_de_novo_recomeca(jogo):
    jogando = jogo_em_andamento(jogo, nivel=2)
    jogando.partida.pontos = 5
    jogando.partida.situacao = Situacao.DERROTA
    encerrar(jogando)
    fim = jogo.estado_atual
    assert isinstance(fim, EstadoFimDePartida)
    assert fim.novo_recorde and not fim.vitoria
    assert jogo.progresso.recorde("CLASSICO") == 5
    desenhar_tudo(jogo)

    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoContagem)
    assert jogo.pilha[0].partida.nivel.numero == 2
    assert jogo.pilha[0].partida.pontos == 0


def test_vitoria_mostra_tela_de_vitoria(jogo):
    jogando = jogo_em_andamento(jogo, nivel=3)
    jogando.partida.situacao = Situacao.VITORIA
    encerrar(jogando)
    assert jogo.estado_atual.vitoria
    desenhar_tudo(jogo)


def test_fim_de_partida_menu_e_sair(jogo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.situacao = Situacao.DERROTA
    encerrar(jogando)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)

    jogando = jogo_em_andamento(jogo)
    jogando.partida.situacao = Situacao.DERROTA
    encerrar(jogando)
    jogo.rodando = True
    enviar(jogo, pygame.K_UP, pygame.K_RETURN)  # sobe do 1º item para o último: SAIR
    assert not jogo.rodando


# Créditos e sons


def test_creditos_abrem_pelo_menu_e_voltam(jogo):
    from cobrinha.estados.creditos import EstadoCreditos

    navegacao.abrir_menu(jogo)
    enviar(jogo, *[pygame.K_DOWN] * 5, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoCreditos)
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_comer_toca_o_som(jogo, monkeypatch):
    from cobrinha.audio import Som

    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    partida.comida = partida.cobra.cabeca.vizinha(partida.cobra.direcao)
    jogando.atualizar(partida.intervalo_passo)
    assert Som.COMER in tocados


def test_contagem_bipa_a_cada_numero(jogo, monkeypatch):
    from cobrinha.audio import Som

    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    navegacao.iniciar_campanha(jogo)
    contagem = jogo.estado_atual
    for _ in range(len(SEQUENCIA) - 1):
        contagem.atualizar(DURACAO_ETAPA)
    assert tocados == [Som.CONTAGEM] * 3 + [Som.CONTAGEM_JA]


def test_clique_pula_a_contagem(jogo):
    navegacao.iniciar_campanha(jogo)
    jogo.estado_atual.tratar_evento(pygame.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(1, 1)))
    assert isinstance(jogo.estado_atual, EstadoJogando)
