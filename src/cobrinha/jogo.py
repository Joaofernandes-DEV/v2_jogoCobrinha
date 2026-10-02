"""Loop principal e gerenciador de estados (telas) do jogo."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import pygame

from cobrinha import persistencia, recursos
from cobrinha.audio import Audio
from cobrinha.config import (
    ALTURA_JANELA,
    DURACAO_FADE,
    FPS,
    FREQUENCIA_AUDIO,
    LARGURA_JANELA,
    TITULO,
    Paleta,
)

if TYPE_CHECKING:
    from cobrinha.estados.base import Estado


class Jogo:
    """Dono da janela e do único loop do jogo.

    As telas ficam numa pilha: só a do topo recebe eventos e é atualizada,
    mas todas são desenhadas de baixo para cima (assim a pausa aparece
    por cima do jogo congelado).
    """

    def __init__(self, debug: bool = False, semente: int | None = None) -> None:
        self.debug = debug
        # Gerador único de aleatoriedade; com semente, as partidas são reproduzíveis.
        self.rng = random.Random(semente)
        # Recordes, níveis liberados e opções salvos de sessões anteriores (J6, I9).
        self.progresso, self.opcoes = persistencia.carregar()
        # Mono, 16 bits, na mesma taxa dos WAVs gerados; buffer pequeno = som sem atraso.
        pygame.mixer.pre_init(FREQUENCIA_AUDIO, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption(TITULO)
        pygame.display.set_icon(pygame.image.load(recursos.PASTA_IMAGENS / "comida.png"))
        # SCALED permite ampliar a janela e usar tela cheia sem borrar a pixel art.
        self.tela = pygame.display.set_mode((LARGURA_JANELA, ALTURA_JANELA), pygame.SCALED)
        self.relogio = pygame.time.Clock()
        self.audio = Audio()
        self.aplicar_opcoes()
        self.pilha: list[Estado] = []
        self.rodando = False
        # Fade de entrada (I7): 1 = tela toda preta, 0 = sem fade.
        self.opacidade_fade = 0.0
        self._camada_fade = pygame.Surface((LARGURA_JANELA, ALTURA_JANELA))
        self._camada_fade.fill(Paleta.PRETO)

    def aplicar_opcoes(self) -> None:
        """Leva as opções atuais para o áudio e o modo de tela."""
        self.audio.definir_volumes(self.opcoes.volume_efeitos, self.opcoes.volume_musica)
        tela_cheia = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        if tela_cheia != self.opcoes.tela_cheia:
            try:
                pygame.display.toggle_fullscreen()
            except pygame.error:
                self.opcoes.tela_cheia = tela_cheia  # sem suporte (ex.: driver de testes)

    def salvar(self) -> None:
        persistencia.salvar(self.progresso, self.opcoes)

    @property
    def estado_atual(self) -> Estado | None:
        return self.pilha[-1] if self.pilha else None

    def trocar_estado(self, estado: Estado) -> None:
        """Substitui a pilha inteira por uma nova tela, com fade de entrada."""
        self.pilha = [estado]
        self.opacidade_fade = 1.0

    def empilhar(self, estado: Estado) -> None:
        """Abre uma tela por cima da atual (ex.: pausa)."""
        self.pilha.append(estado)

    def desempilhar(self) -> None:
        """Fecha a tela do topo e volta para a de baixo."""
        if self.pilha:
            self.pilha.pop()

    def sair(self) -> None:
        """Pede o fim do loop. O pygame é encerrado só em `executar`."""
        self.rodando = False

    def executar(self) -> None:
        self.rodando = True
        try:
            while self.rodando and self.estado_atual is not None:
                dt = self.relogio.tick(FPS) / 1000
                self._processar_eventos()
                if not self.rodando:
                    break
                self.estado_atual.atualizar(dt)
                self.opacidade_fade = max(0.0, self.opacidade_fade - dt / DURACAO_FADE)
                self._desenhar()
        finally:
            # Único ponto de encerramento do pygame (corrige B1 e B5 da V1).
            pygame.quit()

    def _processar_eventos(self) -> None:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.sair()
                return
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_m:
                # M silencia/reativa o som em qualquer tela.
                self.audio.alternar_mudo()
                continue
            if self.estado_atual is not None:
                self.estado_atual.tratar_evento(evento)

    def _desenhar(self) -> None:
        self.tela.fill(Paleta.PRETO)
        for estado in self.pilha:
            estado.desenhar(self.tela)
        if self.opacidade_fade > 0:
            self._camada_fade.set_alpha(round(255 * self.opacidade_fade))
            self.tela.blit(self._camada_fade, (0, 0))
        pygame.display.flip()
