"""Mapa de navegação: todas as trocas de tela do jogo passam por aqui.

    Menu ──Jogar──► Contagem ─► Jogando ──Esc/P/perdeu foco──► Pausa ─► Contagem ─► Jogando
                                 │
                                 ├─ meta do nível ──► Nível concluído ─► Contagem (próximo nível)
                                 └─ bateu/venceu ───► Fim de partida ──► Contagem | Menu

As telas importam este módulo, e ele importa as telas dentro das funções.
Isso evita importações circulares e deixa o fluxo inteiro num lugar só.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cobrinha.dominio.niveis import obter_nivel
from cobrinha.dominio.partida import Partida, Situacao

if TYPE_CHECKING:
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo


def abrir_menu(jogo: Jogo) -> None:
    from cobrinha.estados.menu_principal import EstadoMenuPrincipal

    jogo.trocar_estado(EstadoMenuPrincipal(jogo))


def iniciar_campanha(jogo: Jogo, numero_nivel: int = 1) -> None:
    """Começa uma campanha nova, do nível escolhido, com 0 pontos."""
    jogo.progresso.liberar_nivel(numero_nivel)
    partida = Partida(nivel=obter_nivel(numero_nivel), rng=jogo.rng)
    _comecar_partida(jogo, partida, nivel_inicial=numero_nivel)


def avancar_nivel(jogo: Jogo, jogando: EstadoJogando) -> None:
    _comecar_partida(jogo, jogando.partida.proxima_fase(), jogando.nivel_inicial)


def pausar(jogo: Jogo, jogando: EstadoJogando) -> None:
    from cobrinha.estados.pausa import EstadoPausa

    jogo.empilhar(EstadoPausa(jogo, jogando))


def retomar(jogo: Jogo, jogando: EstadoJogando) -> None:
    """Fecha a pausa e volta ao jogo com contagem 3-2-1 (J10)."""
    from cobrinha.estados.contagem import EstadoContagem

    jogo.desempilhar()
    jogo.empilhar(EstadoContagem(jogo, jogando))


def encerrar_partida(jogo: Jogo, jogando: EstadoJogando) -> None:
    """Chamado quando a partida deixa de estar em andamento."""
    from cobrinha.estados.fim_de_partida import EstadoFimDePartida
    from cobrinha.estados.nivel_concluido import EstadoNivelConcluido

    if jogando.partida.situacao is Situacao.NIVEL_CONCLUIDO:
        jogo.empilhar(EstadoNivelConcluido(jogo, jogando))
    else:
        jogo.empilhar(EstadoFimDePartida(jogo, jogando))


def abandonar_partida(jogo: Jogo, jogando: EstadoJogando) -> None:
    """Sai de uma partida inacabada pelo menu, sem perder os pontos para o recorde."""
    jogo.progresso.registrar_pontuacao(jogando.partida.pontos)
    abrir_menu(jogo)


def _comecar_partida(jogo: Jogo, partida: Partida, nivel_inicial: int) -> None:
    from cobrinha.estados.contagem import EstadoContagem
    from cobrinha.estados.jogando import EstadoJogando

    jogando = EstadoJogando(jogo, partida, nivel_inicial)
    jogo.trocar_estado(jogando)
    jogo.empilhar(EstadoContagem(jogo, jogando, titulo=f"NÍVEL {partida.nivel.numero}"))
