# Ebook: Computação Gráfica na prática

Ebook didático sobre os conceitos de Computação Gráfica aplicados no Jogo da Cobrinha, no formato ABNT (NBR 14724, 10520 e 6023).

**PDF pronto:** [ebook-computacao-grafica-cobrinha.pdf](ebook-computacao-grafica-cobrinha.pdf)

## Gerar de novo

Com o ambiente virtual do projeto ativo:

```bash
pip install -e ".[ebook]"
python docs/ebook/gerar_ebook.py
```

O comando regenera as figuras (`figuras.py`), as capturas de tela (`capturas.py`, com o jogo rodando sem janela) e o PDF. Com `--so-pdf`, só o PDF é refeito. A impressão usa o Microsoft Edge ou o Google Chrome sem janela; para indicar outro navegador Chromium, defina a variável `EBOOK_NAVEGADOR`.

## Estrutura

| Caminho | Conteúdo |
|---------|----------|
| `texto/` | Capítulos e demais seções em Markdown |
| `figuras/` | Figuras geradas (não edite à mão: mude o script e regenere) |
| `figuras.py` | Fluxogramas, diagramas, gráficos, sprites ampliados e paleta (Pillow) |
| `capturas.py` | Capturas de tela, rotações, composição alfa e quantização (pygame-ce) |
| `gerar_ebook.py` | Montagem do HTML e impressão do PDF em duas passadas (sumário com páginas) |
| `estilo.css` | Apresentação ABNT |
| `metadados.toml` | Dados da capa e da folha de rosto |

## Sintaxe especial nos textos

- `::: figura nome` … `:::`: figura `figuras/nome.png`, com título na primeira linha e `Fonte:` opcional.
- `::: codigo #rotulo caminho/arquivo.py 10-20` … `:::`: trecho copiado do arquivo real, com os números de linha; `commit:caminho` lê a versão de um commit.
- `::: quadro #rotulo` … `:::`: quadro com título, tabela em Markdown e `Fonte:`.
- `@fig:nome`, `@cod:rotulo`, `@qua:rotulo`: referências cruzadas ("Figura 3", "Código 8"...).

O teste `tests/test_ebook.py` confere rótulos, figuras e intervalos de código.
