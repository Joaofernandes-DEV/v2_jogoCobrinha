"""Controle de videogame (V3): DualSense do PS5 e outros reconhecidos pelo SDL.

Os botões viram "teclas virtuais" (eventos KEYDOWN marcados com `controle=True`), então
todas as telas funcionam com o controle sem tratar nada de novo. O controle também
vibra nos eventos da partida e muda a cor da luz conforme o estado do jogo.

Se o computador não tiver suporte a controles, o jogo segue só com teclado e mouse.
"""

from __future__ import annotations

from enum import Enum
from typing import Protocol

import pygame
from pygame._sdl2 import controller as sdl_controller

from cobrinha.config import Cor

# Botão → tecla equivalente. Os nomes do SDL seguem o controle do Xbox:
# A = ✕ (Cross), B = ◯ (Circle), START = Options e BACK = Create no DualSense.
TECLA_DO_BOTAO = {
    pygame.CONTROLLER_BUTTON_DPAD_UP: pygame.K_UP,
    pygame.CONTROLLER_BUTTON_DPAD_DOWN: pygame.K_DOWN,
    pygame.CONTROLLER_BUTTON_DPAD_LEFT: pygame.K_LEFT,
    pygame.CONTROLLER_BUTTON_DPAD_RIGHT: pygame.K_RIGHT,
    pygame.CONTROLLER_BUTTON_A: pygame.K_RETURN,
    pygame.CONTROLLER_BUTTON_B: pygame.K_ESCAPE,
    pygame.CONTROLLER_BUTTON_START: pygame.K_p,
    pygame.CONTROLLER_BUTTON_BACK: pygame.K_m,
}

# Analógico esquerdo como direcional. Os eixos vão de -32768 a 32767.
LIMIAR_ANALOGICO = 0.55  # fração do curso para contar como "apertado"
LIMIAR_SOLTURA = 0.30  # precisa voltar abaixo disto para valer de novo (evita repetição)
CURSO_EIXO = 32767
TECLAS_DO_EIXO = {
    pygame.CONTROLLER_AXIS_LEFTX: (pygame.K_LEFT, pygame.K_RIGHT),
    pygame.CONTROLLER_AXIS_LEFTY: (pygame.K_UP, pygame.K_DOWN),
}


class Vibracao(Enum):
    """(motor grave, motor agudo, duração em ms); intensidades de 0 a 1."""

    FRACA = (0.0, 0.35, 70)
    MEDIA = (0.4, 0.6, 140)
    FORTE = (1.0, 1.0, 380)


class ControleFisico(Protocol):
    """O que o jogo usa de um controle (os testes trocam por um falso)."""

    def rumble(self, low_frequency: float, high_frequency: float, duration: int) -> bool: ...

    def set_led(self, color: Cor) -> bool: ...

    def quit(self) -> None: ...


def tecla_virtual(tecla: int) -> pygame.Event:
    return pygame.Event(pygame.KEYDOWN, key=tecla, mod=0, unicode="", scancode=0, controle=True)


def veio_do_controle(evento: pygame.Event) -> bool:
    return bool(getattr(evento, "controle", False))


class Controles:
    """Controles conectados, tradução dos botões, vibração e luz."""

    def __init__(self) -> None:
        self._conectados: dict[int, ControleFisico] = {}
        # Direção do analógico já enviada, por (controle, eixo): -1, 0 ou +1.
        self._eixos: dict[tuple[int, int], int] = {}
        self._cor_atual: Cor | None = None
        try:
            sdl_controller.init()
            self.disponivel = True
        except pygame.error:
            self.disponivel = False

    @property
    def conectados(self) -> int:
        return len(self._conectados)

    def conectar(self, instance_id: int, controle: ControleFisico) -> None:
        self._conectados[instance_id] = controle
        if self._cor_atual is not None:
            controle.set_led(self._cor_atual)

    def traduzir(self, evento: pygame.Event) -> list[pygame.Event]:
        """Converte um evento do controle nos eventos que as telas entendem.

        Eventos que não são de controle passam sem mudança.
        """
        if evento.type == pygame.CONTROLLERDEVICEADDED:
            self._adicionar(evento.device_index)
            return []
        if evento.type == pygame.CONTROLLERDEVICEREMOVED:
            removido = self._conectados.pop(evento.instance_id, None)
            if removido is None:
                return []
            # Controle desconectado no meio do jogo: pausa como ao trocar de janela.
            return [pygame.Event(pygame.WINDOWFOCUSLOST)]
        if evento.type == pygame.CONTROLLERBUTTONDOWN:
            tecla = TECLA_DO_BOTAO.get(evento.button)
            return [tecla_virtual(tecla)] if tecla is not None else []
        if evento.type == pygame.CONTROLLERAXISMOTION:
            return self._traduzir_eixo(evento)
        return [evento]

    def vibrar(self, vibracao: Vibracao) -> None:
        grave, agudo, duracao = vibracao.value
        for controle in self._conectados.values():
            controle.rumble(grave, agudo, duracao)

    def definir_luz(self, cor: Cor) -> None:
        """Muda a luz dos controles (só quando a cor muda, para não sobrecarregar)."""
        if cor == self._cor_atual:
            return
        self._cor_atual = cor
        for controle in self._conectados.values():
            controle.set_led(cor)

    def encerrar(self) -> None:
        for controle in self._conectados.values():
            controle.quit()
        self._conectados.clear()

    def _adicionar(self, device_index: int) -> None:
        try:
            controle = sdl_controller.Controller(device_index)
        except pygame.error:
            return  # aparelho que o SDL não sabe usar como controle
        self.conectar(controle.as_joystick().get_instance_id(), controle)

    def _traduzir_eixo(self, evento: pygame.Event) -> list[pygame.Event]:
        if evento.axis not in TECLAS_DO_EIXO:
            return []
        chave = (evento.instance_id, evento.axis)
        anterior = self._eixos.get(chave, 0)
        valor = evento.value / CURSO_EIXO
        if abs(valor) < LIMIAR_SOLTURA:
            self._eixos[chave] = 0
            return []
        if abs(valor) < LIMIAR_ANALOGICO:
            return []
        sentido = 1 if valor > 0 else -1
        if sentido == anterior:
            return []  # continua inclinado para o mesmo lado: não repete
        self._eixos[chave] = sentido
        negativa, positiva = TECLAS_DO_EIXO[evento.axis]
        return [tecla_virtual(positiva if sentido > 0 else negativa)]
