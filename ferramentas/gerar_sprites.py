"""Gera os sprites em pixel art (25 × 25, paleta do jogo) em `src/cobrinha/assets/imagens/`.

Uso: python ferramentas/gerar_sprites.py

Os PNGs gerados são os assets oficiais e podem ser retocados num editor de pixel art;
este script documenta como foram criados e permite recriá-los do zero.

Orientação das peças-base (o jogo gera as outras direções por rotação de 90°):
- cabeca.png: olhando para a DIREITA (o pescoço sai pela esquerda);
- corpo_reto.png: liga ESQUERDA e DIREITA;
- corpo_curva.png: liga ESQUERDA e BAIXO;
- cauda.png: liga à DIREITA, com a ponta para a esquerda.
"""

import math
import os
import sys
from collections.abc import Callable
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from cobrinha.config import TAMANHO_CELULA, Cor, Paleta  # noqa: E402

DESTINO = RAIZ / "src" / "cobrinha" / "assets" / "imagens"
T = TAMANHO_CELULA

# Faixa do corpo: 17 px de espessura (linhas 4 a 20), centralizada na célula.
BORDA_CORPO = 4
ESPESSURA = 17


def cor_do_corpo(profundidade: int, ao_longo: float | None) -> Cor:
    """Cor de um pixel do corpo a partir da posição na seção transversal.

    `profundidade` vai de 0 a 16 de uma borda à outra; `ao_longo` é a posição no
    sentido do comprimento, usada para desenhar as escamas em "V" (None = sem escamas).
    """
    if profundidade in (0, ESPESSURA - 1):
        return Paleta.PRETO
    if profundidade in (1, ESPESSURA - 2):
        return Paleta.VERDE_ESCURO
    distancia_meio = abs(profundidade - ESPESSURA // 2)
    escama = ao_longo is not None and (round(ao_longo) + distancia_meio) % 8 == 0
    if escama and 3 <= profundidade <= ESPESSURA - 4:
        return Paleta.VERDE_ESCURO
    if distancia_meio <= 1:
        return Paleta.VERDE_CLARO
    return Paleta.VERDE


def nova_superficie() -> pygame.Surface:
    superficie = pygame.Surface((T, T), pygame.SRCALPHA)
    superficie.fill((0, 0, 0, 0))
    return superficie


def contornar(superficie: pygame.Surface, dentro: Callable[[int, int], bool], abertos: set[str]):
    """Pinta de preto os pixels da forma que encostam no lado de fora.

    `abertos` lista as bordas da célula por onde a peça continua (sem contorno ali).
    """
    for y in range(T):
        for x in range(T):
            if not dentro(x, y):
                continue
            for dx, dy, lado in ((-1, 0, "esq"), (1, 0, "dir"), (0, -1, "cima"), (0, 1, "baixo")):
                vx, vy = x + dx, y + dy
                fora_da_celula = not (0 <= vx < T and 0 <= vy < T)
                if fora_da_celula and lado in abertos:
                    continue
                if fora_da_celula or not dentro(vx, vy):
                    superficie.set_at((x, y), Paleta.PRETO)
                    break


def corpo_reto() -> pygame.Surface:
    superficie = nova_superficie()
    for y in range(BORDA_CORPO, BORDA_CORPO + ESPESSURA):
        for x in range(T):
            superficie.set_at((x, y), cor_do_corpo(y - BORDA_CORPO, x))
    return superficie


def corpo_curva() -> pygame.Surface:
    """Quarto de anel centrado no canto inferior esquerdo da célula.

    Sem escamas: dobradas no arco, elas ficavam distorcidas; as faixas de cor bastam.
    """
    superficie = nova_superficie()
    centro_x, centro_y = 0.0, float(T)
    for y in range(T):
        for x in range(T):
            distancia = math.hypot(x + 0.5 - centro_x, y + 0.5 - centro_y)
            profundidade = math.floor(distancia - BORDA_CORPO)
            if not 0 <= profundidade < ESPESSURA:
                continue
            superficie.set_at((x, y), cor_do_corpo(profundidade, None))
    return superficie


def cabeca() -> pygame.Surface:
    superficie = nova_superficie()
    meio_y = BORDA_CORPO + ESPESSURA / 2  # 12,5

    def dentro(x: int, y: int) -> bool:
        cx, cy = x + 0.5, y + 0.5
        if abs(cy - meio_y) > ESPESSURA / 2:
            return False
        if cx <= 13:
            return True
        return ((cx - 13) / 9.5) ** 2 + ((cy - meio_y) / (ESPESSURA / 2)) ** 2 <= 1

    for y in range(T):
        for x in range(T):
            if dentro(x, y):
                profundidade = y - BORDA_CORPO
                cor = cor_do_corpo(profundidade, x) if x < 8 else Paleta.VERDE
                if x >= 8 and abs(profundidade - ESPESSURA // 2) <= 1:
                    cor = Paleta.VERDE_CLARO
                superficie.set_at((x, y), cor)
    contornar(superficie, dentro, abertos={"esq"})

    # Olhos (3 × 3, brancos) com pupila olhando para a frente.
    for olho_y in (6, 16):
        for dy in range(3):
            for dx in range(3):
                superficie.set_at((15 + dx, olho_y + dy), Paleta.BRANCO)
        superficie.set_at((17, olho_y + 1), Paleta.PRETO)
        superficie.set_at((17, olho_y + 2 if olho_y == 6 else olho_y), Paleta.PRETO)
    # Narinas.
    superficie.set_at((21, 10), Paleta.VERDE_ESCURO)
    superficie.set_at((21, 14), Paleta.VERDE_ESCURO)
    # Língua bifurcada saindo da ponta.
    superficie.set_at((23, 12), Paleta.VERMELHO)
    superficie.set_at((24, 11), Paleta.VERMELHO)
    superficie.set_at((24, 13), Paleta.VERMELHO)
    return superficie


def cauda() -> pygame.Surface:
    superficie = nova_superficie()
    meio_y = BORDA_CORPO + ESPESSURA / 2

    def dentro(x: int, y: int) -> bool:
        cx, cy = x + 0.5, y + 0.5
        meia_altura = (ESPESSURA / 2) * (cx - 2) / (T - 2)
        return cx >= 2 and abs(cy - meio_y) <= meia_altura

    for y in range(T):
        for x in range(T):
            if dentro(x, y):
                superficie.set_at((x, y), cor_do_corpo(y - BORDA_CORPO, x))
    contornar(superficie, dentro, abertos={"dir"})
    return superficie


def comida() -> pygame.Surface:
    """Maçã: corpo vermelho com brilho, cabinho e folha."""
    superficie = nova_superficie()
    centro_x, centro_y, raio = 12.5, 14.5, 8.5

    def dentro(x: int, y: int) -> bool:
        return math.hypot(x + 0.5 - centro_x, y + 0.5 - centro_y) <= raio

    for y in range(T):
        for x in range(T):
            if dentro(x, y):
                # Sombra no lado de baixo/direita, para dar volume.
                sombra = (x + 0.5 - centro_x) + (y + 0.5 - centro_y) > raio * 0.9
                superficie.set_at((x, y), Paleta.MARROM if sombra else Paleta.VERMELHO)
    contornar(superficie, dentro, abertos=set())
    for x, y in ((8, 10), (9, 10), (8, 11)):
        superficie.set_at((x, y), Paleta.BRANCO)
    for y in range(2, 7):
        superficie.set_at((12, y), Paleta.MARROM)
    for x, y in ((13, 3), (14, 2), (15, 2), (16, 2), (14, 3), (15, 3), (16, 3), (17, 2)):
        superficie.set_at((x, y), Paleta.VERDE)
    for x, y in ((13, 4), (14, 4), (15, 4)):
        superficie.set_at((x, y), Paleta.VERDE_ESCURO)
    return superficie


SPRITES: dict[str, Callable[[], pygame.Surface]] = {
    "cabeca": cabeca,
    "corpo_reto": corpo_reto,
    "corpo_curva": corpo_curva,
    "cauda": cauda,
    "comida": comida,
}


def main() -> None:
    pygame.init()
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, gerar in SPRITES.items():
        caminho = DESTINO / f"{nome}.png"
        pygame.image.save(gerar(), caminho)
        print(f"gerado: {caminho.relative_to(RAIZ)}")
    pygame.quit()


if __name__ == "__main__":
    main()
