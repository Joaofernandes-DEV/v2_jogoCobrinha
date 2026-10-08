"""Regras do Duelo (V3): de 2 a 4 cobras no mesmo campo, ao mesmo tempo.

Todas as cobras andam no mesmo passo. As colisões de um passo são julgadas juntas,
contra o campo "como se todos tivessem andado":
- borda, pedra ou corpo (o próprio ou o de outra cobra, incluindo a cabeça de antes
  do passo) eliminam; a cauda de quem não está crescendo conta como livre, porque sai
  dali no mesmo passo;
- duas ou mais cabeças que entram na mesma célula eliminam todas elas;
- duas cabeças que trocam de lugar também se eliminam: cada uma entra no pescoço da outra.

A cobra eliminada some do campo. Vence quem sobrar por último; se todas as que
restavam forem eliminadas no mesmo passo, é empate.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from cobrinha.config import (
    CHANCE_FRUTA_DOURADA,
    COMIDAS_NO_DUELO,
    MAX_PASSOS_POR_QUADRO,
    MAXIMO_JOGADORES,
    PONTOS_FRUTA_DOURADA,
    TAMANHO_INICIAL_COBRA,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada

MINIMO_JOGADORES = 2


@dataclass(frozen=True)
class Nascimento:
    cabeca: Posicao
    direcao: Direcao


# Onde nasce a cobra de cada jogador: faixas horizontais diferentes, livres nos 3 mapas,
# para ninguém bater de frente logo no começo.
NASCIMENTOS = (
    Nascimento(Posicao(7, 9), Direcao.DIREITA),  # J1: à esquerda, indo para a direita
    Nascimento(Posicao(24, 12), Direcao.ESQUERDA),  # J2: à direita, indo para a esquerda
    Nascimento(Posicao(24, 1), Direcao.ESQUERDA),  # J3: em cima
    Nascimento(Posicao(7, 20), Direcao.DIREITA),  # J4: embaixo
)
assert len(NASCIMENTOS) == MAXIMO_JOGADORES


@dataclass
class Jogador:
    indice: int  # 0 = J1
    cobra: Cobra
    pontos: int = 0
    vivo: bool = True

    @property
    def nome(self) -> str:
        return f"J{self.indice + 1}"


@dataclass(frozen=True)
class EventoDuelo:
    """O que aconteceu num passo e com quem (None = vale para a partida toda)."""

    evento: Evento
    jogador: int | None = None


class PartidaDuelo:
    def __init__(
        self,
        quantidade: int = MINIMO_JOGADORES,
        nivel: Nivel = NIVEIS[0],
        grade: Grade = GRADE_PADRAO,
        rng: random.Random | None = None,
        cobras: Sequence[Cobra] | None = None,
        comidas: Iterable[Posicao] | None = None,
    ) -> None:
        if cobras is not None:
            quantidade = len(cobras)
        if not MINIMO_JOGADORES <= quantidade <= MAXIMO_JOGADORES:
            raise ValueError(f"O duelo é de {MINIMO_JOGADORES} a {MAXIMO_JOGADORES} jogadores.")
        if cobras is None:
            cobras = [
                Cobra.nova(nascimento.cabeca, nascimento.direcao, TAMANHO_INICIAL_COBRA)
                for nascimento in NASCIMENTOS[:quantidade]
            ]
        self.nivel = nivel
        self.grade = grade
        self.obstaculos = nivel.obstaculos
        self.rng = rng or random.Random()
        self.jogadores = [Jogador(indice, cobra) for indice, cobra in enumerate(cobras)]
        self.fruta_dourada: FrutaDourada | None = None
        self.comidas: list[Posicao] = []
        if comidas is None:
            self._repor_comidas()
        else:
            self.comidas = list(comidas)
        # Maçãs comidas por todos: a velocidade, que é uma só, cresce com elas (J9).
        self.total_comidas = 0
        self.encerrada = False
        self.vencedor: int | None = None  # índice do jogador; None = empate ou em andamento
        self._tempo_acumulado = 0.0

    @property
    def em_andamento(self) -> bool:
        return not self.encerrada

    @property
    def empate(self) -> bool:
        return self.encerrada and self.vencedor is None

    @property
    def vivos(self) -> list[Jogador]:
        return [jogador for jogador in self.jogadores if jogador.vivo]

    @property
    def passos_por_segundo(self) -> float:
        nivel = self.nivel
        return nivel.passos_por_segundo + nivel.aceleracao_por_comida * self.total_comidas

    @property
    def intervalo_passo(self) -> float:
        return 1 / self.passos_por_segundo

    def virar(self, jogador: int, direcao: Direcao) -> None:
        alvo = self.jogadores[jogador]
        if self.em_andamento and alvo.vivo:
            alvo.cobra.virar(direcao)

    def atualizar(self, dt: float) -> list[EventoDuelo]:
        """Avança o relógio em `dt` segundos e executa os passos devidos (passo fixo, D1)."""
        if self.encerrada:
            return []
        self._envelhecer_fruta_dourada(dt)
        limite = self.intervalo_passo * MAX_PASSOS_POR_QUADRO
        self._tempo_acumulado = min(self._tempo_acumulado + dt, limite)
        eventos = []
        while self.em_andamento and self._tempo_acumulado >= self.intervalo_passo:
            self._tempo_acumulado -= self.intervalo_passo
            eventos.extend(self.passo())
        return eventos

    def passo(self) -> list[EventoDuelo]:
        """Move todas as cobras uma célula, ao mesmo tempo, e aplica as regras."""
        vivos = self.vivos
        novas = {
            jogador.indice: jogador.cobra.cabeca.vizinha(jogador.cobra.aplicar_proxima_direcao())
            for jogador in vivos
        }
        # Corpos como ficam depois do passo: todos os segmentos, menos as caudas que saem.
        corpos: set[Posicao] = set()
        for jogador in vivos:
            corpos.update(jogador.cobra.segmentos)
            if jogador.cobra.tamanho_final == len(jogador.cobra):
                corpos.discard(jogador.cobra.cauda)
        cabecas_por_celula = Counter(novas.values())

        eventos = []
        for jogador in vivos:
            nova = novas[jogador.indice]
            if (
                not self.grade.contem(nova)
                or nova in self.obstaculos
                or nova in corpos
                or cabecas_por_celula[nova] > 1
            ):
                jogador.vivo = False
                eventos.append(EventoDuelo(Evento.BATEU, jogador.indice))

        # Só quem sobreviveu anda; as cobras eliminadas já saíram do campo.
        sobreviventes = self.vivos
        for jogador in sobreviventes:
            jogador.cobra.avancar(novas[jogador.indice])
        for jogador in sobreviventes:
            eventos.extend(self._comer_se_houver(jogador))

        if len(sobreviventes) <= 1:
            eventos.append(self._encerrar(sobreviventes))
        return eventos

    def _comer_se_houver(self, jogador: Jogador) -> list[EventoDuelo]:
        cabeca = jogador.cobra.cabeca
        if self.fruta_dourada and cabeca == self.fruta_dourada.posicao:
            # Vale mais pontos e faz crescer, como nos outros modos.
            jogador.pontos += PONTOS_FRUTA_DOURADA
            jogador.cobra.crescer()
            self.fruta_dourada = None
            return [EventoDuelo(Evento.COMEU_DOURADA, jogador.indice)]
        if cabeca not in self.comidas:
            return []
        jogador.pontos += 1
        jogador.cobra.crescer()
        self.total_comidas += 1
        self.comidas.remove(cabeca)
        self._repor_comidas()
        if self.fruta_dourada is None and self.rng.random() < CHANCE_FRUTA_DOURADA:
            posicao = self._sortear_celula_livre()
            if posicao is not None:
                self.fruta_dourada = FrutaDourada(posicao)
        return [EventoDuelo(Evento.COMEU, jogador.indice)]

    def _encerrar(self, sobreviventes: list[Jogador]) -> EventoDuelo:
        self.encerrada = True
        if not sobreviventes:
            return EventoDuelo(Evento.EMPATOU)
        self.vencedor = sobreviventes[0].indice
        return EventoDuelo(Evento.VENCEU, self.vencedor)

    def _repor_comidas(self) -> None:
        while len(self.comidas) < COMIDAS_NO_DUELO:
            posicao = self._sortear_celula_livre()
            if posicao is None:
                return  # campo cheio
            self.comidas.append(posicao)

    def _envelhecer_fruta_dourada(self, dt: float) -> None:
        if self.fruta_dourada is None:
            return
        self.fruta_dourada.tempo_restante -= dt
        if self.fruta_dourada.tempo_restante <= 0:
            self.fruta_dourada = None

    def _sortear_celula_livre(self) -> Posicao | None:
        """Célula sem cobra viva, pedra, maçã nem fruta dourada."""
        ocupadas = set(self.obstaculos) | set(self.comidas)
        for jogador in self.vivos:
            ocupadas.update(jogador.cobra.segmentos)
        if self.fruta_dourada is not None:
            ocupadas.add(self.fruta_dourada.posicao)
        return sortear_posicao_livre(self.grade, ocupadas, self.rng)
