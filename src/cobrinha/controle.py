"""Controle de videogame (V3): DualSense do PS5 e outros reconhecidos pelo SDL.

Os botões viram "teclas virtuais" (eventos KEYDOWN marcados com `controle=True` e com o
`controle_id` de quem apertou), então todas as telas funcionam com o controle sem tratar
nada de novo. O controle também vibra nos eventos da partida e muda a cor da luz conforme
o estado do jogo. No Duelo, cada controle é de um jogador: vibra só com o que acontece com
ele e acende na cor da cobra dele.

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


def tecla_virtual(tecla: int, controle_id: int | None = None) -> pygame.Event:
    return pygame.Event(
        pygame.KEYDOWN,
        key=tecla,
        mod=0,
        unicode="",
        scancode=0,
        controle=True,
        controle_id=controle_id,
    )


def veio_do_controle(evento: pygame.Event) -> bool:
    return bool(getattr(evento, "controle", False))


def id_do_controle(evento: pygame.Event) -> int | None:
    """`instance_id` do controle que gerou a tecla virtual (None se veio do teclado)."""
    return getattr(evento, "controle_id", None)


def controle_desconectado(evento: pygame.Event) -> int | None:
    """`instance_id` do controle que saiu, se o evento for o aviso de desconexão."""
    return getattr(evento, "controle_desconectado", None)


class Controles:
    """Controles conectados, tradução dos botões, vibração e luz."""

    def __init__(self) -> None:
        self._conectados: dict[int, ControleFisico] = {}
        # Direção do analógico já enviada, por (controle, eixo): -1, 0 ou +1.
        self._eixos: dict[tuple[int, int], int] = {}
        # Luz: cor geral, cores próprias de alguns controles e a última cor enviada a cada um.
        self._cor_padrao: Cor | None = None
        self._cores_por_controle: dict[int, Cor] = {}
        self._cores_enviadas: dict[int, Cor] = {}
        try:
            sdl_controller.init()
            self.disponivel = True
        except pygame.error:
            self.disponivel = False

    @property
    def conectados(self) -> int:
        return len(self._conectados)

    @property
    def ids_conectados(self) -> tuple[int, ...]:
        return tuple(self._conectados)

    def conectar(self, instance_id: int, controle: ControleFisico) -> None:
        self._conectados[instance_id] = controle
        if self._cor_padrao is not None:
            self._acender(instance_id, controle)

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
            self._cores_enviadas.pop(evento.instance_id, None)
            # Controle desconectado no meio do jogo: pausa como ao trocar de janela. O
            # evento diz qual saiu, para o Duelo saber se era o de um jogador.
            return [pygame.Event(pygame.WINDOWFOCUSLOST, controle_desconectado=evento.instance_id)]
        if evento.type == pygame.CONTROLLERBUTTONDOWN:
            tecla = TECLA_DO_BOTAO.get(evento.button)
            return [tecla_virtual(tecla, evento.instance_id)] if tecla is not None else []
        if evento.type == pygame.CONTROLLERAXISMOTION:
            return self._traduzir_eixo(evento)
        return [evento]

    def vibrar(self, vibracao: Vibracao, controle_id: int | None = None) -> None:
        """Vibra todos os controles, ou só o `controle_id` (Duelo)."""
        grave, agudo, duracao = vibracao.value
        if controle_id is None:
            alvos = list(self._conectados.values())
        else:
            alvos = [self._conectados[controle_id]] if controle_id in self._conectados else []
        for controle in alvos:
            controle.rumble(grave, agudo, duracao)

    def definir_luz(self, cor: Cor) -> None:
        """Muda a luz de todos os controles para a mesma cor."""
        self.definir_luzes(cor, {})

    def definir_luzes(self, padrao: Cor, por_controle: dict[int, Cor]) -> None:
        """Cada controle acende na cor própria (`por_controle`) ou na `padrao`.

        Só envia a cor ao controle quando ela muda, para não sobrecarregar.
        """
        self._cor_padrao = padrao
        self._cores_por_controle = dict(por_controle)
        for instance_id, controle in self._conectados.items():
            self._acender(instance_id, controle)

    def encerrar(self) -> None:
        for controle in self._conectados.values():
            controle.quit()
        self._conectados.clear()
        self._cores_enviadas.clear()

    def _acender(self, instance_id: int, controle: ControleFisico) -> None:
        cor = self._cores_por_controle.get(instance_id, self._cor_padrao)
        if cor is None or self._cores_enviadas.get(instance_id) == cor:
            return
        self._cores_enviadas[instance_id] = cor
        controle.set_led(cor)

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
        return [tecla_virtual(positiva if sentido > 0 else negativa, evento.instance_id)]
