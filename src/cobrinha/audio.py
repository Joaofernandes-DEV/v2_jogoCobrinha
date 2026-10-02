"""Efeitos sonoros e música (I8).

Se o computador não tiver saída de áudio, o jogo continua funcionando em silêncio.
"""

from enum import Enum

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


ARQUIVO_MUSICA = PASTA_SONS / "musica.wav"


class Audio:
    def __init__(self) -> None:
        self.mudo = False
        self.volume_efeitos = VOLUME_EFEITOS
        self.volume_musica = VOLUME_MUSICA
        self._sons: dict[Som, pygame.mixer.Sound] = {}
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

    def tocar_musica(self) -> None:
        """Começa a música em loop (se já estiver tocando, não reinicia)."""
        if self.disponivel and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(ARQUIVO_MUSICA)
            pygame.mixer.music.play(loops=-1)

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
