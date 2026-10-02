"""A cobra: corpo, movimento, crescimento e fila de comandos de direção."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from cobrinha.config import LIMITE_FILA_DIRECOES
from cobrinha.dominio.grade import Direcao, Posicao


class Cobra:
    def __init__(self, segmentos: Iterable[Posicao], direcao: Direcao) -> None:
        # deque: entrar com a cabeça e sair com a cauda custam O(1) (D4).
        self.segmentos: deque[Posicao] = deque(segmentos)
        if not self.segmentos:
            raise ValueError("A cobra precisa de pelo menos um segmento.")
        # Conjunto espelhando os segmentos, para testar colisão em O(1).
        self._ocupadas: set[Posicao] = set(self.segmentos)
        if len(self._ocupadas) != len(self.segmentos):
            raise ValueError("Os segmentos da cobra não podem se sobrepor.")
        self.direcao = direcao
        self._fila_direcoes: deque[Direcao] = deque()
        self._crescimento_pendente = 0

    @classmethod
    def nova(cls, cabeca: Posicao, direcao: Direcao, tamanho: int) -> Cobra:
        """Cobra reta, com o corpo estendido atrás da cabeça."""
        atras = direcao.oposta
        segmentos = [cabeca]
        for _ in range(tamanho - 1):
            segmentos.append(segmentos[-1].vizinha(atras))
        return cls(segmentos, direcao)

    def __len__(self) -> int:
        return len(self.segmentos)

    @property
    def cabeca(self) -> Posicao:
        return self.segmentos[0]

    @property
    def cauda(self) -> Posicao:
        return self.segmentos[-1]

    @property
    def tamanho_final(self) -> int:
        """Tamanho que a cobra terá depois de terminar de crescer."""
        return len(self.segmentos) + self._crescimento_pendente

    def __contains__(self, posicao: object) -> bool:
        """`posicao in cobra`: a posição está ocupada por algum segmento?"""
        return posicao in self._ocupadas

    def virar(self, nova: Direcao) -> bool:
        """Enfileira um comando de direção. Devolve False se ele for ignorado.

        Cada comando é validado contra o último já enfileirado, e não contra a
        direção atual. Por isso dois toques rápidos (↑ e ←, andando para a →)
        viram duas curvas seguidas, e não uma meia-volta (bug B3 da V1).
        """
        referencia = self._fila_direcoes[-1] if self._fila_direcoes else self.direcao
        if nova in (referencia, referencia.oposta):
            return False
        if len(self._fila_direcoes) >= LIMITE_FILA_DIRECOES:
            return False
        self._fila_direcoes.append(nova)
        return True

    def aplicar_proxima_direcao(self) -> Direcao:
        """Consome um comando da fila (se houver) e devolve a direção deste passo."""
        if self._fila_direcoes:
            self.direcao = self._fila_direcoes.popleft()
        return self.direcao

    def colidiria(self, posicao: Posicao) -> bool:
        """Se a cabeça entrar em `posicao` no próximo passo, bate no próprio corpo?

        A célula da cauda é segura quando a cobra não está crescendo, porque a
        cauda sai dali no mesmo passo.
        """
        if posicao == self.cauda and self._crescimento_pendente == 0:
            return False
        return posicao in self._ocupadas

    def avancar(self, nova_cabeca: Posicao) -> None:
        if self._crescimento_pendente:
            self._crescimento_pendente -= 1
        else:
            # A cauda sai antes de a cabeça entrar: a cabeça pode ocupar a célula da cauda.
            self._ocupadas.discard(self.segmentos.pop())
        self.segmentos.appendleft(nova_cabeca)
        self._ocupadas.add(nova_cabeca)

    def crescer(self, quantidade: int = 1) -> None:
        """A cobra ganha `quantidade` segmentos nos próximos passos (a cauda para)."""
        self._crescimento_pendente += quantidade
