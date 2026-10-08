"""Desenho da cobra e da comida com os sprites em pixel art (I3, I4).

Cada segmento vira uma peça (cabeça, corpo reto, curva ou cauda) girada em
múltiplos de 90°, a partir das 4 imagens-base geradas por ferramentas/gerar_sprites.py.
Cada pele (cor) da cobra tem as próprias imagens-base; a verde é a padrão.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from enum import Enum

import pygame

from cobrinha import recursos
from cobrinha.config import ALTURA_HUD, PELES, TAMANHO_CELULA, PeleCobra
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp
from cobrinha.ui.campo import celula_para_pixel


class TipoPeca(Enum):
    """O valor é o nome do PNG da peça-base."""

    CABECA = "cabeca"
    RETO = "corpo_reto"
    CURVA = "corpo_curva"
    CAUDA = "cauda"


# Rotação (anti-horária, como em pygame.transform.rotate) que leva "→" para cada direção.
ANGULO_DA_DIRECAO = {
    Direcao.DIREITA: 0,
    Direcao.CIMA: 90,
    Direcao.ESQUERDA: 180,
    Direcao.BAIXO: 270,
}
_GIRO_ANTI_HORARIO = {
    Direcao.DIREITA: Direcao.CIMA,
    Direcao.CIMA: Direcao.ESQUERDA,
    Direcao.ESQUERDA: Direcao.BAIXO,
    Direcao.BAIXO: Direcao.DIREITA,
}
LADOS_CURVA_BASE = frozenset({Direcao.ESQUERDA, Direcao.BAIXO})

SPRITE_DO_POWER_UP = {
    TipoPowerUp.CAMERA_LENTA: "power_camera_lenta",
    TipoPowerUp.PONTOS_EM_DOBRO: "power_pontos_em_dobro",
    TipoPowerUp.ENCOLHER: "power_encolher",
}

# Comida "flutuando": sobe e desce 1 px.
VELOCIDADE_FLUTUACAO = 4.0
# A fruta dourada e os power-ups piscam quando estão para sumir.
AVISO_FRUTA_SUMINDO = 1.5  # segundos restantes
PISCADAS_POR_SEGUNDO = 8


@dataclass(frozen=True)
class Peca:
    tipo: TipoPeca
    posicao: Posicao
    angulo: int


def direcao_entre(origem: Posicao, destino: Posicao) -> Direcao:
    """Direção de uma célula para a vizinha.

    Se a vizinha estiver do outro lado do campo (modo sem bordas, Fase 4), o salto
    conta como um passo no sentido contrário.
    """
    dx = destino.coluna - origem.coluna
    dy = destino.linha - origem.linha
    if abs(dx) > 1:
        dx = -int(math.copysign(1, dx))
    if abs(dy) > 1:
        dy = -int(math.copysign(1, dy))
    return Direcao((dx, dy))


def angulo_da_curva(lados: frozenset[Direcao]) -> int:
    """Rotação da curva-base (esquerda + baixo) para ligar os dois `lados` pedidos."""
    atual = LADOS_CURVA_BASE
    for angulo in (0, 90, 180, 270):
        if atual == lados:
            return angulo
        atual = frozenset(_GIRO_ANTI_HORARIO[lado] for lado in atual)
    raise ValueError(f"Lados não formam uma curva: {lados}")


def classificar_pecas(segmentos: Sequence[Posicao], direcao: Direcao) -> list[Peca]:
    """Escolhe a peça e a rotação de cada segmento, da cabeça à cauda."""
    pecas = []
    ultimo = len(segmentos) - 1
    for indice, posicao in enumerate(segmentos):
        if indice == 0:
            frente = direcao if ultimo == 0 else direcao_entre(segmentos[1], posicao)
            pecas.append(Peca(TipoPeca.CABECA, posicao, ANGULO_DA_DIRECAO[frente]))
        elif indice == ultimo:
            ligacao = direcao_entre(posicao, segmentos[indice - 1])
            pecas.append(Peca(TipoPeca.CAUDA, posicao, ANGULO_DA_DIRECAO[ligacao]))
        else:
            para_frente = direcao_entre(posicao, segmentos[indice - 1])
            para_tras = direcao_entre(posicao, segmentos[indice + 1])
            if para_frente is para_tras.oposta:
                horizontal = para_frente in (Direcao.ESQUERDA, Direcao.DIREITA)
                pecas.append(Peca(TipoPeca.RETO, posicao, 0 if horizontal else 90))
            else:
                angulo = angulo_da_curva(frozenset({para_frente, para_tras}))
                pecas.append(Peca(TipoPeca.CURVA, posicao, angulo))
    return pecas


class Sprites:
    """Todas as rotações das peças, em todas as peles, preparadas uma vez (exige a janela)."""

    def __init__(self) -> None:
        # (tipo, ângulo) → peça girada, para cada pele; `_pecas` é a da cobra verde.
        self._pecas_da_pele = {
            pele: {
                (tipo, angulo): pygame.transform.rotate(
                    recursos.imagem(tipo.value + pele.sufixo), angulo
                )
                for tipo in TipoPeca
                for angulo in (0, 90, 180, 270)
            }
            for pele in PELES
        }
        self._pecas = self._pecas_da_pele[PELES[0]]
        self.comida = recursos.imagem("comida")
        self.comida_dourada = recursos.imagem("comida_dourada")
        self.parede = recursos.imagem("parede")
        self.power_ups = {tipo: recursos.imagem(SPRITE_DO_POWER_UP[tipo]) for tipo in TipoPowerUp}

    def desenhar_cobra(
        self, superficie: pygame.Surface, cobra: Cobra, pele: PeleCobra = PELES[0]
    ) -> None:
        # Da cauda para a cabeça, para a cabeça ficar sempre por cima.
        pecas = self._pecas_da_pele[pele]
        for peca in reversed(classificar_pecas(cobra.segmentos, cobra.direcao)):
            imagem = pecas[peca.tipo, peca.angulo]
            superficie.blit(imagem, celula_para_pixel(peca.posicao))

    def desenhar_comida(self, superficie: pygame.Surface, posicao: Posicao, tempo: float) -> None:
        self._desenhar_flutuando(superficie, self.comida, posicao, tempo)

    def desenhar_fruta_dourada(
        self, superficie: pygame.Surface, posicao: Posicao, tempo: float, tempo_restante: float
    ) -> None:
        self._desenhar_temporario(superficie, self.comida_dourada, posicao, tempo, tempo_restante)

    def desenhar_power_up(
        self, superficie: pygame.Surface, power_up: PowerUpNoCampo, tempo: float
    ) -> None:
        imagem = self.power_ups[power_up.tipo]
        self._desenhar_temporario(
            superficie, imagem, power_up.posicao, tempo, power_up.tempo_restante
        )

    def _desenhar_temporario(
        self,
        superficie: pygame.Surface,
        imagem: pygame.Surface,
        posicao: Posicao,
        tempo: float,
        tempo_restante: float,
    ) -> None:
        """Item que some sozinho: pisca quando está para sumir."""
        sumindo = tempo_restante < AVISO_FRUTA_SUMINDO
        if sumindo and int(tempo * PISCADAS_POR_SEGUNDO) % 2:
            return
        self._desenhar_flutuando(superficie, imagem, posicao, tempo)

    def desenhar_obstaculos(
        self, superficie: pygame.Surface, obstaculos: Iterable[Posicao], topo: int = ALTURA_HUD
    ) -> None:
        """Pedras do nível. `topo` = 0 desenha numa superfície que é só o campo, sem o HUD."""
        for posicao in obstaculos:
            x = posicao.coluna * TAMANHO_CELULA
            superficie.blit(self.parede, (x, topo + posicao.linha * TAMANHO_CELULA))

    def _desenhar_flutuando(
        self, superficie: pygame.Surface, imagem: pygame.Surface, posicao: Posicao, tempo: float
    ) -> None:
        x, y = celula_para_pixel(posicao)
        deslocamento = round(math.sin(tempo * VELOCIDADE_FLUTUACAO))
        superficie.blit(imagem, (x, y + deslocamento))
