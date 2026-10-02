"""Configuração dos testes: pygame sem janela nem áudio (funciona no CI)."""

import os

import pytest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402 - precisa vir depois das variáveis de ambiente

from cobrinha import recursos  # noqa: E402
from cobrinha.jogo import Jogo  # noqa: E402
from cobrinha.ui import texto  # noqa: E402


@pytest.fixture(autouse=True)
def limpar_caches_do_pygame():
    """Fontes, imagens e textos em cache pertencem ao pygame encerrado no fim de cada teste."""
    yield
    recursos.limpar_cache()
    texto.limpar_cache()


@pytest.fixture
def jogo():
    """Instância do jogo com janela virtual; o pygame é encerrado no fim do teste."""
    instancia = Jogo()
    yield instancia
    pygame.quit()
