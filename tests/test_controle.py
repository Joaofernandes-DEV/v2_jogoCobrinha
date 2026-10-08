"""Controle de videogame (V3): tradução dos botões, analógico, conexão, vibração e luz."""

import pygame
import pytest
from auxiliares import jogo_em_andamento

from cobrinha.config import Paleta
from cobrinha.controle import Controles, Vibracao, veio_do_controle
from cobrinha.dominio.partida import Situacao
from cobrinha.dominio.power_ups import TipoPowerUp
from cobrinha.estados import navegacao
from cobrinha.estados.contagem import EstadoContagem
from cobrinha.estados.menu_principal import EstadoMenuPrincipal
from cobrinha.estados.pausa import EstadoPausa

ID = 7  # instance_id do controle falso


class ControleFalso:
    def __init__(self) -> None:
        self.vibracoes: list[tuple[float, float, int]] = []
        self.cores: list[tuple[int, int, int]] = []
        self.encerrado = False

    def rumble(self, low_frequency: float, high_frequency: float, duration: int) -> bool:
        self.vibracoes.append((low_frequency, high_frequency, duration))
        return True

    def set_led(self, color) -> bool:
        self.cores.append(tuple(color))
        return True

    def quit(self) -> None:
        self.encerrado = True


def botao(numero: int) -> pygame.Event:
    return pygame.Event(pygame.CONTROLLERBUTTONDOWN, button=numero, instance_id=ID)


def eixo(numero: int, fracao: float) -> pygame.Event:
    return pygame.Event(
        pygame.CONTROLLERAXISMOTION, axis=numero, value=round(fracao * 32767), instance_id=ID
    )


def teclas(eventos: list[pygame.Event]) -> list[int]:
    assert all(e.type == pygame.KEYDOWN and veio_do_controle(e) for e in eventos)
    return [e.key for e in eventos]


@pytest.fixture
def controles(jogo):
    """Os controles do jogo de teste, com um controle falso conectado."""
    falso = ControleFalso()
    jogo.controles.conectar(ID, falso)
    return jogo.controles, falso


# Tradução


@pytest.mark.parametrize(
    ("numero", "tecla"),
    [
        (pygame.CONTROLLER_BUTTON_DPAD_UP, pygame.K_UP),
        (pygame.CONTROLLER_BUTTON_DPAD_DOWN, pygame.K_DOWN),
        (pygame.CONTROLLER_BUTTON_DPAD_LEFT, pygame.K_LEFT),
        (pygame.CONTROLLER_BUTTON_DPAD_RIGHT, pygame.K_RIGHT),
        (pygame.CONTROLLER_BUTTON_A, pygame.K_RETURN),  # ✕
        (pygame.CONTROLLER_BUTTON_B, pygame.K_ESCAPE),  # ◯
        (pygame.CONTROLLER_BUTTON_START, pygame.K_p),  # Options
        (pygame.CONTROLLER_BUTTON_BACK, pygame.K_m),  # Create
    ],
)
def test_botoes_viram_teclas(jogo, numero, tecla):
    assert teclas(Controles().traduzir(botao(numero))) == [tecla]


def test_botoes_sem_funcao_nao_geram_tecla(jogo):
    controles = Controles()
    assert controles.traduzir(botao(pygame.CONTROLLER_BUTTON_Y)) == []
    # Soltar o botão passa adiante sem virar tecla (as telas ignoram).
    soltar = pygame.Event(pygame.CONTROLLERBUTTONUP, button=pygame.CONTROLLER_BUTTON_A)
    assert controles.traduzir(soltar) == [soltar]


def test_eventos_comuns_passam_sem_mudanca(jogo):
    evento = pygame.Event(pygame.KEYDOWN, key=pygame.K_a)
    assert Controles().traduzir(evento) == [evento]
    assert not veio_do_controle(evento)


def test_analogico_vira_direcional_com_zona_morta(jogo):
    controles = Controles()
    assert controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTX, 0.2)) == []  # zona morta
    assert teclas(controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTX, 0.9))) == [pygame.K_RIGHT]
    assert teclas(controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTY, -0.9))) == [pygame.K_UP]
    assert teclas(controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTY, 0.8))) == [pygame.K_DOWN]


def test_analogico_inclinado_nao_repete_ate_voltar_ao_centro(jogo):
    controles = Controles()
    esquerda = eixo(pygame.CONTROLLER_AXIS_LEFTX, -0.9)
    assert teclas(controles.traduzir(esquerda)) == [pygame.K_LEFT]
    assert controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTX, -1.0)) == []
    assert controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTX, -0.4)) == []  # quase solto
    assert controles.traduzir(esquerda) == []
    controles.traduzir(eixo(pygame.CONTROLLER_AXIS_LEFTX, 0.0))  # voltou ao centro
    assert teclas(controles.traduzir(esquerda)) == [pygame.K_LEFT]


def test_analogico_direito_e_gatilhos_sao_ignorados(jogo):
    controles = Controles()
    assert controles.traduzir(eixo(pygame.CONTROLLER_AXIS_RIGHTX, 1.0)) == []
    assert controles.traduzir(eixo(pygame.CONTROLLER_AXIS_TRIGGERLEFT, 1.0)) == []


# Conexão, vibração e luz


def test_desconectar_pausa_e_controle_desconhecido_e_ignorado(controles):
    controles, _ = controles
    removido = pygame.Event(pygame.CONTROLLERDEVICEREMOVED, instance_id=ID)
    assert [e.type for e in controles.traduzir(removido)] == [pygame.WINDOWFOCUSLOST]
    assert controles.conectados == 0
    assert controles.traduzir(removido) == []


def test_vibrar_aciona_todos_os_controles(controles):
    controles, falso = controles
    controles.vibrar(Vibracao.FORTE)
    assert falso.vibracoes == [Vibracao.FORTE.value]


def test_luz_so_muda_quando_a_cor_muda(controles):
    controles, falso = controles
    controles.definir_luz(Paleta.AZUL)
    controles.definir_luz(Paleta.AZUL)
    controles.definir_luz(Paleta.VERDE)
    assert falso.cores == [Paleta.AZUL, Paleta.VERDE]


def test_controle_conectado_depois_recebe_a_cor_atual(jogo):
    controles = Controles()
    controles.definir_luz(Paleta.AMARELO)
    falso = ControleFalso()
    controles.conectar(1, falso)
    assert falso.cores == [Paleta.AMARELO]


def test_encerrar_libera_os_controles(controles):
    controles, falso = controles
    controles.encerrar()
    assert falso.encerrado
    assert controles.conectados == 0


# Integração com as telas


def postar(jogo, *eventos: pygame.Event) -> None:
    pygame.event.clear()
    for evento in eventos:
        pygame.event.post(evento)
    jogo._processar_eventos()


def test_direcional_navega_no_menu(jogo):
    navegacao.abrir_menu(jogo)
    menu = jogo.estado_atual.menu
    antes = menu.selecionado
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_DPAD_DOWN))
    assert menu.selecionado == antes + 1


def test_circulo_no_menu_principal_nao_fecha_o_jogo(jogo):
    navegacao.abrir_menu(jogo)
    jogo.rodando = True
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_B))
    assert jogo.rodando
    assert isinstance(jogo.estado_atual, EstadoMenuPrincipal)


def test_options_pausa_e_continua_e_create_silencia(jogo):
    jogo_em_andamento(jogo)
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_START))
    assert isinstance(jogo.estado_atual, EstadoPausa)
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_START))
    assert isinstance(jogo.estado_atual, EstadoContagem)  # continua com a contagem 3-2-1
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_BACK))
    assert jogo.audio.mudo


def test_direcional_vira_a_cobra(jogo):
    jogando = jogo_em_andamento(jogo)
    postar(jogo, botao(pygame.CONTROLLER_BUTTON_DPAD_UP))
    assert jogando.partida.cobra.tem_comandos_pendentes


def test_desconectar_o_controle_pausa_a_partida(jogo, controles):
    jogo_em_andamento(jogo)
    postar(jogo, pygame.Event(pygame.CONTROLLERDEVICEREMOVED, instance_id=ID))
    assert isinstance(jogo.estado_atual, EstadoPausa)


def test_partida_vibra_ao_comer_e_ao_bater(jogo, controles):
    _, falso = controles
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    partida.comida = partida.cobra.cabeca.vizinha(partida.cobra.direcao)
    jogando.atualizar(partida.intervalo_passo)
    assert falso.vibracoes == [Vibracao.FRACA.value]
    partida.situacao = Situacao.EM_ANDAMENTO
    while partida.em_andamento:  # segue reto até bater na borda
        jogando.atualizar(partida.intervalo_passo)
    assert falso.vibracoes[-1] == Vibracao.FORTE.value


def test_cor_da_luz_acompanha_a_partida(jogo):
    navegacao.abrir_menu(jogo)
    assert jogo.estado_atual.cor_do_controle == Paleta.VERDE_CLARO
    jogando = jogo_em_andamento(jogo)
    partida = jogando.partida
    assert jogando.cor_do_controle == Paleta.VERDE
    partida.efeitos_ativos[TipoPowerUp.PONTOS_EM_DOBRO] = 5.0
    assert jogando.cor_do_controle == Paleta.AMARELO
    partida.efeitos_ativos[TipoPowerUp.CAMERA_LENTA] = 5.0
    assert jogando.cor_do_controle == Paleta.AZUL
    partida.tempo_restante = 5.0  # relógio do contra o tempo acabando
    assert jogando.cor_do_controle == Paleta.VERMELHO
    partida.tempo_restante = None
    partida.situacao = Situacao.DERROTA
    assert jogando.cor_do_controle == Paleta.VERMELHO


def test_cada_quadro_acende_a_luz_da_tela_atual(jogo, controles):
    _, falso = controles
    jogando = jogo_em_andamento(jogo)
    jogo.pilha = [jogando]
    jogando.partida.efeitos_ativos[TipoPowerUp.CAMERA_LENTA] = 5.0
    jogo._atualizar_quadro(0.01)
    assert falso.cores[-1] == Paleta.AZUL
    navegacao.abrir_menu(jogo)
    jogo._atualizar_quadro(0.01)
    assert falso.cores[-1] == Paleta.VERDE_CLARO
