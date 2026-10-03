"""Os assets existem, têm o formato esperado e a fonte atende ao português."""

import wave

import pygame
import pytest

from cobrinha import recursos
from cobrinha.audio import Musica, Som
from cobrinha.config import FREQUENCIA_AUDIO, TAMANHO_CELULA
from cobrinha.ui.pecas import SPRITE_DO_POWER_UP, TipoPeca

SPRITES = [
    *(tipo.value for tipo in TipoPeca),
    "comida",
    "comida_dourada",
    "parede",
    *SPRITE_DO_POWER_UP.values(),
]
MAIUSCULAS_ACENTUADAS = "ÁÀÂÃÉÊÍÓÔÕÚÇ"


@pytest.mark.parametrize("nome", SPRITES)
def test_sprites_tem_25x25_com_transparencia(jogo, nome):
    sprite = recursos.imagem(nome)
    assert sprite.get_size() == (TAMANHO_CELULA, TAMANHO_CELULA)
    assert sprite.get_at((0, 0)).a == 0  # canto transparente


@pytest.mark.parametrize(
    "caminho", [recursos.PASTA_SONS / f"{s.value}.wav" for s in [*Som, *Musica]]
)
def test_efeitos_sao_wav_mono_na_taxa_do_mixer(caminho):
    with wave.open(str(caminho)) as arquivo:
        assert arquivo.getnchannels() == 1
        assert arquivo.getframerate() == FREQUENCIA_AUDIO
        assert arquivo.getnframes() > 0


def test_musicas_sao_diferentes_entre_si():
    conteudos = {musica.arquivo.read_bytes() for musica in Musica}
    assert len(conteudos) == len(Musica)


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


def _caracteres_exibidos() -> set[str]:
    """Caracteres de todos os textos das telas e da interface (sem docstrings)."""
    import ast
    from pathlib import Path

    pacote = Path(recursos.__file__).parent
    caracteres: set[str] = set()
    for arquivo in [*(pacote / "estados").glob("*.py"), *(pacote / "ui").glob("*.py")]:
        arvore = ast.parse(arquivo.read_text(encoding="utf-8"))
        docstrings = {
            id(no.value)
            for no in ast.walk(arvore)
            if isinstance(no, ast.Expr) and isinstance(no.value, ast.Constant)
        }
        for no in ast.walk(arvore):
            eh_texto = isinstance(no, ast.Constant) and isinstance(no.value, str)
            if eh_texto and id(no) not in docstrings:
                caracteres.update(no.value)
    return {c for c in caracteres if not c.isspace()}


def test_todo_caractere_exibido_tem_desenho_na_fonte(jogo):
    """Regressão: as setas ← → tinham métricas na VT323, mas saíam em branco."""
    fonte = recursos.fonte(32)
    vazios = []
    for caractere in sorted(_caracteres_exibidos()):
        imagem = fonte.render(caractere, False, (255, 255, 255), (0, 0, 0))
        largura, altura = imagem.get_size()
        acesos = any(imagem.get_at((x, y))[0] for x in range(largura) for y in range(altura))
        if not acesos:
            vazios.append(caractere)
    assert vazios == []
