"""Entradas do Duelo: de que lado do teclado ou de que controle vem cada comando."""

import pygame

from cobrinha.controle import tecla_virtual
from cobrinha.dominio.grade import Direcao
from cobrinha.entradas import (
    TECLADO_DIREITO,
    TECLADO_ESQUERDO,
    Entrada,
    TipoEntrada,
    dica_dos_controles,
    entrada_do_teclado,
)


def tecla(codigo: int) -> pygame.Event:
    return pygame.Event(pygame.KEYDOWN, key=codigo)


def test_wasd_e_do_lado_esquerdo_e_setas_do_direito():
    assert TECLADO_ESQUERDO.direcao(tecla(pygame.K_w)) is Direcao.CIMA
    assert TECLADO_ESQUERDO.direcao(tecla(pygame.K_d)) is Direcao.DIREITA
    assert TECLADO_ESQUERDO.direcao(tecla(pygame.K_UP)) is None
    assert TECLADO_DIREITO.direcao(tecla(pygame.K_LEFT)) is Direcao.ESQUERDA
    assert TECLADO_DIREITO.direcao(tecla(pygame.K_s)) is None


def test_controle_so_responde_ao_proprio_id():
    controle = Entrada.controle(3)
    assert controle.direcao(tecla_virtual(pygame.K_DOWN, 3)) is Direcao.BAIXO
    assert controle.direcao(tecla_virtual(pygame.K_DOWN, 4)) is None
    assert controle.direcao(tecla(pygame.K_DOWN)) is None  # seta do teclado não é dele


def test_direcional_do_controle_nao_move_quem_joga_nas_setas():
    assert TECLADO_DIREITO.direcao(tecla_virtual(pygame.K_UP, 3)) is None


def test_eventos_que_nao_sao_tecla_nao_dao_direcao():
    assert TECLADO_ESQUERDO.direcao(pygame.Event(pygame.MOUSEBUTTONDOWN, button=1)) is None


def test_entrada_do_teclado_pelo_lado_da_tecla():
    assert entrada_do_teclado(tecla(pygame.K_a)) == TECLADO_ESQUERDO
    assert entrada_do_teclado(tecla(pygame.K_RIGHT)) == TECLADO_DIREITO
    assert entrada_do_teclado(tecla(pygame.K_RETURN)) is None
    assert entrada_do_teclado(tecla_virtual(pygame.K_UP, 3)) is None


def test_entradas_sao_comparaveis_e_tem_rotulo():
    assert Entrada.controle(5) == Entrada.controle(5) != Entrada.controle(6)
    assert Entrada.controle(5).tipo is TipoEntrada.CONTROLE and Entrada.controle(5).e_controle
    assert not TECLADO_ESQUERDO.e_controle
    entradas = (TECLADO_ESQUERDO, Entrada.controle(5), TECLADO_DIREITO)
    assert dica_dos_controles(entradas) == "J1: WASD   J2: CONTROLE   J3: SETAS"
