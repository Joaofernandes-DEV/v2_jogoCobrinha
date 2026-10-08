"""Duelo parado porque o controle de um jogador desconectou (V3).

O SDL dá um `instance_id` novo ao controle que volta, então o vínculo antigo não serve
mais: o primeiro controle livre que apertar ✕ passa a ser do jogador que ficou sem controle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from cobrinha.audio import Som
from cobrinha.config import ALTURA_JANELA, Paleta, TamanhoFonte
from cobrinha.controle import id_do_controle, veio_do_controle
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.estados.duelo import nome_do_jogador, pele_do_jogador
from cobrinha.estados.jogando import TECLAS_PAUSA
from cobrinha.ui.painel import Linha, criar_veu, desenhar_linhas

if TYPE_CHECKING:
    from cobrinha.estados.duelo import EstadoDuelo
    from cobrinha.jogo import Jogo

OPACIDADE_VEU = 170


class EstadoControleDesconectado(Estado):
    def __init__(self, jogo: Jogo, duelo: EstadoDuelo) -> None:
        super().__init__(jogo)
        self.duelo = duelo
        self.veu = criar_veu(OPACIDADE_VEU)
        jogo.audio.tocar(Som.PAUSA)
        jogo.audio.pausar_musica()

    def tratar_evento(self, evento: pygame.Event) -> None:
        if evento.type != pygame.KEYDOWN:
            return
        if veio_do_controle(evento) and evento.key == pygame.K_RETURN:
            self._religar(id_do_controle(evento))
        elif evento.key in TECLAS_PAUSA:
            # Para quem quiser desistir: a pausa tem Reiniciar e Menu principal.
            navegacao.pausar(self.jogo, self.duelo)

    def _religar(self, controle_id: int | None) -> None:
        faltando = self.duelo.jogadores_sem_controle
        em_uso = {entrada.controle_id for entrada in self.duelo.entradas}
        if controle_id is None or not faltando or controle_id in em_uso:
            return  # o controle já é de outro jogador
        self.duelo.religar(faltando[0], controle_id)
        self.jogo.audio.tocar(Som.MENU_CONFIRMAR)
        if not self.duelo.jogadores_sem_controle:
            self.jogo.audio.retomar_musica()
            navegacao.controle_religado(self.jogo, self.duelo)

    def desenhar(self, superficie: pygame.Surface) -> None:
        superficie.blit(self.veu, (0, 0))
        linhas: list[Linha] = [("CONTROLE DESCONECTADO", TamanhoFonte.TITULO, Paleta.BRANCO)]
        for indice in self.duelo.jogadores_sem_controle:
            linhas.append(
                (
                    f"{nome_do_jogador(indice)}: reconecte o controle e aperte X",
                    TamanhoFonte.MEDIO,
                    pele_do_jogador(indice).destaque,
                )
            )
        linhas.append(("ESC ou P: pausa", TamanhoFonte.PEQUENO, Paleta.CINZA_CLARO))
        desenhar_linhas(superficie, linhas, ALTURA_JANELA // 2 - 110, espaco=24)
