# 1862 Golden Spike — Architecture Decision Records

Lightweight ADR log. One entry per non-obvious decision, written so future Claude
(and future you) don't re-litigate the same questions every session.

**Status values:** `ACCEPTED` (decision in force), `SUPERSEDED-BY <ID>` (replaced by a later decision), `REVERTED` (decision was made and then undone).

When a decision changes, **add a new ADR** rather than editing the old one. The history is the value.

---

## ADR-001 — Documentation lives in a separate worktree on the `Documentation` branch

- **Date:** 2026-05-14
- **Status:** ACCEPTED

**Context.** Documentation that lives on a feature branch disappears when you switch branches.
Checking it out on every branch creates merge conflicts.

**Decision.** Use a dedicated `Documentation` branch, materialised as a git worktree at
`~/18xx-docs/`, with symlinks `~/18xx/MD` and `~/18xx/CLAUDE.md` into the worktree.
Symlinks live outside the git repo and are invisible to all code branches.

**Consequences.** Docs are always accessible regardless of which code branch is checked out.
Doc changes are committed separately with no risk of merging docs into code.
Trade-off: you must remember to commit from `~/18xx-docs/`, not from the code repo.

---

## How to add a new ADR

1. Pick the next available ID (e.g. `ADR-002`).
2. Use the template:

   ```markdown
   ## ADR-NNN — Short imperative title

   - **Date:** YYYY-MM-DD
   - **Status:** ACCEPTED
   - (optional) **Replaces:** ADR-XXX

   **Context.** What forces are at play?

   **Decision.** What did we choose?

   **Consequences.** What follows from the choice — both good and bad?
   ```

3. If the new ADR supersedes an old one, update the old entry's status to `SUPERSEDED-BY ADR-NNN`.
4. Commit from `~/18xx-docs/`.
