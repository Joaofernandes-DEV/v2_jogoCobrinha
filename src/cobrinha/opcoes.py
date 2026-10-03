"""Preferências do jogador (I9), salvas junto com o progresso."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from cobrinha.config import VOLUME_EFEITOS, VOLUME_MUSICA
from cobrinha.dominio.partida import Modo

PASSO_VOLUME = 0.1


@dataclass
class Opcoes:
    volume_efeitos: float = VOLUME_EFEITOS
    volume_musica: float = VOLUME_MUSICA
    tela_cheia: bool = False
    # Desligar reduz animações piscantes e textos flutuantes (acessibilidade, I11).
    efeitos_visuais: bool = True
    modo: str = Modo.CLASSICO.name

    @property
    def modo_de_jogo(self) -> Modo:
        return Modo[self.modo]

    def ajustar_volume_efeitos(self, delta: int) -> None:
        self.volume_efeitos = _limitar(self.volume_efeitos + delta * PASSO_VOLUME)

    def ajustar_volume_musica(self, delta: int) -> None:
        self.volume_musica = _limitar(self.volume_musica + delta * PASSO_VOLUME)

    def alternar_modo(self, delta: int = 1) -> None:
        """Passa para o modo seguinte (delta = +1) ou anterior (-1), circulando."""
        modos = list(Modo)
        self.modo = modos[(modos.index(self.modo_de_jogo) + delta) % len(modos)].name

    def para_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> Opcoes:
        """Lê as opções salvas; valores ausentes ou inválidos voltam ao padrão."""
        opcoes = cls()
        if "volume_efeitos" in dados:
            opcoes.volume_efeitos = _limitar(float(dados["volume_efeitos"]))
        if "volume_musica" in dados:
            opcoes.volume_musica = _limitar(float(dados["volume_musica"]))
        opcoes.tela_cheia = bool(dados.get("tela_cheia", opcoes.tela_cheia))
        opcoes.efeitos_visuais = bool(dados.get("efeitos_visuais", opcoes.efeitos_visuais))
        if dados.get("modo") in Modo.__members__:
            opcoes.modo = dados["modo"]
        return opcoes


def _limitar(volume: float) -> float:
    """Mantém o volume entre 0 e 1, arredondado ao passo de 10%."""
    return round(min(1.0, max(0.0, volume)), 1)
