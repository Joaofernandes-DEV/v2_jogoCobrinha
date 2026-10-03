"""Power-ups da V3: itens que aparecem no campo e dão um efeito ao serem pegos."""

from dataclasses import dataclass
from enum import Enum

from cobrinha.config import (
    DURACAO_CAMERA_LENTA,
    DURACAO_PONTOS_EM_DOBRO,
    DURACAO_POWER_UP_NO_CAMPO,
)
from cobrinha.dominio.grade import Posicao


class TipoPowerUp(Enum):
    """O valor é o nome mostrado na tela."""

    CAMERA_LENTA = "Câmera lenta"  # a cobra anda mais devagar por um tempo
    PONTOS_EM_DOBRO = "Pontos em dobro"  # cada comida vale o dobro por um tempo
    ENCOLHER = "Encolher"  # a cauda perde alguns segmentos na hora

    @property
    def duracao(self) -> float:
        """Segundos de efeito; 0 para os instantâneos."""
        return DURACOES.get(self, 0.0)


DURACOES = {
    TipoPowerUp.CAMERA_LENTA: DURACAO_CAMERA_LENTA,
    TipoPowerUp.PONTOS_EM_DOBRO: DURACAO_PONTOS_EM_DOBRO,
}


@dataclass
class PowerUpNoCampo:
    tipo: TipoPowerUp
    posicao: Posicao
    tempo_restante: float = DURACAO_POWER_UP_NO_CAMPO
