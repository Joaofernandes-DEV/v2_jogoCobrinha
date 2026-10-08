"""Telas do Duelo: menu, contagem, controles separados, eliminação, fim, pausa e HUD."""

import random

import pygame
from auxiliares import descer_ate, desenhar_tudo, encerrar, enviar

from cobrinha.audio import Som
from cobrinha.config import PELES
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.duelo import PartidaDuelo
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.duelo import EstadoDuelo
from cobrinha.estados.fim_do_duelo import EstadoFimDoDuelo
from cobrinha.estados.jogando import DURACAO_MORTE, EstadoJogando
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.pausa import EstadoPausa
from cobrinha.estados.quem_joga import EstadoQuemJoga

P = Posicao


def duelo_em_andamento(jogo, nivel: int = 1) -> EstadoDuelo:
    """Começa um duelo e pula a contagem."""
    navegacao.iniciar_duelo(jogo, nivel)
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoDuelo)
    return jogo.estado_atual


def com_cobras(duelo: EstadoDuelo, *cobras: Cobra) -> PartidaDuelo:
    """Troca a partida por uma com cobras em posições conhecidas e maçãs longe."""
    duelo.partida = PartidaDuelo(
        cobras=cobras, nivel=duelo.partida.nivel, comidas=[P(0, 21)], rng=random.Random(0)
    )
    return duelo.partida


def j1_bate_na_parede(duelo: EstadoDuelo) -> PartidaDuelo:
    return com_cobras(
        duelo,
        Cobra.nova(P(31, 5), Direcao.DIREITA, 3),
        Cobra.nova(P(10, 15), Direcao.ESQUERDA, 3),
    )


def um_passo(duelo: EstadoDuelo) -> None:
    duelo.atualizar(duelo.partida.intervalo_passo)


# --- Menu e contagem ---


def test_menu_duelo_abre_quem_joga_e_depois_a_contagem_com_os_controles(jogo):
    navegacao.abrir_menu(jogo)
    desenhar_tudo(jogo)
    descer_ate(jogo, "DUELO")
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoQuemJoga)
    enviar(jogo, pygame.K_d, pygame.K_UP, pygame.K_RETURN)  # WASD entra, setas entram, Enter
    contagem = jogo.estado_atual
    assert isinstance(contagem, EstadoContagem)
    assert contagem.titulo == "DUELO"
    assert contagem.subtitulo == "Campo aberto"
    assert contagem.dica == "J1: WASD   J2: SETAS"
    duelo = jogo.pilha[0]
    assert isinstance(duelo, EstadoDuelo)
    assert len(duelo.partida.jogadores) == 2
    desenhar_tudo(jogo)


def test_duelo_usa_o_mapa_do_nivel_escolhido(jogo):
    jogo.progresso.liberar_nivel(3)
    navegacao.abrir_menu(jogo)
    descer_ate(jogo, "NÍVEL")
    enviar(jogo, pygame.K_LEFT)  # circula para o nível 3
    descer_ate(jogo, "DUELO")
    enviar(jogo, pygame.K_RETURN, pygame.K_w, pygame.K_LEFT, pygame.K_RETURN)
    assert jogo.pilha[0].partida.nivel.numero == 3
    assert jogo.pilha[0].partida.obstaculos


# --- Controles ---


def test_wasd_move_so_o_jogador_1_e_setas_so_o_jogador_2(jogo):
    duelo = duelo_em_andamento(jogo)
    j1, j2 = (jogador.cobra for jogador in duelo.partida.jogadores)
    enviar(jogo, pygame.K_w)
    assert j1.tem_comandos_pendentes and not j2.tem_comandos_pendentes
    enviar(jogo, pygame.K_DOWN)
    assert j2.tem_comandos_pendentes
    um_passo(duelo)
    assert j1.direcao is Direcao.CIMA
    assert j2.direcao is Direcao.BAIXO


def test_setas_nao_movem_o_jogador_1(jogo):
    duelo = duelo_em_andamento(jogo)
    enviar(jogo, pygame.K_UP, pygame.K_LEFT, pygame.K_DOWN)
    assert not duelo.partida.jogadores[0].cobra.tem_comandos_pendentes


def test_esc_e_p_pausam_o_duelo(jogo):
    for tecla in (pygame.K_ESCAPE, pygame.K_p):
        duelo_em_andamento(jogo)
        enviar(jogo, tecla)
        assert isinstance(jogo.estado_atual, EstadoPausa)
        desenhar_tudo(jogo)


def test_perder_o_foco_pausa_o_duelo(jogo):
    duelo_em_andamento(jogo)
    jogo.estado_atual.tratar_evento(pygame.Event(pygame.WINDOWFOCUSLOST))
    assert isinstance(jogo.estado_atual, EstadoPausa)


# --- Pausa ---


def test_continuar_volta_ao_duelo_com_contagem(jogo):
    duelo = duelo_em_andamento(jogo)
    enviar(jogo, pygame.K_p, pygame.K_RETURN)  # CONTINUAR
    assert isinstance(jogo.estado_atual, EstadoContagem)
    assert jogo.pilha[0] is duelo


def test_reiniciar_na_pausa_comeca_outro_duelo_no_mesmo_mapa(jogo):
    jogo.progresso.liberar_nivel(2)
    duelo = duelo_em_andamento(jogo, nivel=2)
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_RETURN)  # REINICIAR
    novo = jogo.pilha[0]
    assert isinstance(novo, EstadoDuelo) and novo is not duelo
    assert novo.partida.nivel.numero == 2
    assert isinstance(jogo.estado_atual, EstadoContagem)


def test_menu_principal_na_pausa_volta_sem_gravar_recorde(jogo):
    duelo = duelo_em_andamento(jogo)
    duelo.partida.jogadores[0].pontos = 7
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_DOWN, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)
    assert jogo.progresso.rankings == {}


def test_sair_na_pausa_encerra_o_jogo(jogo):
    duelo_em_andamento(jogo)
    jogo.rodando = True
    enviar(jogo, pygame.K_p, *[pygame.K_DOWN] * 3, pygame.K_RETURN)
    assert not jogo.rodando
    assert jogo.progresso.rankings == {}


# --- Eliminação e fim ---


def test_eliminado_pisca_e_depois_some_enquanto_o_outro_vence(jogo):
    duelo = duelo_em_andamento(jogo)
    j1_bate_na_parede(duelo)
    um_passo(duelo)
    assert not duelo.partida.jogadores[0].vivo
    assert duelo.partida.vencedor == 1
    assert duelo.cobra_visivel(1)
    visibilidade = set()
    for _ in range(8):
        visibilidade.add(duelo.cobra_visivel(0))
        desenhar_tudo(jogo)
        duelo.piscando[0] -= DURACAO_MORTE / 10
    assert visibilidade == {True, False}  # piscou
    del duelo.piscando[0]
    assert not duelo.cobra_visivel(0)  # sumiu do campo


def test_vitoria_abre_o_fim_com_o_vencedor_e_os_pontos(jogo):
    duelo = duelo_em_andamento(jogo)
    j1_bate_na_parede(duelo).jogadores[1].pontos = 4
    um_passo(duelo)
    assert jogo.estado_atual is duelo  # animação antes da tela de fim
    encerrar(duelo)
    fim = jogo.estado_atual
    assert isinstance(fim, EstadoFimDoDuelo)
    assert fim.vencedor == 1 and not fim.empate
    assert fim.pontos == [0, 4]
    desenhar_tudo(jogo)
    assert jogo.progresso.rankings == {}  # duelo não entra nos recordes


def test_empate_abre_o_fim_sem_vencedor(jogo):
    duelo = duelo_em_andamento(jogo)
    com_cobras(
        duelo,
        Cobra.nova(P(9, 5), Direcao.DIREITA, 3),
        Cobra.nova(P(11, 5), Direcao.ESQUERDA, 3),
    )
    um_passo(duelo)
    assert duelo.partida.empate
    encerrar(duelo)
    fim = jogo.estado_atual
    assert isinstance(fim, EstadoFimDoDuelo)
    assert fim.empate
    desenhar_tudo(jogo)


def test_teclas_sao_ignoradas_durante_a_animacao_de_fim(jogo):
    duelo = duelo_em_andamento(jogo)
    j1_bate_na_parede(duelo)
    um_passo(duelo)
    enviar(jogo, pygame.K_ESCAPE)
    assert jogo.estado_atual is duelo


def test_jogar_de_novo_recomeca_o_duelo_no_mesmo_mapa(jogo):
    jogo.progresso.liberar_nivel(2)
    duelo = duelo_em_andamento(jogo, nivel=2)
    j1_bate_na_parede(duelo)
    um_passo(duelo)
    encerrar(duelo)
    enviar(jogo, pygame.K_RETURN)  # JOGAR DE NOVO
    novo = jogo.pilha[0]
    assert isinstance(novo, EstadoDuelo) and novo is not duelo
    assert novo.partida.em_andamento
    assert novo.partida.nivel.numero == 2


def test_esc_e_menu_no_fim_voltam_ao_menu(jogo):
    for teclas in ((pygame.K_ESCAPE,), (pygame.K_DOWN, pygame.K_RETURN)):
        duelo = duelo_em_andamento(jogo)
        j1_bate_na_parede(duelo)
        um_passo(duelo)
        encerrar(duelo)
        enviar(jogo, *teclas)
        assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_sons_da_eliminacao_e_da_vitoria_e_a_musica_para(jogo, monkeypatch):
    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    duelo = duelo_em_andamento(jogo)
    tocados.clear()
    j1_bate_na_parede(duelo)
    um_passo(duelo)
    assert tocados == [Som.BATER, Som.VITORIA]
    assert jogo.audio.musica_atual is None


def test_comer_toca_som_e_mostra_pontos_na_cor_de_quem_comeu(jogo, monkeypatch):
    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    duelo = duelo_em_andamento(jogo)
    tocados.clear()
    partida = com_cobras(
        duelo,
        Cobra.nova(P(5, 5), Direcao.DIREITA, 3),
        Cobra.nova(P(20, 15), Direcao.ESQUERDA, 3),
    )
    partida.comidas = [P(19, 15)]
    um_passo(duelo)
    assert tocados == [Som.COMER]
    assert partida.jogadores[1].pontos == 1
    assert [efeito.cor for efeito in duelo.efeitos.textos] == [PELES[1].destaque]


# --- HUD e 1 jogador ---


def test_hud_do_duelo_desenha_vivos_eliminados_e_mudo(jogo):
    duelo = duelo_em_andamento(jogo)
    j1_bate_na_parede(duelo)
    um_passo(duelo)
    jogo.audio.alternar_mudo()
    superficie = pygame.Surface(jogo.tela.get_size())
    duelo.desenhar(superficie)


def test_nos_modos_de_1_jogador_setas_e_wasd_continuam_movendo_a_mesma_cobra(jogo):
    navegacao.iniciar_campanha(jogo, 1)
    enviar(jogo, pygame.K_RETURN)
    jogando = jogo.estado_atual
    assert isinstance(jogando, EstadoJogando)
    enviar(jogo, pygame.K_w)
    assert jogando.partida.cobra.tem_comandos_pendentes
    jogando.partida.passo()
    enviar(jogo, pygame.K_LEFT)
    jogando.partida.passo()
    assert jogando.partida.cobra.direcao is Direcao.ESQUERDA
