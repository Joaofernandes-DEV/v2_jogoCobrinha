"""Funções compartilhadas pelos testes de fluxo entre telas."""

import pygame

from cobrinha.estados import navegacao
from cobrinha.estados.jogando import EstadoJogando


def tecla(codigo: int) -> pygame.Event:
    return pygame.Event(pygame.KEYDOWN, key=codigo)


def enviar(jogo, *codigos: int) -> None:
    for codigo in codigos:
        jogo.estado_atual.tratar_evento(tecla(codigo))


def descer_ate(jogo, rotulo_inicial: str) -> None:
    """Desce com a seta no menu da tela atual até o item cujo texto começa com `rotulo_inicial`."""
    menu = jogo.estado_atual.menu
    for _ in menu.itens:
        if menu.item_atual.texto.startswith(rotulo_inicial):
            return
        enviar(jogo, pygame.K_DOWN)
    raise AssertionError(f"o menu não tem o item {rotulo_inicial!r}")


def desenhar_tudo(jogo) -> None:
    superficie = pygame.Surface(jogo.tela.get_size())
    for estado in jogo.pilha:
        estado.desenhar(superficie)


def encerrar(jogando: EstadoJogando) -> None:
    """Avança o tempo até a partida encerrada abrir a tela seguinte (pula a animação de morte)."""
    for _ in range(5):
        if jogando.jogo.estado_atual is not jogando:
            return
        jogando.atualizar(0.5)
    raise AssertionError("a partida não abriu a tela seguinte")


def jogo_em_andamento(jogo, nivel: int = 1) -> EstadoJogando:
    """Começa uma campanha e pula a contagem."""
    navegacao.iniciar_campanha(jogo, nivel)
    enviar(jogo, pygame.K_RETURN)
    assert isinstance(jogo.estado_atual, EstadoJogando)
    return jogo.estado_atual


class ControleFalso:
    """Faz o papel de um controle físico: guarda as vibrações e as cores recebidas."""

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


def conectar_controles(jogo, *ids: int) -> dict[int, ControleFalso]:
    """Conecta um controle falso para cada `instance_id`."""
    falsos = {instance_id: ControleFalso() for instance_id in ids}
    for instance_id, falso in falsos.items():
        jogo.controles.conectar(instance_id, falso)
    return falsos


def botao(numero: int, instance_id: int) -> pygame.Event:
    return pygame.Event(pygame.CONTROLLERBUTTONDOWN, button=numero, instance_id=instance_id)


def desconectar(instance_id: int) -> pygame.Event:
    return pygame.Event(pygame.CONTROLLERDEVICEREMOVED, instance_id=instance_id)


def postar(jogo, *eventos: pygame.Event) -> None:
    """Entrega eventos pelo caminho real (os botões do controle viram teclas)."""
    pygame.event.clear()
    for evento in eventos:
        pygame.event.post(evento)
    jogo._processar_eventos()
