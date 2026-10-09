"""Tela do Duelo (V3): cada jogador controla a própria cobra.

Cada jogador tem a sua entrada (WASD, setas ou um controle; ver `entradas.py`), escolhida
na tela "Quem joga?". O controle de cada jogador acende na cor da cobra dele e só vibra
com o que acontece com ele. Se o controle de um jogador desconectar, o duelo para até ele
ser reconectado.

Cada tela de duelo é uma rodada; o `Placar` passa de uma rodada para a outra até alguém
fazer 3 vitórias. O item MODO do menu vale também aqui (Clássico, Sem bordas ou a variante
com relógio, Contra o tempo).
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

import pygame

from cobrinha.audio import Som, musica_da_fase
from cobrinha.config import (
    ALTURA_HUD,
    ALTURA_JANELA,
    LARGURA_JANELA,
    PELES,
    PONTOS_FRUTA_DOURADA,
    TAMANHO_CELULA,
    Cor,
    Paleta,
    PeleCobra,
    TamanhoFonte,
)
from cobrinha.controle import Vibracao, controle_desconectado
from cobrinha.dominio.duelo import PartidaDuelo, Placar
from cobrinha.dominio.niveis import obter_nivel
from cobrinha.dominio.partida import Evento, Modo
from cobrinha.entradas import TECLADO_DIREITO, TECLADO_ESQUERDO, Entrada
from cobrinha.estados import navegacao
from cobrinha.estados.base import EstadoDePartida
from cobrinha.estados.jogando import (
    DURACAO_MORTE,
    DURACAO_MORTE_SEM_EFEITOS,
    PISCADAS_POR_SEGUNDO,
    ROTULO_DO_POWER_UP,
    TECLAS_PAUSA,
    TEXTO_AO_PEGAR,
)
from cobrinha.ui import texto
from cobrinha.ui.campo import celula_para_pixel, criar_fundo_campo
from cobrinha.ui.efeitos import Efeitos
from cobrinha.ui.hud import DadosHudDuelo, PlacarJogador, desenhar_hud_duelo
from cobrinha.ui.pecas import Sprites

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

# Sem a tela "Quem joga?" (ex.: nos testes), o duelo é no teclado: J1 no WASD, J2 nas setas.
ENTRADAS_PADRAO = (TECLADO_ESQUERDO, TECLADO_DIREITO)
# Luz do controle de quem foi eliminado (como o "FORA" do HUD).
COR_ELIMINADO = Paleta.CINZA
# Luz dos controles conectados que não estão no duelo (diferente de todas as cobras).
COR_FORA_DO_DUELO = Paleta.BRANCO

SOM_DO_EVENTO = {
    Evento.COMEU: Som.COMER,
    Evento.COMEU_DOURADA: Som.BONUS,
    Evento.PEGOU_POWER_UP: Som.POWER_UP,
    Evento.BATEU: Som.BATER,
    Evento.VENCEU: Som.VITORIA,
    Evento.TEMPO_ESGOTADO: Som.NIVEL,
}
# Só o controle de quem comeu, pegou um power-up, bateu ou venceu vibra (os atingidos por um
# power-up vibram fraco).
VIBRACAO_DO_EVENTO = {
    Evento.COMEU: Vibracao.FRACA,
    Evento.COMEU_DOURADA: Vibracao.MEDIA,
    Evento.PEGOU_POWER_UP: Vibracao.MEDIA,
    Evento.BATEU: Vibracao.FORTE,
    Evento.VENCEU: Vibracao.MEDIA,
}
VIBRACAO_DO_ALVO = Vibracao.FRACA
PONTOS_DO_EVENTO = {Evento.COMEU: 1, Evento.COMEU_DOURADA: PONTOS_FRUTA_DOURADA}


def nome_do_jogador(indice: int) -> str:
    return f"JOGADOR {indice + 1}"


def pele_do_jogador(indice: int) -> PeleCobra:
    return PELES[indice]


class EstadoDuelo(EstadoDePartida):
    def __init__(
        self,
        jogo: Jogo,
        numero_nivel: int = 1,
        entradas: Sequence[Entrada] = ENTRADAS_PADRAO,
        partida: PartidaDuelo | None = None,
        modo: Modo = Modo.CLASSICO,
        placar: Placar | None = None,
    ):
        super().__init__(jogo)
        # Entrada de cada jogador, na ordem J1, J2... (muda se um controle for religado).
        self.entradas = list(entradas)
        self.partida = (
            partida
            if partida is not None
            else PartidaDuelo(
                len(self.entradas), nivel=obter_nivel(numero_nivel), rng=jogo.rng, modo=modo
            )
        )
        # Vitórias até aqui; a primeira rodada começa um placar novo.
        self.placar = placar if placar is not None else Placar(len(self.entradas))
        self.sprites = Sprites()
        self.fundo_campo = criar_fundo_campo()
        self.sprites.desenhar_obstaculos(self.fundo_campo, self.partida.obstaculos, topo=0)
        self.tempo = 0.0
        self.efeitos = Efeitos()
        # Jogador eliminado → segundos que a cobra dele ainda pisca antes de sumir.
        self.piscando: dict[int, float] = {}
        self.tempo_ate_encerrar: float | None = None
        jogo.audio.tocar_musica(musica_da_fase(self.partida.nivel.numero))

    @property
    def numero_nivel(self) -> int:
        return self.partida.nivel.numero

    @property
    def jogadores_sem_controle(self) -> list[int]:
        """Jogadores ainda vivos cujo controle não está mais conectado."""
        if not self.partida.em_andamento:
            return []
        conectados = self.jogo.controles.ids_conectados
        return [
            indice
            for indice, entrada in enumerate(self.entradas)
            if entrada.e_controle
            and entrada.controle_id not in conectados
            and self.partida.jogadores[indice].vivo
        ]

    def religar(self, indice: int, controle_id: int) -> None:
        """O jogador `indice` passa a jogar com o controle `controle_id` (reconectado)."""
        self.entradas[indice] = Entrada.controle(controle_id)

    def tratar_evento(self, evento: pygame.Event) -> None:
        if self.tempo_ate_encerrar is not None:
            return  # animação de fim em andamento
        if evento.type == pygame.WINDOWFOCUSLOST:
            if controle_desconectado(evento) is None:
                navegacao.pausar(self.jogo, self)  # a janela perdeu o foco
            elif self.jogadores_sem_controle:
                navegacao.pedir_controle(self.jogo, self)
            # Saiu o controle de quem não está jogando: o duelo segue.
        elif evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_PAUSA:
                navegacao.pausar(self.jogo, self)
                return
            for indice, entrada in enumerate(self.entradas):
                direcao = entrada.direcao(evento)
                if direcao is not None:
                    self.partida.virar(indice, direcao)

    @property
    def cor_do_controle(self) -> Cor:
        return COR_FORA_DO_DUELO

    @property
    def luzes_dos_controles(self) -> dict[int, Cor]:
        """O controle de cada jogador na cor da cobra dele; cinza depois de eliminado."""
        return {
            entrada.controle_id: (
                pele_do_jogador(indice).destaque
                if self.partida.jogadores[indice].vivo
                else COR_ELIMINADO
            )
            for indice, entrada in enumerate(self.entradas)
            if entrada.controle_id is not None
        }

    def reiniciar(self) -> None:
        """REINICIAR na pausa recomeça a disputa, com o placar zerado."""
        navegacao.iniciar_duelo(self.jogo, self.numero_nivel, self.entradas, self.partida.modo)

    def abandonar(self) -> None:
        navegacao.abrir_menu(self.jogo)

    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        self.efeitos.atualizar(dt)
        for indice in list(self.piscando):
            self.piscando[indice] -= dt
            if self.piscando[indice] <= 0:
                del self.piscando[indice]
        if self.tempo_ate_encerrar is not None:
            self.tempo_ate_encerrar -= dt
            if self.tempo_ate_encerrar <= 0:
                navegacao.encerrar_duelo(self.jogo, self)
            return
        if self.jogadores_sem_controle:
            # Ex.: o controle saiu durante a pausa ou a contagem.
            navegacao.pedir_controle(self.jogo, self)
            return

        for acontecimento in self.partida.atualizar(dt):
            evento, indice = acontecimento.evento, acontecimento.jogador
            if evento in (Evento.VENCEU, Evento.EMPATOU):
                self.jogo.audio.parar_musica()
            if evento in SOM_DO_EVENTO:
                self.jogo.audio.tocar(SOM_DO_EVENTO[evento])
            if indice is None:
                continue
            if evento in VIBRACAO_DO_EVENTO:
                self._vibrar(VIBRACAO_DO_EVENTO[evento], indice)
            if evento is Evento.BATEU and self.jogo.opcoes.efeitos_visuais:
                self.piscando[indice] = DURACAO_MORTE
            jogador = self.partida.jogadores[indice]
            if evento in PONTOS_DO_EVENTO:
                pontos = PONTOS_DO_EVENTO[evento] * jogador.multiplicador_pontos
                self._texto_flutuante(indice, f"+{pontos}")
            if evento is Evento.PEGOU_POWER_UP and acontecimento.power_up is not None:
                self._texto_flutuante(indice, TEXTO_AO_PEGAR[acontecimento.power_up])
                for alvo in acontecimento.alvos:
                    self._vibrar(VIBRACAO_DO_ALVO, alvo)

        if self.partida.encerrada:
            self.placar.registrar(self.partida.vencedor)
            efeitos = self.jogo.opcoes.efeitos_visuais
            self.tempo_ate_encerrar = DURACAO_MORTE if efeitos else DURACAO_MORTE_SEM_EFEITOS

    def _vibrar(self, vibracao: Vibracao, indice: int) -> None:
        entrada = self.entradas[indice]
        if entrada.controle_id is not None:
            self.jogo.controles.vibrar(vibracao, entrada.controle_id)

    def _texto_flutuante(self, indice: int, conteudo: str) -> None:
        """Texto que sobe da cabeça do jogador, na cor da cobra dele (ex.: "+1", "LENTO!")."""
        if not self.jogo.opcoes.efeitos_visuais:
            return
        x, y = celula_para_pixel(self.partida.jogadores[indice].cobra.cabeca)
        meio = TAMANHO_CELULA // 2
        cor = pele_do_jogador(indice).destaque
        self.efeitos.texto_flutuante(conteudo, cor, (x + meio, y + meio))

    def cobra_visivel(self, indice: int) -> bool:
        """Cobra viva aparece sempre; a eliminada pisca e depois some do campo."""
        if self.partida.jogadores[indice].vivo:
            return True
        if indice not in self.piscando:
            return False
        return int(self.piscando[indice] * PISCADAS_POR_SEGUNDO) % 2 == 0

    def desenhar(self, superficie: pygame.Surface) -> None:
        partida = self.partida
        dados = DadosHudDuelo(
            jogadores=tuple(
                PlacarJogador(
                    nome_do_jogador(jogador.indice),
                    jogador.pontos,
                    pele_do_jogador(jogador.indice).destaque,
                    jogador.vivo,
                    vitorias=self.placar.vitorias[jogador.indice],
                    efeitos=tuple(
                        (ROTULO_DO_POWER_UP[tipo], restante)
                        for tipo, restante in jogador.efeitos.items()
                    ),
                )
                for jogador in partida.jogadores
            ),
            nome_nivel=partida.nivel.nome,
            mudo=self.jogo.audio.mudo,
            rodada=self.placar.rodada,
            tempo=partida.tempo_restante,
        )
        desenhar_hud_duelo(superficie, dados)
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
        for comida in partida.comidas:
            self.sprites.desenhar_comida(superficie, comida, self.tempo)
        if partida.fruta_dourada is not None:
            self.sprites.desenhar_fruta_dourada(
                superficie,
                partida.fruta_dourada.posicao,
                self.tempo,
                partida.fruta_dourada.tempo_restante,
            )
        if partida.power_up is not None:
            self.sprites.desenhar_power_up(superficie, partida.power_up, self.tempo)
        for jogador in partida.jogadores:
            if self.cobra_visivel(jogador.indice):
                pele = pele_do_jogador(jogador.indice)
                self.sprites.desenhar_cobra(superficie, jogador.cobra, pele)
        self.efeitos.desenhar(superficie)
        if self.jogo.debug:
            info = (
                f"FPS {self.jogo.relogio.get_fps():.0f}"
                f"  VELOCIDADE {partida.passos_por_segundo:.2f}"
            )
            imagem = texto.renderizar(info, TamanhoFonte.MINIMO, Paleta.PRETO)
            superficie.blit(
                imagem, imagem.get_rect(bottomright=(LARGURA_JANELA - 6, ALTURA_JANELA - 4))
            )
