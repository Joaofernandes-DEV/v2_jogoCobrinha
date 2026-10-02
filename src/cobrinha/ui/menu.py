"""Menu vertical navegável por teclado e mouse (I1)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pygame

from cobrinha import recursos
from cobrinha.audio import Som
from cobrinha.config import LARGURA_JANELA, Paleta, TamanhoFonte
from cobrinha.ui import texto

TECLAS_CIMA = (pygame.K_UP, pygame.K_w)
TECLAS_BAIXO = (pygame.K_DOWN, pygame.K_s)
TECLAS_ESQUERDA = (pygame.K_LEFT, pygame.K_a)
TECLAS_DIREITA = (pygame.K_RIGHT, pygame.K_d)
TECLAS_CONFIRMAR = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
BOTAO_ESQUERDO = 1

DISTANCIA_MARCADOR = 18  # px entre o texto e o triângulo de seleção
FOLGA_CLIQUE = (60, 10)  # a área clicável é um pouco maior que o texto
FRACAO_SETA = 0.25  # em itens ajustáveis, clicar no quarto esquerdo/direito ajusta o valor


@dataclass
class ItemMenu:
    rotulo: str | Callable[[], str]  # função para rótulos que mudam (ex.: nível escolhido)
    acao: Callable[[], None] | None = None  # Enter ou clique
    ajustar: Callable[[int], None] | None = None  # ← (-1) e → (+1)

    @property
    def texto(self) -> str:
        return self.rotulo() if callable(self.rotulo) else self.rotulo


class Menu:
    def __init__(self, itens: list[ItemMenu], tocar: Callable[[Som], None] | None = None) -> None:
        if not itens:
            raise ValueError("O menu precisa de pelo menos um item.")
        self.itens = itens
        self.selecionado = 0
        self._tocar = tocar or (lambda som: None)
        # Áreas clicáveis de cada item, calculadas no último desenho.
        self._areas: list[pygame.Rect] = []

    @property
    def item_atual(self) -> ItemMenu:
        return self.itens[self.selecionado]

    def tratar_evento(self, evento: pygame.Event) -> bool:
        """Processa teclado ou mouse. Devolve True se o menu usou o evento."""
        if evento.type == pygame.KEYDOWN:
            return self._tratar_tecla(evento.key)
        if evento.type == pygame.MOUSEMOTION:
            indice = self._item_em(evento.pos)
            if indice is not None and indice != self.selecionado:
                self._selecionar(indice)
            return indice is not None
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == BOTAO_ESQUERDO:
            return self._tratar_clique(evento.pos)
        return False

    def _tratar_tecla(self, tecla: int) -> bool:
        item = self.item_atual
        if tecla in TECLAS_CIMA:
            self._selecionar((self.selecionado - 1) % len(self.itens))
        elif tecla in TECLAS_BAIXO:
            self._selecionar((self.selecionado + 1) % len(self.itens))
        elif tecla in TECLAS_ESQUERDA and item.ajustar:
            self._ajustar(item, -1)
        elif tecla in TECLAS_DIREITA and item.ajustar:
            self._ajustar(item, +1)
        elif tecla in TECLAS_CONFIRMAR and item.acao:
            self._confirmar(item)
        else:
            return False
        return True

    def _tratar_clique(self, posicao: tuple[int, int]) -> bool:
        indice = self._item_em(posicao)
        if indice is None:
            return False
        self.selecionado = indice
        item, area = self.itens[indice], self._areas[indice]
        margem_seta = area.width * FRACAO_SETA
        if item.ajustar and posicao[0] < area.left + margem_seta:
            self._ajustar(item, -1)
        elif item.ajustar and posicao[0] > area.right - margem_seta:
            self._ajustar(item, +1)
        elif item.acao:
            self._confirmar(item)
        return True

    def _item_em(self, posicao: tuple[int, int]) -> int | None:
        for indice, area in enumerate(self._areas):
            if area.collidepoint(posicao):
                return indice
        return None

    def _selecionar(self, indice: int) -> None:
        self.selecionado = indice
        self._tocar(Som.MENU_MOVER)

    def _ajustar(self, item: ItemMenu, delta: int) -> None:
        assert item.ajustar is not None
        item.ajustar(delta)
        self._tocar(Som.MENU_MOVER)

    def _confirmar(self, item: ItemMenu) -> None:
        assert item.acao is not None
        self._tocar(Som.MENU_CONFIRMAR)
        item.acao()

    def desenhar(
        self,
        superficie: pygame.Surface,
        topo: int,
        tamanho: int = TamanhoFonte.MEDIO,
        espaco: int = 18,
    ) -> None:
        # Passo fixo por linha: a altura da imagem varia com acentos e deixaria o espaçamento torto.
        passo = recursos.fonte(tamanho).get_linesize() + espaco
        self._areas = []
        for indice, item in enumerate(self.itens):
            selecionado = indice == self.selecionado
            cor = Paleta.AMARELO if selecionado else Paleta.BRANCO
            retangulo = texto.desenhar_centralizado(
                superficie, item.texto, tamanho, cor, LARGURA_JANELA // 2, topo + indice * passo
            )
            self._areas.append(retangulo.inflate(*FOLGA_CLIQUE))
            if selecionado:
                _desenhar_marcadores(superficie, retangulo)


def _desenhar_marcadores(superficie: pygame.Surface, alvo: pygame.Rect) -> None:
    """Triângulos apontando para o item selecionado, um de cada lado.

    São desenhados, e não texto, para não se confundir com os "<  >" de itens ajustáveis.
    """
    meia_altura = max(alvo.height // 3, 4)
    meio = alvo.centery
    esquerda = alvo.left - DISTANCIA_MARCADOR
    direita = alvo.right + DISTANCIA_MARCADOR
    pontos_esquerda = [
        (esquerda - meia_altura, meio - meia_altura),
        (esquerda, meio),
        (esquerda - meia_altura, meio + meia_altura),
    ]
    pontos_direita = [
        (direita + meia_altura, meio - meia_altura),
        (direita, meio),
        (direita + meia_altura, meio + meia_altura),
    ]
    pygame.draw.polygon(superficie, Paleta.AMARELO, pontos_esquerda)
    pygame.draw.polygon(superficie, Paleta.AMARELO, pontos_direita)
