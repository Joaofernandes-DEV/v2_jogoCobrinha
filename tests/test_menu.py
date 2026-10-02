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


def _base_do_texto(rotulo: str) -> int:
    """Desenha o rótulo e devolve a última linha com pixels acesos (a base das letras)."""
    from cobrinha.ui import texto

    superficie = pygame.Surface((400, 100))
    superficie.fill((0, 0, 0))
    texto.desenhar_centralizado(superficie, rotulo, 32, (255, 255, 255), 200, 10)
    return max(y for y in range(100) if any(superficie.get_at((x, y))[0] for x in range(400)))


def test_texto_acentuado_fica_na_mesma_linha_de_base(jogo):
    assert _base_do_texto("NIVEL") == _base_do_texto("NÍVEL") == _base_do_texto("NÓS")


def _menu_desenhado(registro, sons):
    menu = Menu(
        [
            ItemMenu("JOGAR", acao=lambda: registro.append("jogar")),
            ItemMenu("NÍVEL < 1 >", acao=lambda: registro.append("nivel"), ajustar=registro.append),
            ItemMenu("SAIR", acao=lambda: registro.append("sair")),
        ],
        tocar=sons.append,
    )
    menu.desenhar(pygame.Surface((800, 600)), topo=100)
    return menu


def test_passar_o_mouse_seleciona_o_item(jogo):
    from cobrinha.audio import Som

    registro, sons = [], []
    menu = _menu_desenhado(registro, sons)
    centro_sair = menu._areas[2].center
    assert menu.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=centro_sair))
    assert menu.selecionado == 2
    assert sons == [Som.MENU_MOVER]
    assert not menu.tratar_evento(pygame.Event(pygame.MOUSEMOTION, pos=(5, 5)))
    assert menu.selecionado == 2


def test_clique_confirma_e_nas_pontas_ajusta(jogo):
    from cobrinha.audio import Som

    registro, sons = [], []
    menu = _menu_desenhado(registro, sons)

    def clicar(x, y):
        return menu.tratar_evento(pygame.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(x, y)))

    area = menu._areas[1]
    assert clicar(area.left + 2, area.centery)
    assert clicar(area.right - 2, area.centery)
    assert clicar(*area.center)
    assert registro == [-1, +1, "nivel"]
    assert sons[-1] is Som.MENU_CONFIRMAR
    assert not clicar(5, 5)
    # Botão direito não faz nada.
    menu.tratar_evento(pygame.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=menu._areas[0].center))
    assert registro == [-1, +1, "nivel"]


def test_teclado_toca_sons_de_navegacao(jogo):
    from cobrinha.audio import Som

    registro, sons = [], []
    menu = _menu_desenhado(registro, sons)
    menu.tratar_evento(tecla(pygame.K_DOWN))
    menu.tratar_evento(tecla(pygame.K_RETURN))
    assert sons == [Som.MENU_MOVER, Som.MENU_CONFIRMAR]
