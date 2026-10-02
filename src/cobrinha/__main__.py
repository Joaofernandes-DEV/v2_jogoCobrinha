"""Ponto de entrada: `python -m cobrinha [--debug] [--semente N] [--nivel N] [--fechar-em S]`."""

import argparse
from collections.abc import Sequence

import pygame

from cobrinha.dominio.niveis import NIVEIS
from cobrinha.estados import navegacao
from cobrinha.jogo import Jogo


def analisar_argumentos(argumentos: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cobrinha", description="Jogo da Cobrinha V2")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="mostra FPS e informações de depuração na tela",
    )
    parser.add_argument(
        "--semente",
        type=int,
        default=None,
        help="semente do sorteio da comida, para repetir uma partida",
    )
    parser.add_argument(
        "--nivel",
        type=int,
        choices=range(1, len(NIVEIS) + 1),
        default=None,
        help="pula o menu e começa direto neste nível (para testes)",
    )
    parser.add_argument(
        "--fechar-em",
        type=float,
        default=None,
        metavar="SEGUNDOS",
        help="fecha o jogo sozinho depois desse tempo (teste automático do executável)",
    )
    return parser.parse_args(argumentos)


def preparar_jogo(opcoes: argparse.Namespace) -> Jogo:
    jogo = Jogo(debug=opcoes.debug, semente=opcoes.semente)
    if opcoes.nivel is not None:
        navegacao.iniciar_campanha(jogo, opcoes.nivel)
    else:
        navegacao.abrir_menu(jogo)
    if opcoes.fechar_em is not None:
        # Um evento QUIT agendado: o jogo encerra pelo caminho normal, como se a janela fechasse.
        pygame.time.set_timer(pygame.Event(pygame.QUIT), round(opcoes.fechar_em * 1000), loops=1)
    return jogo


def main(argumentos: Sequence[str] | None = None) -> None:
    preparar_jogo(analisar_argumentos(argumentos)).executar()


if __name__ == "__main__":
    main()
