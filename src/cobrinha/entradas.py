"""De onde vêm os comandos de cada jogador do Duelo (V3): um lado do teclado ou um controle.

Nos modos de 1 jogador, setas, WASD e qualquer controle movem a mesma cobra. No Duelo,
cada jogador tem a sua entrada: o lado esquerdo do teclado (WASD), o direito (setas) ou
um controle, identificado pelo `instance_id` que o SDL deu a ele.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import pygame

from cobrinha.controle import id_do_controle, veio_do_controle
from cobrinha.dominio.grade import Direcao

TECLAS_WASD = {
    pygame.K_w: Direcao.CIMA,
    pygame.K_s: Direcao.BAIXO,
    pygame.K_a: Direcao.ESQUERDA,
    pygame.K_d: Direcao.DIREITA,
}
# As setas também são as teclas virtuais do direcional e do analógico do controle.
TECLAS_SETAS = {
    pygame.K_UP: Direcao.CIMA,
    pygame.K_DOWN: Direcao.BAIXO,
    pygame.K_LEFT: Direcao.ESQUERDA,
    pygame.K_RIGHT: Direcao.DIREITA,
}


class TipoEntrada(Enum):
    """O valor é o nome mostrado na tela."""

    TECLADO_ESQUERDO = "WASD"
    TECLADO_DIREITO = "SETAS"
    CONTROLE = "CONTROLE"


@dataclass(frozen=True)
class Entrada:
    tipo: TipoEntrada
    controle_id: int | None = None  # só para TipoEntrada.CONTROLE

    @classmethod
    def controle(cls, controle_id: int) -> Entrada:
        return cls(TipoEntrada.CONTROLE, controle_id)

    @property
    def rotulo(self) -> str:
        return self.tipo.value

    @property
    def e_controle(self) -> bool:
        return self.tipo is TipoEntrada.CONTROLE

    def direcao(self, evento: pygame.Event) -> Direcao | None:
        """A direção que este evento pede a esta entrada (None se não for dela)."""
        if evento.type != pygame.KEYDOWN:
            return None
        if self.e_controle:
            if not veio_do_controle(evento) or id_do_controle(evento) != self.controle_id:
                return None
            return TECLAS_SETAS.get(evento.key)
        if veio_do_controle(evento):
            return None  # o direcional do controle não move quem joga no teclado
        teclas = TECLAS_WASD if self.tipo is TipoEntrada.TECLADO_ESQUERDO else TECLAS_SETAS
        return teclas.get(evento.key)


TECLADO_ESQUERDO = Entrada(TipoEntrada.TECLADO_ESQUERDO)
TECLADO_DIREITO = Entrada(TipoEntrada.TECLADO_DIREITO)


def entrada_do_teclado(evento: pygame.Event) -> Entrada | None:
    """Lado do teclado da tecla apertada (WASD ou setas), ou None."""
    if evento.type != pygame.KEYDOWN or veio_do_controle(evento):
        return None
    if evento.key in TECLAS_WASD:
        return TECLADO_ESQUERDO
    if evento.key in TECLAS_SETAS:
        return TECLADO_DIREITO
    return None


def dica_dos_controles(entradas: tuple[Entrada, ...]) -> str:
    """Ex.: "J1: WASD   J2: CONTROLE   J3: SETAS"."""
    return "   ".join(f"J{indice + 1}: {entrada.rotulo}" for indice, entrada in enumerate(entradas))
