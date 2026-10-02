# Como contribuir

O fluxo é o mesmo usado em todo o desenvolvimento da V2: **branch → mudança pequena → teste → entrada no LOG → um commit por arquivo → Pull Request**.

## 1. Preparar o ambiente

```bash
git clone https://github.com/Joaofernandes-DEV/v2_jogoCobrinha.git
cd v2_jogoCobrinha
python -m venv .venv
```

Ative o ambiente virtual (Windows: `.venv\Scripts\activate`; Linux/macOS: `source .venv/bin/activate`) e instale:

```bash
pip install -e ".[dev]"
```

## 2. Criar uma branch

Nunca trabalhe direto na `main`.

```bash
git switch -c feat/nome-curto-da-mudanca
```

Prefixos: `feat/`, `fix/`, `test/`, `docs/`, `chore/`.

## 3. Implementar com testes

- Regras do jogo ficam em `src/cobrinha/dominio/` (sem pygame) e devem ter teste em `tests/`.
- Toda mudança de comportamento traz teste novo ou ajustado.
- Antes de commitar, rode os três comandos e só prossiga se todos passarem:

```bash
ruff check .
ruff format --check .
pytest
```

## 4. Registrar no LOG.md

Adicione **uma entrada no final** do [LOG.md](LOG.md) (a mais recente por último), seguindo o modelo do próprio arquivo:

```markdown
### AAAA-MM-DD HH:MM — Título curto

**Feito:**
- ...

**Arquivos:** `caminho/arquivo.py`, ...

**Motivo / observações:** ...
```

- Horário de Brasília, no momento em que a mudança foi concluída.
- Explique o **quê** e o **porquê**; o "como" fica no código e nos commits.
- Se corrigir algo do [briefing_v2.md](briefing_v2.md), cite o item (ex.: `B3`).

## 5. Um commit por arquivo

Cada arquivo alterado vira um commit próprio, com mensagem curta em português no formato [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git add src/cobrinha/dominio/cobra.py
git commit -m "feat: impede a cobra de nascer encostada na parede"

git add tests/test_cobra.py
git commit -m "test: cobre o nascimento da cobra perto da parede"

git add LOG.md
git commit -m "docs: registra a mudança no diário de bordo"
```

Tipos usados: `feat`, `fix`, `test`, `docs`, `build`, `ci`, `chore`. Mensagens no imperativo/presente, sem ponto final, explicando o que muda.

Ordem recomendada: código → testes → documentação (README, se afetado) → LOG por último.

## 6. Abrir o Pull Request

```bash
git push -u origin feat/nome-curto-da-mudanca
gh pr create
```

Descreva o que mudou e como testar. O CI (lint + testes em Linux e Windows) precisa passar antes do merge.

## Notas

- Sprites e sons são gerados por código; edite `ferramentas/gerar_sprites.py` / `gerar_sons.py` e regenere, em vez de alterar os arquivos binários à mão.
- Versões são publicadas por tag (`vX.Y.Z`) e feitas pelo mantenedor.
