"""Telas do Duelo, etapa 3: rodadas com placar, campeão, modos do menu e power-ups."""

import random

import pygame
from auxiliares import conectar_controles, desenhar_tudo, encerrar, enviar

from cobrinha.audio import Som
from cobrinha.config import PELES, TEMPO_DUELO_COM_RELOGIO, VITORIAS_PARA_VENCER
from cobrinha.controle import Vibracao
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.duelo import PartidaDuelo
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.dominio.partida import Modo
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp
from cobrinha.entradas import TECLADO_DIREITO, TECLADO_ESQUERDO, Entrada
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.duelo import EstadoDuelo
from cobrinha.estados.fim_do_duelo import EstadoFimDoDuelo
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.quem_joga import EstadoQuemJoga

P = Posicao


def duelo_em_andamento(jogo, *entradas) -> EstadoDuelo:
    navegacao.iniciar_duelo(jogo, 1, entradas or None)
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoDuelo)
    return jogo.estado_atual


def vence_a_rodada(duelo: EstadoDuelo, vencedor: int | None) -> EstadoFimDoDuelo:
    """Termina a rodada: o outro jogador bate na borda (ou os dois, se `vencedor` for None)."""
    perdedor_bate = Cobra.nova(P(31, 5), Direcao.DIREITA, 3)
    vivo = Cobra.nova(P(10, 15), Direcao.ESQUERDA, 3)
    if vencedor is None:
        cobras = [
            Cobra.nova(P(9, 5), Direcao.DIREITA, 3),
            Cobra.nova(P(11, 5), Direcao.ESQUERDA, 3),
        ]
    elif vencedor == 1:
        cobras = [perdedor_bate, vivo]
    else:
        cobras = [vivo, perdedor_bate]
    duelo.partida = PartidaDuelo(
        cobras=cobras, comidas=[P(0, 21)], rng=random.Random(0), modo=duelo.partida.modo
    )
    duelo.atualizar(duelo.partida.intervalo_passo)
    encerrar(duelo)
    fim = duelo.jogo.estado_atual
    assert isinstance(fim, EstadoFimDoDuelo)
    desenhar_tudo(duelo.jogo)
    return fim


def proxima_rodada(jogo) -> EstadoDuelo:
    enviar(jogo, pygame.K_RETURN)  # PRÓXIMA RODADA (ou JOGAR DE NOVO)
    assert isinstance(jogo.estado_atual, EstadoContagem)
    enviar(jogo, pygame.K_RETURN)
    return jogo.estado_atual


# --- Rodadas e placar ---


def test_vitoria_conta_no_placar_e_proxima_rodada_continua(jogo):
    duelo = duelo_em_andamento(jogo, TECLADO_DIREITO, TECLADO_ESQUERDO)
    fim = vence_a_rodada(duelo, 1)
    assert fim.placar.vitorias == [0, 1]
    assert fim.campeao is None
    assert fim.menu.itens[0].texto == "PRÓXIMA RODADA"
    enviar(jogo, pygame.K_RETURN)
    contagem = jogo.estado_atual
    assert contagem.titulo == "RODADA 2"
    enviar(jogo, pygame.K_RETURN)
    nova = jogo.estado_atual
    assert nova is not duelo and nova.placar is duelo.placar
    assert nova.entradas == [TECLADO_DIREITO, TECLADO_ESQUERDO]
    assert nova.partida.em_andamento


def test_empate_nao_conta_vitoria(jogo):
    duelo = duelo_em_andamento(jogo)
    fim = vence_a_rodada(duelo, None)
    assert fim.empate and fim.placar.vitorias == [0, 0]


def test_tres_vitorias_fazem_o_campeao_e_jogar_de_novo_zera_o_placar(jogo):
    duelo = duelo_em_andamento(jogo)
    for rodada in range(1, VITORIAS_PARA_VENCER + 1):
        fim = vence_a_rodada(duelo, 0)
        assert fim.placar.rodada == rodada
        if rodada < VITORIAS_PARA_VENCER:
            duelo = proxima_rodada(jogo)
    assert fim.campeao == 0
    assert fim.menu.itens[0].texto == "JOGAR DE NOVO"
    nova = proxima_rodada(jogo)
    assert nova.placar.vitorias == [0, 0] and nova.placar.rodada == 1


def test_reiniciar_na_pausa_zera_o_placar(jogo):
    duelo = duelo_em_andamento(jogo)
    vence_a_rodada(duelo, 1)
    duelo = proxima_rodada(jogo)
    assert duelo.placar.vitorias == [0, 1]
    enviar(jogo, pygame.K_p, pygame.K_DOWN, pygame.K_RETURN)  # REINICIAR
    assert jogo.pilha[0].placar.vitorias == [0, 0]
    assert jogo.pilha[0].placar.rodada == 1


def test_esc_no_placar_volta_ao_menu(jogo):
    duelo = duelo_em_andamento(jogo)
    vence_a_rodada(duelo, 0)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


# --- Modos do menu ---


def test_duelo_segue_o_modo_do_menu(jogo):
    jogo.opcoes.modo = Modo.SEM_BORDAS.name
    navegacao.abrir_quem_joga(jogo)
    assert isinstance(jogo.estado_atual, EstadoQuemJoga)
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_w, pygame.K_UP, pygame.K_RETURN)
    assert jogo.estado_atual.subtitulo == "Campo aberto   Sem bordas"
    duelo = jogo.pilha[0]
    assert duelo.partida.modo is Modo.SEM_BORDAS and not duelo.partida.tem_relogio


def test_variante_com_relogio_e_tempo_esgotado(jogo, monkeypatch):
    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    jogo.opcoes.modo = Modo.CONTRA_O_TEMPO.name
    duelo = duelo_em_andamento(jogo)
    assert duelo.partida.tempo_restante == TEMPO_DUELO_COM_RELOGIO
    desenhar_tudo(jogo)  # HUD com o relógio
    duelo.partida.jogadores[1].pontos = 3
    duelo.partida.tempo_restante = 0.01
    tocados.clear()
    duelo.atualizar(0.02)
    assert Som.NIVEL in tocados and Som.VITORIA in tocados
    encerrar(duelo)
    fim = jogo.estado_atual
    assert fim.vencedor == 1 and fim.tempo_esgotado
    assert fim.placar.vitorias == [0, 1]
    desenhar_tudo(jogo)
    nova = proxima_rodada(jogo)
    assert nova.partida.tem_relogio  # a próxima rodada mantém o modo


def test_empate_por_pontos_no_relogio_mostra_o_motivo(jogo):
    jogo.opcoes.modo = Modo.CONTRA_O_TEMPO.name
    duelo = duelo_em_andamento(jogo)
    duelo.partida.tempo_restante = 0.01
    duelo.atualizar(0.02)
    encerrar(duelo)
    fim = jogo.estado_atual
    assert fim.empate and fim.tem_relogio
    desenhar_tudo(jogo)


# --- Power-ups ---


def test_pegar_camera_lenta_toca_som_vibra_e_mostra_o_efeito(jogo, monkeypatch):
    falsos = conectar_controles(jogo, 5, 6)
    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    duelo = duelo_em_andamento(jogo, Entrada.controle(5), Entrada.controle(6))
    duelo.partida = PartidaDuelo(
        cobras=[
            Cobra.nova(P(5, 5), Direcao.DIREITA, 3),
            Cobra.nova(P(20, 15), Direcao.ESQUERDA, 3),
        ],
        comidas=[P(0, 21)],
        rng=random.Random(0),
    )
    duelo.partida.power_up = PowerUpNoCampo(TipoPowerUp.CAMERA_LENTA, P(6, 5))
    desenhar_tudo(jogo)  # power-up no campo
    tocados.clear()
    duelo.atualizar(duelo.partida.intervalo_passo)
    assert tocados == [Som.POWER_UP]
    assert falsos[5].vibracoes == [Vibracao.MEDIA.value]  # quem pegou
    assert falsos[6].vibracoes == [Vibracao.FRACA.value]  # quem ficou lento
    assert duelo.partida.jogadores[1].lento
    (texto,) = duelo.efeitos.textos
    assert texto.conteudo == "LENTO!" and texto.cor == PELES[0].destaque
    desenhar_tudo(jogo)  # HUD com "LENTO" embaixo do J2


def test_pontos_em_dobro_mostram_o_valor_dobrado(jogo):
    jogo.opcoes.modo = Modo.CONTRA_O_TEMPO.name
    duelo = duelo_em_andamento(jogo)
    duelo.partida = PartidaDuelo(
        cobras=[
            Cobra.nova(P(5, 5), Direcao.DIREITA, 3),
            Cobra.nova(P(20, 15), Direcao.ESQUERDA, 3),
        ],
        comidas=[P(6, 5)],
        rng=random.Random(0),
        modo=Modo.CONTRA_O_TEMPO,
    )
    duelo.partida.jogadores[0].efeitos[TipoPowerUp.PONTOS_EM_DOBRO] = 5.0
    duelo.atualizar(duelo.partida.intervalo_passo)
    assert [efeito.conteudo for efeito in duelo.efeitos.textos] == ["+2"]
    desenhar_tudo(jogo)
