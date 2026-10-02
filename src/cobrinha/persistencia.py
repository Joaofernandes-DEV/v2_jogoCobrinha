"""Leitura e gravação do progresso e das opções em JSON, na pasta de dados do usuário.

- Windows: %APPDATA%\\Cobrinha\\dados.json
- Linux/macOS: $XDG_DATA_HOME/cobrinha/dados.json (ou ~/.local/share/cobrinha)
- A variável de ambiente COBRINHA_DADOS troca a pasta (usada nos testes).

Arquivo corrompido não derruba o jogo: ele é guardado como `.corrompido` e o jogo
recomeça com os padrões. Falhas de gravação são avisadas no terminal e ignoradas.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
from pathlib import Path

from cobrinha.dominio.progresso import Progresso
from cobrinha.opcoes import Opcoes

NOME_ARQUIVO = "dados.json"
VERSAO = 1


def pasta_dados() -> Path:
    if personalizada := os.environ.get("COBRINHA_DADOS"):
        return Path(personalizada)
    if sys.platform == "win32" and (appdata := os.environ.get("APPDATA")):
        return Path(appdata) / "Cobrinha"
    base = os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share"
    return Path(base) / "cobrinha"


def caminho_arquivo() -> Path:
    return pasta_dados() / NOME_ARQUIVO


def carregar() -> tuple[Progresso, Opcoes]:
    arquivo = caminho_arquivo()
    if not arquivo.is_file():
        return Progresso(), Opcoes()
    try:
        dados = json.loads(arquivo.read_text(encoding="utf-8"))
        return Progresso.de_dict(dados.get("progresso", {})), Opcoes.de_dict(
            dados.get("opcoes", {})
        )
    except (ValueError, TypeError, KeyError, AttributeError) as erro:
        reserva = arquivo.with_suffix(".corrompido")
        print(f"[cobrinha] dados ilegíveis ({erro}); guardados em {reserva}", file=sys.stderr)
        with contextlib.suppress(OSError):
            arquivo.replace(reserva)
        return Progresso(), Opcoes()


def salvar(progresso: Progresso, opcoes: Opcoes) -> None:
    arquivo = caminho_arquivo()
    dados = {"versao": VERSAO, "progresso": progresso.para_dict(), "opcoes": opcoes.para_dict()}
    try:
        arquivo.parent.mkdir(parents=True, exist_ok=True)
        # Grava num temporário e troca de uma vez: um travamento no meio não corrompe o save.
        temporario = arquivo.with_suffix(".tmp")
        temporario.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        temporario.replace(arquivo)
    except OSError as erro:
        print(f"[cobrinha] não foi possível salvar em {arquivo}: {erro}", file=sys.stderr)
