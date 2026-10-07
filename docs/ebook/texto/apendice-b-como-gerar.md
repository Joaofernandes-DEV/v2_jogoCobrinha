# Apêndice B – Como este ebook foi gerado

Como os sprites e os sons do jogo, este ebook é gerado por código. O texto-fonte, os scripts e as figuras ficam na pasta `docs/ebook/` do repositório, e qualquer pessoa pode regenerar o PDF a partir deles.

## Estrutura da pasta

| Caminho | Conteúdo |
|---|---|
| `texto/` | Capítulos e demais seções em Markdown |
| `figuras/` | Figuras geradas (PNG) |
| `figuras.py` | Fluxogramas, diagramas, gráficos, folha de sprites e paleta (só Pillow) |
| `capturas.py` | Capturas de tela e figuras que usam o pygame-ce (rotação, composição alfa e quantização) |
| `gerar_ebook.py` | Montagem do HTML e impressão do PDF |
| `estilo.css` | Apresentação conforme a ABNT |
| `metadados.toml` | Dados da capa e da folha de rosto |

## Como gerar

Com o ambiente virtual do projeto ativo, instale as dependências do ebook e rode o script:

```
pip install -e ".[ebook]"
python docs/ebook/gerar_ebook.py
```

O script regenera todas as figuras e capturas e grava o PDF em `docs/ebook/ebook-computacao-grafica-cobrinha.pdf`. Para gerar só o PDF, reaproveitando as figuras, use a opção `--so-pdf`. A impressão usa um navegador baseado no Chromium (Microsoft Edge ou Google Chrome) sem janela; o caminho pode ser indicado pela variável de ambiente `EBOOK_NAVEGADOR`.

## Como funciona

**Figuras.** Os fluxogramas são desenhados por um pequeno motor escrito sobre a Pillow, com nós (terminal, processo, decisão) e setas ortogonais posicionados por coordenadas no próprio código. O texto usa a fonte VT323 do jogo, e o script falha se algum caractere não tiver desenho nessa fonte. As capturas de tela rodam o jogo de verdade com o driver de vídeo `dummy` da SDL, como `ferramentas/gravar_demo.py`, reaproveitando o piloto automático desse script e uma semente fixa: as imagens saem sempre iguais.

**Trechos de código.** Os capítulos não contêm código copiado à mão. Um bloco como `::: codigo #executar src/cobrinha/jogo.py 92-105` é substituído, na montagem, pelas linhas 92 a 105 do arquivo real, com os números de linha. Trechos de versões antigas, como os do movimento interpolado, são lidos do histórico com `git show`, a partir de um prefixo de commit (por exemplo, `e22164c:src/cobrinha/ui/pecas.py`). Se um arquivo mudar e o intervalo deixar de existir, a montagem falha em vez de publicar um trecho errado.

**Numeração e sumário.** Seções, figuras, quadros e códigos são numerados automaticamente, e as referências cruzadas no texto (`@fig:nome`, `@qua:nome`, `@cod:nome`) viram "Figura 3", "Quadro 1" etc. O PDF é impresso uma primeira vez; o script lê os marcadores (*outline*) do PDF para descobrir em que página caiu cada título e cada legenda, preenche o sumário e as listas e imprime de novo, até a paginação se estabilizar.

## Normas seguidas

A apresentação segue a NBR 14724 (Associação Brasileira de Normas Técnicas, 2024): papel A4; margens de 3 cm à esquerda e em cima e de 2 cm à direita e embaixo; fonte tamanho 12 no texto e menor nas citações longas, legendas e fontes das ilustrações; espaçamento de 1,5 no texto; páginas contadas a partir da folha de rosto e numeradas a partir da primeira folha textual, no canto superior direito; e legendas das ilustrações na parte superior, com a fonte embaixo. As citações seguem a NBR 10520 (Associação Brasileira de Normas Técnicas, 2023), no sistema autor-data, e as referências seguem a NBR 6023 (Associação Brasileira de Normas Técnicas, 2018).
