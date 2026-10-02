"""Regras de uma partida (um nível): tempo, movimento, colisões, pontuação e fim."""

from __future__ import annotations

import random
from enum import Enum, auto

from cobrinha.config import MAX_PASSOS_POR_QUADRO, TAMANHO_INICIAL_COBRA
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel, proximo_nivel


class Situacao(Enum):
    EM_ANDAMENTO = auto()
    NIVEL_CONCLUIDO = auto()
    DERROTA = auto()
    VITORIA = auto()


class Evento(Enum):
    """O que aconteceu num passo; a interface usa para efeitos e sons."""

    MOVEU = auto()
    COMEU = auto()
    CONCLUIU_NIVEL = auto()
    BATEU = auto()
    VENCEU = auto()


class Partida:
    def __init__(
        self,
        nivel: Nivel = NIVEIS[0],
        grade: Grade = GRADE_PADRAO,
        rng: random.Random | None = None,
        cobra: Cobra | None = None,
        comida: Posicao | None = None,
        pontos: int = 0,
    ) -> None:
        self.nivel = nivel
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
        self.passos_por_segundo = nivel.passos_por_segundo
        # Pontos acumulados na campanha; comidas contam só neste nível.
        self.pontos = pontos
        self.comidas_no_nivel = 0
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
        self.comidas_no_nivel += 1
        self.cobra.crescer()

        # Vitória quando a cobra, ao terminar de crescer, vai ocupar o campo inteiro.
        # (No passo em que come, a cauda ainda sai: sempre sobra uma célula livre.)
        if self.cobra.tamanho_final >= self.grade.total_celulas:
            return self._vencer()
        if self.comidas_no_nivel >= self.nivel.meta_comidas:
            if proximo_nivel(self.nivel) is None:
                return self._vencer()
            self.situacao = Situacao.NIVEL_CONCLUIDO
            self.comida = None
            return Evento.CONCLUIU_NIVEL

        self.comida = sortear_posicao_livre(self.grade, self.cobra, self.rng)
        if self.comida is None:
            return self._vencer()
        return Evento.COMEU

    def proxima_fase(self) -> Partida:
        """Partida do nível seguinte, levando os pontos. A cobra recomeça do tamanho inicial."""
        seguinte = proximo_nivel(self.nivel)
        if self.situacao is not Situacao.NIVEL_CONCLUIDO or seguinte is None:
            raise RuntimeError("Só é possível avançar depois de concluir um nível.")
        return Partida(nivel=seguinte, grade=self.grade, rng=self.rng, pontos=self.pontos)

    def _vencer(self) -> Evento:
        self.situacao = Situacao.VITORIA
        self.comida = None
        return Evento.VENCEU
