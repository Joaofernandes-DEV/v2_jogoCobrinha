"""Gera os fluxogramas, diagramas e gráficos do ebook em `docs/ebook/figuras/` (só Pillow).

Uso: python docs/ebook/figuras.py

Tudo é desenhado por código, como os sprites e os sons do jogo: o resultado é
determinístico e pode ser regenerado a qualquer momento. As figuras que precisam
do pygame (capturas de tela, rotações e composição alfa) ficam em `capturas.py`.
"""

from __future__ import annotations

import math
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "src"))

from cobrinha.config import Paleta  # noqa: E402  (config.py não importa o pygame)

DESTINO = Path(__file__).resolve().parent / "figuras"
IMAGENS = RAIZ / "src" / "cobrinha" / "assets" / "imagens"
# A fonte do próprio jogo: tem todos os acentos do português (há teste para isso).
ARQUIVO_FONTE = RAIZ / "src" / "cobrinha" / "assets" / "fontes" / "VT323-Regular.ttf"

ESCALA = 2  # tudo é desenhado no dobro do tamanho lógico, para sair nítido no PDF
TAMANHO_TEXTO = 22
ALTURA_LINHA = 22

Ponto = tuple[float, float]
Cor = tuple[int, int, int]

FUNDO: Cor = (255, 255, 255)
TINTA: Cor = Paleta.PRETO
CINZA_LINHA: Cor = (150, 146, 160)
PREENCHIMENTO: dict[str, Cor] = {
    "terminal": (208, 226, 242),
    "processo": (226, 240, 212),
    "decisao": (253, 238, 196),
    "destaque": (250, 216, 190),
    "alerta": (244, 200, 200),
    "empilhada": (232, 222, 244),
    "nota": (244, 244, 240),
}


# Símbolos sem desenho na VT323 e o que vai no lugar deles.
SUBSTITUTOS = {"→": "->", "←": "<-", "α": "alfa", "⌊": "piso(", "⌋": ")"}


def fonte(tamanho: int = TAMANHO_TEXTO) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(ARQUIVO_FONTE), tamanho * ESCALA)


def preparar(conteudo: str) -> str:
    """Troca os símbolos que a fonte não tem e falha se sobrar algum sem desenho."""
    for simbolo, troca in SUBSTITUTOS.items():
        conteudo = conteudo.replace(simbolo, troca)
    teste = fonte(20)
    faltando = {c for c in conteudo if not c.isspace() and teste.getmask(c).getbbox() is None}
    if faltando:
        raise ValueError(f"A fonte não desenha: {sorted(faltando)}")
    return conteudo


# ---------------------------------------------------------------------------
# Motor de diagramas: nós com formas de fluxograma e setas ortogonais
# ---------------------------------------------------------------------------


@dataclass
class No:
    x: float
    y: float
    largura: float
    altura: float
    texto: str
    forma: str

    def porta(self, lado: str) -> Ponto:
        meia_l, meia_a = self.largura / 2, self.altura / 2
        return {
            "cima": (self.x, self.y - meia_a),
            "baixo": (self.x, self.y + meia_a),
            "esquerda": (self.x - meia_l, self.y),
            "direita": (self.x + meia_l, self.y),
        }[lado]


class Diagrama:
    def __init__(self, largura: int, altura: int) -> None:
        self.imagem = Image.new("RGB", (largura * ESCALA, altura * ESCALA), FUNDO)
        self.desenho = ImageDraw.Draw(self.imagem)
        self.nos: dict[str, No] = {}

    # Conversões de unidades lógicas para pixels da imagem.
    @staticmethod
    def _p(ponto: Ponto) -> tuple[int, int]:
        return round(ponto[0] * ESCALA), round(ponto[1] * ESCALA)

    def texto(
        self,
        posicao: Ponto,
        conteudo: str,
        tamanho: int = TAMANHO_TEXTO,
        cor: Cor = TINTA,
        ancora: str = "mm",
    ) -> None:
        linhas = preparar(conteudo).split("\n")
        altura_linha = tamanho * ALTURA_LINHA / TAMANHO_TEXTO
        topo = posicao[1] - altura_linha * (len(linhas) - 1) / 2
        for i, linha in enumerate(linhas):
            self.desenho.text(
                self._p((posicao[0], topo + i * altura_linha)),
                linha,
                font=fonte(tamanho),
                fill=cor,
                anchor=ancora,
            )

    def largura_texto(self, conteudo: str, tamanho: int = TAMANHO_TEXTO) -> float:
        linhas = preparar(conteudo).split("\n")
        return max(fonte(tamanho).getlength(linha) for linha in linhas) / ESCALA

    def no(
        self,
        nome: str,
        x: float,
        y: float,
        texto: str,
        forma: str = "processo",
        largura: float | None = None,
        altura: float | None = None,
        preenchimento: str | None = None,
    ) -> No:
        linhas = texto.count("\n") + 1
        if largura is None:
            largura = self.largura_texto(texto) + (70 if forma == "decisao" else 32)
        if altura is None:
            altura = linhas * ALTURA_LINHA + (44 if forma == "decisao" else 18)
        if forma == "ponto":
            largura = altura = 8
        no = No(x, y, largura, altura, texto, forma)
        self.nos[nome] = no
        cor = PREENCHIMENTO.get(preenchimento or forma, PREENCHIMENTO["processo"])
        esq, topo = x - largura / 2, y - altura / 2
        dir_, base = x + largura / 2, y + altura / 2
        contorno = {"outline": TINTA, "width": 2 * ESCALA}
        if forma == "terminal":
            self.desenho.rounded_rectangle(
                [*self._p((esq, topo)), *self._p((dir_, base))],
                radius=round(altura / 2 * ESCALA),
                fill=cor,
                **contorno,
            )
        elif forma == "decisao":
            vertices = [(x, topo), (dir_, y), (x, base), (esq, y)]
            self.desenho.polygon([self._p(v) for v in vertices], fill=cor, **contorno)
        elif forma == "es":
            inclinacao = 14
            vertices = [
                (esq + inclinacao, topo),
                (dir_, topo),
                (dir_ - inclinacao, base),
                (esq, base),
            ]
            self.desenho.polygon([self._p(v) for v in vertices], fill=cor, **contorno)
        elif forma == "ponto":
            self.desenho.ellipse([*self._p((x - 4, y - 4)), *self._p((x + 4, y + 4))], fill=TINTA)
            return no
        else:
            raio = 6 if forma != "nota" else 0
            self.desenho.rounded_rectangle(
                [*self._p((esq, topo)), *self._p((dir_, base))],
                radius=raio * ESCALA,
                fill=cor,
                **contorno,
            )
        self.texto((x, y), texto)
        return no

    def linha(self, pontos: Sequence[Ponto], cor: Cor = TINTA, espessura: int = 2) -> None:
        self.desenho.line([self._p(p) for p in pontos], fill=cor, width=espessura * ESCALA)

    def ponta(self, de: Ponto, para: Ponto, cor: Cor = TINTA) -> None:
        angulo = math.atan2(para[1] - de[1], para[0] - de[0])
        tamanho, abertura = 12, math.radians(24)
        a = (
            para[0] - tamanho * math.cos(angulo - abertura),
            para[1] - tamanho * math.sin(angulo - abertura),
        )
        b = (
            para[0] - tamanho * math.cos(angulo + abertura),
            para[1] - tamanho * math.sin(angulo + abertura),
        )
        self.desenho.polygon([self._p(para), self._p(a), self._p(b)], fill=cor)

    def seta(
        self,
        origem: str,
        destino: str,
        rotulo: str | None = None,
        saida: str = "baixo",
        entrada: str = "cima",
        pontos: Sequence[Ponto] = (),
        posicao_rotulo: float = 0.5,
        tracejada: bool = False,
        segmento: int = 0,
        dupla: bool = False,
    ) -> None:
        inicio = self.nos[origem].porta(saida)
        fim = self.nos[destino].porta(entrada)
        if self.nos[destino].forma == "ponto":
            fim = (self.nos[destino].x, self.nos[destino].y)
        caminho = [inicio, *pontos, fim] if pontos else self._cotovelo(inicio, fim, saida, entrada)
        if tracejada:
            for a, b in zip(caminho, caminho[1:], strict=False):
                self._tracejado(a, b)
        else:
            self.linha(caminho)
        if self.nos[destino].forma != "ponto":
            self.ponta(caminho[-2], caminho[-1])
        if dupla:
            self.ponta(caminho[1], caminho[0])
        if rotulo:
            a, b = caminho[segmento], caminho[segmento + 1]
            meio = (a[0] + (b[0] - a[0]) * posicao_rotulo, a[1] + (b[1] - a[1]) * posicao_rotulo)
            self.rotulo(meio, rotulo)

    def _tracejado(self, a: Ponto, b: Ponto, traco: float = 8) -> None:
        comprimento = math.dist(a, b)
        passos = max(1, int(comprimento // traco))
        for i in range(0, passos, 2):
            t0, t1 = i / passos, min(1.0, (i + 1) / passos)
            p0 = (a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0)
            p1 = (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)
            self.linha([p0, p1])

    @staticmethod
    def _cotovelo(inicio: Ponto, fim: Ponto, saida: str, entrada: str) -> list[Ponto]:
        vertical_sai = saida in ("cima", "baixo")
        vertical_entra = entrada in ("cima", "baixo")
        (x0, y0), (x1, y1) = inicio, fim
        if vertical_sai and vertical_entra:
            if x0 == x1:
                return [inicio, fim]
            meio = (y0 + y1) / 2
            return [inicio, (x0, meio), (x1, meio), fim]
        if vertical_sai:
            return [inicio, (x0, y1), fim]
        if vertical_entra:
            return [inicio, (x1, y0), fim]
        if y0 == y1:
            return [inicio, fim]
        meio = (x0 + x1) / 2
        return [inicio, (meio, y0), (meio, y1), fim]

    def rotulo(self, centro: Ponto, conteudo: str, tamanho: int = 20) -> None:
        largura = self.largura_texto(conteudo, tamanho) + 10
        linhas = conteudo.count("\n") + 1
        altura = linhas * tamanho * ALTURA_LINHA / TAMANHO_TEXTO + 4
        x, y = centro
        self.desenho.rectangle(
            [
                *self._p((x - largura / 2, y - altura / 2)),
                *self._p((x + largura / 2, y + altura / 2)),
            ],
            fill=FUNDO,
        )
        self.texto(centro, conteudo, tamanho, cor=(60, 56, 72))

    def regiao(self, esq: float, topo: float, dir_: float, base: float, titulo: str, cor: Cor):
        """Retângulo de fundo agrupando nós (ex.: "depende do pygame")."""
        self.desenho.rounded_rectangle(
            [*self._p((esq, topo)), *self._p((dir_, base))],
            radius=10 * ESCALA,
            fill=cor,
            outline=CINZA_LINHA,
            width=ESCALA,
        )
        self.texto((esq + 12, topo + 16), titulo, 20, (70, 66, 82), ancora="lm")

    def salvar(self, nome: str) -> None:
        DESTINO.mkdir(parents=True, exist_ok=True)
        self.imagem.save(DESTINO / f"{nome}.png", optimize=True)
        print(f"gerado: figuras/{nome}.png")


# ---------------------------------------------------------------------------
# Fluxogramas
# ---------------------------------------------------------------------------


def fluxo_laco_principal() -> None:
    d = Diagrama(1000, 1110)
    d.no("inicio", 420, 40, "Início: python -m cobrinha", "terminal")
    d.no("init", 420, 130, "Jogo.__init__()\npygame.init() e set_mode((800, 600), SCALED)")
    d.no("menu", 420, 225, "navegacao.abrir_menu(jogo)\npilha = [Menu]")
    d.no("cond", 420, 340, "rodando e pilha\nnão está vazia?", "decisao", largura=270)
    d.no("tick", 420, 470, "dt = relogio.tick(60) / 1000\n(espera o quadro e mede o tempo)")
    d.no("eventos", 420, 570, "_processar_eventos()\nQUIT → sair   M → mudo   resto → tela do topo")
    d.no("sair", 420, 685, "pediu para\nsair?", "decisao", largura=270)
    d.no("atualizar", 420, 800, "estado_atual.atualizar(dt)\n(lógica da tela do topo)")
    d.no("fade", 420, 885, "opacidade_fade diminui (transição)")
    d.no(
        "desenhar", 420, 970, "_desenhar(): todas as telas da pilha,\nde baixo para cima, e o fade"
    )
    d.no(
        "flip", 420, 1065, "pygame.display.flip()\nmostra o quadro pronto", preenchimento="destaque"
    )
    d.no("quit", 820, 470, "finally:\npygame.quit()", preenchimento="alerta")
    d.no("fim", 820, 570, "Fim", "terminal")
    for a, b in (
        ("inicio", "init"),
        ("init", "menu"),
        ("menu", "cond"),
        ("tick", "eventos"),
        ("eventos", "sair"),
        ("atualizar", "fade"),
        ("fade", "desenhar"),
        ("desenhar", "flip"),
        ("quit", "fim"),
    ):
        d.seta(a, b)
    d.seta("cond", "tick", "sim")
    d.seta("sair", "atualizar", "não")
    d.seta("cond", "quit", "não", saida="direita", entrada="cima")
    d.seta(
        "sair",
        "quit",
        "sim",
        saida="direita",
        entrada="esquerda",
        pontos=((680, 685), (680, 470)),
        posicao_rotulo=0.4,
    )
    d.seta(
        "flip",
        "cond",
        "próximo quadro",
        saida="esquerda",
        entrada="esquerda",
        pontos=((70, 1065), (70, 340)),
        posicao_rotulo=0.7,
    )
    d.salvar("fluxo-laco-principal")


def fluxo_passo_fixo() -> None:
    d = Diagrama(960, 800)
    d.no("ini", 400, 40, "Partida.atualizar(dt)", "terminal")
    d.no("c1", 400, 150, "partida em\nandamento?", "decisao", largura=270)
    d.no("vazio", 790, 150, "devolve [ ]", "terminal")
    d.no("envelhecer", 400, 265, "envelhece fruta dourada,\npower-up e efeitos ativos (− dt)")
    d.no(
        "acumular",
        400,
        365,
        "limite = intervalo × 3\nacumulado = min(acumulado + dt, limite)",
        preenchimento="destaque",
    )
    d.no("c2", 400, 490, "acumulado ≥ intervalo\ne em andamento?", "decisao", largura=320)
    d.no("passo", 400, 620, "acumulado −= intervalo\neventos.append(passo())")
    d.no("relogio", 790, 490, "relógio do Contra o\ntempo: − min(dt, limite)")
    d.no("fim", 790, 620, "devolve eventos", "terminal")
    d.no(
        "nota",
        400,
        740,
        "intervalo = 1 / passos_por_segundo\n"
        "(velocidade do nível + aceleração; × 0,5 na câmera lenta)",
        "nota",
    )
    d.seta("ini", "c1")
    d.seta("c1", "vazio", "não", saida="direita", entrada="esquerda")
    d.seta("c1", "envelhecer", "sim")
    d.seta("envelhecer", "acumular")
    d.seta("acumular", "c2")
    d.seta("c2", "passo", "sim")
    d.seta(
        "passo",
        "c2",
        "repete",
        saida="esquerda",
        entrada="esquerda",
        pontos=((130, 620), (130, 490)),
        posicao_rotulo=0.6,
    )
    d.seta("c2", "relogio", "não", saida="direita", entrada="esquerda")
    d.seta("relogio", "fim")
    d.salvar("fluxo-passo-fixo")


def fluxo_estados() -> None:
    d = Diagrama(960, 880)
    d.regiao(20, 380, 940, 860, "lilás: empilhadas sobre Jogando", (250, 248, 252))
    d.no("recordes", 140, 70, "Recordes", "terminal")
    d.no("opcoes", 380, 70, "Opções", "terminal")
    d.no("creditos", 620, 70, "Créditos", "terminal")
    d.no("menu", 380, 250, "Menu principal", "terminal", largura=220, preenchimento="destaque")
    d.no("contagem", 380, 470, "Contagem 3-2-1", "terminal", largura=220, preenchimento="empilhada")
    d.no("jogando", 380, 620, "Jogando", "terminal", largura=220)
    d.no("pausa", 760, 620, "Pausa", "terminal", largura=180, preenchimento="empilhada")
    d.no("nivel", 230, 790, "Nível concluído", "terminal", largura=220, preenchimento="empilhada")
    d.no("fimp", 600, 790, "Fim de partida", "terminal", largura=220, preenchimento="empilhada")
    for tela in ("recordes", "opcoes", "creditos"):
        d.seta("menu", tela, saida="cima", entrada="baixo", dupla=True)
    d.seta("menu", "contagem", "Jogar")
    d.seta("contagem", "jogando", "3-2-1 ou Enter")
    d.seta("jogando", "pausa", "Esc, P ou\nperdeu o foco", saida="direita", entrada="esquerda")
    d.seta(
        "pausa",
        "contagem",
        "Continuar",
        saida="cima",
        entrada="direita",
        posicao_rotulo=0.5,
    )
    d.seta("jogando", "nivel", "meta atingida", saida="baixo", entrada="cima")
    d.seta("jogando", "fimp", "bateu, venceu ou\ntempo esgotado", saida="baixo", entrada="cima")
    d.seta(
        "nivel",
        "contagem",
        "Próximo nível",
        saida="esquerda",
        entrada="esquerda",
        pontos=((100, 790), (100, 470)),
        segmento=1,
    )
    d.seta(
        "fimp",
        "menu",
        "Menu principal",
        saida="direita",
        entrada="direita",
        pontos=((870, 790), (870, 250)),
        segmento=1,
    )
    d.rotulo((660, 300), "trocar_estado(): a pilha recomeça\nempilhar(): a tela vai por cima", 18)
    d.salvar("fluxo-estados")


def fluxo_passo_partida() -> None:
    d = Diagrama(1000, 1540)
    x, saida_x = 330, 750
    d.no("ini", x, 40, "Partida.passo()", "terminal")
    d.no("dir", x, 130, "direção = próxima da fila (J1)\nnova = cabeça.vizinha(direção)")
    d.no("c1", x, 245, "modo Sem\nbordas?", "decisao", largura=200)
    d.no("envolver", 680, 245, "nova = grade.envolver(nova)\n(coluna % 32, linha % 22)")
    d.no("j1", x, 340, "", "ponto")
    d.no("c2", x, 460, "fora da grade,\nna pedra ou\nno corpo?", "decisao", largura=270)
    d.no("bateu", saida_x, 460, "DERROTA\n→ Evento.BATEU", "terminal", preenchimento="alerta")
    d.no("avancar", x, 580, "cobra.avancar(nova)\n(cauda sai, cabeça entra)")
    d.no("c3", x, 690, "na fruta\ndourada?", "decisao", largura=210)
    d.no("dourada", saida_x, 690, "+5 × multiplicador, cresce, +5 s\n→ COMEU_DOURADA (ou VENCEU)")
    d.no("c4", x, 810, "no power-up?", "decisao", largura=210)
    d.no("power", saida_x, 810, "aplica o efeito (encolher\nou duração) → PEGOU_POWER_UP")
    d.no("c5", x, 925, "na comida?", "decisao", largura=200)
    d.no("moveu", saida_x, 925, "→ Evento.MOVEU", "terminal")
    d.no("comer", x, 1040, "comer: + multiplicador, cresce,\n+3 s, comidas_no_nivel += 1")
    d.no("c6", x, 1155, "campo vai\nficar cheio?", "decisao", largura=220)
    d.no("venceu", saida_x, 1155, "VITÓRIA → VENCEU", "terminal", preenchimento="destaque")
    d.no("c7", x, 1280, "meta do nível\natingida?", "decisao", largura=270)
    d.no("meta", saida_x, 1280, "último nível? VENCEU\nsenão: CONCLUIU_NIVEL", "terminal")
    d.no("sortear", x, 1395, "sorteia nova comida; chance de\nfruta dourada (10%) e power-up (8%)")
    d.no("comeu", x, 1490, "→ Evento.COMEU", "terminal")
    d.seta("ini", "dir")
    d.seta("dir", "c1")
    d.seta("c1", "envolver", "sim", saida="direita", entrada="esquerda")
    d.seta("envolver", "j1", saida="baixo", entrada="direita")
    d.seta("c1", "j1", "não")
    d.desenho.line([d._p((x, 340)), d._p(d.nos["c2"].porta("cima"))], fill=TINTA, width=2 * ESCALA)
    d.ponta((x, 340), d.nos["c2"].porta("cima"))
    d.seta("c2", "bateu", "sim", saida="direita", entrada="esquerda")
    d.seta("c2", "avancar", "não")
    d.seta("avancar", "c3")
    d.seta("c3", "dourada", "sim", saida="direita", entrada="esquerda")
    d.seta("c3", "c4", "não")
    d.seta("c4", "power", "sim", saida="direita", entrada="esquerda")
    d.seta("c4", "c5", "não")
    d.seta("c5", "moveu", "não", saida="direita", entrada="esquerda")
    d.seta("c5", "comer", "sim")
    d.seta("comer", "c6")
    d.seta("c6", "venceu", "sim", saida="direita", entrada="esquerda")
    d.seta("c6", "c7", "não")
    d.seta("c7", "meta", "sim", saida="direita", entrada="esquerda")
    d.seta("c7", "sortear", "não")
    d.seta("sortear", "comeu")
    d.salvar("fluxo-passo-partida")


def fluxo_pipeline_quadro() -> None:
    d = Diagrama(1000, 950)
    x = 300
    etapas = [
        ("fill", "tela.fill(PRETO)", "processo"),
        ("hud", "1. HUD: faixa de 50 px no topo", "processo"),
        ("fundo", "2. blit do fundo pré-renderizado\n(xadrez de grama + pedras)", "processo"),
        ("veu", "3. véu azul (só na câmera lenta)", "processo"),
        ("itens", "4. comida, fruta dourada e power-up\n(flutuando e piscando)", "processo"),
        ("cobra", "5. cobra, da cauda para a cabeça", "processo"),
        ("textos", "6. textos flutuantes (+1, X2!)", "processo"),
        ("empilhada", "7. telas empilhadas (ex.: Pausa):\nvéu escuro α = 170 + menu", "empilhada"),
        ("fade", "8. fade de transição (set_alpha)", "processo"),
        ("flip", "pygame.display.flip()", "destaque"),
    ]
    d.regiao(70, 95, 530, 625, "", (246, 250, 242))
    y = 50
    for nome, texto, cor in etapas:
        d.no(nome, x, y, texto, largura=420, preenchimento=cor)
        y += 102 if "\n" in texto else 92
    nomes = [e[0] for e in etapas]
    for a, b in zip(nomes, nomes[1:], strict=False):
        d.seta(a, b)
    d.texto((80, 642), "EstadoJogando.desenhar()", 18, (70, 66, 82), ancora="lm")
    _camadas(d, 640, 140)
    d.salvar("fluxo-pipeline-quadro")


def _camadas(d: Diagrama, esq: float, topo: float) -> None:
    """Pilha de camadas em perspectiva: a de baixo é pintada primeiro."""
    camadas = [
        ("fade (preto, α variável)", (40, 36, 46)),
        ("véu da pausa (α = 170)", (90, 86, 100)),
        ("textos flutuantes", Paleta.AMARELO),
        ("cobra", Paleta.VERDE),
        ("comida e itens", Paleta.VERMELHO),
        ("véu azul (α = 40)", Paleta.AZUL_CLARO),
        ("fundo: grama + pedras", Paleta.GRAMA_CLARA),
        ("HUD", Paleta.CINZA_ESCURO),
    ]
    largura, altura, inclinacao, passo = 230, 46, 50, 84
    for i, (nome, cor) in enumerate(reversed(camadas)):
        y = topo + (len(camadas) - 1 - i) * passo
        vertices = [
            (esq + inclinacao, y),
            (esq + inclinacao + largura, y),
            (esq + largura, y + altura),
            (esq, y + altura),
        ]
        d.desenho.polygon([d._p(v) for v in vertices], fill=cor, outline=TINTA, width=2 * ESCALA)
        d.rotulo((esq + inclinacao / 2 + largura / 2, y + altura + 14), nome, 18)
    d.linha([(esq - 20, topo + 8 * passo - 30), (esq - 20, topo)])
    d.ponta((esq - 20, topo + 30), (esq - 20, topo))
    d.texto((esq - 34, topo + 4 * passo), "ordem\nde\npintura", 18, ancora="rm")


def diagrama_arquitetura() -> None:
    d = Diagrama(1000, 660)
    d.regiao(20, 20, 740, 420, "depende do pygame (visão e infraestrutura)", (240, 246, 252))
    d.regiao(20, 450, 740, 640, "não importa o pygame (modelo, testável)", (246, 250, 240))
    d.no("jogo", 370, 90, "jogo.py\nlaço principal e pilha de estados", preenchimento="destaque")
    d.no("estados", 180, 215, "estados/\ntelas (menu, jogando...)")
    d.no("ui", 560, 215, "ui/\nHUD, campo, sprites, texto")
    d.no("infra", 560, 345, "recursos.py · audio.py\npersistencia.py")
    d.no(
        "dominio",
        370,
        555,
        "dominio/\ngrade, cobra, comida, níveis,\npower-ups, progresso, partida",
    )
    d.no("ferramentas", 880, 120, "ferramentas/\ngerar_sprites.py\ngerar_sons.py")
    d.no("assets", 880, 345, "assets/\nPNG · WAV · TTF", "es")
    d.no("testes", 880, 555, "tests/ (pytest)\n240 testes")
    d.seta("jogo", "estados")
    d.seta("estados", "ui", "desenha com", saida="direita", entrada="esquerda")
    d.seta("ui", "infra", "usa")
    d.seta("estados", "dominio", "cria e comanda a Partida", segmento=1)
    d.seta("ferramentas", "assets", "geram")
    d.seta("assets", "infra", "carrega", saida="esquerda", entrada="direita")
    d.seta("testes", "dominio", "verificam", saida="esquerda", entrada="direita")
    d.salvar("diagrama-arquitetura")


def linha_do_tempo() -> None:
    eventos = [
        ("2025", "V1 em grupo\n(disciplina de CG)"),
        ("02/10/2026", "briefing e\nFases 0 a 5 (V2)"),
        ("02/10 11:43", "release\nv2.0.0"),
        ("02/10 22:44", "movimento\ninterpolado (PR 2)"),
        ("02/10 22:55", "power-ups\n(PR 3)"),
        ("02/10 23:07", "volta ao passo\ndiscreto (PR 4)"),
        ("03/10 10:24", "release\nv3.0.0"),
        ("03/10 13:42", "Contra o tempo,\nJoão Pedro (PR 8)"),
        ("03/10 14:56", "release\nv3.1.0"),
    ]
    d = Diagrama(1200, 330)
    eixo_y, esq, dir_ = 165, 70, 1130
    d.linha([(esq - 30, eixo_y), (dir_ + 30, eixo_y)], espessura=3)
    d.ponta((dir_, eixo_y), (dir_ + 40, eixo_y))
    passo = (dir_ - esq) / (len(eventos) - 1)
    for i, (data, texto) in enumerate(eventos):
        x = esq + i * passo
        release = texto.startswith("release")
        cor = Paleta.AMARELO if release else Paleta.VERDE_CLARO
        d.desenho.ellipse(
            [*d._p((x - 9, eixo_y - 9)), *d._p((x + 9, eixo_y + 9))],
            fill=cor,
            outline=TINTA,
            width=2 * ESCALA,
        )
        acima = i % 2 == 0
        y_texto = eixo_y - 80 if acima else eixo_y + 80
        d.linha(
            [(x, eixo_y + (-12 if acima else 12)), (x, y_texto + (28 if acima else -28))],
            cor=CINZA_LINHA,
        )
        d.texto((x, y_texto), texto, 19)
        d.texto((x, eixo_y + (24 if acima else -24)), data, 17, (90, 86, 100))
    d.salvar("linha-do-tempo")


# ---------------------------------------------------------------------------
# Diagramas geométricos
# ---------------------------------------------------------------------------


def diagrama_coordenadas() -> None:
    d = Diagrama(1060, 770)
    ox, oy, s = 120, 70, 1.0  # a janela de 800 × 600 em escala 1:1 (unidades lógicas)
    janela = (ox, oy, ox + 800 * s, oy + 600 * s)
    d.desenho.rectangle([*d._p(janela[:2]), *d._p(janela[2:])], fill=(236, 246, 226))
    d.desenho.rectangle([*d._p((ox, oy)), *d._p((ox + 800, oy + 50))], fill=(70, 66, 82))
    d.texto((ox + 400, oy + 25), "HUD: y de 0 a 49", 20, Paleta.BRANCO)
    for coluna in range(33):
        x = ox + coluna * 25
        d.linha([(x, oy + 50), (x, oy + 600)], cor=(196, 214, 180), espessura=1)
    for linha in range(23):
        y = oy + 50 + linha * 25
        d.linha([(ox, y), (ox + 800, y)], cor=(196, 214, 180), espessura=1)
    d.desenho.rectangle([*d._p(janela[:2]), *d._p(janela[2:])], outline=TINTA, width=2 * ESCALA)
    # Célula (4, 3) destacada.
    cx, cy = ox + 4 * 25, oy + 50 + 3 * 25
    d.desenho.rectangle([*d._p((cx, cy)), *d._p((cx + 25, cy + 25))], fill=Paleta.VERMELHO)
    d.desenho.ellipse([*d._p((cx - 4, cy - 4)), *d._p((cx + 4, cy + 4))], fill=TINTA)
    d.rotulo(
        (cx + 215, cy + 75),
        "célula (coluna 4, linha 3)\n→ pixel (4 × 25, 50 + 3 × 25)\n= (100, 125)",
        20,
    )
    d.linha([(cx + 4, cy + 4), (cx + 110, cy + 45)], cor=TINTA)
    # Eixos.
    d.linha([(ox, oy - 30), (ox + 860, oy - 30)], espessura=2)
    d.ponta((ox + 840, oy - 30), (ox + 870, oy - 30))
    d.texto((ox + 880, oy - 30), "x", 24, ancora="lm")
    d.linha([(ox - 40, oy), (ox - 40, oy + 650)], espessura=2)
    d.ponta((ox - 40, oy + 630), (ox - 40, oy + 660))
    d.texto((ox - 40, oy + 675), "y", 24)
    d.texto((ox, oy - 48), "(0, 0)", 18)
    d.texto((ox + 800, oy - 48), "800", 18)
    d.texto((ox - 52, oy + 600), "600", 18, ancora="rm")
    d.texto((ox - 52, oy + 50), "50", 18, ancora="rm")
    d.texto((ox + 400, oy + 625), "32 colunas × 22 linhas de 25 px (campo de 800 × 550)", 20)
    d.salvar("diagrama-coordenadas")


def diagrama_envolvimento() -> None:
    d = Diagrama(1160, 440)
    colunas, linhas, t = 10, 6, 50
    for painel, (ox, titulo) in enumerate(((60, "passo n"), (600, "passo n + 1"))):
        oy = 60
        d.texto((ox + colunas * t / 2, oy - 30), titulo, 22)
        for c in range(colunas):
            for li in range(linhas):
                cor = Paleta.GRAMA_CLARA if (c + li) % 2 == 0 else Paleta.GRAMA_ESCURA
                d.desenho.rectangle(
                    [
                        *d._p((ox + c * t, oy + li * t)),
                        *d._p((ox + (c + 1) * t, oy + (li + 1) * t)),
                    ],
                    fill=cor,
                )
        corpo = [(9, 2), (8, 2), (7, 2)] if painel == 0 else [(0, 2), (9, 2), (8, 2)]
        for i, (c, li) in enumerate(corpo):
            cor = Paleta.VERDE_ESCURO if i == 0 else Paleta.VERDE
            d.desenho.rectangle(
                [
                    *d._p((ox + c * t + 5, oy + li * t + 5)),
                    *d._p((ox + (c + 1) * t - 5, oy + (li + 1) * t - 5)),
                ],
                fill=cor,
                outline=TINTA,
                width=2 * ESCALA,
            )
        d.desenho.rectangle(
            [*d._p((ox, oy)), *d._p((ox + colunas * t, oy + linhas * t))],
            outline=TINTA,
            width=2 * ESCALA,
        )
    # Seta saindo pela direita e entrando pela esquerda.
    vermelho = Paleta.VERMELHO
    d.linha([(600 + 10 * 50 + 4, 185), (600 + 10 * 50 + 30, 185)], cor=vermelho, espessura=3)
    d.linha([(600 - 30, 185), (600 - 4, 185)], cor=vermelho, espessura=3)
    d.ponta((600 - 30, 185), (600 - 2, 185), vermelho)
    d.texto(
        (570, 395),
        "cabeça em (9, 2) indo para a direita → vizinha (10, 2)\n"
        "→ envolver: (10 % 10, 2 % 6) = (0, 2)",
        20,
    )
    d.salvar("diagrama-envolvimento")


# ---------------------------------------------------------------------------
# Gráficos simples (eixos, linhas e marcadores)
# ---------------------------------------------------------------------------


class Grafico:
    def __init__(
        self,
        d: Diagrama,
        caixa: tuple[float, float, float, float],
        xlim: tuple[float, float],
        ylim: tuple[float, float],
        titulo: str,
        rotulo_x: str,
        rotulo_y: str,
    ) -> None:
        self.d, self.caixa, self.xlim, self.ylim = d, caixa, xlim, ylim
        esq, topo, dir_, base = caixa
        d.linha([(esq, topo), (esq, base), (dir_, base)], espessura=2)
        d.texto(((esq + dir_) / 2, topo - 22), titulo, 21)
        d.texto(((esq + dir_) / 2, base + 40), rotulo_x, 19, (70, 66, 82))
        d.texto((esq - 12, topo - 4), rotulo_y, 19, (70, 66, 82), ancora="rs")

    def mapa(self, x: float, y: float) -> Ponto:
        esq, topo, dir_, base = self.caixa
        fx = (x - self.xlim[0]) / (self.xlim[1] - self.xlim[0])
        fy = (y - self.ylim[0]) / (self.ylim[1] - self.ylim[0])
        return esq + fx * (dir_ - esq), base - fy * (base - topo)

    def marcas(self, xs: Sequence[float], ys: Sequence[float], formato: Callable[[float], str]):
        esq, _, _, base = self.caixa
        for x in xs:
            px, _ = self.mapa(x, self.ylim[0])
            self.d.linha([(px, base), (px, base + 6)])
            self.d.texto((px, base + 18), formato(x), 17, (70, 66, 82))
        for y in ys:
            _, py = self.mapa(self.xlim[0], y)
            self.d.linha([(esq - 6, py), (esq, py)])
            self.d.texto((esq - 10, py), formato(y), 17, (70, 66, 82), ancora="rm")

    def curva(self, pontos: Sequence[Ponto], cor: Cor, espessura: int = 2) -> None:
        self.d.linha([self.mapa(x, y) for x, y in pontos], cor=cor, espessura=espessura)

    def horizontal(self, y: float, cor: Cor, rotulo: str = "") -> None:
        a, b = self.mapa(self.xlim[0], y), self.mapa(self.xlim[1], y)
        self.d._tracejado(a, b)
        if rotulo:
            self.d.texto((b[0] - 4, b[1] - 12), rotulo, 17, cor, ancora="rm")

    def pontos(self, pontos: Sequence[Ponto], cor: Cor, raio: float = 4) -> None:
        for x, y in pontos:
            px, py = self.mapa(x, y)
            self.d.desenho.ellipse(
                [*self.d._p((px - raio, py - raio)), *self.d._p((px + raio, py + raio))], fill=cor
            )


def grafico_acumulador() -> None:
    """Simula o acumulador da Partida: quadros a 60 FPS e passos a 8 por segundo."""
    dt, intervalo, total = 1 / 60, 1 / 8, 0.6
    d = Diagrama(1000, 420)
    g = Grafico(
        d,
        (110, 60, 960, 330),
        (0, total),
        (0, 0.15),
        "acumulador ao longo do tempo",
        "tempo (s)",
        "acumulado (s)",
    )
    g.marcas(
        [0.1 * i for i in range(7)], [0, 0.05, 0.1, 0.125], lambda v: f"{v:g}".replace(".", ",")
    )
    g.horizontal(intervalo, Paleta.VERMELHO, "intervalo do passo = 0,125 s")
    acumulado, tempo, linha, passos = 0.0, 0.0, [(0.0, 0.0)], []
    while tempo < total - 1e-9:
        tempo += dt
        acumulado += dt
        linha.append((tempo, acumulado))
        while acumulado >= intervalo - 1e-9:
            acumulado -= intervalo
            passos.append((tempo, acumulado))
            linha.append((tempo, acumulado))
    g.curva(linha, Paleta.AZUL, 2)
    g.pontos([(t, 0.0) for t, _ in passos], Paleta.VERMELHO, 5)
    quadros = [(i * dt, 0.0) for i in range(int(total / dt) + 1)]
    for t, _ in quadros:
        px, py = g.mapa(t, 0)
        d.linha([(px, py - 4), (px, py)], cor=CINZA_LINHA, espessura=1)
    d.texto(
        (960, 395),
        "traços cinza: quadros (60 por segundo)   pontos vermelhos: passos da cobra",
        18,
        (70, 66, 82),
        ancora="rm",
    )
    d.salvar("grafico-acumulador")


def grafico_animacoes() -> None:
    d = Diagrama(1000, 900)
    # (a) Flutuação da comida: round(sin(4 t)).
    g = Grafico(
        d,
        (110, 60, 960, 220),
        (0, 3),
        (-1.5, 1.5),
        "(a) flutuação da comida: deslocamento = round(sen(4 t))",
        "tempo (s)",
        "y (px)",
    )
    g.marcas([0, 0.5, 1, 1.5, 2, 2.5, 3], [-1, 0, 1], lambda v: f"{v:g}".replace(".", ","))
    amostras = [i / 200 * 3 for i in range(201)]
    g.curva([(t, math.sin(4 * t)) for t in amostras], CINZA_LINHA, 1)
    g.curva([(t, round(math.sin(4 * t))) for t in amostras], Paleta.VERMELHO, 3)
    # (b) Pisca-pisca: int(t * 8) % 2 nos últimos 1,5 s.
    g = Grafico(
        d,
        (110, 340, 960, 480),
        (0, 1.5),
        (0, 1.4),
        "(b) item sumindo: visível quando int(t × 8) % 2 == 0",
        "tempo (s)",
        "visível",
    )
    g.marcas([0, 0.25, 0.5, 0.75, 1, 1.25, 1.5], [0, 1], lambda v: f"{v:g}".replace(".", ","))
    pontos: list[Ponto] = []
    for i in range(301):
        t = i / 200
        visivel = 1.0 if int(t * 8) % 2 == 0 else 0.0
        if pontos and pontos[-1][1] != visivel:
            pontos.append((t, pontos[-1][1]))
        pontos.append((t, visivel))
    g.curva(pontos, Paleta.LARANJA, 3)
    # (c) Texto flutuante: alfa = 255 (1 − p²) e subida de 30 px.
    g = Grafico(
        d,
        (110, 620, 960, 800),
        (0, 0.8),
        (0, 255),
        "(c) texto flutuante: alfa = 255 × (1 − p²), p = idade / 0,8 s",
        "idade (s)",
        "alfa",
    )
    g.marcas([0, 0.2, 0.4, 0.6, 0.8], [0, 128, 255], lambda v: f"{v:g}".replace(".", ","))
    g.curva([(i / 100 * 0.8, 255 * (1 - (i / 100) ** 2)) for i in range(101)], Paleta.AZUL, 3)
    g.curva([(i / 100 * 0.8, 255 * (i / 100)) for i in range(101)], CINZA_LINHA, 2)
    d.texto(
        (960, 860),
        "azul: opacidade   cinza: subida (0 a 30 px, fora de escala)",
        18,
        (70, 66, 82),
        ancora="rm",
    )
    d.salvar("grafico-animacoes")


def grafico_interpolacao() -> None:
    """Posição da cabeça na lógica (degraus) e no desenho interpolado (rampa atrasada)."""
    intervalo, total = 0.125, 0.75
    d = Diagrama(1000, 470)
    g = Grafico(
        d,
        (110, 60, 960, 360),
        (0, total),
        (0, 6.5),
        "posição da cabeça (em células) ao longo do tempo",
        "tempo (s)",
        "coluna",
    )
    g.marcas(
        [0.125 * i for i in range(7)], [0, 1, 2, 3, 4, 5, 6], lambda v: f"{v:g}".replace(".", ",")
    )
    logica: list[Ponto] = []
    desenho: list[Ponto] = []
    for i in range(int(total / intervalo)):
        t0, t1 = i * intervalo, (i + 1) * intervalo
        logica += [(t0, i + 1), (t1, i + 1)]
        desenho += [(t0, i), (t1, i + 1)]
    g.curva(logica, Paleta.VERMELHO, 3)
    g.curva(desenho, Paleta.AZUL, 3)
    d.texto(
        (960, 425),
        "vermelho: célula na lógica (discreta)   azul: posição desenhada (interpolada)",
        18,
        (70, 66, 82),
        ancora="rm",
    )
    d.texto(
        (960, 450),
        "a distância vertical entre as curvas é o atraso visual: até 1 célula",
        18,
        (70, 66, 82),
        ancora="rm",
    )
    d.salvar("grafico-interpolacao")


def grafico_ondas() -> None:
    """Formas de onda do gerar_sons.py: quadrada e triangular com envelope e amostras."""
    d = Diagrama(1000, 640)
    taxa, freq, duracao = 22_050, 440.0, 0.01
    total = int(duracao * taxa)

    def envelope(i: int) -> float:
        tempo, restante = i / taxa, (total - i) / taxa
        return min(1.0, tempo / 0.002, restante / 0.003)

    quadrada = [(1.0 if (i * freq / taxa) % 1 < 0.5 else -1.0) * envelope(i) for i in range(total)]
    triangular = [(4 * abs((i * freq / taxa) % 1 - 0.5) - 1) * envelope(i) for i in range(total)]
    for indice, (titulo, amostras, cor) in enumerate(
        (
            ("onda quadrada (ciclo ativo 50%) com envelope", quadrada, Paleta.VERMELHO),
            ("onda triangular com envelope", triangular, Paleta.AZUL),
        )
    ):
        topo = 60 + indice * 300
        g = Grafico(
            d,
            (110, topo, 960, topo + 200),
            (0, duracao * 1000),
            (-1.2, 1.2),
            titulo,
            "tempo (ms)",
            "amostra",
        )
        g.marcas([0, 2, 4, 6, 8, 10], [-1, 0, 1], lambda v: f"{v:g}")
        g.curva([(i / taxa * 1000, a) for i, a in enumerate(amostras)], cor, 2)
        g.pontos([(i / taxa * 1000, a) for i, a in enumerate(amostras) if i % 6 == 0], TINTA, 2)
    d.salvar("grafico-ondas")


# ---------------------------------------------------------------------------
# Figuras a partir dos sprites e da paleta
# ---------------------------------------------------------------------------

SPRITES = [
    ("cabeca", "cabeça"),
    ("corpo_reto", "corpo reto"),
    ("corpo_curva", "curva"),
    ("cauda", "cauda"),
    ("comida", "maçã"),
    ("comida_dourada", "maçã dourada"),
    ("parede", "pedra"),
    ("power_camera_lenta", "câmera lenta"),
    ("power_pontos_em_dobro", "pontos em dobro"),
    ("power_encolher", "encolher"),
]


def ampliar(imagem: Image.Image, fator: int, metodo=Image.Resampling.NEAREST) -> Image.Image:
    return imagem.resize((imagem.width * fator, imagem.height * fator), metodo)


def xadrez_transparencia(largura: int, altura: int, lado: int) -> Image.Image:
    fundo = Image.new("RGB", (largura, altura), (236, 236, 236))
    desenho = ImageDraw.Draw(fundo)
    for y in range(0, altura, lado):
        for x in range(0, largura, lado):
            if (x // lado + y // lado) % 2:
                desenho.rectangle([x, y, x + lado - 1, y + lado - 1], fill=(206, 206, 206))
    return fundo


def folha_de_sprites() -> None:
    fator = 8  # 25 px → 200 px; × ESCALA para o PDF
    lado = 25 * fator * ESCALA // 2
    colunas, margem = 5, 30 * ESCALA
    largura = colunas * (lado + margem) + margem
    altura = 2 * (lado + 70 * ESCALA) + margem
    folha = Image.new("RGB", (largura, altura), FUNDO)
    desenho = ImageDraw.Draw(folha)
    for i, (nome, legenda) in enumerate(SPRITES):
        sprite = Image.open(IMAGENS / f"{nome}.png").convert("RGBA")
        grande = ampliar(sprite, lado // 25)
        x = margem + (i % colunas) * (lado + margem)
        y = margem + (i // colunas) * (lado + 70 * ESCALA)
        base = xadrez_transparencia(grande.width, grande.height, lado // 25)
        base.paste(grande, (0, 0), grande)
        folha.paste(base, (x, y))
        desenho.rectangle([x, y, x + grande.width - 1, y + grande.height - 1], outline=CINZA_LINHA)
        desenho.text(
            (x + grande.width // 2, y + grande.height + 24 * ESCALA),
            legenda,
            font=fonte(22),
            fill=TINTA,
            anchor="mm",
        )
    DESTINO.mkdir(parents=True, exist_ok=True)
    folha.save(DESTINO / "sprites-ampliados.png", optimize=True)
    print("gerado: figuras/sprites-ampliados.png")


def curva_por_distancia() -> None:
    """A curva do corpo com os círculos de raio 4 e 21 centrados no canto inferior esquerdo."""
    fator = 24
    sprite = Image.open(IMAGENS / "corpo_curva.png").convert("RGBA")
    grande = ampliar(sprite, fator)
    base = xadrez_transparencia(grande.width, grande.height, fator).convert("RGBA")
    base.alpha_composite(grande)
    desenho = ImageDraw.Draw(base)
    for i in range(26):
        desenho.line([(i * fator, 0), (i * fator, 25 * fator)], fill=(180, 180, 190), width=1)
        desenho.line([(0, i * fator), (25 * fator, i * fator)], fill=(180, 180, 190), width=1)
    centro = (0, 25 * fator)
    for raio, cor in ((4, Paleta.VERMELHO), (21, Paleta.AZUL)):
        r = raio * fator
        desenho.ellipse(
            [centro[0] - r, centro[1] - r, centro[0] + r, centro[1] + r], outline=cor, width=4
        )
    desenho.ellipse([centro[0] - 10, centro[1] - 10, centro[0] + 10, centro[1] + 10], fill=TINTA)
    margem = 40
    final = Image.new("RGB", (base.width + 2 * margem + 420, base.height + 2 * margem), FUNDO)
    final.paste(base.convert("RGB"), (margem, margem))
    texto = ImageDraw.Draw(final)
    legenda = (
        "centro: canto (0, 25)\n\n"
        "vermelho: raio 4\n(início do corpo)\n\n"
        "azul: raio 21\n(4 + 17 de espessura)\n\n"
        "pixel pintado se\n0 ≤ ⌊d − 4⌋ < 17,\n"
        "com d = hypot(x + 0,5,\n  y + 0,5 − 25)"
    )
    texto.multiline_text(
        (base.width + 2 * margem, margem + 20),
        preparar(legenda),
        font=fonte(16),
        fill=TINTA,
        spacing=10,
    )
    final.save(DESTINO / "curva-distancia.png", optimize=True)
    print("gerado: figuras/curva-distancia.png")


def escala_vizinho_bilinear() -> None:
    sprite = Image.open(IMAGENS / "comida.png").convert("RGBA")
    fator = 16
    paineis = [
        ("original (25 × 25)", sprite.resize((25 * 2, 25 * 2), Image.Resampling.NEAREST), True),
        ("vizinho mais próximo × 16", ampliar(sprite, fator), False),
        ("bilinear × 16", ampliar(sprite, fator, Image.Resampling.BILINEAR), False),
    ]
    lado, margem = 25 * fator, 40
    final = Image.new("RGB", (3 * lado + 4 * margem, lado + 2 * margem + 50), FUNDO)
    desenho = ImageDraw.Draw(final)
    for i, (titulo, imagem, pequeno) in enumerate(paineis):
        x = margem + i * (lado + margem)
        base = xadrez_transparencia(imagem.width, imagem.height, 16).convert("RGBA")
        base.alpha_composite(imagem)
        destino = (
            (x + (lado - imagem.width) // 2, margem + (lado - imagem.height) // 2)
            if pequeno
            else (x, margem)
        )
        final.paste(base.convert("RGB"), destino)
        desenho.text(
            (x + lado // 2, margem + lado + 28), titulo, font=fonte(24), fill=TINTA, anchor="mm"
        )
    final.save(DESTINO / "escala-vizinho-bilinear.png", optimize=True)
    print("gerado: figuras/escala-vizinho-bilinear.png")


def paleta() -> None:
    cores = [(nome, valor) for nome, valor in vars(Paleta).items() if nome.isupper()]
    colunas, lado, margem = 4, 150, 24
    linhas = math.ceil(len(cores) / colunas)
    d = Diagrama(colunas * (lado + margem) + margem, linhas * (lado + 70) + margem)
    for i, (nome, (r, g, b)) in enumerate(cores):
        x = margem + (i % colunas) * (lado + margem)
        y = margem + (i // colunas) * (lado + 70)
        d.desenho.rectangle(
            [*d._p((x, y)), *d._p((x + lado, y + lado - 40))],
            fill=(r, g, b),
            outline=TINTA,
            width=ESCALA,
        )
        d.texto((x + lado / 2, y + lado - 18), nome, 19)
        d.texto((x + lado / 2, y + lado + 4), f"({r}, {g}, {b})", 18, (70, 66, 82))
    d.salvar("paleta")


FIGURAS: dict[str, Callable[[], None]] = {
    "fluxo-laco-principal": fluxo_laco_principal,
    "fluxo-passo-fixo": fluxo_passo_fixo,
    "fluxo-estados": fluxo_estados,
    "fluxo-passo-partida": fluxo_passo_partida,
    "fluxo-pipeline-quadro": fluxo_pipeline_quadro,
    "diagrama-arquitetura": diagrama_arquitetura,
    "linha-do-tempo": linha_do_tempo,
    "diagrama-coordenadas": diagrama_coordenadas,
    "diagrama-envolvimento": diagrama_envolvimento,
    "grafico-acumulador": grafico_acumulador,
    "grafico-animacoes": grafico_animacoes,
    "grafico-interpolacao": grafico_interpolacao,
    "grafico-ondas": grafico_ondas,
    "sprites-ampliados": folha_de_sprites,
    "curva-distancia": curva_por_distancia,
    "escala-vizinho-bilinear": escala_vizinho_bilinear,
    "paleta": paleta,
}


def main() -> None:
    for gerar in FIGURAS.values():
        gerar()


if __name__ == "__main__":
    main()
