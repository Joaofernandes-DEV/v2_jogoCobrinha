"""Mapa de navegação: todas as trocas de tela do jogo passam por aqui.

    Menu ──Recordes / Opções / Créditos──► (tela) ──► Menu
    Menu ──Jogar──► Contagem ─► Jogando ──Esc/P/perdeu foco──► Pausa ─► Contagem ─► Jogando
                                 │
                                 ├─ meta do nível ──► Nível concluído ─► Contagem (próximo nível)
                                 └─ bateu/venceu ───► Fim de partida ──► Contagem | Menu
    Menu ──Duelo──► Quem joga? ─► Contagem ─► Duelo ──Esc/P/perdeu foco──► Pausa ─► Contagem
                                               │
                                               ├─ saiu o controle de alguém ─► Reconecte ─► Contagem
                                               └─ sobrou 1 ou 0 ─► Fim do duelo ─► Contagem | Menu

As telas importam este módulo, e ele importa as telas dentro das funções.
Isso evita importações circulares e deixa o fluxo inteiro num lugar só.
Também é aqui que o progresso é salvo em disco, sempre que muda.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from cobrinha.config import TEMPO_INICIAL, TEMPO_POR_COMIDA, TEMPO_POR_FRUTA_DOURADA
from cobrinha.dominio.niveis import obter_nivel
from cobrinha.dominio.partida import Partida, Situacao

if TYPE_CHECKING:
    from collections.abc import Sequence

    from cobrinha.dominio.duelo import Placar
    from cobrinha.dominio.partida import Modo
    from cobrinha.entradas import Entrada
    from cobrinha.estados.base import EstadoDePartida
    from cobrinha.estados.duelo import EstadoDuelo
    from cobrinha.estados.jogando import EstadoJogando
    from cobrinha.jogo import Jogo


def abrir_menu(jogo: Jogo) -> None:
    from cobrinha.estados.menu_principal import EstadoMenuPrincipal

    jogo.trocar_estado(EstadoMenuPrincipal(jogo))


def abrir_creditos(jogo: Jogo) -> None:
    from cobrinha.estados.creditos import EstadoCreditos

    jogo.trocar_estado(EstadoCreditos(jogo))


def abrir_recordes(jogo: Jogo) -> None:
    from cobrinha.estados.recordes import EstadoRecordes

    jogo.trocar_estado(EstadoRecordes(jogo))


def abrir_opcoes(jogo: Jogo) -> None:
    from cobrinha.estados.opcoes import EstadoOpcoes

    jogo.trocar_estado(EstadoOpcoes(jogo))


def iniciar_campanha(jogo: Jogo, numero_nivel: int = 1) -> None:
    """Começa uma campanha nova, do nível escolhido e no modo das opções, com 0 pontos."""
    jogo.progresso.liberar_nivel(numero_nivel)
    jogo.salvar()
    partida = Partida(nivel=obter_nivel(numero_nivel), rng=jogo.rng, modo=jogo.opcoes.modo_de_jogo)
    _comecar_partida(jogo, partida, nivel_inicial=numero_nivel)


def avancar_nivel(jogo: Jogo, jogando: EstadoJogando) -> None:
    _comecar_partida(jogo, jogando.partida.proxima_fase(), jogando.nivel_inicial)


def concluir_nivel(jogo: Jogo, numero_liberado: int) -> None:
    jogo.progresso.liberar_nivel(numero_liberado)
    jogo.salvar()


def pausar(jogo: Jogo, jogando: EstadoDePartida) -> None:
    from cobrinha.estados.pausa import EstadoPausa

    jogo.empilhar(EstadoPausa(jogo, jogando))


def retomar(jogo: Jogo, jogando: EstadoDePartida) -> None:
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


def registrar_resultado(jogo: Jogo, partida: Partida) -> int | None:
    """Põe os pontos da campanha no ranking do modo e salva. Devolve a colocação (ou None)."""
    colocacao = jogo.progresso.registrar_pontuacao(
        partida.modo.name, partida.pontos, partida.nivel.numero, date.today().isoformat()
    )
    if colocacao is not None:
        jogo.salvar()
    return colocacao


def abandonar_partida(jogo: Jogo, jogando: EstadoJogando) -> None:
    """Sai de uma partida inacabada pelo menu, sem perder os pontos para o ranking."""
    registrar_resultado(jogo, jogando.partida)
    abrir_menu(jogo)


def abrir_quem_joga(jogo: Jogo, numero_nivel: int = 1) -> None:
    """Tela em que cada pessoa entra no duelo pelo teclado ou pelo controle."""
    from cobrinha.estados.quem_joga import EstadoQuemJoga

    jogo.trocar_estado(EstadoQuemJoga(jogo, numero_nivel))


def iniciar_duelo(
    jogo: Jogo,
    numero_nivel: int = 1,
    entradas: Sequence[Entrada] | None = None,
    modo: Modo | None = None,
    placar: Placar | None = None,
) -> None:
    """Começa uma rodada de duelo no mapa e na velocidade do nível escolhido.

    `entradas` diz com o que cada jogador joga (padrão: J1 no WASD e J2 nas setas); `modo`
    vem das opções do menu; sem `placar`, começa uma disputa nova. Não entra nos recordes.
    """
    from cobrinha.entradas import dica_dos_controles
    from cobrinha.estados.contagem import EstadoContagem
    from cobrinha.estados.duelo import ENTRADAS_PADRAO, EstadoDuelo

    entradas = tuple(entradas or ENTRADAS_PADRAO)
    modo = modo or jogo.opcoes.modo_de_jogo
    duelo = EstadoDuelo(jogo, numero_nivel, entradas, modo=modo, placar=placar)
    jogo.trocar_estado(duelo)
    jogo.empilhar(
        EstadoContagem(
            jogo,
            duelo,
            titulo=f"RODADA {duelo.placar.rodada}",
            subtitulo=f"{duelo.partida.nivel.nome}   {modo.value}",
            dica=dica_dos_controles(entradas),
        )
    )


def proxima_rodada(jogo: Jogo, duelo: EstadoDuelo) -> None:
    """Mesmos jogadores, mapa e modo; o placar continua."""
    duelo.placar.nova_rodada()
    iniciar_duelo(jogo, duelo.numero_nivel, duelo.entradas, duelo.partida.modo, duelo.placar)


def pedir_controle(jogo: Jogo, duelo: EstadoDuelo) -> None:
    """O controle de um jogador desconectou: o duelo espera ele voltar."""
    from cobrinha.estados.controle_desconectado import EstadoControleDesconectado

    jogo.empilhar(EstadoControleDesconectado(jogo, duelo))


def controle_religado(jogo: Jogo, duelo: EstadoDuelo) -> None:
    """Todos os jogadores têm controle de novo: volta ao duelo com a contagem 3-2-1."""
    from cobrinha.estados.contagem import EstadoContagem

    jogo.desempilhar()
    jogo.empilhar(EstadoContagem(jogo, duelo))


def encerrar_duelo(jogo: Jogo, duelo: EstadoDuelo) -> None:
    from cobrinha.estados.fim_do_duelo import EstadoFimDoDuelo

    jogo.empilhar(EstadoFimDoDuelo(jogo, duelo))


def _comecar_partida(jogo: Jogo, partida: Partida, nivel_inicial: int) -> None:
    from cobrinha.estados.contagem import EstadoContagem
    from cobrinha.estados.jogando import EstadoJogando

    jogando = EstadoJogando(jogo, partida, nivel_inicial)
    jogo.trocar_estado(jogando)
    dica = None
    if partida.tempo_restante is not None:
        dica = (
            f"{TEMPO_INICIAL:g} s no relógio   maçã +{TEMPO_POR_COMIDA:g} s"
            f"   dourada +{TEMPO_POR_FRUTA_DOURADA:g} s"
        )
    jogo.empilhar(
        EstadoContagem(
            jogo,
            jogando,
            titulo=f"NÍVEL {partida.nivel.numero}",
            subtitulo=partida.nivel.nome,
            dica=dica,
        )
    )
