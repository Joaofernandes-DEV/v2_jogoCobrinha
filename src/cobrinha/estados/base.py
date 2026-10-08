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
