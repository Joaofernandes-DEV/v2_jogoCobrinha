"""Ponto de entrada: `python -m cobrinha`."""

from cobrinha.estados.jogando import EstadoJogando
from cobrinha.jogo import Jogo


def main() -> None:
    jogo = Jogo()
    jogo.trocar_estado(EstadoJogando(jogo))
    jogo.executar()


if __name__ == "__main__":
    main()
