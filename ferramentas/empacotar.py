"""Gera o executável do jogo (Windows: dist/Cobrinha.exe) com o PyInstaller.

Uso: python ferramentas/empacotar.py
Requer: pip install -e ".[ferramentas]"

Passos:
1. cria o ícone (.ico) a partir do sprite da maçã, ampliado sem borrar a pixel art;
2. inclui só os assets versionados no Git (nada de arquivo solto da pasta local);
3. roda o PyInstaller em modo arquivo único, sem janela de console;
4. faz um teste de fumaça: abre o executável com --fechar-em e confere que ele fecha sem erro.
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parents[1]
PACOTE = RAIZ / "src" / "cobrinha"
CONSTRUCAO = RAIZ / "build"
DESTINO = RAIZ / "dist"
NOME = "Cobrinha"
TAMANHOS_ICONE = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
SEPARADOR_DADOS = ";" if sys.platform == "win32" else ":"


def gerar_icone() -> Path:
    sprite = Image.open(PACOTE / "assets" / "imagens" / "comida.png").convert("RGBA")
    # NEAREST mantém os pixels quadrados; o .ico guarda vários tamanhos.
    grande = sprite.resize((250, 250), Image.Resampling.NEAREST)
    quadro = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    quadro.paste(grande, (3, 3))
    caminho = CONSTRUCAO / "cobrinha.ico"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    quadro.save(caminho, sizes=TAMANHOS_ICONE)
    return caminho


def assets_versionados() -> list[Path]:
    saida = subprocess.run(
        ["git", "ls-files", "src/cobrinha/assets"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return [RAIZ / linha for linha in saida.splitlines() if linha.strip()]


def empacotar(icone: Path) -> Path:
    argumentos = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        NOME,
        "--icon",
        str(icone),
        "--paths",
        str(RAIZ / "src"),
        "--workpath",
        str(CONSTRUCAO),
        "--specpath",
        str(CONSTRUCAO),
        "--distpath",
        str(DESTINO),
    ]
    for arquivo in assets_versionados():
        pasta_no_pacote = arquivo.parent.relative_to(RAIZ / "src")
        argumentos += ["--add-data", f"{arquivo}{SEPARADOR_DADOS}{pasta_no_pacote.as_posix()}"]
    argumentos.append(str(RAIZ / "ferramentas" / "iniciar_jogo.py"))
    subprocess.run(argumentos, cwd=RAIZ, check=True)
    executavel = DESTINO / (f"{NOME}.exe" if sys.platform == "win32" else NOME)
    if not executavel.is_file():
        raise SystemExit(f"Executável não encontrado em {executavel}")
    return executavel


def testar(executavel: Path) -> None:
    """Abre o executável, que deve fechar sozinho e sem erro em poucos segundos."""
    ambiente = dict(os.environ, COBRINHA_DADOS=tempfile.mkdtemp(prefix="cobrinha-teste-"))
    if os.environ.get("CI"):
        ambiente.update(SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
    resultado = subprocess.run(
        [str(executavel), "--fechar-em", "3", "--nivel", "3"], env=ambiente, timeout=90
    )
    if resultado.returncode != 0:
        raise SystemExit(f"O executável terminou com erro (código {resultado.returncode}).")


def main() -> None:
    icone = gerar_icone()
    executavel = empacotar(icone)
    testar(executavel)
    tamanho = executavel.stat().st_size / 1024 / 1024
    print(f"\nPronto: {executavel.relative_to(RAIZ)} ({tamanho:.1f} MB), teste de fumaça ok.")


if __name__ == "__main__":
    main()
