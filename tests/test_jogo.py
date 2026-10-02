import pygame
import pytest

from cobrinha.__main__ import analisar_argumentos, preparar_jogo
from cobrinha.config import ALTURA_HUD, Paleta
from cobrinha.dominio.grade import Posicao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.jogando import EstadoJogando
from cobrinha.estados.menu_principal import EstadoMenuPrincipal


def test_janela_tem_800x600(jogo):
    assert jogo.tela.get_size() == (800, 600)


def test_fechar_janela_encerra_sem_erro(jogo):
    jogo.trocar_estado(EstadoJogando(jogo))
    pygame.event.post(pygame.Event(pygame.QUIT))
    jogo.executar()
    assert not jogo.rodando
    assert not pygame.get_init()


def test_esc_no_menu_principal_encerra_sem_erro(jogo):
    jogo.trocar_estado(EstadoMenuPrincipal(jogo))
    pygame.event.post(pygame.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
    jogo.executar()
    assert not pygame.get_init()


def test_pilha_de_estados(jogo):
    primeiro, segundo = EstadoJogando(jogo), EstadoJogando(jogo)
    jogo.trocar_estado(primeiro)
    jogo.empilhar(segundo)
    assert jogo.estado_atual is segundo
    jogo.desempilhar()
    assert jogo.estado_atual is primeiro


def test_desenha_hud_e_campo_em_xadrez(jogo):
    estado = EstadoJogando(jogo)
    estado.partida.comida = Posicao(20, 5)  # longe das células conferidas
    superficie = pygame.Surface(jogo.tela.get_size())
    estado.desenhar(superficie)

    assert superficie.get_at((0, 0))[:3] == Paleta.CINZA_ESCURO
    assert superficie.get_at((0, ALTURA_HUD))[:3] == Paleta.GRAMA_CLARA
    assert superficie.get_at((25, ALTURA_HUD))[:3] == Paleta.GRAMA_ESCURA
    assert superficie.get_at((25, ALTURA_HUD + 25))[:3] == Paleta.GRAMA_CLARA


def test_argumentos_de_linha_de_comando():
    padrao = analisar_argumentos([])
    assert (padrao.debug, padrao.semente, padrao.nivel) == (False, None, None)
    opcoes = analisar_argumentos(["--debug", "--semente", "7", "--nivel", "2"])
    assert (opcoes.debug, opcoes.semente, opcoes.nivel) == (True, 7, 2)


def test_nivel_inexistente_e_recusado():
    with pytest.raises(SystemExit):
        analisar_argumentos(["--nivel", "9"])


def test_sem_argumentos_abre_o_menu():
    jogo = preparar_jogo(analisar_argumentos([]))
    try:
        assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)
    finally:
        pygame.quit()


def test_opcao_nivel_comeca_direto_no_nivel():
    jogo = preparar_jogo(analisar_argumentos(["--nivel", "3"]))
    try:
        assert isinstance(jogo.estado_atual, EstadoContagem)
        assert jogo.pilha[0].partida.nivel.numero == 3
        assert jogo.progresso.maior_nivel_liberado == 3
    finally:
        pygame.quit()


def test_trocar_de_tela_comeca_com_fade(jogo):
    jogo.trocar_estado(EstadoMenuPrincipal(jogo))
    assert jogo.opacidade_fade == 1.0
    jogo._desenhar()  # desenha com a camada de fade sem erro


def test_tecla_m_silencia_em_qualquer_tela(jogo):
    jogo.trocar_estado(EstadoMenuPrincipal(jogo))
    pygame.event.post(pygame.Event(pygame.KEYDOWN, key=pygame.K_m))
    jogo._processar_eventos()
    assert jogo.audio.mudo


def test_fechar_em_encerra_o_jogo_sozinho():
    """Usado no teste automático do executável: o loop real roda e fecha sem ninguém clicar."""
    import time

    from cobrinha.__main__ import main

    inicio = time.monotonic()
    main(["--fechar-em", "0.3", "--nivel", "2"])
    assert time.monotonic() - inicio < 10
    assert not pygame.get_init()
