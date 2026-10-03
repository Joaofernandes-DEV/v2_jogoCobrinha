"""Grava o GIF de demonstração do README (docs/demo.gif) jogando o jogo de verdade, sem janela.

Uso: python ferramentas/gravar_demo.py
Requer: pip install -e ".[ferramentas]"

Um "piloto automático" busca a comida pelo caminho mais curto (busca em largura),
desviando do corpo e das pedras. Roteiro: menu → contagem do nível 2 → partida
(com uma fruta dourada e os power-ups de câmera lenta e pontos em dobro) → batida
proposital → tela de fim. A semente é fixa, então
o GIF sai sempre igual.
"""

import os
import sys
import tempfile
from collections import deque
from pathlib import Path

os.environ.update(
    SDL_VIDEODRIVER="dummy",
    SDL_AUDIODRIVER="dummy",
    COBRINHA_DADOS=tempfile.mkdtemp(prefix="cobrinha-demo-"),
)

import pygame  # noqa: E402
from PIL import Image  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from cobrinha.dominio.grade import Direcao, Posicao  # noqa: E402
from cobrinha.dominio.partida import FrutaDourada, Partida  # noqa: E402
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp  # noqa: E402
from cobrinha.estados import navegacao  # noqa: E402
from cobrinha.estados.jogando import EstadoJogando  # noqa: E402
from cobrinha.jogo import Jogo  # noqa: E402

DESTINO = RAIZ / "docs" / "demo.gif"
FPS = 15
DT = 1 / FPS
ESCALA = 0.75  # 800 × 600 → 600 × 450
SEMENTE = 4


def proximo_passo(partida: Partida, alvo: Posicao) -> Direcao | None:
    """Primeira direção do caminho mais curto da cabeça até o alvo, ou None se não houver."""
    cobra = partida.cobra
    bloqueadas = (set(cobra.segmentos) - {cobra.cauda}) | partida.obstaculos
    inicio = cobra.cabeca
    primeira_direcao: dict[Posicao, Direcao] = {}
    fila = deque([inicio])
    visitadas = {inicio}
    while fila:
        atual = fila.popleft()
        if atual == alvo:
            return primeira_direcao.get(atual)
        for direcao in Direcao:
            if atual == inicio and direcao is cobra.direcao.oposta:
                continue
            vizinha = atual.vizinha(direcao)
            if not partida.grade.contem(vizinha) or vizinha in bloqueadas | visitadas:
                continue
            visitadas.add(vizinha)
            primeira_direcao[vizinha] = primeira_direcao.get(atual, direcao)
            fila.append(vizinha)
    return None


def pilotar(partida: Partida) -> None:
    if partida.cobra.tem_comandos_pendentes:
        return
    alvos = [partida.comida]
    if partida.fruta_dourada:
        alvos.insert(0, partida.fruta_dourada.posicao)
    if partida.power_up:
        alvos.insert(0, partida.power_up.posicao)
    for alvo in alvos:
        if alvo is not None and (direcao := proximo_passo(partida, alvo)):
            partida.virar(direcao)
            return


def celula_livre_perto(partida: Partida) -> Posicao:
    """Célula livre a alguns passos da cabeça, para o item aparecer logo no GIF."""
    cabeca = partida.cobra.cabeca
    ocupadas = {partida.comida}
    if partida.fruta_dourada:
        ocupadas.add(partida.fruta_dourada.posicao)
    if partida.power_up:
        ocupadas.add(partida.power_up.posicao)
    return next(
        p
        for p in (
            Posicao(cabeca.coluna + dx, cabeca.linha + dy)
            for dx, dy in ((4, 3), (-4, 3), (4, -3), (-4, -3), (3, 4), (-3, -4))
        )
        if partida.grade.contem(p)
        and p not in partida.cobra
        and p not in partida.obstaculos
        and p not in ocupadas
    )


class Gravador:
    def __init__(self, jogo: Jogo) -> None:
        self.jogo = jogo
        self.quadros: list[Image.Image] = []

    def quadro(self) -> None:
        self.jogo.opacidade_fade = max(0.0, self.jogo.opacidade_fade - DT / 0.25)
        self.jogo._desenhar()
        tela = self.jogo.tela
        tamanho = (round(tela.get_width() * ESCALA), round(tela.get_height() * ESCALA))
        dados = pygame.image.tobytes(tela, "RGB")
        imagem = Image.frombytes("RGB", tela.get_size(), dados)
        self.quadros.append(imagem.resize(tamanho, Image.Resampling.NEAREST))

    def rodar(self, segundos: float, antes_de_cada_quadro=None) -> None:
        for _ in range(round(segundos * FPS)):
            if antes_de_cada_quadro:
                antes_de_cada_quadro()
            self.jogo.estado_atual.atualizar(DT)
            self.quadro()

    def salvar(self) -> None:
        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        paleta = [
            quadro.quantize(colors=48, method=Image.Quantize.MEDIANCUT) for quadro in self.quadros
        ]
        paleta[0].save(
            DESTINO,
            save_all=True,
            append_images=paleta[1:],
            duration=round(1000 / FPS),
            loop=0,
            optimize=True,
            disposal=1,
        )


def main() -> None:
    jogo = Jogo(semente=SEMENTE)
    gravador = Gravador(jogo)

    navegacao.abrir_menu(jogo)
    gravador.rodar(1.6)

    navegacao.iniciar_campanha(jogo, 2)
    gravador.rodar(1.4)  # contagem: "NÍVEL 2 / Pedras no caminho / 3, 2..."
    jogo.estado_atual.tratar_evento(pygame.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
    jogando = jogo.estado_atual
    assert isinstance(jogando, EstadoJogando)
    partida = jogando.partida

    def jogar() -> None:
        pilotar(partida)

    gravador.rodar(4.0, jogar)
    # Uma fruta dourada perto da cabeça, para aparecer no GIF.
    partida.fruta_dourada = FrutaDourada(celula_livre_perto(partida))
    gravador.rodar(4.0, jogar)
    # Power-ups da V3: câmera lenta (campo azulado) e, depois, pontos em dobro.
    for tipo, segundos in ((TipoPowerUp.CAMERA_LENTA, 4.0), (TipoPowerUp.PONTOS_EM_DOBRO, 3.5)):
        partida.power_up = PowerUpNoCampo(tipo, celula_livre_perto(partida))
        gravador.rodar(segundos, jogar)

    # Final: o piloto "se distrai" e segue reto até bater.
    while partida.em_andamento:
        gravador.rodar(DT)
    gravador.rodar(2.6)  # pisca e mostra a tela de fim
    pygame.quit()

    gravador.salvar()
    tamanho = DESTINO.stat().st_size / 1024 / 1024
    print(
        f"gerado: {DESTINO.relative_to(RAIZ)} ({len(gravador.quadros)} quadros, {tamanho:.1f} MB)"
    )


if __name__ == "__main__":
    main()
