"""Tela "Quem joga?" (V3): cada pessoa entra no Duelo pelo teclado ou pelo controle.

- Teclado: WASD entra pelo lado esquerdo e as setas pelo lado direito (no máximo 2).
- Controle: ✕ entra; ✕ de novo começa; ◯ sai da vaga.
- Enter começa (com 2 a 4 jogadores) e Esc volta ao menu.

As vagas são preenchidas na ordem de chegada, e cada uma tem a sua cor de cobra.
O controle que entra já acende na cor da vaga.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.audio import Som
from cobrinha.config import (
    ALTURA_HUD,
    LARGURA_JANELA,
    MAXIMO_JOGADORES,
    TAMANHO_CELULA,
    VITORIAS_PARA_VENCER,
    Cor,
    Paleta,
    TamanhoFonte,
)
from cobrinha.controle import id_do_controle, veio_do_controle
from cobrinha.dominio.cobra import Cobra
from cobrinha.dominio.duelo import MINIMO_JOGADORES
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.dominio.niveis import obter_nivel
from cobrinha.entradas import Entrada, entrada_do_teclado
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.estados.duelo import COR_FORA_DO_DUELO, nome_do_jogador, pele_do_jogador
from cobrinha.ui import texto
from cobrinha.ui.campo import criar_fundo_campo
from cobrinha.ui.menu import TECLAS_CONFIRMAR
from cobrinha.ui.painel import Linha, criar_veu, desenhar_linhas
from cobrinha.ui.pecas import Sprites

if TYPE_CHECKING:
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 150
LARGURA_VAGA = 180
ALTURA_VAGA = 130
TOPO_VAGAS = 150
# Cobrinha de 3 segmentos desenhada em cada vaga ocupada. Ela é desenhada numa superfície
# à parte, por isso a linha -2: a célula (0, -2) cai no canto (0, 0) dessa superfície,
# porque o desenho das células desconta o HUD.
COBRA_DA_VAGA = (Posicao(2, -2), Posicao(1, -2), Posicao(0, -2))
assert ALTURA_HUD == 2 * TAMANHO_CELULA


class EstadoQuemJoga(Estado):
    def __init__(self, jogo: Jogo, numero_nivel: int = 1) -> None:
        super().__init__(jogo)
        self.numero_nivel = numero_nivel
        self.entradas: list[Entrada] = []
        self.fundo_campo = criar_fundo_campo()
        self.veu = criar_veu(OPACIDADE_VEU)
        self.sprites = Sprites()

    @property
    def pode_comecar(self) -> bool:
        return len(self.entradas) >= MINIMO_JOGADORES

    def entrar(self, entrada: Entrada) -> bool:
        """Ocupa a próxima vaga livre. Devolve False se já entrou ou se não há vaga."""
        if entrada in self.entradas or len(self.entradas) >= MAXIMO_JOGADORES:
            return False
        self.entradas.append(entrada)
        self.jogo.audio.tocar(Som.MENU_CONFIRMAR)
        return True

    def sair(self, entrada: Entrada) -> None:
        """Libera a vaga; quem estava depois sobe uma posição (e troca de cor)."""
        self.entradas.remove(entrada)
        self.jogo.audio.tocar(Som.MENU_MOVER)

    def comecar(self) -> None:
        if self.pode_comecar:
            navegacao.iniciar_duelo(self.jogo, self.numero_nivel, tuple(self.entradas))

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type != pygame.KEYDOWN:
            return
        if veio_do_controle(evento):
            self._tratar_controle(evento)
        elif evento.key == pygame.K_ESCAPE:
            navegacao.abrir_menu(self.jogo)
        elif evento.key in TECLAS_CONFIRMAR:
            self.comecar()
        elif (lado := entrada_do_teclado(evento)) is not None:
            self.entrar(lado)

    def _tratar_controle(self, evento: pygame.Event) -> None:
        controle_id = id_do_controle(evento)
        if controle_id is None:
            return
        entrada = Entrada.controle(controle_id)
        if evento.key == pygame.K_RETURN:  # ✕
            if entrada in self.entradas:
                self.comecar()
            else:
                self.entrar(entrada)
        elif evento.key == pygame.K_ESCAPE:  # ◯
            if entrada in self.entradas:
                self.sair(entrada)
            else:
                navegacao.abrir_menu(self.jogo)

    @property
    def cor_do_controle(self) -> Cor:
        """Controle que ainda não entrou: branco, diferente das cores das vagas."""
        return COR_FORA_DO_DUELO

    @property
    def luzes_dos_controles(self) -> dict[int, Cor]:
        return {
            entrada.controle_id: pele_do_jogador(indice).destaque
            for indice, entrada in enumerate(self.entradas)
            if entrada.controle_id is not None
        }

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.fundo_campo, (0, 0))
        superficie.blit(self.fundo_campo, (0, self.fundo_campo.get_height()))
        superficie.blit(self.veu, (0, 0))
        desenhar_linhas(
            superficie,
            [
                ("QUEM JOGA?", TamanhoFonte.TITULO, Paleta.BRANCO),
                (
                    # O modo vem do menu principal, como o mapa.
                    f"{obter_nivel(self.numero_nivel).nome}   "
                    f"{self.jogo.opcoes.modo_de_jogo.value}   "
                    f"campeão: {VITORIAS_PARA_VENCER} vitórias",
                    TamanhoFonte.PEQUENO,
                    Paleta.VERDE_CLARO,
                ),
            ],
            topo=30,
            espaco=6,
        )
        for indice in range(MAXIMO_JOGADORES):
            self._desenhar_vaga(superficie, indice)

        faltam = MINIMO_JOGADORES - len(self.entradas)
        if faltam > 0:
            situacao = (
                "FALTA 1 JOGADOR" if faltam == 1 else f"FALTAM {faltam} JOGADORES",
                TamanhoFonte.MEDIO,
                Paleta.LARANJA,
            )
        else:
            situacao = (
                f"ENTER: começar com {len(self.entradas)} jogadores",
                TamanhoFonte.MEDIO,
                Paleta.AMARELO,
            )
        rodape: list[Linha] = [
            situacao,
            (
                "TECLADO: WASD (lado esquerdo) ou SETAS (lado direito) para entrar",
                TamanhoFonte.PEQUENO,
                Paleta.BRANCO,
            ),
            (
                "CONTROLE: X para entrar ou começar, BOLA para sair",
                TamanhoFonte.PEQUENO,
                Paleta.BRANCO,
            ),
            ("ESC: voltar ao menu", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO),
        ]
        desenhar_linhas(superficie, rodape, topo=TOPO_VAGAS + ALTURA_VAGA + 40, espaco=10)

    def _desenhar_vaga(self, superficie: pygame.Surface, indice: int) -> None:
        espaco = (LARGURA_JANELA - MAXIMO_JOGADORES * LARGURA_VAGA) // (MAXIMO_JOGADORES + 1)
        vaga = pygame.Rect(
            espaco + indice * (LARGURA_VAGA + espaco), TOPO_VAGAS, LARGURA_VAGA, ALTURA_VAGA
        )
        ocupada = indice < len(self.entradas)
        pele = pele_do_jogador(indice)
        superficie.fill(Paleta.PRETO, vaga.inflate(6, 6))
        superficie.fill(Paleta.CINZA_ESCURO, vaga)
        cor_nome = pele.destaque if ocupada else Paleta.CINZA
        texto.desenhar_centralizado(
            superficie,
            nome_do_jogador(indice),
            TamanhoFonte.PEQUENO,
            cor_nome,
            vaga.centerx,
            vaga.top + 8,
        )
        if not ocupada:
            texto.desenhar_centralizado(
                superficie, "LIVRE", TamanhoFonte.MEDIO, Paleta.CINZA, vaga.centerx, vaga.top + 52
            )
            return
        cobra = pygame.Surface((3 * TAMANHO_CELULA, TAMANHO_CELULA), pygame.SRCALPHA)
        self.sprites.desenhar_cobra(cobra, Cobra(COBRA_DA_VAGA, Direcao.DIREITA), pele)
        superficie.blit(cobra, cobra.get_rect(center=(vaga.centerx, vaga.top + 58)))
        texto.desenhar_centralizado(
            superficie,
            self.entradas[indice].rotulo,
            TamanhoFonte.MEDIO,
            Paleta.BRANCO,
            vaga.centerx,
            vaga.top + 82,
        )
