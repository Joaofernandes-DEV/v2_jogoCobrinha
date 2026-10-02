"""Efeitos sonoros e música (I8).

Música de fundo:
- telas do menu (menu, recordes, opções, créditos): música do menu;
- partida: cada fase tem a própria música, que troca a cada fase (`musica_da_fase`);
- ao bater ou vencer, a música para na hora e só volta no menu (ou numa nova partida);
- na pausa, a música pausa e continua de onde parou.

Se o computador não tiver saída de áudio, o jogo continua funcionando em silêncio.
"""

from enum import Enum
from pathlib import Path

import pygame

from cobrinha.config import VOLUME_EFEITOS, VOLUME_MUSICA
from cobrinha.recursos import PASTA_SONS


class Som(Enum):
    """Efeitos disponíveis; o valor é o nome do arquivo em assets/sons/."""

    COMER = "comer"
    BONUS = "bonus"
    NIVEL = "nivel"
    BATER = "bater"
    VITORIA = "vitoria"
    MENU_MOVER = "menu_mover"
    MENU_CONFIRMAR = "menu_confirmar"
    CONTAGEM = "contagem"
    CONTAGEM_JA = "contagem_ja"
    PAUSA = "pausa"


class Musica(Enum):
    """Músicas de fundo; o valor é o nome do arquivo em assets/sons/."""

    MENU = "musica_menu"
    FASE_1 = "musica_fase1"
    FASE_2 = "musica_fase2"
    FASE_3 = "musica_fase3"

    @property
    def arquivo(self) -> Path:
        return PASTA_SONS / f"{self.value}.wav"


MUSICAS_DAS_FASES = (Musica.FASE_1, Musica.FASE_2, Musica.FASE_3)


def musica_da_fase(numero: int) -> Musica:
    """Música de uma fase. Se houver mais fases que músicas, elas se revezam."""
    return MUSICAS_DAS_FASES[(numero - 1) % len(MUSICAS_DAS_FASES)]


class Audio:
    def __init__(self) -> None:
        self.mudo = False
        self.volume_efeitos = VOLUME_EFEITOS
        self.volume_musica = VOLUME_MUSICA
        self._sons: dict[Som, pygame.mixer.Sound] = {}
        # Música de fundo atual (None = em silêncio), mesmo sem saída de áudio.
        self.musica_atual: Musica | None = None
        self.disponivel = self._iniciar_mixer()
        if self.disponivel:
            for som in Som:
                self._sons[som] = pygame.mixer.Sound(PASTA_SONS / f"{som.value}.wav")
            self._aplicar_volumes()

    @staticmethod
    def _iniciar_mixer() -> bool:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return False
        return True

    def tocar(self, som: Som) -> None:
        if self.disponivel:
            self._sons[som].play()

    def tocar_musica(self, musica: Musica) -> None:
        """Troca a música de fundo, em loop. Se já for a atual, segue sem reiniciar."""
        if musica is self.musica_atual:
            return
        self.musica_atual = musica
        if self.disponivel:
            pygame.mixer.music.load(musica.arquivo)
            pygame.mixer.music.play(loops=-1)

    def parar_musica(self) -> None:
        """Silencia a música de fundo na hora (ex.: ao bater)."""
        self.musica_atual = None
        if self.disponivel:
            pygame.mixer.music.stop()

    def pausar_musica(self) -> None:
        if self.disponivel:
            pygame.mixer.music.pause()

    def retomar_musica(self) -> None:
        if self.disponivel:
            pygame.mixer.music.unpause()

    def definir_volumes(self, efeitos: float, musica: float) -> None:
        self.volume_efeitos = efeitos
        self.volume_musica = musica
        self._aplicar_volumes()

    def alternar_mudo(self) -> None:
        self.mudo = not self.mudo
        self._aplicar_volumes()

    def _aplicar_volumes(self) -> None:
        if not self.disponivel:
            return
        fator = 0.0 if self.mudo else 1.0
        for efeito in self._sons.values():
            efeito.set_volume(self.volume_efeitos * fator)
        pygame.mixer.music.set_volume(self.volume_musica * fator)
