"""Ponto de entrada: `python -m cobrinha [--debug] [--semente N]`."""

import argparse
from collections.abc import Sequence

from cobrinha.estados.jogando import EstadoJogando
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
    return parser.parse_args(argumentos)


def main(argumentos: Sequence[str] | None = None) -> None:
    opcoes = analisar_argumentos(argumentos)
    jogo = Jogo(debug=opcoes.debug, semente=opcoes.semente)
    jogo.trocar_estado(EstadoJogando(jogo))
    jogo.executar()


if __name__ == "__main__":
    main()
