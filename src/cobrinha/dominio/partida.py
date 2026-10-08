"""Regras de uma partida (um nível): tempo, movimento, colisões, pontuação e fim."""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto

from cobrinha.config import (
    CHANCE_FRUTA_DOURADA,
    CHANCE_POWER_UP,
    DURACAO_FRUTA_DOURADA,
    FATOR_CAMERA_LENTA,
    MAX_PASSOS_POR_QUADRO,
    PONTOS_FRUTA_DOURADA,
    SEGMENTOS_ENCOLHER,
    TAMANHO_INICIAL_COBRA,
    TEMPO_INICIAL,
    TEMPO_MAXIMO,
    TEMPO_POR_COMIDA,
    TEMPO_POR_FRUTA_DOURADA,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel, proximo_nivel
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp


class Modo(Enum):
    """Modos de jogo (J8); o valor é o nome mostrado na tela."""

    CLASSICO = "Clássico"  # as bordas do campo matam
    SEM_BORDAS = "Sem bordas"  # a cobra atravessa e sai do outro lado
    # Bordas matam, não há meta de comidas e o relógio corre: comer devolve segundos.
    CONTRA_O_TEMPO = "Contra o tempo"


class Situacao(Enum):
    EM_ANDAMENTO = auto()
    NIVEL_CONCLUIDO = auto()
    DERROTA = auto()
    VITORIA = auto()
    TEMPO_ESGOTADO = auto()  # só no modo contra o tempo


class Evento(Enum):
    """O que aconteceu num passo; a interface usa para efeitos e sons."""

    MOVEU = auto()
    COMEU = auto()
    COMEU_DOURADA = auto()
    PEGOU_POWER_UP = auto()
    CONCLUIU_NIVEL = auto()
    BATEU = auto()
    VENCEU = auto()
    TEMPO_ESGOTADO = auto()
    EMPATOU = auto()  # só no duelo: todos eliminados no mesmo passo


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
        self.power_up: PowerUpNoCampo | None = None
        # Efeitos com duração em andamento → segundos restantes (V3).
        self.efeitos_ativos: dict[TipoPowerUp, float] = {}
        self.comida: Posicao | None = None
        self.comida = comida if comida is not None else self._sortear_celula_livre()
        # Pontos acumulados na campanha; comidas contam só neste nível.
        self.pontos = pontos
        self.comidas_no_nivel = 0
        self.situacao = Situacao.EM_ANDAMENTO
        self._tempo_acumulado = 0.0
        # Relógio do modo contra o tempo; None nos outros modos.
        self.tempo_restante: float | None = TEMPO_INICIAL if modo is Modo.CONTRA_O_TEMPO else None

    @property
    def em_andamento(self) -> bool:
        return self.situacao is Situacao.EM_ANDAMENTO

    @property
    def tem_meta(self) -> bool:
        """O nível termina ao atingir a meta de comidas? (No contra o tempo, não.)"""
        return self.modo is not Modo.CONTRA_O_TEMPO

    @property
    def passos_por_segundo(self) -> float:
        """Velocidade atual: a do nível mais a aceleração por comida (J9).

        Com a câmera lenta ativa (V3), a velocidade cai pelo `FATOR_CAMERA_LENTA`.
        """
        velocidade = self.nivel.passos_por_segundo + self.nivel.aceleracao_por_comida * (
            self.comidas_no_nivel
        )
        if TipoPowerUp.CAMERA_LENTA in self.efeitos_ativos:
            velocidade *= FATOR_CAMERA_LENTA
        return velocidade

    @property
    def multiplicador_pontos(self) -> int:
        return 2 if TipoPowerUp.PONTOS_EM_DOBRO in self.efeitos_ativos else 1

    @property
    def intervalo_passo(self) -> float:
        return 1 / self.passos_por_segundo

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
        self._envelhecer_power_ups(dt)
        limite = self.intervalo_passo * MAX_PASSOS_POR_QUADRO
        self._tempo_acumulado = min(self._tempo_acumulado + dt, limite)
        eventos = []
        while self.em_andamento and self._tempo_acumulado >= self.intervalo_passo:
            self._tempo_acumulado -= self.intervalo_passo
            eventos.append(self.passo())
        # O relógio nunca anda mais rápido que a cobra: um travamento não rouba segundos.
        if self.em_andamento and self._descontar_tempo(min(dt, limite)):
            eventos.append(Evento.TEMPO_ESGOTADO)
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
        if self.power_up and nova_cabeca == self.power_up.posicao:
            return self._pegar_power_up(self.power_up.tipo)
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
        self.pontos += self.multiplicador_pontos
        self.comidas_no_nivel += 1
        self.cobra.crescer()
        self._ganhar_tempo(TEMPO_POR_COMIDA)

        # Vitória quando a cobra, ao terminar de crescer, vai ocupar todo o espaço livre.
        # (No passo em que come, a cauda ainda sai: sempre sobra uma célula livre.)
        if self.cobra.tamanho_final >= self.celulas_livres_no_campo:
            return self._vencer()
        if self.tem_meta and self.comidas_no_nivel >= self.nivel.meta_comidas:
            if proximo_nivel(self.nivel) is None:
                return self._vencer()
            self.situacao = Situacao.NIVEL_CONCLUIDO
            self.comida = None
            self.fruta_dourada = None
            self.power_up = None
            return Evento.CONCLUIU_NIVEL

        self.comida = self._sortear_celula_livre()
        if self.comida is None:
            return self._vencer()
        if self.fruta_dourada is None and self.rng.random() < CHANCE_FRUTA_DOURADA:
            posicao = self._sortear_celula_livre()
            if posicao is not None:
                self.fruta_dourada = FrutaDourada(posicao)
        if self.power_up is None and self.rng.random() < CHANCE_POWER_UP:
            tipo = self.rng.choice(list(TipoPowerUp))
            posicao = self._sortear_celula_livre()
            if posicao is not None:
                self.power_up = PowerUpNoCampo(tipo, posicao)
        return Evento.COMEU

    def _comer_fruta_dourada(self) -> Evento:
        # Vale mais pontos, mas não conta para a meta do nível.
        self.pontos += PONTOS_FRUTA_DOURADA * self.multiplicador_pontos
        self.cobra.crescer()
        self._ganhar_tempo(TEMPO_POR_FRUTA_DOURADA)
        self.fruta_dourada = None
        if self.cobra.tamanho_final >= self.celulas_livres_no_campo:
            return self._vencer()
        return Evento.COMEU_DOURADA

    def _pegar_power_up(self, tipo: TipoPowerUp) -> Evento:
        """Não dá pontos nem faz crescer: só aplica o efeito."""
        self.power_up = None
        if tipo is TipoPowerUp.ENCOLHER:
            self.cobra.encolher(SEGMENTOS_ENCOLHER, minimo=TAMANHO_INICIAL_COBRA)
        else:
            # Pegar de novo um efeito ativo renova a duração, sem somar.
            self.efeitos_ativos[tipo] = tipo.duracao
        return Evento.PEGOU_POWER_UP

    def _envelhecer_power_ups(self, dt: float) -> None:
        if self.power_up is not None:
            self.power_up.tempo_restante -= dt
            if self.power_up.tempo_restante <= 0:
                self.power_up = None
        for tipo in list(self.efeitos_ativos):
            self.efeitos_ativos[tipo] -= dt
            if self.efeitos_ativos[tipo] <= 0:
                del self.efeitos_ativos[tipo]

    def _ganhar_tempo(self, segundos: float) -> None:
        if self.tempo_restante is not None:
            self.tempo_restante = min(TEMPO_MAXIMO, self.tempo_restante + segundos)

    def _descontar_tempo(self, dt: float) -> bool:
        """Gasta `dt` do relógio. Devolve True se o tempo acabou neste instante."""
        if self.tempo_restante is None:
            return False
        self.tempo_restante = max(0.0, self.tempo_restante - dt)
        if self.tempo_restante > 0:
            return False
        self.situacao = Situacao.TEMPO_ESGOTADO
        self.comida = None
        self.fruta_dourada = None
        self.power_up = None
        return True

    def _envelhecer_fruta_dourada(self, dt: float) -> None:
        if self.fruta_dourada is None:
            return
        self.fruta_dourada.tempo_restante -= dt
        if self.fruta_dourada.tempo_restante <= 0:
            self.fruta_dourada = None

    def _sortear_celula_livre(self) -> Posicao | None:
        """Célula sem cobra, pedra, comida, fruta dourada nem power-up."""
        ocupadas = set(self.cobra.segmentos) | self.obstaculos
        if self.comida is not None:
            ocupadas.add(self.comida)
        if self.fruta_dourada is not None:
            ocupadas.add(self.fruta_dourada.posicao)
        if self.power_up is not None:
            ocupadas.add(self.power_up.posicao)
        return sortear_posicao_livre(self.grade, ocupadas, self.rng)

    def _vencer(self) -> Evento:
        self.situacao = Situacao.VITORIA
        self.comida = None
        self.fruta_dourada = None
        self.power_up = None
        return Evento.VENCEU
