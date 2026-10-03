"""Regras de uma partida (um nível): tempo, movimento, colisões, pontuação e fim."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto

from cobrinha.config import (
    CHANCE_FRUTA_DOURADA,
    DURACAO_FRUTA_DOURADA,
    MAX_PASSOS_POR_QUADRO,
    PONTOS_FRUTA_DOURADA,
    TAMANHO_INICIAL_COBRA,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel, proximo_nivel


class Modo(Enum):
    """Modos de jogo (J8); o valor é o nome mostrado na tela."""

    CLASSICO = "Clássico"  # as bordas do campo matam
    SEM_BORDAS = "Sem bordas"  # a cobra atravessa e sai do outro lado


class Situacao(Enum):
    EM_ANDAMENTO = auto()
    NIVEL_CONCLUIDO = auto()
    DERROTA = auto()
    VITORIA = auto()


class Evento(Enum):
    """O que aconteceu num passo; a interface usa para efeitos e sons."""

    MOVEU = auto()
    COMEU = auto()
    COMEU_DOURADA = auto()
    CONCLUIU_NIVEL = auto()
    BATEU = auto()
    VENCEU = auto()


@dataclass
class FrutaDourada:
    posicao: Posicao
    tempo_restante: float = DURACAO_FRUTA_DOURADA


class Partida:
    def __init__(
        self,
        nivel: Nivel = NIVEIS[0],
        grade: Grade = GRADE_PADRAO,
        rng: random.Random | None = None,
        cobra: Cobra | None = None,
        comida: Posicao | None = None,
        pontos: int = 0,
        modo: Modo = Modo.CLASSICO,
    ) -> None:
        self.nivel = nivel
        self.grade = grade
        self.modo = modo
        self.obstaculos = nivel.obstaculos
        self.rng = rng or random.Random()
        if cobra is None:
            cobra = Cobra.nova(
                Posicao(grade.colunas // 4, grade.linhas // 2),
                Direcao.DIREITA,
                TAMANHO_INICIAL_COBRA,
            )
        self.cobra = cobra
        self.fruta_dourada: FrutaDourada | None = None
        self.comida: Posicao | None = None
        self.comida = comida if comida is not None else self._sortear_celula_livre()
        # Pontos acumulados na campanha; comidas contam só neste nível.
        self.pontos = pontos
        self.comidas_no_nivel = 0
        self.situacao = Situacao.EM_ANDAMENTO
        self._tempo_acumulado = 0.0

    @property
    def em_andamento(self) -> bool:
        return self.situacao is Situacao.EM_ANDAMENTO

    @property
    def passos_por_segundo(self) -> float:
        """Velocidade atual: a do nível mais a aceleração por comida (J9)."""
        return self.nivel.passos_por_segundo + self.nivel.aceleracao_por_comida * (
            self.comidas_no_nivel
        )

    @property
    def intervalo_passo(self) -> float:
        return 1 / self.passos_por_segundo

    @property
    def progresso_passo(self) -> float:
        """Quanto do passo atual já passou (0 a 1), para animar o movimento entre células (V3).

        Parada a partida (fim do nível, derrota ou vitória), a cobra fica na célula final.
        """
        if not self.em_andamento:
            return 1.0
        return min(1.0, self._tempo_acumulado / self.intervalo_passo)

    @property
    def celulas_livres_no_campo(self) -> int:
        return self.grade.total_celulas - len(self.obstaculos)

    def virar(self, direcao: Direcao) -> None:
        if self.em_andamento:
            self.cobra.virar(direcao)

    def atualizar(self, dt: float) -> list[Evento]:
        """Avança o relógio da partida em `dt` segundos e executa os passos devidos.

        A lógica anda em passo fixo, independente do FPS da tela (D1).
        """
        if not self.em_andamento:
            return []
        self._envelhecer_fruta_dourada(dt)
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
        if self.modo is Modo.SEM_BORDAS:
            nova_cabeca = self.grade.envolver(nova_cabeca)

        if (
            not self.grade.contem(nova_cabeca)
            or nova_cabeca in self.obstaculos
            or self.cobra.colidiria(nova_cabeca)
        ):
            self.situacao = Situacao.DERROTA
            return Evento.BATEU

        self.cobra.avancar(nova_cabeca)
        if self.fruta_dourada and nova_cabeca == self.fruta_dourada.posicao:
            return self._comer_fruta_dourada()
        if nova_cabeca != self.comida:
            return Evento.MOVEU
        return self._comer()

    def proxima_fase(self) -> Partida:
        """Partida do nível seguinte, levando pontos e modo. A cobra recomeça do tamanho inicial."""
        seguinte = proximo_nivel(self.nivel)
        if self.situacao is not Situacao.NIVEL_CONCLUIDO or seguinte is None:
            raise RuntimeError("Só é possível avançar depois de concluir um nível.")
        return Partida(
            nivel=seguinte, grade=self.grade, rng=self.rng, pontos=self.pontos, modo=self.modo
        )

    def _comer(self) -> Evento:
        self.pontos += 1
        self.comidas_no_nivel += 1
        self.cobra.crescer()

        # Vitória quando a cobra, ao terminar de crescer, vai ocupar todo o espaço livre.
        # (No passo em que come, a cauda ainda sai: sempre sobra uma célula livre.)
        if self.cobra.tamanho_final >= self.celulas_livres_no_campo:
            return self._vencer()
        if self.comidas_no_nivel >= self.nivel.meta_comidas:
            if proximo_nivel(self.nivel) is None:
                return self._vencer()
            self.situacao = Situacao.NIVEL_CONCLUIDO
            self.comida = None
            self.fruta_dourada = None
            return Evento.CONCLUIU_NIVEL

        self.comida = self._sortear_celula_livre()
        if self.comida is None:
            return self._vencer()
        if self.fruta_dourada is None and self.rng.random() < CHANCE_FRUTA_DOURADA:
            posicao = self._sortear_celula_livre()
            if posicao is not None:
                self.fruta_dourada = FrutaDourada(posicao)
        return Evento.COMEU

    def _comer_fruta_dourada(self) -> Evento:
        # Vale mais pontos, mas não conta para a meta do nível.
        self.pontos += PONTOS_FRUTA_DOURADA
        self.cobra.crescer()
        self.fruta_dourada = None
        if self.cobra.tamanho_final >= self.celulas_livres_no_campo:
            return self._vencer()
        return Evento.COMEU_DOURADA

    def _envelhecer_fruta_dourada(self, dt: float) -> None:
        if self.fruta_dourada is None:
            return
        self.fruta_dourada.tempo_restante -= dt
        if self.fruta_dourada.tempo_restante <= 0:
            self.fruta_dourada = None

    def _sortear_celula_livre(self) -> Posicao | None:
        """Célula sem cobra, pedra, comida nem fruta dourada."""
        ocupadas = set(self.cobra.segmentos) | self.obstaculos
        if self.comida is not None:
            ocupadas.add(self.comida)
        if self.fruta_dourada is not None:
            ocupadas.add(self.fruta_dourada.posicao)
        return sortear_posicao_livre(self.grade, ocupadas, self.rng)

    def _vencer(self) -> Evento:
        self.situacao = Situacao.VITORIA
        self.comida = None
        self.fruta_dourada = None
        return Evento.VENCEU
