"""Funções compartilhadas pelos testes de fluxo entre telas."""

import pygame

from cobrinha.estados import navegacao
from cobrinha.estados.jogando import EstadoJogando


def tecla(codigo: int) -> pygame.Event:
    return pygame.Event(pygame.KEYDOWN, key=codigo)


def enviar(jogo, *codigos: int) -> None:
    for codigo in codigos:
        jogo.estado_atual.tratar_evento(tecla(codigo))


def desenhar_tudo(jogo) -> None:
    superficie = pygame.Surface(jogo.tela.get_size())
    for estado in jogo.pilha:
        estado.desenhar(superficie)


def encerrar(jogando: EstadoJogando) -> None:
    """Avança o tempo até a partida encerrada abrir a tela seguinte (pula a animação de morte)."""
    for _ in range(5):
        if jogando.jogo.estado_atual is not jogando:
            return
        jogando.atualizar(0.5)
    raise AssertionError("a partida não abriu a tela seguinte")


def jogo_em_andamento(jogo, nivel: int = 1) -> EstadoJogando:
    """Começa uma campanha e pula a contagem."""
    navegacao.iniciar_campanha(jogo, nivel)
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoJogando)
    return jogo.estado_atual
