"""Gera as capturas de tela e as figuras do ebook que dependem do pygame.

Uso: python docs/ebook/capturas.py
Requer: pip install -e ".[ebook]" (pygame-ce e Pillow)

O jogo roda de verdade, sem janela (driver de vídeo "dummy", como em
ferramentas/gravar_demo.py), com semente fixa: as imagens saem sempre iguais.
Cada captura é exatamente o que `Jogo._desenhar()` põe na tela antes do flip.
"""

from __future__ import annotations

import os
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

os.environ.update(
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    COBRINHA_DADOS=tempfile.mkdtemp(prefix="cobrinha-ebook-"),
)

import pygame  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
sys.path[:0] = [str(RAIZ / "src"), str(RAIZ / "ferramentas"), str(PASTA)]

from figuras import DESTINO, FUNDO, TINTA, fonte, preparar  # noqa: E402
from gravar_demo import celula_livre_perto, pilotar  # noqa: E402

from cobrinha import recursos  # noqa: E402
from cobrinha.config import Paleta  # noqa: E402
from cobrinha.dominio.cobra import Cobra  # noqa: E402
from cobrinha.dominio.grade import Direcao, Posicao  # noqa: E402
from cobrinha.dominio.niveis import obter_nivel  # noqa: E402
from cobrinha.dominio.partida import FrutaDourada, Modo, Partida  # noqa: E402
from cobrinha.dominio.power_ups import TipoPowerUp  # noqa: E402
from cobrinha.estados import navegacao  # noqa: E402
from cobrinha.estados.jogando import OPACIDADE_VEU_LENTO, EstadoJogando  # noqa: E402
from cobrinha.jogo import Jogo  # noqa: E402
from cobrinha.ui import texto  # noqa: E402
from cobrinha.ui.campo import criar_fundo_campo  # noqa: E402
from cobrinha.ui.painel import criar_veu  # noqa: E402

DT = 1 / 60
SEMENTE = 7


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------


def encerrar() -> None:
    """Fecha o pygame e descarta as superfícies em cache, que pertencem à janela antiga."""
    pygame.quit()
    recursos.limpar_cache()
    texto.limpar_cache()


def para_pil(superficie: pygame.Surface) -> Image.Image:
    dados = pygame.image.tobytes(superficie, "RGB")
    return Image.frombytes("RGB", superficie.get_size(), dados)


def salvar_tela(jogo: Jogo, nome: str) -> Image.Image:
    """Desenha um quadro (sem o fade de transição) e salva o que estaria na tela."""
    jogo.opacidade_fade = 0.0
    jogo._desenhar()
    imagem = para_pil(jogo.tela)
    imagem.save(DESTINO / f"{nome}.png", optimize=True)
    print(f"gerado: figuras/{nome}.png")
    return imagem


def rodar(jogo: Jogo, segundos: float, antes: Callable[[], None] | None = None) -> None:
    for _ in range(round(segundos / DT)):
        if antes:
            antes()
        jogo.estado_atual.atualizar(DT)


def pular_contagem(jogo: Jogo) -> EstadoJogando:
    jogo.estado_atual.tratar_evento(pygame.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    jogando = jogo.estado_atual
    assert isinstance(jogando, EstadoJogando)
    return jogando


def jogar_ate(jogo: Jogo, partida: Partida, condicao: Callable[[], bool], limite: float = 60):
    """Deixa o piloto automático jogar até a condição valer (ou o tempo-limite passar)."""
    tempo = 0.0
    while not condicao() and tempo < limite and partida.em_andamento:
        pilotar(partida)
        jogo.estado_atual.atualizar(DT)
        tempo += DT


def novo_jogo(modo: Modo = Modo.CLASSICO) -> Jogo:
    jogo = Jogo(semente=SEMENTE)
    jogo.opcoes.modo = modo.name
    return jogo


def rotular(imagem: Image.Image, conteudo: str, x: int, y: int, tamanho: int = 12) -> None:
    ImageDraw.Draw(imagem).text(
        (x, y), preparar(conteudo), font=fonte(tamanho), fill=TINTA, anchor="mm"
    )


# ---------------------------------------------------------------------------
# Capturas de tela
# ---------------------------------------------------------------------------


def capturas_de_tela() -> None:
    # Menu principal.
    jogo = novo_jogo()
    navegacao.abrir_menu(jogo)
    rodar(jogo, 0.5)
    salvar_tela(jogo, "captura-menu")
    encerrar()

    # Contagem antes do nível 2 (tela empilhada sobre a partida).
    jogo = novo_jogo()
    navegacao.iniciar_campanha(jogo, 2)
    rodar(jogo, 0.4)
    salvar_tela(jogo, "captura-contagem")

    # Partida do nível 2 logo depois de comer: texto flutuante e maçã dourada.
    jogando = pular_contagem(jogo)
    partida = jogando.partida
    jogar_ate(jogo, partida, lambda: partida.comidas_no_nivel >= 6)
    partida.fruta_dourada = FrutaDourada(celula_livre_perto(partida))
    comidas = partida.comidas_no_nivel
    jogar_ate(jogo, partida, lambda: partida.comidas_no_nivel > comidas)
    rodar(jogo, 0.2)
    salvar_tela(jogo, "captura-jogando")

    # Câmera lenta e pontos em dobro ativos: véu azul e efeitos no HUD.
    partida.efeitos_ativos[TipoPowerUp.CAMERA_LENTA] = 4.6
    partida.efeitos_ativos[TipoPowerUp.PONTOS_EM_DOBRO] = 7.2
    rodar(jogo, 0.1, lambda: pilotar(partida))
    salvar_tela(jogo, "captura-camera-lenta")

    # Pausa por cima da partida congelada.
    navegacao.pausar(jogo, jogando)
    rodar(jogo, 0.2)
    salvar_tela(jogo, "captura-pausa")
    jogo.desempilhar()

    # Fim de partida: o piloto "se distrai" e a cobra segue reto até bater.
    while partida.em_andamento:
        jogo.estado_atual.atualizar(DT)
    rodar(jogo, 1.5)
    salvar_tela(jogo, "captura-fim")
    encerrar()

    # Nível 3 (labirinto).
    jogo = novo_jogo()
    navegacao.iniciar_campanha(jogo, 3)
    jogando = pular_contagem(jogo)
    partida = jogando.partida
    jogar_ate(jogo, partida, lambda: partida.comidas_no_nivel >= 5)
    rodar(jogo, 0.9, lambda: pilotar(partida))
    salvar_tela(jogo, "captura-labirinto")
    encerrar()

    # Contra o tempo, com o relógio já no alerta (vermelho abaixo de 10 s).
    jogo = novo_jogo(Modo.CONTRA_O_TEMPO)
    navegacao.iniciar_campanha(jogo, 1)
    jogando = pular_contagem(jogo)
    partida = jogando.partida
    jogar_ate(jogo, partida, lambda: partida.comidas_no_nivel >= 4)
    partida.tempo_restante = 8.4
    rodar(jogo, 0.3, lambda: pilotar(partida))
    salvar_tela(jogo, "captura-contra-o-tempo")
    encerrar()

    # Sem bordas: a cobra atravessando a borda direita e saindo pela esquerda.
    jogo = novo_jogo(Modo.SEM_BORDAS)
    cobra = Cobra(
        [Posicao(1, 9), Posicao(0, 9), Posicao(31, 9), Posicao(30, 9), Posicao(29, 9)],
        Direcao.DIREITA,
    )
    partida = Partida(
        nivel=obter_nivel(1),
        rng=jogo.rng,
        cobra=cobra,
        comida=Posicao(6, 9),
        modo=Modo.SEM_BORDAS,
    )
    jogo.trocar_estado(EstadoJogando(jogo, partida))
    salvar_tela(jogo, "captura-sem-bordas")
    encerrar()


# ---------------------------------------------------------------------------
# Figuras com superfícies do pygame
# ---------------------------------------------------------------------------


def rotacoes() -> None:
    """As peças-base giradas por pygame.transform.rotate, como o jogo faz (ui/pecas.py)."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    fator, margem = 7, 26
    lado = 25 * fator
    pecas = ("cabeca", "corpo_curva")
    angulos = (0, 90, 180, 270)
    largura = len(angulos) * (lado + margem) + margem + 170
    altura = len(pecas) * (lado + 60) + 60
    folha = Image.new("RGB", (largura, altura), FUNDO)
    for linha, nome in enumerate(pecas):
        base = recursos.imagem(nome)
        y = 50 + linha * (lado + 60)
        rotular(folha, {"cabeca": "cabeça", "corpo_curva": "curva"}[nome], 85, y + lado // 2, 14)
        for coluna, angulo in enumerate(angulos):
            girada = pygame.transform.rotate(base, angulo)
            imagem = Image.frombytes(
                "RGBA", girada.get_size(), pygame.image.tobytes(girada, "RGBA")
            )
            grande = imagem.resize((lado, lado), Image.Resampling.NEAREST)
            x = 170 + margem + coluna * (lado + margem)
            fundo = Image.new("RGBA", (lado, lado), (*Paleta.GRAMA_CLARA, 255))
            fundo.alpha_composite(grande)
            folha.paste(fundo.convert("RGB"), (x, y))
            if linha == 0:
                rotular(folha, f"rotate({angulo}°)", x + lado // 2, 24, 12)
    folha.save(DESTINO / "rotacoes.png", optimize=True)
    print("gerado: figuras/rotacoes.png")
    encerrar()


def composicao_alfa() -> None:
    """O mesmo trecho do campo sob cada camada semitransparente usada no jogo."""
    pygame.init()
    pygame.display.set_mode((1, 1))
    campo = criar_fundo_campo()
    recursos.limpar_cache()
    trecho = pygame.Rect(0, 0, 200, 150)
    cobra = recursos.imagem("corpo_reto")
    comida = recursos.imagem("comida")

    def cena() -> pygame.Surface:
        superficie = campo.subsurface(trecho).copy()
        for coluna in range(2, 6):
            superficie.blit(cobra, (coluna * 25, 50))
        superficie.blit(comida, (125, 100))
        return superficie

    veu_azul = pygame.Surface(trecho.size, pygame.SRCALPHA)
    veu_azul.fill((*Paleta.AZUL, OPACIDADE_VEU_LENTO))
    fade = pygame.Surface(trecho.size)
    fade.fill(Paleta.PRETO)
    fade.set_alpha(128)
    paineis: list[tuple[str, pygame.Surface]] = [("sem camada", cena())]
    for titulo, camada in (
        (f"véu azul, α = {OPACIDADE_VEU_LENTO}", veu_azul),
        ("véu da pausa, α = 170", criar_veu(170).subsurface(trecho).copy()),
        ("fade no meio, α = 128", fade),
    ):
        superficie = cena()
        superficie.blit(camada, (0, 0))
        paineis.append((titulo, superficie))
    fator, margem = 2, 24
    largura = len(paineis) * (trecho.width * fator + margem) + margem
    folha = Image.new("RGB", (largura, trecho.height * fator + 80), FUNDO)
    for i, (titulo, superficie) in enumerate(paineis):
        imagem = para_pil(superficie).resize(
            (trecho.width * fator, trecho.height * fator), Image.Resampling.NEAREST
        )
        x = margem + i * (trecho.width * fator + margem)
        folha.paste(imagem, (x, 20))
        rotular(folha, titulo, x + trecho.width * fator // 2, trecho.height * fator + 50, 12)
    folha.save(DESTINO / "composicao-alfa.png", optimize=True)
    print("gerado: figuras/composicao-alfa.png")
    encerrar()


def quantizacao() -> None:
    """Um trecho da captura reduzido a poucas cores pelo median cut (como no GIF do README)."""
    original = Image.open(DESTINO / "captura-jogando.png").convert("RGB")
    trecho = original.crop((400, 260, 800, 560))  # cobra, pedras, power-up e "+1"
    fator, margem = 1, 24
    versoes = [("original", trecho)]
    for cores in (48, 8, 4):
        quantizada = trecho.quantize(colors=cores, method=Image.Quantize.MEDIANCUT, dither=0)
        versoes.append((f"median cut, {cores} cores", quantizada.convert("RGB")))
    largura = 2 * (trecho.width * fator + margem) + margem
    altura = 2 * (trecho.height * fator + 70) + margem
    folha = Image.new("RGB", (largura, altura), FUNDO)
    for i, (titulo, imagem) in enumerate(versoes):
        x = margem + (i % 2) * (trecho.width * fator + margem)
        y = margem + (i // 2) * (trecho.height * fator + 70)
        folha.paste(imagem, (x, y))
        rotular(folha, titulo, x + trecho.width // 2, y + trecho.height + 32, 12)
    folha.save(DESTINO / "quantizacao.png", optimize=True)
    print("gerado: figuras/quantizacao.png")


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    capturas_de_tela()
    rotacoes()
    composicao_alfa()
    quantizacao()


if __name__ == "__main__":
    main()
