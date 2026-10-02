"""Os assets existem, têm o formato esperado e a fonte atende ao português."""

import wave

import pygame
import pytest

from cobrinha import recursos
from cobrinha.audio import ARQUIVO_MUSICA, Som
from cobrinha.config import FREQUENCIA_AUDIO, TAMANHO_CELULA
from cobrinha.ui.pecas import TipoPeca

SPRITES = [tipo.value for tipo in TipoPeca] + ["comida"]
MAIUSCULAS_ACENTUADAS = "ÁÀÂÃÉÊÍÓÔÕÚÇ"


@pytest.mark.parametrize("nome", SPRITES)
def test_sprites_tem_25x25_com_transparencia(jogo, nome):
    sprite = recursos.imagem(nome)
    assert sprite.get_size() == (TAMANHO_CELULA, TAMANHO_CELULA)
    assert sprite.get_at((0, 0)).a == 0  # canto transparente


@pytest.mark.parametrize("caminho", [recursos.PASTA_SONS / f"{s.value}.wav" for s in Som])
def test_efeitos_sao_wav_mono_na_taxa_do_mixer(caminho):
    with wave.open(str(caminho)) as arquivo:
        assert arquivo.getnchannels() == 1
        assert arquivo.getframerate() == FREQUENCIA_AUDIO
        assert arquivo.getnframes() > 0


def test_musica_existe():
    assert ARQUIVO_MUSICA.is_file()


def test_fonte_e_licenca_estao_no_pacote():
    assert recursos.ARQUIVO_FONTE.is_file()
    assert (recursos.PASTA_FONTES / "OFL.txt").is_file()


def _glifo(fonte: pygame.font.Font, caractere: str) -> bytes:
    imagem = fonte.render(caractere, False, (255, 255, 255), (0, 0, 0))
    return pygame.image.tobytes(imagem, "RGB")


def test_fonte_tem_maiusculas_acentuadas_de_verdade(jogo):
    """Regressão: a Press Start 2P desenhava Ó, Ô e Õ iguais às minúsculas."""
    fonte = recursos.fonte(32)
    assert all(m is not None for m in fonte.metrics(MAIUSCULAS_ACENTUADAS))
    for maiuscula in MAIUSCULAS_ACENTUADAS:
        assert _glifo(fonte, maiuscula) != _glifo(fonte, maiuscula.lower()), maiuscula
