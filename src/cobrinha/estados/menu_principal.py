"""Menu principal: jogar, escolher o nível inicial (entre os liberados), créditos e sair."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.grade import GRADE_PADRAO, Direcao, Posicao
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.menu import ItemMenu, Menu
from cobrinha.ui.painel import criar_veu, desenhar_linhas
from cobrinha.ui.pecas import Sprites

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 150

assert GRADE_PADRAO.linhas % 2 == 0, "o fundo do menu depende de um número par de linhas"

# Cobra decorativa em "S" no rodapé do menu (posições em células).
COBRA_DECORATIVA = [
    Posicao(21, 17),
    Posicao(20, 17),
    Posicao(19, 17),
    Posicao(19, 18),
    Posicao(18, 18),
    Posicao(17, 18),
    Posicao(16, 18),
    Posicao(15, 18),
    Posicao(15, 17),
    Posicao(14, 17),
    Posicao(13, 17),
    Posicao(12, 17),
    Posicao(11, 17),
]
COMIDA_DECORATIVA = Posicao(23, 17)


class EstadoMenuPrincipal(Estado):
    def __init__(self, jogo: Jogo) -> None:
        super().__init__(jogo)
        self.fundo_campo = criar_fundo_campo()
        self.veu = criar_veu(OPACIDADE_VEU)
        self.sprites = Sprites()
        self.cobra_decorativa = Cobra(COBRA_DECORATIVA, Direcao.DIREITA)
        self.tempo = 0.0
        self.nivel_escolhido = 1
        self.menu = Menu(
            [
                ItemMenu("JOGAR", acao=self._jogar),
                ItemMenu(self._rotulo_nivel, acao=self._jogar, ajustar=self._mudar_nivel),
                ItemMenu("CRÉDITOS", acao=lambda: navegacao.abrir_creditos(jogo)),
                ItemMenu("SAIR", acao=jogo.sair),
            ],
            tocar=jogo.audio.tocar,
        )
        jogo.audio.tocar_musica()

    @property
    def niveis_liberados(self) -> int:
        return self.jogo.progresso.maior_nivel_liberado

    def _rotulo_nivel(self) -> str:
        if self.niveis_liberados == 1:
            return "NÍVEL INICIAL: 1"
        return f"NÍVEL INICIAL: < {self.nivel_escolhido} >"

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

    def atualizar(self, dt: float) -> None:
        self.tempo += dt

    def desenhar(self, superficie: pygame.Surface) -> None:
        # Sem HUD no menu: o xadrez cobre a janela inteira. A segunda cópia preenche
        # só a faixa de baixo e continua o padrão sem emenda (número par de linhas).
        superficie.blit(self.fundo_campo, (0, 0))
        superficie.blit(self.fundo_campo, (0, self.fundo_campo.get_height()))
        superficie.blit(self.veu, (0, 0))
        self.sprites.desenhar_cobra(superficie, self.cobra_decorativa)
        self.sprites.desenhar_comida(superficie, COMIDA_DECORATIVA, self.tempo)

        y = desenhar_linhas(
            superficie,
            [
                ("JOGO DA", TamanhoFonte.GRANDE, Paleta.BRANCO),
                ("COBRINHA", TamanhoFonte.ENORME, Paleta.VERDE_CLARO),
                ("V2", TamanhoFonte.MEDIO, Paleta.AMARELO),
            ],
            topo=36,
            espaco=6,
        )
        self.menu.desenhar(superficie, topo=y + 16, espaco=14)

        rodape = []
        if self.jogo.progresso.recorde:
            rodape.append(
                (f"RECORDE {self.jogo.progresso.recorde}", TamanhoFonte.PEQUENO, Paleta.AMARELO)
            )
        rodape.append(
            (
                "SETAS/MOUSE: escolher   ENTER: confirmar   M: som   ESC: sair",
                TamanhoFonte.MINIMO,
                Paleta.CINZA_CLARO,
            )
        )
        desenhar_linhas(superficie, rodape, ALTURA_JANELA - 28 * len(rodape) - 6, espaco=4)
