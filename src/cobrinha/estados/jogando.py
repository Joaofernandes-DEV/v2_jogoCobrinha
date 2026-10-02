"""Tela da partida em andamento."""

import pygame

from cobrinha.config import ALTURA_HUD, ALTURA_JANELA, LARGURA_JANELA, Paleta
from cobrinha.dominio.grade import Direcao
from cobrinha.dominio.partida import Partida
from cobrinha.estados.base import Estado
from cobrinha.estados.fim_de_partida import EstadoFimDePartida
from cobrinha.jogo import Jogo
from cobrinha.ui import texto
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.hud import desenhar_hud
from cobrinha.ui.pecas import desenhar_cobra, desenhar_comida

# Setas e WASD funcionam sempre, ao mesmo tempo.
TECLAS_DIRECAO = {
    pygame.K_UP: Direcao.CIMA,
    pygame.K_w: Direcao.CIMA,
    pygame.K_DOWN: Direcao.BAIXO,
    pygame.K_s: Direcao.BAIXO,
    pygame.K_LEFT: Direcao.ESQUERDA,
    pygame.K_a: Direcao.ESQUERDA,
    pygame.K_RIGHT: Direcao.DIREITA,
    pygame.K_d: Direcao.DIREITA,
}


class EstadoJogando(Estado):
    def __init__(self, jogo: Jogo, recorde: int = 0) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.partida = Partida(rng=jogo.rng)
        self.nivel = 1
        self.recorde = recorde

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type != pygame.KEYDOWN:
            return
        if evento.key in TECLAS_DIRECAO:
            self.partida.virar(TECLAS_DIRECAO[evento.key])
        elif evento.key == pygame.K_ESCAPE:
            # Na Fase 2, Esc passa a abrir a pausa.
            self.jogo.sair()

    def atualizar(self, dt: float) -> None:
        self.partida.atualizar(dt)
        if not self.partida.em_andamento:
            self.jogo.empilhar(EstadoFimDePartida(self.jogo, self.partida, self.recorde))

    def desenhar(self, superficie: pygame.Surface) -> None:
        recorde = max(self.recorde, self.partida.pontos)
        desenhar_hud(superficie, self.partida.pontos, self.nivel, recorde)
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
        if self.partida.comida is not None:
            desenhar_comida(superficie, self.partida.comida)
        desenhar_cobra(superficie, self.partida.cobra)
        if self.jogo.debug:
            self._desenhar_depuracao(superficie)

    def _desenhar_depuracao(self, superficie: pygame.Surface) -> None:
        info = f"FPS {self.jogo.relogio.get_fps():.0f}  COBRA {len(self.partida.cobra)}"
        imagem = texto.renderizar(info, 20, Paleta.PRETO)
        superficie.blit(
            imagem, imagem.get_rect(bottomright=(LARGURA_JANELA - 6, ALTURA_JANELA - 4))
        )
