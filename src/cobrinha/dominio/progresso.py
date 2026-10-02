"""Progresso do jogador: ranking de recordes por modo (J6) e níveis liberados.

Só regras e conversão para dicionário; quem lê e grava o arquivo é `persistencia.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cobrinha.config import TAMANHO_RANKING
from cobrinha.dominio.niveis import NIVEIS


@dataclass(frozen=True)
class Recorde:
    pontos: int
    nivel: int  # nível alcançado
    data: str  # AAAA-MM-DD


@dataclass
class Progresso:
    # Ranking por modo de jogo (chave = nome do Modo, ex.: "CLASSICO"), do maior para o menor.
    rankings: dict[str, list[Recorde]] = field(default_factory=dict)
    maior_nivel_liberado: int = 1

    def ranking(self, modo: str) -> list[Recorde]:
        return list(self.rankings.get(modo, []))

    def recorde(self, modo: str) -> int:
        ranking = self.rankings.get(modo)
        return ranking[0].pontos if ranking else 0

    def registrar_pontuacao(self, modo: str, pontos: int, nivel: int, data: str) -> int | None:
        """Coloca a pontuação no ranking do modo. Devolve a colocação (1 = recorde) ou None."""
        if pontos <= 0:
            return None
        ranking = self.rankings.setdefault(modo, [])
        # Em caso de empate, quem chegou antes fica na frente.
        colocacao = sum(1 for recorde in ranking if recorde.pontos >= pontos) + 1
        if colocacao > TAMANHO_RANKING:
            return None
        ranking.insert(colocacao - 1, Recorde(pontos, nivel, data))
        del ranking[TAMANHO_RANKING:]
        return colocacao

    def liberar_nivel(self, numero: int) -> None:
        """Libera o nível `numero` (e, com ele, todos os anteriores) no menu."""
        numero = min(numero, len(NIVEIS))
        self.maior_nivel_liberado = max(self.maior_nivel_liberado, numero)

    def para_dict(self) -> dict[str, Any]:
        return {
            "maior_nivel_liberado": self.maior_nivel_liberado,
            "rankings": {
                modo: [vars(recorde) for recorde in ranking]
                for modo, ranking in self.rankings.items()
            },
        }

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> Progresso:
        """Reconstrói o progresso a partir do arquivo salvo, descartando valores inválidos."""
        progresso = cls()
        progresso.liberar_nivel(int(dados.get("maior_nivel_liberado", 1)))
        for modo, ranking in dict(dados.get("rankings", {})).items():
            recordes = [
                Recorde(int(item["pontos"]), int(item["nivel"]), str(item["data"]))
                for item in ranking
            ]
            recordes.sort(key=lambda recorde: recorde.pontos, reverse=True)
            progresso.rankings[str(modo)] = recordes[:TAMANHO_RANKING]
        return progresso
