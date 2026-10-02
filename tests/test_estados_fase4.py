"""Fluxos da Fase 4: modos, recordes, opções, fruta dourada e efeitos visuais."""

import pygame
from auxiliares import desenhar_tudo, encerrar, enviar, jogo_em_andamento

from cobrinha.audio import Som
from cobrinha.dominio.partida import FrutaDourada, Situacao
from cobrinha.estados import navegacao
from cobrinha.estados.fim_de_partida import EstadoFimDePartida
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.opcoes import EstadoOpcoes
from cobrinha.estados.pausa import EstadoPausa
from cobrinha.estados.recordes import EstadoRecordes


def item_do_menu(jogo, rotulo_inicial: str) -> None:
    """Seleciona no menu atual o item cujo texto começa com `rotulo_inicial`."""
    menu = jogo.estado_atual.menu
    menu.selecionado = next(
        i for i, item in enumerate(menu.itens) if item.texto.startswith(rotulo_inicial)
    )


def ler_dados(pasta) -> str:
    return (pasta / "dados.json").read_text(encoding="utf-8")


def test_modo_escolhido_no_menu_vale_para_a_partida(jogo):
    navegacao.abrir_menu(jogo)
    item_do_menu(jogo, "MODO")
    enviar(jogo, pygame.K_RIGHT)
    assert jogo.opcoes.modo == "SEM_BORDAS"
    item_do_menu(jogo, "JOGAR")
    enviar(jogo, pygame.K_RETURN)
    assert jogo.pilha[0].partida.modo.name == "SEM_BORDAS"


def test_recorde_vai_para_o_ranking_do_modo_e_para_o_disco(jogo, pasta_de_dados_temporaria):
    jogo.opcoes.modo = "SEM_BORDAS"
    jogando = jogo_em_andamento(jogo)
    jogando.partida.pontos = 9
    jogando.partida.situacao = Situacao.DERROTA
    encerrar(jogando)
    assert jogo.progresso.recorde("SEM_BORDAS") == 9
    assert jogo.progresso.recorde("CLASSICO") == 0
    assert '"SEM_BORDAS"' in ler_dados(pasta_de_dados_temporaria)


def test_fim_de_partida_mostra_colocacao_no_top_5(jogo):
    jogo.progresso.registrar_pontuacao("CLASSICO", 50, 3, "2026-10-01")
    jogando = jogo_em_andamento(jogo)
    jogando.partida.pontos = 20
    jogando.partida.situacao = Situacao.DERROTA
    encerrar(jogando)
    fim = jogo.estado_atual
    assert fim.colocacao == 2
    assert not fim.novo_recorde
    desenhar_tudo(jogo)


def test_tela_de_recordes_troca_de_modo_e_volta(jogo):
    jogo.progresso.registrar_pontuacao("CLASSICO", 30, 2, "2026-10-02")
    navegacao.abrir_menu(jogo)
    item_do_menu(jogo, "RECORDES")
    enviar(jogo, pygame.K_RETURN)
    recordes = jogo.estado_atual
    assert isinstance(recordes, EstadoRecordes)
    assert "0030" in recordes.linhas_do_ranking()[0][0]
    assert "02/10/2026" in recordes.linhas_do_ranking()[0][0]
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_RIGHT)
    assert recordes.modo.name == "SEM_BORDAS"
    assert "Nenhum recorde" in recordes.linhas_do_ranking()[0][0]
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_opcoes_mudam_o_volume_na_hora_e_salvam_ao_sair(jogo, pasta_de_dados_temporaria):
    navegacao.abrir_menu(jogo)
    item_do_menu(jogo, "OPÇÕES")
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoOpcoes)
    volume_inicial = jogo.opcoes.volume_efeitos
    enviar(jogo, pygame.K_LEFT)  # 1º item: efeitos sonoros
    assert jogo.opcoes.volume_efeitos == round(volume_inicial - 0.1, 1)
    assert jogo.audio.volume_efeitos == jogo.opcoes.volume_efeitos
    item_do_menu(jogo, "EFEITOS VISUAIS")
    enviar(jogo, pygame.K_RETURN)
    assert not jogo.opcoes.efeitos_visuais
    item_do_menu(jogo, "TELA CHEIA")
    enviar(jogo, pygame.K_RETURN)  # sem suporte no driver de testes: não pode quebrar
    desenhar_tudo(jogo)
    enviar(jogo, pygame.K_ESCAPE)
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)
    assert '"efeitos_visuais": false' in ler_dados(pasta_de_dados_temporaria)


def test_comer_mostra_mais_um_flutuando(jogo):
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    partida.comida = partida.cobra.cabeca.vizinha(partida.cobra.direcao)
    jogando.atualizar(partida.intervalo_passo)
    assert [t.conteudo for t in jogando.efeitos.textos] == ["+1"]
    desenhar_tudo(jogo)


def test_fruta_dourada_toca_bonus_e_mostra_mais_cinco(jogo, monkeypatch):
    tocados = []
    monkeypatch.setattr(jogo.audio, "tocar", tocados.append)
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    partida.fruta_dourada = FrutaDourada(partida.cobra.cabeca.vizinha(partida.cobra.direcao))
    desenhar_tudo(jogo)
    jogando.atualizar(partida.intervalo_passo)
    assert Som.BONUS in tocados
    assert [t.conteudo for t in jogando.efeitos.textos] == ["+5"]


def test_fruta_dourada_pisca_quando_esta_sumindo(jogo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.fruta_dourada = FrutaDourada(jogando.partida.comida, tempo_restante=0.5)
    jogando.partida.comida = None
    for _ in range(4):
        jogando.tempo += 0.07
        desenhar_tudo(jogo)


def test_cobra_pisca_ao_bater_e_ignora_teclas_ate_a_tela_de_fim(jogo):
    jogando = jogo_em_andamento(jogo)
    jogando.partida.situacao = Situacao.DERROTA
    jogando.atualizar(0.01)
    assert jogando.tempo_ate_encerrar is not None
    visibilidade = set()
    for _ in range(8):
        visibilidade.add(jogando.cobra_visivel)
        desenhar_tudo(jogo)
        enviar(jogo, pygame.K_ESCAPE)  # não pausa durante a animação
        jogando.atualizar(0.07)
    assert visibilidade == {True, False}
    assert not isinstance(jogo.estado_atual, EstadoPausa)
    encerrar(jogando)
    assert isinstance(jogo.estado_atual, EstadoFimDePartida)


def test_sem_efeitos_visuais_nao_pisca_nem_mostra_pontos(jogo):
    jogo.opcoes.efeitos_visuais = False
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    partida.comida = partida.cobra.cabeca.vizinha(partida.cobra.direcao)
    jogando.atualizar(partida.intervalo_passo)
    assert jogando.efeitos.textos == []
    partida.situacao = Situacao.DERROTA
    jogando.atualizar(0.01)
    assert jogando.cobra_visivel
    jogando.atualizar(0.31)
    assert isinstance(jogo.estado_atual, EstadoFimDePartida)


def test_niveis_com_pedras_desenham_sem_erro(jogo):
    for nivel in (2, 3):
        jogo_em_andamento(jogo, nivel=nivel)
        desenhar_tudo(jogo)
