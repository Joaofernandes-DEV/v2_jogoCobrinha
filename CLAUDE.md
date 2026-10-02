# Jogo da Cobrinha V2

Python 3.11+ com pygame-ce. Código em `src/cobrinha/`, testes em `tests/`. Idioma do projeto: português (código, commits, LOG, README).

## Fluxo obrigatório

Siga o [CONTRIBUTING.md](CONTRIBUTING.md). Em resumo, a cada mudança:

1. Trabalhe em uma branch (`feat/...`, `fix/...`), nunca na `main`.
2. Escreva ou ajuste testes. Regras do jogo ficam em `src/cobrinha/dominio/` (sem pygame).
3. Rode `ruff check .`, `ruff format --check .` e `pytest`; só avance se passarem.
4. Adicione uma entrada **no final** do `LOG.md`, no modelo descrito no topo dele (data e horário de Brasília, o quê e por quê, arquivos).
5. Faça **um commit por arquivo**, com mensagem Conventional Commits em português (`feat:`, `fix:`, `test:`, `docs:`, `build:`, `ci:`, `chore:`). Ordem: código, testes, docs, LOG por último.
6. Não use `git add .` nem `git add -A`; adicione arquivo por arquivo.

## Cuidados

- Sprites e sons são gerados por `ferramentas/gerar_*.py`; não edite os binários à mão.
- Não publique tags/releases nem faça push na `main` sem pedido explícito.
