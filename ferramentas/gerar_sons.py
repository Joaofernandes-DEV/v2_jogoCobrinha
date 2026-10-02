"""Sintetiza os efeitos sonoros e a música (estilo chiptune) em `src/cobrinha/assets/sons/`.

Uso: python ferramentas/gerar_sons.py

Só usa a biblioteca padrão: ondas quadrada, triangular e ruído com envelope,
gravadas em WAV mono de 16 bits a 22 050 Hz. O resultado é determinístico.
"""

import random
import struct
import wave
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "src" / "cobrinha" / "assets" / "sons"
TAXA = 22_050

Onda = Callable[[float], float]  # fase (em ciclos) → amostra entre -1 e 1


def quadrada(ciclo_ativo: float = 0.5) -> Onda:
    return lambda fase: 1.0 if fase % 1.0 < ciclo_ativo else -1.0


def triangular(fase: float) -> float:
    return 4 * abs(fase % 1.0 - 0.5) - 1


def nota(nome: str) -> float:
    """Frequência de uma nota no formato 'A4', 'C#5', 'Eb3'."""
    semitons = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    base, oitava = nome[:-1], int(nome[-1])
    valor = semitons[base[0]] + (1 if "#" in base else -1 if "b" in base else 0)
    return 440.0 * 2 ** ((valor + 12 * (oitava - 4)) / 12)


def tom(
    frequencia_inicial: float,
    duracao: float,
    onda: Onda,
    frequencia_final: float | None = None,
    volume: float = 0.5,
    ataque: float = 0.005,
    soltura: float = 0.03,
) -> list[float]:
    """Um tom com envelope linear e, se pedido, deslizando de uma frequência para outra."""
    frequencia_final = frequencia_final or frequencia_inicial
    total = int(duracao * TAXA)
    amostras, fase = [], 0.0
    for i in range(total):
        progresso = i / max(total - 1, 1)
        fase += (frequencia_inicial + (frequencia_final - frequencia_inicial) * progresso) / TAXA
        tempo, restante = i / TAXA, (total - i) / TAXA
        envelope = min(1.0, tempo / ataque if ataque else 1.0, restante / soltura)
        amostras.append(onda(fase) * envelope * volume)
    return amostras


def ruido(duracao: float, volume: float = 0.4, semente: int = 7) -> list[float]:
    """Ruído branco com decaimento: a "batida" da colisão."""
    rng = random.Random(semente)
    total = int(duracao * TAXA)
    return [rng.uniform(-1, 1) * volume * (1 - i / total) ** 2 for i in range(total)]


def passa_baixa(amostras: list[float], suavidade: float) -> list[float]:
    """Filtro passa-baixa de um polo: tira o chiado do ruído e deixa um som "crocante"."""
    saida, anterior = [], 0.0
    for amostra in amostras:
        anterior += suavidade * (amostra - anterior)
        saida.append(anterior)
    return saida


def mordida() -> list[float]:
    """Mordida na maçã ("nhac!"): dois estalos de ruído filtrado e um blip subindo."""
    estalo_1 = passa_baixa(ruido(0.045, volume=1.0, semente=11), 0.45)
    estalo_2 = passa_baixa(ruido(0.035, volume=0.7, semente=23), 0.55)
    blip = tom(520, 0.07, quadrada(0.25), frequencia_final=1040, volume=0.35)
    return juntar(estalo_1, silencio(0.012), estalo_2, blip)


def silencio(duracao: float) -> list[float]:
    return [0.0] * int(duracao * TAXA)


def juntar(*partes: Iterable[float]) -> list[float]:
    return [amostra for parte in partes for amostra in parte]


def misturar(*faixas: list[float]) -> list[float]:
    tamanho = max(len(faixa) for faixa in faixas)
    return [sum(faixa[i] for faixa in faixas if i < len(faixa)) for i in range(tamanho)]


def arpejo(notas: list[str], duracao_nota: float, onda: Onda, volume: float = 0.4) -> list[float]:
    return juntar(*(tom(nota(n), duracao_nota, onda, volume=volume) for n in notas))


# Pico final de cada arquivo (−1 dBFS). O equilíbrio entre os sons fica em INTENSIDADE.
PICO_ALVO = 0.89
# Sons de interface mais discretos que os da partida (fração do pico-alvo).
INTENSIDADE = {"menu_mover": 0.5, "menu_confirmar": 0.7, "pausa": 0.7}
INTENSIDADE_MUSICA = 0.8


def salvar(nome: str, amostras: list[float]) -> None:
    """Normaliza para o pico-alvo e grava. (Antes, a normalização só reduzia o volume,
    nunca aumentava, e os sons saíam ~10 dB baixos demais.)"""
    pico = max((abs(a) for a in amostras), default=1.0) or 1.0
    intensidade = INTENSIDADE_MUSICA if nome.startswith("musica") else INTENSIDADE.get(nome, 1.0)
    escala = PICO_ALVO * intensidade / pico * 32767
    caminho = DESTINO / f"{nome}.wav"
    with wave.open(str(caminho), "wb") as arquivo:
        arquivo.setnchannels(1)
        arquivo.setsampwidth(2)
        arquivo.setframerate(TAXA)
        arquivo.writeframes(b"".join(struct.pack("<h", int(a * escala)) for a in amostras))
    print(f"gerado: {caminho.relative_to(RAIZ)} ({len(amostras) / TAXA:.2f} s)")


# Efeitos


def efeitos() -> dict[str, list[float]]:
    q25, q50 = quadrada(0.25), quadrada(0.5)
    return {
        "comer": mordida(),
        "bonus": juntar(
            mordida(),
            arpejo(["E6", "G6", "B6", "E7"], 0.045, q25, volume=0.4),
            tom(nota("E7"), 0.12, q25, volume=0.3, soltura=0.1),
        ),
        "nivel": arpejo(["C5", "E5", "G5", "C6"], 0.08, q25),
        "bater": misturar(ruido(0.35), tom(330, 0.35, q50, frequencia_final=80, volume=0.35)),
        "vitoria": juntar(
            arpejo(["C5", "E5", "G5"], 0.1, q25),
            tom(nota("C6"), 0.45, q25, volume=0.4, soltura=0.2),
        ),
        "menu_mover": tom(880, 0.035, q50, volume=0.25, soltura=0.02),
        "menu_confirmar": juntar(
            tom(660, 0.05, q25, volume=0.35), tom(990, 0.08, q25, volume=0.35)
        ),
        "contagem": tom(440, 0.12, q25, volume=0.4),
        "contagem_ja": tom(880, 0.3, q25, volume=0.45, soltura=0.15),
        "pausa": juntar(tom(784, 0.06, q50, volume=0.3), tom(523, 0.09, q50, volume=0.3)),
    }


# Músicas: uma para o menu e uma para cada fase, cada uma com tom, andamento e timbre
# próprios, para o jogo não ficar repetitivo. Todas têm 8 compassos e tocam em loop.

Padrao = list[int | None]  # 8 colcheias: índice da nota no arpejo, ou None = pausa


@dataclass(frozen=True)
class Faixa:
    bpm: int
    # (nota do baixo, arpejo da melodia), 2 compassos cada.
    acordes: list[tuple[str, list[str]]]
    padrao_1: Padrao  # 1º compasso de cada acorde
    padrao_2: Padrao  # 2º compasso (variação)
    ciclo_ativo: float  # timbre da melodia: 0,125 = fino, 0,25 = mais cheio


FAIXAS: dict[str, Faixa] = {
    # Menu: lá menor, calma (a mesma música das versões anteriores).
    "musica_menu": Faixa(
        bpm=140,
        acordes=[
            ("A2", ["A4", "C5", "E5", "C5"]),
            ("F2", ["F4", "A4", "C5", "A4"]),
            ("C3", ["E4", "G4", "C5", "G4"]),
            ("G2", ["D4", "G4", "B4", "G4"]),
        ],
        padrao_1=[0, 1, 2, 3, 0, 1, 2, 3],
        padrao_2=[0, 1, 2, 3, 2, None, 1, 2],
        ciclo_ativo=0.125,
    ),
    # Fase 1, "Campo aberto": dó maior, alegre.
    "musica_fase1": Faixa(
        bpm=150,
        acordes=[
            ("C3", ["C5", "E5", "G5", "E5"]),
            ("G2", ["B4", "D5", "G5", "D5"]),
            ("A2", ["A4", "C5", "E5", "C5"]),
            ("F2", ["A4", "C5", "F5", "C5"]),
        ],
        padrao_1=[0, 1, 2, 1, 3, 2, 1, 2],
        padrao_2=[3, 2, 1, 0, None, 0, 1, None],
        ciclo_ativo=0.25,
    ),
    # Fase 2, "Pedras no caminho": ré menor, sincopada.
    "musica_fase2": Faixa(
        bpm=160,
        acordes=[
            ("D3", ["D5", "F5", "A5", "F5"]),
            ("Bb2", ["Bb4", "D5", "F5", "D5"]),
            ("F2", ["A4", "C5", "F5", "C5"]),
            ("C3", ["G4", "C5", "E5", "C5"]),
        ],
        padrao_1=[0, None, 2, 1, 0, None, 3, 2],
        padrao_2=[0, 1, 2, 3, 3, 2, 1, None],
        ciclo_ativo=0.125,
    ),
    # Fase 3, "Labirinto": mi menor, rápida e tensa.
    "musica_fase3": Faixa(
        bpm=172,
        acordes=[
            ("E2", ["E5", "G5", "B5", "G5"]),
            ("C3", ["E5", "G5", "C6", "G5"]),
            ("D3", ["D5", "F#5", "A5", "F#5"]),
            ("B2", ["D#5", "F#5", "B5", "F#5"]),
        ],
        padrao_1=[0, 0, 2, 1, 0, 0, 3, 2],
        padrao_2=[3, 2, 3, 1, 2, 0, 1, None],
        ciclo_ativo=0.25,
    ),
}


def compor(faixa: Faixa) -> list[float]:
    colcheia = 60 / faixa.bpm / 2
    melodia, baixo = [], []
    timbre = quadrada(faixa.ciclo_ativo)
    for nota_baixo, arpejo_notas in faixa.acordes:
        for padrao in (faixa.padrao_1, faixa.padrao_2):
            for numero_colcheia, indice in enumerate(padrao):
                if indice is None:
                    melodia.extend(silencio(colcheia))
                else:
                    melodia.extend(
                        tom(nota(arpejo_notas[indice]), colcheia, timbre, volume=0.22, soltura=0.05)
                    )
                # Baixo pulsando em colcheias, uma oitava acima no tempo fraco.
                oitava = int(nota_baixo[-1]) + (numero_colcheia % 2)
                frequencia = nota(nota_baixo[:-1] + str(oitava))
                baixo.extend(tom(frequencia, colcheia, triangular, volume=0.3, soltura=0.02))
    return misturar(melodia, baixo)


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nome, amostras in efeitos().items():
        salvar(nome, amostras)
    for nome, faixa in FAIXAS.items():
        salvar(nome, compor(faixa))


if __name__ == "__main__":
    main()
