import pygame

from cobrinha.__main__ import analisar_argumentos
from cobrinha.config import ALTURA_HUD, Paleta
from cobrinha.dominio.grade import Posicao
from cobrinha.dominio.partida import Situacao
from cobrinha.estados.fim_de_partida import EstadoFimDePartida
from cobrinha.estados.jogando import EstadoJogando


def tecla(codigo: int) -> pygame.Event:
    return pygame.Event(pygame.KEYDOWN, key=codigo)


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
    pygame.event.post(tecla(pygame.K_ESCAPE))
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


def test_setas_e_wasd_viram_a_cobra(jogo):
    estado = EstadoJogando(jogo)
    estado.tratar_evento(tecla(pygame.K_w))
    assert estado.partida.cobra.aplicar_proxima_direcao().name == "CIMA"
    estado.tratar_evento(tecla(pygame.K_LEFT))
    assert estado.partida.cobra.aplicar_proxima_direcao().name == "ESQUERDA"


def test_derrota_abre_fim_de_partida_e_enter_recomeca(jogo):
    estado = EstadoJogando(jogo, recorde=2)
    jogo.trocar_estado(estado)
    estado.partida.pontos = 5
    estado.partida.situacao = Situacao.DERROTA

    estado.atualizar(0.016)
    fim = jogo.estado_atual
    assert isinstance(fim, EstadoFimDePartida)
    assert fim.novo_recorde
    assert fim.recorde == 5
    fim.desenhar(pygame.Surface(jogo.tela.get_size()))

    fim.tratar_evento(tecla(pygame.K_RETURN))
    novo = jogo.estado_atual
    assert isinstance(novo, EstadoJogando)
    assert novo.recorde == 5
    assert novo.partida.em_andamento
    assert len(jogo.pilha) == 1


def test_esc_no_fim_de_partida_encerra(jogo):
    estado = EstadoJogando(jogo)
    jogo.trocar_estado(estado)
    estado.partida.situacao = Situacao.DERROTA
    estado.atualizar(0.016)
    jogo.estado_atual.tratar_evento(tecla(pygame.K_ESCAPE))
    assert not jogo.rodando


def test_argumentos_de_linha_de_comando():
    padrao = analisar_argumentos([])
    assert (padrao.debug, padrao.semente) == (False, None)
    opcoes = analisar_argumentos(["--debug", "--semente", "7"])
    assert (opcoes.debug, opcoes.semente) == (True, 7)
