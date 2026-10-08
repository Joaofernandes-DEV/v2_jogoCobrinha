"""Contrato comum a todas as telas do jogo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

from cobrinha.config import Cor, Paleta

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo


class Estado(ABC):
    """Uma tela do jogo. O loop principal chama, a cada quadro, os três métodos abaixo."""

    def __init__(self, jogo: Jogo) -> None:
        self.jogo = jogo

    @abstractmethod
    def tratar_evento(self, evento: pygame.Event) -> None:
        """Reage a um evento do pygame (teclado, mouse etc.)."""

    @property
    def cor_do_controle(self) -> Cor:
        """Cor da luz do controle enquanto esta tela está no topo (V3)."""
        return Paleta.VERDE_CLARO

    def atualizar(self, dt: float) -> None:  # noqa: B027 - opcional nas subclasses
        """Avança a lógica da tela. `dt` é o tempo do quadro, em segundos."""

    @abstractmethod
    def desenhar(self, superficie: pygame.Surface) -> None:
        """Desenha a tela inteira na superfície recebida."""


class EstadoDePartida(Estado):
    """Tela de uma partida em andamento (1 jogador ou duelo).

    A pausa e a contagem ficam por cima dela e pedem a ela o que fazer ao reiniciar
    ou sair, porque isso muda conforme o tipo de partida (ex.: só 1 jogador tem ranking).
    """

    @abstractmethod
    def reiniciar(self) -> None:
        """Recomeça do início (REINICIAR na pausa)."""

    @abstractmethod
    def abandonar(self) -> None:
        """Volta ao menu principal no meio da partida."""

    def antes_de_sair_do_jogo(self) -> None:  # noqa: B027 - opcional nas subclasses
        """Guarda o que for preciso antes de o jogo fechar (SAIR DO JOGO na pausa)."""
