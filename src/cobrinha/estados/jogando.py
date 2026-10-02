"""Tela da partida em andamento."""

import pygame

from cobrinha.audio import Som, musica_da_fase
from cobrinha.config import (
    ALTURA_HUD,
    ALTURA_JANELA,
    LARGURA_JANELA,
    PONTOS_FRUTA_DOURADA,
    TAMANHO_CELULA,
    Paleta,
    TamanhoFonte,
)
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.dominio.partida import Evento, Partida, Situacao
from cobrinha.estados import navegacao
from cobrinha.estados.base import Estado
from cobrinha.jogo import Jogo
from cobrinha.ui import texto
from cobrinha.ui.campo import celula_para_pixel, criar_fundo_campo
from cobrinha.ui.efeitos import Efeitos
from cobrinha.ui.hud import DadosHud, desenhar_hud
from cobrinha.ui.pecas import Sprites

# Setas e WASD funcionam sempre, ao mesmo tempo.
TECLAS_DIRECAO = {
    pygame.K_UP: Direcao.CIMA,
    pygame.K_w: Direcao.CIMA,
    pygame.K_DOWN: Direcao.BAIXO,
    pygame.K_s: Direcao.BAIXO,
    pygame.K_LEFT: Direcao.ESQUERDA,
    pygame.K_a: Direcao.ESQUERDA,
    pygame.K_RIGHT: Direcao.DIREITA,
    pygame.K_d: Direcao.DIREITA,
}
TECLAS_PAUSA = (pygame.K_ESCAPE, pygame.K_p)

SOM_DO_EVENTO = {
    Evento.COMEU: Som.COMER,
    Evento.COMEU_DOURADA: Som.BONUS,
    Evento.CONCLUIU_NIVEL: Som.NIVEL,
    Evento.BATEU: Som.BATER,
    Evento.VENCEU: Som.VITORIA,
}

# Ao bater, a cobra pisca antes da tela de fim (I10); sem efeitos visuais, a pausa é curta.
DURACAO_MORTE = 0.9
DURACAO_MORTE_SEM_EFEITOS = 0.3
PISCADAS_POR_SEGUNDO = 7


class EstadoJogando(Estado):
    def __init__(self, jogo: Jogo, partida: Partida | None = None, nivel_inicial: int = 1) -> None:
        super().__init__(jogo)
        self.sprites = Sprites()
        self.partida = partida if partida is not None else Partida(rng=jogo.rng)
        # Pedras não mudam durante o nível: vão desenhadas no fundo uma vez só.
        self.fundo_campo = criar_fundo_campo()
        self.sprites.desenhar_obstaculos(self.fundo_campo, self.partida.obstaculos, topo=0)
        # Nível em que a campanha começou: "jogar de novo" volta para ele.
        self.nivel_inicial = nivel_inicial
        self.tempo = 0.0  # para animações (comida flutuando)
        self.efeitos = Efeitos()
        self.tempo_ate_encerrar: float | None = None
        # A música muda ao sair do menu e a cada troca de fase.
        jogo.audio.tocar_musica(musica_da_fase(self.partida.nivel.numero))

    def tratar_evento(self, evento: pygame.Event) -> None:
        if self.tempo_ate_encerrar is not None:
            return  # animação de fim em andamento
        if evento.type == pygame.WINDOWFOCUSLOST:
            # Pausa automática ao trocar de janela (J2).
            navegacao.pausar(self.jogo, self)
        elif evento.type == pygame.KEYDOWN:
            if evento.key in TECLAS_DIRECAO:
                self.partida.virar(TECLAS_DIRECAO[evento.key])
            elif evento.key in TECLAS_PAUSA:
                navegacao.pausar(self.jogo, self)

    def atualizar(self, dt: float) -> None:
        self.tempo += dt
        self.efeitos.atualizar(dt)
        if self.tempo_ate_encerrar is not None:
            self.tempo_ate_encerrar -= dt
            if self.tempo_ate_encerrar <= 0:
                navegacao.encerrar_partida(self.jogo, self)
            return

        comida_antes = self.partida.comida
        dourada_antes = self.partida.fruta_dourada
        for evento in self.partida.atualizar(dt):
            if evento in (Evento.BATEU, Evento.VENCEU):
                # Fim de jogo: a música para na hora e só volta no menu.
                self.jogo.audio.parar_musica()
            if evento in SOM_DO_EVENTO:
                self.jogo.audio.tocar(SOM_DO_EVENTO[evento])
            if evento is Evento.COMEU_DOURADA and dourada_antes:
                self._pontos_flutuantes(f"+{PONTOS_FRUTA_DOURADA}", dourada_antes.posicao)
            elif evento in (Evento.COMEU, Evento.CONCLUIU_NIVEL, Evento.VENCEU) and comida_antes:
                self._pontos_flutuantes("+1", comida_antes)

        if not self.partida.em_andamento:
            self._iniciar_encerramento()

    def _iniciar_encerramento(self) -> None:
        if self.partida.situacao is Situacao.DERROTA:
            efeitos = self.jogo.opcoes.efeitos_visuais
            self.tempo_ate_encerrar = DURACAO_MORTE if efeitos else DURACAO_MORTE_SEM_EFEITOS
        else:
            navegacao.encerrar_partida(self.jogo, self)

    def _pontos_flutuantes(self, conteudo: str, posicao: Posicao) -> None:
        if not self.jogo.opcoes.efeitos_visuais:
            return
        x, y = celula_para_pixel(posicao)
        meio = TAMANHO_CELULA // 2
        self.efeitos.texto_flutuante(conteudo, Paleta.AMARELO, (x + meio, y + meio))

    @property
    def cobra_visivel(self) -> bool:
        """Durante a animação de morte, a cobra pisca."""
        if self.tempo_ate_encerrar is None or not self.jogo.opcoes.efeitos_visuais:
            return True
        return int(self.tempo_ate_encerrar * PISCADAS_POR_SEGUNDO) % 2 == 0

    def desenhar(self, superficie: pygame.Surface) -> None:
        partida = self.partida
        modo = partida.modo
        dados = DadosHud(
            pontos=partida.pontos,
            recorde=max(self.jogo.progresso.recorde(modo.name), partida.pontos),
            nivel=partida.nivel.numero,
            comidas=partida.comidas_no_nivel,
            meta=partida.nivel.meta_comidas,
            modo=modo.value,
            mudo=self.jogo.audio.mudo,
        )
        desenhar_hud(superficie, dados)
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
        if partida.comida is not None:
            self.sprites.desenhar_comida(superficie, partida.comida, self.tempo)
        if partida.fruta_dourada is not None:
            self.sprites.desenhar_fruta_dourada(
                superficie,
                partida.fruta_dourada.posicao,
                self.tempo,
                partida.fruta_dourada.tempo_restante,
            )
        if self.cobra_visivel:
            self.sprites.desenhar_cobra(superficie, partida.cobra)
        self.efeitos.desenhar(superficie)
        if self.jogo.debug:
            self._desenhar_depuracao(superficie)

    def _desenhar_depuracao(self, superficie: pygame.Surface) -> None:
        info = (
            f"FPS {self.jogo.relogio.get_fps():.0f}  COBRA {len(self.partida.cobra)}"
            f"  VELOCIDADE {self.partida.passos_por_segundo:.2f}"
        )
        imagem = texto.renderizar(info, TamanhoFonte.MINIMO, Paleta.PRETO)
        superficie.blit(
            imagem, imagem.get_rect(bottomright=(LARGURA_JANELA - 6, ALTURA_JANELA - 4))
        )
