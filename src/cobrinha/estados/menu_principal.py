"""Menu principal: jogar, escolher o nível inicial (entre os liberados) e sair."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta
from cobrinha.dominio.grade import GRADE_PADRAO
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 150

assert GRADE_PADRAO.linhas % 2 == 0, "o fundo do menu depende de um número par de linhas"


class EstadoMenuPrincipal(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.veu = criar_veu(OPACIDADE_VEU)
        self.nivel_escolhido = 1
        self.menu = Menu(
            [
                ItemMenu("JOGAR", acao=self._jogar),
                ItemMenu(self._rotulo_nivel, acao=self._jogar, ajustar=self._mudar_nivel),
                ItemMenu("SAIR", acao=jogo.sair),
            ]
        )

    @property
    def niveis_liberados(self) -> int:
        return self.jogo.progresso.maior_nivel_liberado

    def _rotulo_nivel(self) -> str:
        if self.niveis_liberados == 1:
            return "NÍVEL INICIAL: 1"
        return f"NÍVEL INICIAL: <  {self.nivel_escolhido}  >"

    def _mudar_nivel(self, delta: int) -> None:
        # Circula só entre os níveis já alcançados (J3).
        self.nivel_escolhido = (self.nivel_escolhido - 1 + delta) % self.niveis_liberados + 1

    def _jogar(self) -> None:
        navegacao.iniciar_campanha(self.jogo, self.nivel_escolhido)

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
            self.jogo.sair()
        else:
            self.menu.tratar_evento(evento)

    def desenhar(self, superficie: pygame.Surface) -> None:
        # Sem HUD no menu: o xadrez cobre a janela inteira. A segunda cópia preenche
        # só a faixa de baixo e continua o padrão sem emenda (número par de linhas).
        superficie.blit(self.fundo_campo, (0, 0))
        superficie.blit(self.fundo_campo, (0, self.fundo_campo.get_height()))
        superficie.blit(self.veu, (0, 0))
        y = desenhar_linhas(
            superficie,
            [
                ("JOGO DA COBRINHA", 72, Paleta.VERDE_CLARO),
                ("V2", 36, Paleta.AMARELO),
            ],
            topo=110,
        )
        self.menu.desenhar(superficie, topo=y + 30)
        rodape = []
        if self.jogo.progresso.recorde:
            rodape.append((f"RECORDE {self.jogo.progresso.recorde}", 26, Paleta.BRANCO))
        rodape.append(("SETAS: escolher    ENTER: confirmar    ESC: sair", 22, Paleta.CINZA_CLARO))
        desenhar_linhas(superficie, rodape, ALTURA_JANELA - 40 * len(rodape) - 10)
