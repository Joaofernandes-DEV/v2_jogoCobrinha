"""Consistência do texto-fonte do ebook (docs/ebook/): rótulos, figuras e trechos de código.

Só usa a biblioteca padrão, para rodar no CI sem as dependências do extra [ebook].
"""

import re
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
EBOOK = RAIZ / "docs" / "ebook"
BLOCO = re.compile(r"^::: *(figura|quadro|codigo)(.*?)\n(.*?)^:::\s*$", re.M | re.S)
PREFIXO = {"figura": "fig", "quadro": "qua", "codigo": "cod"}


def _textos() -> dict[str, str]:
    return {
        arquivo.name: arquivo.read_text(encoding="utf-8") for arquivo in EBOOK.glob("texto/*.md")
    }


def _blocos() -> list[tuple[str, list[str]]]:
    return [
        (bloco.group(1), bloco.group(2).split())
        for texto in _textos().values()
        for bloco in BLOCO.finditer(texto)
    ]


def _rotulo(tipo: str, cabecalho: list[str]) -> str:
    nome = next(p for p in cabecalho if p.startswith("#")) if tipo == "codigo" else cabecalho[0]
    return f"{PREFIXO[tipo]}:{nome.lstrip('#')}"


def test_rotulos_sao_unicos():
    rotulos = [_rotulo(tipo, cabecalho) for tipo, cabecalho in _blocos()]
    assert rotulos
    assert len(rotulos) == len(set(rotulos))


def test_toda_referencia_cruzada_aponta_para_um_bloco():
    rotulos = {_rotulo(tipo, cabecalho) for tipo, cabecalho in _blocos()}
    for nome, texto in _textos().items():
        for referencia in re.findall(r"(?<!`)@((?:fig|qua|cod):[\w-]+)", texto):
            assert referencia in rotulos, f"{nome}: @{referencia} sem bloco correspondente"


def test_figuras_existem_e_todas_sao_citadas():
    usadas = {cabecalho[0] for tipo, cabecalho in _blocos() if tipo == "figura"}
    geradas = {arquivo.stem for arquivo in (EBOOK / "figuras").glob("*.png")}
    assert usadas <= geradas, f"figuras faltando: {usadas - geradas}"
    assert geradas <= usadas, f"figuras sem legenda no texto: {geradas - usadas}"


def _commit_disponivel(commit: str) -> bool:
    resultado = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=RAIZ, capture_output=True
    )
    return resultado.returncode == 0


def test_trechos_de_codigo_existem():
    for tipo, cabecalho in _blocos():
        if tipo != "codigo":
            continue
        caminho, intervalo = [p for p in cabecalho if not p.startswith("#")]
        inicio, fim = (int(n) for n in intervalo.split("-"))
        assert 1 <= inicio <= fim
        if ":" in caminho:
            commit, arquivo = caminho.split(":", 1)
            if not _commit_disponivel(commit):
                continue  # clone raso (ex.: CI): o commit antigo não está disponível
            linhas = subprocess.run(
                ["git", "show", f"{commit}:{arquivo}"],
                cwd=RAIZ,
                capture_output=True,
                check=True,
                encoding="utf-8",
            ).stdout.splitlines()
        else:
            linhas = (RAIZ / caminho).read_text(encoding="utf-8").splitlines()
        assert fim <= len(linhas), f"{caminho} tem {len(linhas)} linhas; pedido {intervalo}"
