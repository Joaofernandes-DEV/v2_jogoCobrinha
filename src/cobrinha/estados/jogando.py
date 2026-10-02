"""Tela da partida em andamento."""

import pygame

from cobrinha.config import ALTURA_HUD, ALTURA_JANELA, LARGURA_JANELA, Paleta
from cobrinha.dominio.grade import Direcao
from cobrinha.dominio.partida import Partida
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
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
TECLAS_PAUSA = (pygame.K_ESCAPE, pygame.K_p)


class EstadoJogando(Estado):
    def __init__(self, jogo: Jogo, partida: Partida | None = None, nivel_inicial: int = 1) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.partida = partida if partida is not None else Partida(rng=jogo.rng)
        # Nível em que a campanha começou: "jogar de novo" volta para ele.
        self.nivel_inicial = nivel_inicial

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.WINDOWFOCUSLOST:
            # Pausa automática ao trocar de janela (J2).
            navegacao.pausar(self.jogo, self)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_DIRECAO:
                self.partida.virar(TECLAS_DIRECAO[evento.key])
            elif evento.key in TECLAS_PAUSA:
                navegacao.pausar(self.jogo, self)

    def atualizar(self, dt: float) -> None:
        self.partida.atualizar(dt)
        if not self.partida.em_andamento:
            navegacao.encerrar_partida(self.jogo, self)

    def desenhar(self, superficie: pygame.Surface) -> None:
        partida = self.partida
        recorde = max(self.jogo.progresso.recorde, partida.pontos)
        desenhar_hud(
            superficie,
            partida.pontos,
            partida.nivel.numero,
            recorde,
            partida.comidas_no_nivel,
            partida.nivel.meta_comidas,
        )
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
        if partida.comida is not None:
            desenhar_comida(superficie, partida.comida)
        desenhar_cobra(superficie, partida.cobra)
        if self.jogo.debug:
            self._desenhar_depuracao(superficie)

    def _desenhar_depuracao(self, superficie: pygame.Surface) -> None:
        info = f"FPS {self.jogo.relogio.get_fps():.0f}  COBRA {len(self.partida.cobra)}"
        imagem = texto.renderizar(info, 20, Paleta.PRETO)
        superficie.blit(
            imagem, imagem.get_rect(bottomright=(LARGURA_JANELA - 6, ALTURA_JANELA - 4))
        )
