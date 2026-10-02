"""Regras de uma partida: tempo, movimento, colisões, pontuação e fim de jogo."""

from __future__ import annotations

import random
from enum import Enum, auto

from cobrinha.config import (
    MAX_PASSOS_POR_QUADRO,
    PASSOS_POR_SEGUNDO_INICIAL,
    TAMANHO_INICIAL_COBRA,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao


class Situacao(Enum):
    EM_ANDAMENTO = auto()
    DERROTA = auto()
    VITORIA = auto()


class Evento(Enum):
    """O que aconteceu num passo; a interface usa para efeitos e sons."""

    MOVEU = auto()
    COMEU = auto()
    BATEU = auto()
    VENCEU = auto()


class Partida:
    def __init__(
        self,
        grade: Grade = GRADE_PADRAO,
        rng: random.Random | None = None,
        cobra: Cobra | None = None,
        comida: Posicao | None = None,
        passos_por_segundo: float = PASSOS_POR_SEGUNDO_INICIAL,
    ) -> None:
        self.grade = grade
        self.rng = rng or random.Random()
        if cobra is None:
            cobra = Cobra.nova(
                Posicao(grade.colunas // 4, grade.linhas // 2),
                Direcao.DIREITA,
                TAMANHO_INICIAL_COBRA,
            )
        self.cobra = cobra
        if comida is None:
            comida = sortear_posicao_livre(grade, cobra, self.rng)
        self.comida: Posicao | None = comida
        self.passos_por_segundo = passos_por_segundo
        self.pontos = 0
        self.situacao = Situacao.EM_ANDAMENTO
        self._tempo_acumulado = 0.0

    @property
    def em_andamento(self) -> bool:
        return self.situacao is Situacao.EM_ANDAMENTO

    @property
    def intervalo_passo(self) -> float:
        return 1 / self.passos_por_segundo

    def virar(self, direcao: Direcao) -> None:
        if self.em_andamento:
            self.cobra.virar(direcao)

    def atualizar(self, dt: float) -> list[Evento]:
        """Avança o relógio da partida em `dt` segundos e executa os passos devidos.

        A lógica anda em passo fixo, independente do FPS da tela (D1).
        """
        if not self.em_andamento:
            return []
        limite = self.intervalo_passo * MAX_PASSOS_POR_QUADRO
        self._tempo_acumulado = min(self._tempo_acumulado + dt, limite)
        eventos = []
        while self.em_andamento and self._tempo_acumulado >= self.intervalo_passo:
            self._tempo_acumulado -= self.intervalo_passo
            eventos.append(self.passo())
        return eventos

    def passo(self) -> Evento:
        """Move a cobra uma célula e aplica as regras."""
        direcao = self.cobra.aplicar_proxima_direcao()
        nova_cabeca = self.cobra.cabeca.vizinha(direcao)

        if not self.grade.contem(nova_cabeca) or self.cobra.colidiria(nova_cabeca):
            self.situacao = Situacao.DERROTA
            return Evento.BATEU

        self.cobra.avancar(nova_cabeca)
        if nova_cabeca != self.comida:
            return Evento.MOVEU

        self.pontos += 1
        self.cobra.crescer()
        # Vitória quando a cobra, ao terminar de crescer, vai ocupar o campo inteiro.
        # (No passo em que come, a cauda ainda sai: sempre sobra uma célula livre.)
        if self.cobra.tamanho_final >= self.grade.total_celulas:
            self.comida = None
        else:
            self.comida = sortear_posicao_livre(self.grade, self.cobra, self.rng)
        if self.comida is None:
            self.situacao = Situacao.VITORIA
            return Evento.VENCEU
        return Evento.COMEU
