"""Tela da partida em andamento."""

import pygame

from cobrinha.audio import Som, musica_da_fase
from cobrinha.config import (
    ALTURA_HUD,
    ALTURA_JANELA,
    LARGURA_JANELA,
    PONTOS_FRUTA_DOURADA,
    SEGMENTOS_ENCOLHER,
    TAMANHO_CELULA,
    TEMPO_ALERTA,
    TEMPO_POR_COMIDA,
    TEMPO_POR_FRUTA_DOURADA,
    Cor,
    Paleta,
    TamanhoFonte,
)
from cobrinha.controle import Vibracao
from cobrinha.dominio.grade import Direcao, Posicao
from cobrinha.dominio.partida import Evento, Partida, Situacao
from cobrinha.dominio.power_ups import TipoPowerUp
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
    Evento.PEGOU_POWER_UP: Som.POWER_UP,
    Evento.CONCLUIU_NIVEL: Som.NIVEL,
    Evento.BATEU: Som.BATER,
    Evento.VENCEU: Som.VITORIA,
    Evento.TEMPO_ESGOTADO: Som.NIVEL,
}

# Vibração do controle (V3) em cada acontecimento da partida.
VIBRACAO_DO_EVENTO = {
    Evento.COMEU: Vibracao.FRACA,
    Evento.COMEU_DOURADA: Vibracao.MEDIA,
    Evento.PEGOU_POWER_UP: Vibracao.MEDIA,
    Evento.CONCLUIU_NIVEL: Vibracao.MEDIA,
    Evento.VENCEU: Vibracao.MEDIA,
    Evento.BATEU: Vibracao.FORTE,
    Evento.TEMPO_ESGOTADO: Vibracao.FORTE,
}

# Power-ups (V3): rótulo curto no HUD e texto que sobe ao pegar.
ROTULO_DO_POWER_UP = {
    TipoPowerUp.CAMERA_LENTA: "LENTO",
    TipoPowerUp.PONTOS_EM_DOBRO: "X2",
}
TEXTO_AO_PEGAR = {
    TipoPowerUp.CAMERA_LENTA: "LENTO!",
    TipoPowerUp.PONTOS_EM_DOBRO: "X2!",
    TipoPowerUp.ENCOLHER: f"-{SEGMENTOS_ENCOLHER}",
}
# Véu azulado sobre o campo durante a câmera lenta (só com efeitos visuais ligados).
OPACIDADE_VEU_LENTO = 40

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
        self.veu_lento = pygame.Surface(self.fundo_campo.get_size(), pygame.SRCALPHA)
        self.veu_lento.fill((*Paleta.AZUL, OPACIDADE_VEU_LENTO))
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
        power_up_antes = self.partida.power_up
        multiplicador = self.partida.multiplicador_pontos
        for evento in self.partida.atualizar(dt):
            if evento in (Evento.BATEU, Evento.VENCEU, Evento.TEMPO_ESGOTADO):
                # Fim de jogo: a música para na hora e só volta no menu.
                self.jogo.audio.parar_musica()
            if evento in SOM_DO_EVENTO:
                self.jogo.audio.tocar(SOM_DO_EVENTO[evento])
            if evento in VIBRACAO_DO_EVENTO:
                self.jogo.controles.vibrar(VIBRACAO_DO_EVENTO[evento])
            if evento is Evento.COMEU_DOURADA and dourada_antes:
                pontos = PONTOS_FRUTA_DOURADA * multiplicador
                self._pontos_flutuantes(
                    self._texto_do_bonus(pontos, TEMPO_POR_FRUTA_DOURADA), dourada_antes.posicao
                )
            elif evento is Evento.PEGOU_POWER_UP and power_up_antes:
                conteudo = TEXTO_AO_PEGAR[power_up_antes.tipo]
                self._pontos_flutuantes(conteudo, power_up_antes.posicao, Paleta.AZUL_CLARO)
            elif evento in (Evento.COMEU, Evento.CONCLUIU_NIVEL, Evento.VENCEU) and comida_antes:
                texto = self._texto_do_bonus(multiplicador, TEMPO_POR_COMIDA)
                self._pontos_flutuantes(texto, comida_antes)

        if not self.partida.em_andamento:
            self._iniciar_encerramento()

    def _iniciar_encerramento(self) -> None:
        if self.partida.situacao is Situacao.DERROTA:
            efeitos = self.jogo.opcoes.efeitos_visuais
            self.tempo_ate_encerrar = DURACAO_MORTE if efeitos else DURACAO_MORTE_SEM_EFEITOS
        else:
            navegacao.encerrar_partida(self.jogo, self)

    def _texto_do_bonus(self, pontos: int, segundos: float) -> str:
        """\"+1\"; no contra o tempo, também os segundos ganhos (\"+1  +3s\")."""
        if self.partida.tempo_restante is None:
            return f"+{pontos}"
        return f"+{pontos}  +{segundos:g}s"

    def _pontos_flutuantes(
        self, conteudo: str, posicao: Posicao, cor: Cor = Paleta.AMARELO
    ) -> None:
        if not self.jogo.opcoes.efeitos_visuais:
            return
        x, y = celula_para_pixel(posicao)
        meio = TAMANHO_CELULA // 2
        self.efeitos.texto_flutuante(conteudo, cor, (x + meio, y + meio))

    @property
    def cor_do_controle(self) -> Cor:
        """Luz do controle: vermelha ao bater ou com o relógio acabando; azul na câmera
        lenta; amarela com pontos em dobro; verde no resto da partida."""
        partida = self.partida
        if partida.situacao is Situacao.DERROTA:
            return Paleta.VERMELHO
        if partida.tempo_restante is not None and partida.tempo_restante <= TEMPO_ALERTA:
            return Paleta.VERMELHO
        if TipoPowerUp.CAMERA_LENTA in partida.efeitos_ativos:
            return Paleta.AZUL
        if TipoPowerUp.PONTOS_EM_DOBRO in partida.efeitos_ativos:
            return Paleta.AMARELO
        return Paleta.VERDE

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
            efeitos=tuple(
                (ROTULO_DO_POWER_UP[tipo], restante)
                for tipo, restante in partida.efeitos_ativos.items()
            ),
            tempo=partida.tempo_restante,
        )
        desenhar_hud(superficie, dados)
        superficie.blit(self.fundo_campo, (0, ALTURA_HUD))
        lento = TipoPowerUp.CAMERA_LENTA in partida.efeitos_ativos
        if lento and self.jogo.opcoes.efeitos_visuais:
            superficie.blit(self.veu_lento, (0, ALTURA_HUD))
        if partida.comida is not None:
            self.sprites.desenhar_comida(superficie, partida.comida, self.tempo)
        if partida.fruta_dourada is not None:
            self.sprites.desenhar_fruta_dourada(
                superficie,
                partida.fruta_dourada.posicao,
                self.tempo,
                partida.fruta_dourada.tempo_restante,
            )
        if partida.power_up is not None:
            self.sprites.desenhar_power_up(superficie, partida.power_up, self.tempo)
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
