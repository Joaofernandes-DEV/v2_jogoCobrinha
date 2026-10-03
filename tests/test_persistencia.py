"""Recordes e opções sobrevivem entre sessões, e dados ruins não derrubam o jogo."""

import json

import pygame

from cobrinha import persistencia
from cobrinha.dominio.progresso import Progresso
from cobrinha.jogo import Jogo
from cobrinha.opcoes import Opcoes


def test_pasta_de_dados_pode_ser_trocada_por_variavel(pasta_de_dados_temporaria):
    assert persistencia.pasta_dados() == pasta_de_dados_temporaria


def test_sem_arquivo_comeca_com_os_padroes():
    progresso, opcoes = persistencia.carregar()
    assert progresso == Progresso()
    assert opcoes == Opcoes()


def test_salvar_e_carregar_de_volta(pasta_de_dados_temporaria):
    progresso = Progresso()
    opcoes = Opcoes(volume_musica=0.2, tela_cheia=True, modo="SEM_BORDAS")
    progresso.registrar_pontuacao("SEM_BORDAS", 42, 3, "2026-10-02")
    progresso.liberar_nivel(3)
    persistencia.salvar(progresso, opcoes)

    assert (pasta_de_dados_temporaria / "dados.json").is_file()
    progresso_lido, opcoes_lidas = persistencia.carregar()
    assert progresso_lido == progresso
    assert opcoes_lidas == opcoes


def test_arquivo_corrompido_vira_reserva_e_jogo_segue(pasta_de_dados_temporaria):
    pasta_de_dados_temporaria.mkdir(parents=True)
    (pasta_de_dados_temporaria / "dados.json").write_text("{ isto não é json", encoding="utf-8")
    progresso, _opcoes = persistencia.carregar()
    assert progresso == Progresso()
    assert (pasta_de_dados_temporaria / "dados.corrompido").is_file()


def test_valores_invalidos_voltam_ao_padrao(pasta_de_dados_temporaria):
    pasta_de_dados_temporaria.mkdir(parents=True)
    dados = {
        "progresso": {"maior_nivel_liberado": 99, "rankings": {}},
        "opcoes": {"volume_efeitos": 7, "volume_musica": -1, "modo": "INEXISTENTE"},
    }
    (pasta_de_dados_temporaria / "dados.json").write_text(json.dumps(dados), encoding="utf-8")
    progresso, opcoes = persistencia.carregar()
    assert progresso.maior_nivel_liberado == 3
    assert (opcoes.volume_efeitos, opcoes.volume_musica) == (1.0, 0.0)
    assert opcoes.modo == "CLASSICO"


def test_jogo_carrega_o_que_foi_salvo():
    progresso = Progresso()
    progresso.registrar_pontuacao("CLASSICO", 17, 2, "2026-10-02")
    persistencia.salvar(progresso, Opcoes(volume_efeitos=0.3))
    jogo = Jogo()
    try:
        assert jogo.progresso.recorde("CLASSICO") == 17
        assert jogo.audio.volume_efeitos == 0.3
    finally:
        pygame.quit()


def test_opcoes_ajustam_volume_em_passos_de_10_por_cento_e_com_limites():
    opcoes = Opcoes(volume_efeitos=0.95)
    opcoes.ajustar_volume_efeitos(+1)
    assert opcoes.volume_efeitos == 1.0
    for _ in range(15):
        opcoes.ajustar_volume_musica(-1)
    assert opcoes.volume_musica == 0.0


def test_alternar_modo_circula():
    opcoes = Opcoes()
    opcoes.alternar_modo()
    assert opcoes.modo == "SEM_BORDAS"
    opcoes.alternar_modo()
    assert opcoes.modo == "CONTRA_O_TEMPO"
    opcoes.alternar_modo()
    assert opcoes.modo == "CLASSICO"


def test_alternar_modo_para_tras():
    opcoes = Opcoes()
    opcoes.alternar_modo(-1)
    assert opcoes.modo == "CONTRA_O_TEMPO"
    opcoes.alternar_modo(-1)
    assert opcoes.modo == "SEM_BORDAS"
