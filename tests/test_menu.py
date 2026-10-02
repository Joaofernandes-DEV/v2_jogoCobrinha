import pygame
import pytest

from cobrinha.ui.menu import ItemMenu, Menu


def tecla(codigo: int) -> pygame.Event:
    return pygame.Event(pygame.KEYDOWN, key=codigo)


@pytest.fixture
def registro():
    return []


@pytest.fixture
def menu(registro):
    return Menu(
        [
            ItemMenu("A", acao=lambda: registro.append("A")),
            ItemMenu(lambda: "B dinâmico", ajustar=registro.append),
            ItemMenu("C"),
        ]
    )


def test_setas_e_ws_navegam_circulando(menu):
    menu.tratar_evento(tecla(pygame.K_UP))
    assert menu.selecionado == 2
    menu.tratar_evento(tecla(pygame.K_s))
    assert menu.selecionado == 0
    menu.tratar_evento(tecla(pygame.K_DOWN))
    assert menu.selecionado == 1


def test_enter_executa_a_acao_do_item(menu, registro):
    assert menu.tratar_evento(tecla(pygame.K_RETURN))
    assert registro == ["A"]


def test_esquerda_e_direita_ajustam_o_item(menu, registro):
    menu.selecionado = 1
    menu.tratar_evento(tecla(pygame.K_LEFT))
    menu.tratar_evento(tecla(pygame.K_d))
    assert registro == [-1, +1]
    assert menu.item_atual.texto == "B dinâmico"


def test_item_sem_acao_e_teclas_desconhecidas_sao_ignorados(menu, registro):
    menu.selecionado = 2
    assert not menu.tratar_evento(tecla(pygame.K_RETURN))
    assert not menu.tratar_evento(tecla(pygame.K_x))
    assert not menu.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=(0, 0)))
    assert registro == []


def test_menu_vazio_e_recusado():
    with pytest.raises(ValueError):
        Menu([])


def test_texto_acentuado_fica_na_mesma_linha_de_base(jogo):
    from cobrinha.ui import texto

    superficie = pygame.Surface((400, 100))
    caixas = [
        texto.desenhar_centralizado(superficie, rotulo, 32, (255, 255, 255), 200, 10)
        for rotulo in ("NIVEL", "NÍVEL")
    ]
    assert caixas[0].top == caixas[1].top == 10
    assert caixas[0].height == caixas[1].height
    assert texto._excesso_acima("NÍVEL", 32) > texto._excesso_acima("NIVEL", 32) == 0
