import pygame

from cobrinha.config import ALTURA_HUD, Paleta
from cobrinha.estados.jogando import EstadoJogando


def test_janela_tem_800x600(jogo):
    assert jogo.tela.get_size() == (800, 600)


def test_fechar_janela_encerra_sem_erro(jogo):
    jogo.trocar_estado(EstadoJogando(jogo))
    pygame.event.post(pygame.Event(pygame.QUIT))
    jogo.executar()
    assert not jogo.rodando
    assert not pygame.get_init()


def test_esc_encerra_sem_erro(jogo):
    jogo.trocar_estado(EstadoJogando(jogo))
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
    superficie = pygame.Surface(jogo.tela.get_size())
    EstadoJogando(jogo).desenhar(superficie)

    assert superficie.get_at((0, 0))[:3] == Paleta.CINZA_ESCURO
    assert superficie.get_at((0, ALTURA_HUD))[:3] == Paleta.GRAMA_CLARA
    assert superficie.get_at((25, ALTURA_HUD))[:3] == Paleta.GRAMA_ESCURA
    assert superficie.get_at((25, ALTURA_HUD + 25))[:3] == Paleta.GRAMA_CLARA
