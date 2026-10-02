"""Progresso do jogador: recorde e níveis liberados.

Por enquanto vale só durante a sessão; a gravação em disco entra na Fase 4 (J6).
"""

from dataclasses import dataclass

from cobrinha.dominio.niveis import NIVEIS


@dataclass
class Progresso:
    recorde: int = 0
    maior_nivel_liberado: int = 1

    def registrar_pontuacao(self, pontos: int) -> bool:
        """Atualiza o recorde. Devolve True se `pontos` for um novo recorde."""
        if pontos > self.recorde:
            self.recorde = pontos
            return True
        return False

    def liberar_nivel(self, numero: int) -> None:
        """Libera o nível `numero` (e, com ele, todos os anteriores) no menu."""
        numero = min(numero, len(NIVEIS))
        self.maior_nivel_liberado = max(self.maior_nivel_liberado, numero)
