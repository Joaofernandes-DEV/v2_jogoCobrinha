"""Tela da partida em andamento."""

import pygame

from cobrinha.audio import Som
from cobrinha.config import ALTURA_HUD, ALTURA_JANELA, LARGURA_JANELA, Paleta, TamanhoFonte
from cobrinha.dominio.grade import Direcao
from cobrinha.dominio.partida import Evento, Partida
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.jogo import Jogo
from cobrinha.ui import texto
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.hud import DadosHud, desenhar_hud
from cobrinha.ui.pecas import Sprites

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

SOM_DO_EVENTO = {
    Evento.COMEU: Som.COMER,
    Evento.CONCLUIU_NIVEL: Som.NIVEL,
    Evento.BATEU: Som.BATER,
    Evento.VENCEU: Som.VITORIA,
}


class EstadoJogando(Estado):
    def __init__(self, jogo: Jogo, partida: Partida | None = None, nivel_inicial: int = 1) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.sprites = Sprites()
        self.partida = partida if partida is not None else Partida(rng=jogo.rng)
        # Nível em que a campanha começou: "jogar de novo" volta para ele.
        self.nivel_inicial = nivel_inicial
        self.tempo = 0.0  # para animações (comida flutuando)
        jogo.audio.tocar_musica()

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
        self.tempo += dt
        for evento in self.partida.atualizar(dt):
            if evento in SOM_DO_EVENTO:
                self.jogo.audio.tocar(SOM_DO_EVENTO[evento])
        if not self.partida.em_andamento:
            navegacao.encerrar_partida(self.jogo, self)

    def desenhar(self, superficie: pygame.Surface) -> None:
        partida = self.partida
        dados = DadosHud(
            pontos=partida.pontos,
            recorde=max(self.jogo.progresso.recorde, partida.pontos),
            nivel=partida.nivel.numero,
            comidas=partida.comidas_no_nivel,
            meta=partida.nivel.meta_comidas,
            mudo=self.jogo.audio.mudo,
        )
        desenhar_hud(superficie, dados)
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
        if partida.comida is not None:
            self.sprites.desenhar_comida(superficie, partida.comida, self.tempo)
        self.sprites.desenhar_cobra(superficie, partida.cobra)
        if self.jogo.debug:
            self._desenhar_depuracao(superficie)

    def _desenhar_depuracao(self, superficie: pygame.Surface) -> None:
        info = f"FPS {self.jogo.relogio.get_fps():.0f}  COBRA {len(self.partida.cobra)}"
        imagem = texto.renderizar(info, TamanhoFonte.MINIMO, Paleta.PRETO)
        superficie.blit(
            imagem, imagem.get_rect(bottomright=(LARGURA_JANELA - 6, ALTURA_JANELA - 4))
        )
