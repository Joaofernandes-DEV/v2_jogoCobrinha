"""Tela do Duelo (V3): cada jogador controla a própria cobra, no mesmo teclado.

Nos modos de 1 jogador, setas e WASD movem a mesma cobra; aqui eles se separam:
WASD é do jogador 1 e as setas são do jogador 2.
"""

from __future__ import annotations

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
    Paleta,
    PeleCobra,
    TamanhoFonte,
)
from cobrinha.controle import Vibracao
from cobrinha.dominio.duelo import PartidaDuelo
from cobrinha.dominio.grade import Direcao
from cobrinha.dominio.niveis import obter_nivel
from cobrinha.dominio.partida import Evento
from cobrinha.estados import navegacao
from cobrinha.estados.base import EstadoDePartida
from cobrinha.estados.jogando import (
    DURACAO_MORTE,
    DURACAO_MORTE_SEM_EFEITOS,
    PISCADAS_POR_SEGUNDO,
    TECLAS_PAUSA,
)
from cobrinha.ui import texto
from cobrinha.ui.campo import celula_para_pixel, criar_fundo_campo
from cobrinha.ui.efeitos import Efeitos
from cobrinha.ui.hud import DadosHudDuelo, PlacarJogador, desenhar_hud_duelo
from cobrinha.ui.pecas import Sprites

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

# Teclas de cada jogador, na ordem J1, J2.
TECLAS_DOS_JOGADORES = (
    {
        pygame.K_w: Direcao.CIMA,
        pygame.K_s: Direcao.BAIXO,
        pygame.K_a: Direcao.ESQUERDA,
        pygame.K_d: Direcao.DIREITA,
    },
    {
        pygame.K_UP: Direcao.CIMA,
        pygame.K_DOWN: Direcao.BAIXO,
        pygame.K_LEFT: Direcao.ESQUERDA,
        pygame.K_RIGHT: Direcao.DIREITA,
    },
)
DICA_DOS_CONTROLES = "J1: WASD   J2: SETAS"

SOM_DO_EVENTO = {
    Evento.COMEU: Som.COMER,
    Evento.COMEU_DOURADA: Som.BONUS,
    Evento.BATEU: Som.BATER,
    Evento.VENCEU: Som.VITORIA,
}
VIBRACAO_DO_EVENTO = {
    Evento.COMEU: Vibracao.FRACA,
    Evento.COMEU_DOURADA: Vibracao.MEDIA,
    Evento.BATEU: Vibracao.FORTE,
}
PONTOS_DO_EVENTO = {Evento.COMEU: 1, Evento.COMEU_DOURADA: PONTOS_FRUTA_DOURADA}


def nome_do_jogador(indice: int) -> str:
    return f"JOGADOR {indice + 1}"


def pele_do_jogador(indice: int) -> PeleCobra:
    return PELES[indice]


class EstadoDuelo(EstadoDePartida):
    def __init__(self, jogo: Jogo, numero_nivel: int = 1, partida: PartidaDuelo | None = None):
        super().__init__(jogo)
        self.partida = (
            partida
            if partida is not None
            else PartidaDuelo(nivel=obter_nivel(numero_nivel), rng=jogo.rng)
        )
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

    def tratar_evento(self, evento: pygame.Event) -> None:
        if self.tempo_ate_encerrar is not None:
            return  # animação de fim em andamento
        if evento.type == pygame.WINDOWFOCUSLOST:
            navegacao.pausar(self.jogo, self)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_PAUSA:
                navegacao.pausar(self.jogo, self)
                return
            for indice, teclas in enumerate(TECLAS_DOS_JOGADORES[: len(self.partida.jogadores)]):
                if evento.key in teclas:
                    self.partida.virar(indice, teclas[evento.key])

    def reiniciar(self) -> None:
        navegacao.iniciar_duelo(self.jogo, self.numero_nivel)

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

        for acontecimento in self.partida.atualizar(dt):
            evento, indice = acontecimento.evento, acontecimento.jogador
            if evento in (Evento.VENCEU, Evento.EMPATOU):
                self.jogo.audio.parar_musica()
            if evento in SOM_DO_EVENTO:
                self.jogo.audio.tocar(SOM_DO_EVENTO[evento])
            if evento in VIBRACAO_DO_EVENTO:
                self.jogo.controles.vibrar(VIBRACAO_DO_EVENTO[evento])
            if evento is Evento.BATEU and self.jogo.opcoes.efeitos_visuais:
                self.piscando[indice] = DURACAO_MORTE
            if evento in PONTOS_DO_EVENTO:
                self._pontos_flutuantes(indice, PONTOS_DO_EVENTO[evento])

        if self.partida.encerrada:
            efeitos = self.jogo.opcoes.efeitos_visuais
            self.tempo_ate_encerrar = DURACAO_MORTE if efeitos else DURACAO_MORTE_SEM_EFEITOS

    def _pontos_flutuantes(self, indice: int, pontos: int) -> None:
        if not self.jogo.opcoes.efeitos_visuais:
            return
        x, y = celula_para_pixel(self.partida.jogadores[indice].cobra.cabeca)
        meio = TAMANHO_CELULA // 2
        cor = pele_do_jogador(indice).destaque
        self.efeitos.texto_flutuante(f"+{pontos}", cor, (x + meio, y + meio))

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
                )
                for jogador in partida.jogadores
            ),
            nome_nivel=partida.nivel.nome,
            mudo=self.jogo.audio.mudo,
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
