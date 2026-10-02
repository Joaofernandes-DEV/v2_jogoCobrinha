import pygame

from cobrinha.config import Paleta
from cobrinha.ui.efeitos import DURACAO, Efeitos


def test_texto_flutuante_sobe_e_some(jogo):
    efeitos = Efeitos()
    efeitos.texto_flutuante("+1", Paleta.AMARELO, (100, 100))
    efeitos.desenhar(pygame.Surface((200, 200)))
    efeitos.atualizar(DURACAO / 2)
    assert len(efeitos.textos) == 1
    efeitos.desenhar(pygame.Surface((200, 200)))
    efeitos.atualizar(DURACAO)
    assert efeitos.textos == []
