"""Regras do Duelo (V3): de 2 a 4 cobras no mesmo campo, ao mesmo tempo.

Todas as cobras andam no mesmo passo. As colisões de um passo são julgadas juntas,
contra o campo "como se todos tivessem andado":
- borda (no modo Sem bordas, a cobra atravessa), pedra ou corpo (o próprio ou o de
  outra cobra, incluindo a cabeça de antes do passo) eliminam; a cauda de quem anda e
  não está crescendo conta como livre, porque sai dali no mesmo passo;
- duas ou mais cabeças que entram na mesma célula eliminam todas elas;
- duas cabeças que trocam de lugar também se eliminam: cada uma entra no pescoço da outra.

A cobra eliminada some do campo. Sem relógio, vence quem sobrar por último; se todas as
que restavam forem eliminadas no mesmo passo, é empate. Com relógio (modo Contra o
tempo), vence quem tiver mais pontos quando o tempo acabar (pontos iguais: empate); quem
é eliminado sai do campo, mas os pontos dele continuam valendo.

Power-ups disputados: quem pega a câmera lenta deixa os adversários lentos, quem pega o
cogumelo encolhe a cauda deles e os pontos em dobro (só com relógio) valem para quem pegou.
"""

from __future__ import annotations

import random
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from cobrinha.config import (
    CHANCE_FRUTA_DOURADA,
    CHANCE_POWER_UP,
    COMIDAS_NO_DUELO,
    MAX_PASSOS_POR_QUADRO,
    MAXIMO_JOGADORES,
    PONTOS_FRUTA_DOURADA,
    SEGMENTOS_ENCOLHER,
    TAMANHO_INICIAL_COBRA,
    TEMPO_DUELO_COM_RELOGIO,
    VITORIAS_PARA_VENCER,
)
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.comida import sortear_posicao_livre
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Grade, Posicao
from cobrinha.dominio.niveis import NIVEIS, Nivel
from cobrinha.dominio.partida import Evento, FrutaDourada, Modo
from cobrinha.dominio.power_ups import PowerUpNoCampo, TipoPowerUp

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

# Sem relógio, os pontos não decidem a rodada: os pontos em dobro não teriam serventia.
POWER_UPS_SEM_RELOGIO = (TipoPowerUp.CAMERA_LENTA, TipoPowerUp.ENCOLHER)


@dataclass
class Jogador:
    indice: int  # 0 = J1
    cobra: Cobra
    pontos: int = 0
    vivo: bool = True
    # Efeitos com duração sobre este jogador → segundos restantes.
    efeitos: dict[TipoPowerUp, float] = field(default_factory=dict)

    @property
    def nome(self) -> str:
        return f"J{self.indice + 1}"

    @property
    def lento(self) -> bool:
        return TipoPowerUp.CAMERA_LENTA in self.efeitos

    @property
    def multiplicador_pontos(self) -> int:
        return 2 if TipoPowerUp.PONTOS_EM_DOBRO in self.efeitos else 1


@dataclass(frozen=True)
class EventoDuelo:
    """O que aconteceu num passo e com quem (None = vale para a partida toda).

    Num power-up, `power_up` diz qual foi e `alvos`, os adversários atingidos.
    """

    evento: Evento
    jogador: int | None = None
    power_up: TipoPowerUp | None = None
    alvos: tuple[int, ...] = ()


class PartidaDuelo:
    """Uma rodada do duelo."""

    def __init__(
        self,
        quantidade: int = MINIMO_JOGADORES,
        nivel: Nivel = NIVEIS[0],
        grade: Grade = GRADE_PADRAO,
        rng: random.Random | None = None,
        cobras: Sequence[Cobra] | None = None,
        comidas: Iterable[Posicao] | None = None,
        modo: Modo = Modo.CLASSICO,
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
        self.modo = modo
        self.obstaculos = nivel.obstaculos
        self.rng = rng or random.Random()
        self.jogadores = [Jogador(indice, cobra) for indice, cobra in enumerate(cobras)]
        self.fruta_dourada: FrutaDourada | None = None
        self.power_up: PowerUpNoCampo | None = None
        self.comidas: list[Posicao] = []
        if comidas is None:
            self._repor_comidas()
        else:
            self.comidas = list(comidas)
        # Maçãs comidas por todos: a velocidade, que é uma só, cresce com elas (J9).
        self.total_comidas = 0
        self.encerrada = False
        self.vencedor: int | None = None  # índice do jogador; None = empate ou em andamento
        # Relógio da variante Contra o tempo; None nos outros modos.
        self.tempo_restante: float | None = (
            TEMPO_DUELO_COM_RELOGIO if modo is Modo.CONTRA_O_TEMPO else None
        )
        self._tempo_acumulado = 0.0
        self._passos = 0  # contagem de passos: a cobra lenta só anda nos pares

    @property
    def em_andamento(self) -> bool:
        return not self.encerrada

    @property
    def empate(self) -> bool:
        return self.encerrada and self.vencedor is None

    @property
    def tem_relogio(self) -> bool:
        return self.tempo_restante is not None

    @property
    def tempo_esgotado(self) -> bool:
        return self.tempo_restante == 0

    @property
    def vivos(self) -> list[Jogador]:
        return [jogador for jogador in self.jogadores if jogador.vivo]

    @property
    def lider(self) -> int | None:
        """Quem tem mais pontos sozinho (None se houver empate no topo)."""
        maior = max(jogador.pontos for jogador in self.jogadores)
        primeiros = [jogador.indice for jogador in self.jogadores if jogador.pontos == maior]
        return primeiros[0] if len(primeiros) == 1 else None

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
        self._envelhecer_itens_e_efeitos(dt)
        limite = self.intervalo_passo * MAX_PASSOS_POR_QUADRO
        self._tempo_acumulado = min(self._tempo_acumulado + dt, limite)
        eventos = []
        while self.em_andamento and self._tempo_acumulado >= self.intervalo_passo:
            self._tempo_acumulado -= self.intervalo_passo
            eventos.extend(self.passo())
        # Como no Contra o tempo de 1 jogador, um travamento não rouba segundos.
        if self.em_andamento and self.tem_relogio:
            eventos.extend(self._descontar_tempo(min(dt, limite)))
        return eventos

    def passo(self) -> list[EventoDuelo]:
        """Move as cobras uma célula, ao mesmo tempo, e aplica as regras.

        A cobra lenta só anda nos passos pares; nos outros, fica parada e o corpo inteiro
        dela (inclusive a cauda) é obstáculo.
        """
        self._passos += 1
        vivos = self.vivos
        andam = [jogador for jogador in vivos if not (jogador.lento and self._passos % 2)]
        novas = {}
        for jogador in andam:
            nova = jogador.cobra.cabeca.vizinha(jogador.cobra.aplicar_proxima_direcao())
            if self.modo is Modo.SEM_BORDAS:
                nova = self.grade.envolver(nova)
            novas[jogador.indice] = nova
        # Corpos como ficam depois do passo: todos os segmentos, menos as caudas que saem.
        corpos: set[Posicao] = set()
        for jogador in vivos:
            corpos.update(jogador.cobra.segmentos)
            if jogador.indice in novas and jogador.cobra.tamanho_final == len(jogador.cobra):
                corpos.discard(jogador.cobra.cauda)
        cabecas_por_celula = Counter(novas.values())

        eventos = []
        for jogador in andam:
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
        moveram = [jogador for jogador in andam if jogador.vivo]
        for jogador in moveram:
            jogador.cobra.avancar(novas[jogador.indice])
        for jogador in moveram:
            eventos.extend(self._comer_se_houver(jogador))

        fim = self._verificar_fim()
        if fim is not None:
            eventos.append(fim)
        return eventos

    def _comer_se_houver(self, jogador: Jogador) -> list[EventoDuelo]:
        cabeca = jogador.cobra.cabeca
        if self.fruta_dourada and cabeca == self.fruta_dourada.posicao:
            # Vale mais pontos e faz crescer, como nos outros modos.
            jogador.pontos += PONTOS_FRUTA_DOURADA * jogador.multiplicador_pontos
            jogador.cobra.crescer()
            self.fruta_dourada = None
            return [EventoDuelo(Evento.COMEU_DOURADA, jogador.indice)]
        if self.power_up and cabeca == self.power_up.posicao:
            return [self._pegar_power_up(jogador, self.power_up.tipo)]
        if cabeca not in self.comidas:
            return []
        jogador.pontos += jogador.multiplicador_pontos
        jogador.cobra.crescer()
        self.total_comidas += 1
        self.comidas.remove(cabeca)
        self._repor_comidas()
        if self.fruta_dourada is None and self.rng.random() < CHANCE_FRUTA_DOURADA:
            posicao = self._sortear_celula_livre()
            if posicao is not None:
                self.fruta_dourada = FrutaDourada(posicao)
        if self.power_up is None and self.rng.random() < CHANCE_POWER_UP:
            tipos = list(TipoPowerUp) if self.tem_relogio else list(POWER_UPS_SEM_RELOGIO)
            tipo = self.rng.choice(tipos)
            posicao = self._sortear_celula_livre()
            if posicao is not None:
                self.power_up = PowerUpNoCampo(tipo, posicao)
        return [EventoDuelo(Evento.COMEU, jogador.indice)]

    def _pegar_power_up(self, jogador: Jogador, tipo: TipoPowerUp) -> EventoDuelo:
        """Não dá pontos nem faz crescer: aplica o efeito nos adversários (ou em quem pegou)."""
        self.power_up = None
        adversarios = [outro for outro in self.vivos if outro is not jogador]
        alvos: tuple[int, ...] = ()
        if tipo is TipoPowerUp.CAMERA_LENTA:
            # Quem pega fica livre da lentidão e deixa os outros lentos.
            jogador.efeitos.pop(TipoPowerUp.CAMERA_LENTA, None)
            for outro in adversarios:
                outro.efeitos[TipoPowerUp.CAMERA_LENTA] = tipo.duracao
            alvos = tuple(outro.indice for outro in adversarios)
        elif tipo is TipoPowerUp.ENCOLHER:
            for outro in adversarios:
                outro.cobra.encolher(SEGMENTOS_ENCOLHER, minimo=TAMANHO_INICIAL_COBRA)
            alvos = tuple(outro.indice for outro in adversarios)
        else:
            # Pontos em dobro: só para quem pegou; pegar de novo renova, sem somar.
            jogador.efeitos[tipo] = tipo.duracao
        return EventoDuelo(Evento.PEGOU_POWER_UP, jogador.indice, tipo, alvos)

    def _verificar_fim(self) -> EventoDuelo | None:
        vivos = self.vivos
        if not self.tem_relogio:
            if len(vivos) <= 1:
                return self._encerrar(vivos[0].indice if vivos else None)
            return None
        # Com relógio, os pontos decidem. A rodada só acaba antes do tempo se não sobrar
        # ninguém, ou se sobrar um só e ele já estiver na frente.
        if not vivos:
            return self._encerrar(self.lider)
        if len(vivos) == 1 and self.lider == vivos[0].indice:
            return self._encerrar(vivos[0].indice)
        return None

    def _descontar_tempo(self, dt: float) -> list[EventoDuelo]:
        assert self.tempo_restante is not None
        self.tempo_restante = max(0.0, self.tempo_restante - dt)
        if self.tempo_restante > 0:
            return []
        return [EventoDuelo(Evento.TEMPO_ESGOTADO), self._encerrar(self.lider)]

    def _encerrar(self, vencedor: int | None) -> EventoDuelo:
        self.encerrada = True
        self.vencedor = vencedor
        if vencedor is None:
            return EventoDuelo(Evento.EMPATOU)
        return EventoDuelo(Evento.VENCEU, vencedor)

    def _repor_comidas(self) -> None:
        while len(self.comidas) < COMIDAS_NO_DUELO:
            posicao = self._sortear_celula_livre()
            if posicao is None:
                return  # campo cheio
            self.comidas.append(posicao)

    def _envelhecer_itens_e_efeitos(self, dt: float) -> None:
        """Fruta dourada e power-up somem com o tempo; os efeitos acabam."""
        if self.fruta_dourada is not None:
            self.fruta_dourada.tempo_restante -= dt
            if self.fruta_dourada.tempo_restante <= 0:
                self.fruta_dourada = None
        if self.power_up is not None:
            self.power_up.tempo_restante -= dt
            if self.power_up.tempo_restante <= 0:
                self.power_up = None
        for jogador in self.jogadores:
            for tipo in list(jogador.efeitos):
                jogador.efeitos[tipo] -= dt
                if jogador.efeitos[tipo] <= 0:
                    del jogador.efeitos[tipo]

    def _sortear_celula_livre(self) -> Posicao | None:
        """Célula sem cobra viva, pedra, maçã, fruta dourada nem power-up."""
        ocupadas = set(self.obstaculos) | set(self.comidas)
        for jogador in self.vivos:
            ocupadas.update(jogador.cobra.segmentos)
        if self.fruta_dourada is not None:
            ocupadas.add(self.fruta_dourada.posicao)
        if self.power_up is not None:
            ocupadas.add(self.power_up.posicao)
        return sortear_posicao_livre(self.grade, ocupadas, self.rng)


@dataclass
class Placar:
    """Vitórias de cada jogador ao longo das rodadas, até alguém ser campeão."""

    quantidade: int
    vitorias: list[int] = field(default_factory=list)
    rodada: int = 1

    def __post_init__(self) -> None:
        if not self.vitorias:
            self.vitorias = [0] * self.quantidade

    @property
    def campeao(self) -> int | None:
        for indice, vitorias in enumerate(self.vitorias):
            if vitorias >= VITORIAS_PARA_VENCER:
                return indice
        return None

    def registrar(self, vencedor: int | None) -> None:
        """Conta o resultado da rodada (empate não dá vitória a ninguém)."""
        if self.campeao is not None:
            raise RuntimeError("A disputa já tem campeão.")
        if vencedor is not None:
            self.vitorias[vencedor] += 1

    def nova_rodada(self) -> None:
        if self.campeao is not None:
            raise RuntimeError("A disputa já tem campeão.")
        self.rodada += 1
