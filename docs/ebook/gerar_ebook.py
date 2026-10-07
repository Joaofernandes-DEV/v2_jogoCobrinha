"""Monta o ebook em PDF (ABNT) a partir dos textos em Markdown de `docs/ebook/texto/`.

Uso:
    python docs/ebook/gerar_ebook.py               # figuras + capturas + PDF
    python docs/ebook/gerar_ebook.py --so-pdf      # reaproveita as figuras já geradas

Requer: pip install -e ".[ebook]" e um navegador Chromium (Edge ou Chrome) instalado.
O caminho do navegador pode ser forçado pela variável de ambiente EBOOK_NAVEGADOR.

Etapas:
1. Lê os capítulos e expande os blocos especiais (figura, quadro e código).
   Os trechos de código são copiados dos arquivos reais (ou de um commit do Git),
   com os números de linha verdadeiros.
2. Numera seções, figuras, quadros e códigos e resolve as referências cruzadas
   (`@fig:nome`, `@qua:nome`, `@cod:nome`).
3. Gera o HTML com o estilo ABNT (`estilo.css`) e imprime em PDF com o navegador.
4. Lê o sumário do PDF (outline) para descobrir a página de cada título e de cada
   legenda, preenche o sumário e as listas e imprime de novo (segunda passada).
"""

from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import markdown

PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parents[1]
TEXTO = PASTA / "texto"
FIGURAS = PASTA / "figuras"
CONSTRUCAO = PASTA / "build"
SAIDA = PASTA / "ebook-computacao-grafica-cobrinha.pdf"

PRE_TEXTUAIS = ("resumo.md", "abstract.md")
POS_TEXTUAIS = ("referencias.md", "glossario.md")
NOMES_TIPO = {"figura": "Figura", "quadro": "Quadro", "codigo": "Código"}
PREFIXO_ROTULO = {"figura": "fig", "quadro": "qua", "codigo": "cod"}

NAVEGADORES = (
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google-chrome",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
)


# ---------------------------------------------------------------------------
# Estrutura do livro
# ---------------------------------------------------------------------------


@dataclass
class Titulo:
    nivel: int
    numero: str  # "" nos títulos sem indicativo numérico (referências, apêndices...)
    texto: str
    ancora: str

    @property
    def rotulo(self) -> str:
        return f"{self.numero} {self.texto}".strip()


@dataclass
class Legenda:
    tipo: str
    numero: int
    texto: str  # já em HTML (pode ter <code>)
    ancora: str

    @property
    def rotulo(self) -> str:
        return f"{NOMES_TIPO[self.tipo]} {self.numero} – {texto_puro(self.texto)}"


@dataclass
class Livro:
    meta: dict
    titulos: list[Titulo] = field(default_factory=list)
    legendas: list[Legenda] = field(default_factory=list)
    rotulos: dict[str, str] = field(default_factory=dict)  # "fig:x" → "Figura 3"
    ancoras: dict[str, str] = field(default_factory=dict)  # "fig:x" → "fig-x"
    paginas: dict[str, int] = field(default_factory=dict)  # rótulo puro → página


def texto_puro(conteudo: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", conteudo))).strip()


def chave(conteudo: str) -> str:
    """Título sem espaços, para comparar com o outline do PDF.

    O Chromium tira o espaço onde o título quebra de linha ("O TEMPO" vira "OTEMPO").
    """
    return re.sub(r"\s+", "", texto_puro(conteudo))


def inline(conteudo: str) -> str:
    """Markdown de uma linha (negrito, código...) sem o <p> em volta."""
    convertido = markdown.markdown(conteudo.strip())
    return re.sub(r"^<p>(.*)</p>$", r"\1", convertido, flags=re.S)


# ---------------------------------------------------------------------------
# Blocos especiais
# ---------------------------------------------------------------------------

BLOCO = re.compile(r"^::: *(figura|quadro|codigo)(.*?)\n(.*?)^:::\s*$", re.M | re.S)


def numerar_blocos(livro: Livro, textos: list[str]) -> None:
    """Primeira varredura: numera figuras, quadros e códigos na ordem em que aparecem."""
    contagem = dict.fromkeys(NOMES_TIPO, 0)
    for texto in textos:
        for bloco in BLOCO.finditer(texto):
            tipo, cabecalho = bloco.group(1), bloco.group(2).split()
            contagem[tipo] += 1
            nome = _nome_do_bloco(tipo, cabecalho)
            chave = f"{PREFIXO_ROTULO[tipo]}:{nome}"
            if chave in livro.rotulos:
                raise ValueError(f"Rótulo repetido: {chave}")
            livro.rotulos[chave] = f"{NOMES_TIPO[tipo]} {contagem[tipo]}"
            livro.ancoras[chave] = f"{PREFIXO_ROTULO[tipo]}-{nome}"


def _nome_do_bloco(tipo: str, cabecalho: list[str]) -> str:
    if tipo == "codigo":
        rotulos = [p[1:] for p in cabecalho if p.startswith("#")]
        if not rotulos:
            raise ValueError(f"Bloco de código sem rótulo (#nome): {cabecalho}")
        return rotulos[0]
    return cabecalho[0].lstrip("#")


def expandir_blocos(livro: Livro, texto: str) -> str:
    def substituir(bloco: re.Match[str]) -> str:
        tipo, cabecalho, corpo = bloco.group(1), bloco.group(2).split(), bloco.group(3)
        nome = _nome_do_bloco(tipo, cabecalho)
        chave = f"{PREFIXO_ROTULO[tipo]}:{nome}"
        numero = int(livro.rotulos[chave].split()[-1])
        linhas = [linha for linha in corpo.strip("\n").split("\n")]
        fonte_linhas = [linha for linha in linhas if linha.startswith("Fonte:")]
        largura = next(
            (linha.split(":", 1)[1].strip() for linha in linhas if linha.startswith("largura:")),
            None,
        )
        resto = [linha for linha in linhas if not linha.startswith(("Fonte:", "largura:"))]
        titulo_md = resto[0] if resto else ""
        legenda = Legenda(tipo, numero, inline(titulo_md), livro.ancoras[chave])
        livro.legendas.append(legenda)
        if tipo == "figura":
            miolo = _html_figura(nome, legenda, largura)
            fonte = fonte_linhas[0] if fonte_linhas else "Fonte: elaborada pelo autor (2026)."
        elif tipo == "quadro":
            tabela = "\n".join(resto[1:])
            miolo = markdown.markdown(tabela, extensions=["tables"])
            fonte = fonte_linhas[0] if fonte_linhas else "Fonte: elaborado pelo autor (2026)."
        else:
            caminho, intervalo = [p for p in cabecalho if not p.startswith("#")]
            miolo, fonte_padrao = _html_codigo(caminho, intervalo)
            fonte = fonte_linhas[0] if fonte_linhas else fonte_padrao
        return (
            f'\n<div class="bloco bloco-{tipo}" id="{legenda.ancora}">\n'
            f'<h6 class="legenda">{NOMES_TIPO[tipo]} {numero} – {legenda.texto}</h6>\n'
            f"{miolo}\n"
            f'<p class="fonte">{inline(fonte)}</p>\n</div>\n'
        )

    return BLOCO.sub(substituir, texto)


def _html_figura(nome: str, legenda: Legenda, largura: str | None) -> str:
    arquivo = FIGURAS / f"{nome}.png"
    if not arquivo.is_file():
        raise FileNotFoundError(f"Figura não encontrada: {arquivo}")
    estilo = f' style="width: {largura}"' if largura else ""
    alt = html.escape(texto_puro(legenda.texto), quote=True)
    return f'<img src="{arquivo.as_uri()}" alt="{alt}"{estilo}>'


def ler_codigo(caminho: str) -> list[str]:
    """Linhas de um arquivo do repositório; `commit:caminho` lê a versão daquele commit."""
    if ":" in caminho:
        commit, arquivo = caminho.split(":", 1)
        resultado = subprocess.run(
            ["git", "show", f"{commit}:{arquivo}"],
            cwd=RAIZ,
            capture_output=True,
            check=True,
            encoding="utf-8",
        )
        return resultado.stdout.splitlines()
    return (RAIZ / caminho).read_text(encoding="utf-8").splitlines()


def _html_codigo(caminho: str, intervalo: str) -> tuple[str, str]:
    inicio, fim = (int(n) for n in intervalo.split("-"))
    linhas = ler_codigo(caminho)
    if fim > len(linhas):
        raise ValueError(f"{caminho} tem só {len(linhas)} linhas (pedido: {intervalo})")
    trecho = linhas[inicio - 1 : fim]
    realcado = realcar_python(trecho)
    largura = len(str(fim))
    corpo = "\n".join(
        f'<span class="ln">{str(inicio + i).rjust(largura)}</span>{linha}'
        for i, linha in enumerate(realcado)
    )
    if ":" in caminho:
        commit, arquivo = caminho.split(":", 1)
        fonte = f"Fonte: `{arquivo}`, linhas {inicio}–{fim}, na versão do commit `{commit}`."
    else:
        fonte = f"Fonte: `{caminho}`, linhas {inicio}–{fim}."
    return f'<pre class="codigo"><code>{corpo}</code></pre>', fonte


PALAVRAS_CHAVE = (
    "False|None|True|and|as|assert|break|class|continue|def|del|elif|else|except|finally|"
    "for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|"
    "with|yield|match|case"
)
TOKEN = re.compile(
    rf"(?P<comentario>#.*)"
    rf"|(?P<texto>[rbfu]{{0,2}}(\"\"\"|'''|\"[^\"\n]*\"|'[^'\n]*'))"
    rf"|(?P<chave>\b(?:{PALAVRAS_CHAVE})\b)"
    rf"|(?P<numero>\b\d[\d_]*(?:\.\d+)?\b)"
    rf"|(?P<decorador>^\s*@\w+)"
)


def realcar_python(linhas: list[str]) -> list[str]:
    """Realce simples (comentários, textos, palavras-chave e números), linha a linha."""
    saida = []
    em_docstring: str | None = None
    for linha in linhas:
        if em_docstring:
            fim = linha.find(em_docstring)
            if fim == -1:
                saida.append(f'<span class="s">{html.escape(linha)}</span>')
                continue
            fim += 3
            saida.append(
                f'<span class="s">{html.escape(linha[:fim])}</span>' + _realcar(linha[fim:])
            )
            em_docstring = None
            continue
        partes = _realcar(linha)
        # Docstring de várias linhas que começa aqui e não termina na mesma linha.
        abertura = re.search(r"(\"\"\"|''')", linha)
        inicio = abertura.start() if abertura else 0
        if abertura and linha.count(abertura.group(1)) == 1 and "#" not in linha[:inicio]:
            em_docstring = abertura.group(1)
            resto = html.escape(linha[inicio:])
            partes = _realcar(linha[:inicio]) + f'<span class="s">{resto}</span>'
        saida.append(partes)
    return saida


def _realcar(linha: str) -> str:
    resultado, posicao = [], 0
    for token in TOKEN.finditer(linha):
        resultado.append(html.escape(linha[posicao : token.start()]))
        classe = {"comentario": "c", "texto": "s", "chave": "k", "numero": "n", "decorador": "d"}[
            token.lastgroup
        ]
        resultado.append(f'<span class="{classe}">{html.escape(token.group())}</span>')
        posicao = token.end()
    resultado.append(html.escape(linha[posicao:]))
    return "".join(resultado)


# ---------------------------------------------------------------------------
# Títulos, referências cruzadas e conversão
# ---------------------------------------------------------------------------


def converter_arquivo(livro: Livro, arquivo: Path, categoria: str, contador: list[int]) -> str:
    texto = arquivo.read_text(encoding="utf-8")
    texto = expandir_blocos(livro, texto)
    # Referências entre crases (exemplos de sintaxe) ficam como estão.
    texto = re.sub(r"(?<!`)@(fig|qua|cod):([\w-]+)", lambda m: _referencia(livro, m), texto)
    linhas, em_cerca = [], False
    for linha in texto.split("\n"):
        if linha.startswith("```"):
            em_cerca = not em_cerca
        cabecalho = re.match(r"^(#{1,4}) (.+)$", linha)
        if cabecalho and not em_cerca:
            linhas.append(
                "\n"
                + _titulo(livro, categoria, len(cabecalho.group(1)), cabecalho.group(2), contador)
                + "\n"
            )
        else:
            linhas.append(linha)
    extensoes = ["tables", "fenced_code", "sane_lists", "attr_list", "def_list", "md_in_html"]
    corpo = markdown.markdown("\n".join(linhas), extensions=extensoes)
    return f'<section class="{categoria} {arquivo.stem}">\n{corpo}\n</section>'


def _referencia(livro: Livro, achado: re.Match[str]) -> str:
    chave = f"{achado.group(1)}:{achado.group(2)}"
    if chave not in livro.rotulos:
        raise KeyError(f"Referência a rótulo inexistente: @{chave}")
    return f'<a href="#{livro.ancoras[chave]}">{livro.rotulos[chave]}</a>'


def _titulo(livro: Livro, categoria: str, nivel: int, texto: str, contador: list[int]) -> str:
    texto = texto.strip()
    if categoria == "capitulo":
        contador[nivel - 1] += 1
        for i in range(nivel, len(contador)):
            contador[i] = 0
        numero = ".".join(str(n) for n in contador[:nivel])
    else:
        numero = ""
    exibido = texto.upper() if nivel <= 2 else texto
    simples = _sem_acentos(f"{numero} {texto}").lower()
    ancora = "sec-" + re.sub(r"[^a-z0-9]+", "-", simples).strip("-")
    if categoria != "pre":
        livro.titulos.append(Titulo(nivel, numero, exibido, ancora))
    classe = f"nivel-{nivel}" + (" sem-numero" if not numero else "")
    rotulo = f"{numero} {exibido}".strip()
    return f'<h{nivel} id="{ancora}" class="{classe}">{html.escape(rotulo)}</h{nivel}>'


def _sem_acentos(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texto) if not unicodedata.combining(c))


# ---------------------------------------------------------------------------
# Elementos pré-textuais gerados (capa, folha de rosto, listas e sumário)
# ---------------------------------------------------------------------------


def _pagina(livro: Livro, rotulo: str) -> str:
    pagina = livro.paginas.get(chave(rotulo))
    return str(pagina) if pagina is not None else "00"


def capa(meta: dict) -> str:
    return f"""
<section class="capa">
  <p class="instituicao">{meta["instituicao"]}<br>{meta["curso"]}</p>
  <p class="autor">{meta["autor"]}</p>
  <div class="titulo-capa">
    <p class="titulo">{meta["titulo"]}:</p>
    <p class="subtitulo">{meta["subtitulo"]}</p>
  </div>
  <p class="local">{meta["local"]}<br>{meta["ano"]}</p>
</section>"""


def folha_de_rosto(meta: dict) -> str:
    professor = meta.get("professor")
    orientador = f'<p class="orientador">Professor(a): {professor}</p>' if professor else ""
    return f"""
<section class="folha-de-rosto">
  <p class="autor">{meta["autor"]}</p>
  <div class="titulo-capa">
    <p class="titulo">{meta["titulo"]}:</p>
    <p class="subtitulo">{meta["subtitulo"]}</p>
  </div>
  <div class="natureza"><p>{meta["natureza"]}</p>{orientador}</div>
  <p class="local">{meta["local"]}<br>{meta["ano"]}</p>
</section>"""


def lista(livro: Livro, tipo: str, titulo: str) -> str:
    itens = [
        f'<li><a href="#{legenda.ancora}"><span class="item">{NOMES_TIPO[tipo]} {legenda.numero}'
        f' – {legenda.texto}</span><span class="pontos"></span>'
        f'<span class="pagina">{_pagina(livro, legenda.rotulo)}</span></a></li>'
        for legenda in livro.legendas
        if legenda.tipo == tipo
    ]
    return (
        f'<section class="pre lista"><h1 class="sem-numero">{titulo}</h1>'
        f'<ul class="indice">{"".join(itens)}</ul></section>'
    )


def sumario(livro: Livro) -> str:
    itens = []
    for titulo in livro.titulos:
        if titulo.nivel > 3:
            continue
        itens.append(
            f'<li class="nivel-{titulo.nivel}{" sem-numero" if not titulo.numero else ""}">'
            f'<a href="#{titulo.ancora}"><span class="numero">{titulo.numero}</span>'
            f'<span class="item">{html.escape(titulo.texto)}</span><span class="pontos"></span>'
            f'<span class="pagina">{_pagina(livro, titulo.rotulo)}</span></a></li>'
        )
    return (
        f'<section class="pre sumario"><h1 class="sem-numero">SUMÁRIO</h1>'
        f'<ul class="indice">{"".join(itens)}</ul></section>'
    )


def montar_html(livro: Livro) -> str:
    """Converte tudo (zerando os registros) e devolve o documento completo."""
    livro.titulos.clear()
    livro.legendas.clear()
    capitulos = sorted(TEXTO.glob("[0-9][0-9]-*.md"))
    apendices = sorted(TEXTO.glob("apendice-*.md"))
    contador = [0, 0, 0, 0]
    pre = [converter_arquivo(livro, TEXTO / nome, "pre", contador) for nome in PRE_TEXTUAIS]
    abreviaturas = converter_arquivo(livro, TEXTO / "abreviaturas.md", "pre", contador)
    corpo = [converter_arquivo(livro, arquivo, "capitulo", contador) for arquivo in capitulos]
    pos = [converter_arquivo(livro, TEXTO / nome, "pos", contador) for nome in POS_TEXTUAIS]
    pos += [converter_arquivo(livro, arquivo, "pos", contador) for arquivo in apendices]
    estilo = (PASTA / "estilo.css").read_text(encoding="utf-8")
    meta = livro.meta
    partes = [
        capa(meta),
        folha_de_rosto(meta),
        *pre,
        lista(livro, "figura", "LISTA DE FIGURAS"),
        lista(livro, "quadro", "LISTA DE QUADROS"),
        lista(livro, "codigo", "LISTA DE CÓDIGOS"),
        abreviaturas,
        sumario(livro),
        '<div class="textuais">',
        *corpo,
        "</div>",
        *pos,
    ]
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{meta["titulo"]}: {meta["subtitulo"]}</title>
<meta name="author" content="{meta["autor"]}">
<style>{estilo}</style>
</head>
<body>
{"".join(partes)}
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Impressão em PDF e leitura do outline
# ---------------------------------------------------------------------------


def achar_navegador() -> str:
    candidatos = [os.environ["EBOOK_NAVEGADOR"]] if "EBOOK_NAVEGADOR" in os.environ else []
    candidatos += NAVEGADORES
    for candidato in candidatos:
        caminho = candidato if Path(candidato).is_file() else shutil.which(candidato)
        if caminho:
            return caminho
    raise FileNotFoundError("Nenhum navegador Chromium encontrado; defina EBOOK_NAVEGADOR.")


def imprimir(navegador: str, pagina_html: Path, pdf: Path, espera: float = 180) -> None:
    """Imprime a página em PDF com o navegador sem janela.

    No Windows, o Edge às vezes devolve o controle antes de terminar (ele se relança
    num processo filho), então a função espera o arquivo ficar completo.
    """
    pdf.unlink(missing_ok=True)
    perfil = tempfile.mkdtemp(prefix="ebook-perfil-")
    subprocess.run(
        [
            navegador,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--generate-pdf-document-outline",
            "--allow-file-access-from-files",
            f"--user-data-dir={perfil}",
            f"--print-to-pdf={pdf}",
            pagina_html.as_uri(),
        ],
        capture_output=True,
        timeout=300,
        check=False,
    )
    limite = time.monotonic() + espera
    tamanho_anterior = -1
    while time.monotonic() < limite:
        if pdf.is_file():
            tamanho = pdf.stat().st_size
            if tamanho == tamanho_anterior and pdf.read_bytes().rstrip().endswith(b"%%EOF"):
                break
            tamanho_anterior = tamanho
        time.sleep(0.5)
    else:
        raise RuntimeError(f"O navegador não gerou o PDF a tempo: {navegador}")
    time.sleep(1)  # dá tempo de o navegador soltar o perfil antes de apagá-lo
    shutil.rmtree(perfil, ignore_errors=True)


def _decodificar_titulo(bruto: bytes) -> str:
    if bruto.startswith(b"<"):
        dados = bytes.fromhex(bruto[1:-1].decode())
        if dados[:2] == b"\xfe\xff":
            return dados[2:].decode("utf-16-be")
        return dados.decode("latin-1")
    conteudo = bruto[1:-1]
    conteudo = re.sub(rb"\\([0-7]{1,3})", lambda m: bytes([int(m.group(1), 8)]), conteudo)
    conteudo = re.sub(rb"\\(.)", rb"\1", conteudo)
    if conteudo.startswith(b"\xfe\xff"):
        return conteudo[2:].decode("utf-16-be")
    return conteudo.decode("latin-1")


def ler_outline(pdf: Path) -> dict[str, int]:
    """Título de cada marcador do PDF → número da página física (1 = capa)."""
    dados = pdf.read_bytes()
    objetos = {
        int(m.group(1)): m.group(2) for m in re.finditer(rb"(\d+) 0 obj\s*(.*?)endobj", dados, re.S)
    }
    catalogo = next(c for c in objetos.values() if b"/Type /Catalog" in c)
    raiz = int(re.search(rb"/Pages (\d+) 0 R", catalogo).group(1))
    # A árvore de páginas pode ter nós intermediários (/Type /Pages) quando há muitas.
    sequencia: list[int] = []

    def visitar(numero: int) -> None:
        corpo = objetos[numero]
        if re.search(rb"/Type /Pages\b", corpo):
            kids = re.search(rb"/Kids \[(.*?)\]", corpo, re.S).group(1)
            for filho in re.findall(rb"(\d+) 0 R", kids):
                visitar(int(filho))
        else:
            sequencia.append(numero)

    visitar(raiz)
    ordem = {numero: i + 1 for i, numero in enumerate(sequencia)}
    paginas = {}
    for corpo in objetos.values():
        titulo = re.search(rb"/Title\s*(\((?:\\.|[^\\)])*\)|<[0-9A-Fa-f]*>)", corpo)
        destino = re.search(rb"/Dest \[(\d+) 0 R", corpo)
        if titulo and destino and int(destino.group(1)) in ordem:
            paginas[chave(_decodificar_titulo(titulo.group(1)))] = ordem[int(destino.group(1))]
    return paginas


def gerar_pdf(livro: Livro) -> None:
    navegador = achar_navegador()
    CONSTRUCAO.mkdir(exist_ok=True)
    pagina_html = CONSTRUCAO / "ebook.html"
    pdf = CONSTRUCAO / "ebook.pdf"
    anteriores: dict[str, int] = {}
    for passada in (1, 2, 3):
        pagina_html.write_text(montar_html(livro), encoding="utf-8")
        imprimir(navegador, pagina_html, pdf)
        fisicas = ler_outline(pdf)
        # A capa não é contada (ABNT): a folha de rosto é a página 1.
        livro.paginas = {titulo: fisica - 1 for titulo, fisica in fisicas.items()}
        faltando = [t.rotulo for t in livro.titulos if chave(t.rotulo) not in livro.paginas]
        faltando += [g.rotulo for g in livro.legendas if chave(g.rotulo) not in livro.paginas]
        if faltando:
            raise ValueError(f"Sem página no outline do PDF: {faltando[:5]}")
        print(f"passada {passada}: {len(fisicas)} marcadores no PDF")
        if livro.paginas == anteriores:
            break
        anteriores = livro.paginas
    else:
        raise RuntimeError("A paginação não estabilizou em 3 passadas.")
    shutil.copyfile(pdf, SAIDA)
    total = len(re.findall(rb"/Type /Page\b", SAIDA.read_bytes()))
    tamanho = SAIDA.stat().st_size / 1e6
    print(f"gerado: {SAIDA.relative_to(RAIZ)} ({total} páginas, {tamanho:.1f} MB)")


def main() -> None:
    argumentos = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    argumentos.add_argument("--so-pdf", action="store_true", help="não regenera as figuras")
    opcoes = argumentos.parse_args()
    if not opcoes.so_pdf:
        sys.path.insert(0, str(PASTA))
        import capturas
        import figuras

        figuras.main()
        capturas.main()
    meta = tomllib.loads((PASTA / "metadados.toml").read_text(encoding="utf-8"))
    livro = Livro(meta)
    arquivos = [TEXTO / nome for nome in PRE_TEXTUAIS]
    arquivos += sorted(TEXTO.glob("[0-9][0-9]-*.md"))
    arquivos += [TEXTO / nome for nome in POS_TEXTUAIS]
    arquivos += sorted(TEXTO.glob("apendice-*.md"))
    numerar_blocos(livro, [arquivo.read_text(encoding="utf-8") for arquivo in arquivos])
    gerar_pdf(livro)


if __name__ == "__main__":
    main()
