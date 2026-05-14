# 18OE — Architecture Decision Records

Lightweight ADR log. One entry per non-obvious decision, written so future Claude
(and future you) don't re-litigate the same questions every session.

**Format:** ID, date, status, context (what we're choosing between), decision
(what was chosen), consequences. Keep entries short — if it grows past a page,
extract details into a referenced doc.

**Status values:** `ACCEPTED` (decision in force), `SUPERSEDED-BY <ID>` (replaced
by a later decision), `REVERTED` (decision was made and then undone).

When a decision changes, **add a new ADR** rather than editing the old one. The
history is the value.

---

## ADR-001 — Documentation lives in a separate worktree on the `Documentation` branch

- **Date:** pre-2026-04 (legacy decision; recorded retroactively)
- **Status:** ACCEPTED

**Context.** Documentation that lives on a feature branch disappears when you
switch branches. Checking it out on every branch creates merge conflicts.

**Decision.** Use a dedicated `Documentation` branch, materialised as a git
worktree at `~/18xx-docs/`, with symlinks `~/18xx/MD` and `~/18xx/CLAUDE.md`
into the worktree. Symlinks live outside the git repo and are invisible to
all code branches.

**Consequences.** Docs are always accessible regardless of which code branch
is checked out. Doc changes are committed separately, with no risk of merging
docs into code. See `MD/git.md` for the full setup. Trade-off: you must
remember to commit from `~/18xx-docs/`, not from the code repo.

---

## ADR-002 — `MD/status.md` is the single source of truth for implementation state

- **Date:** 2026-05-05
- **Status:** ACCEPTED
- **Replaces:** the multi-file split (`openpoints.md` / `done.md` / `working.md` / `18OEstatus.md`)

**Context.** Before 2026-05-05 the project tracked implementation state across
five overlapping files. They drifted: `working.md` and `18OEstatus.md`
disagreed on whether stale `NATIONAL_REGION_HEXES` entries had been removed.
Branch references diverged (`18oe_fullmap` vs `18oe_testgame`).

**Decision.** Collapse to a single tracker, `MD/status.md` (renamed from
`18OEstatus.md`). It carries the `[x]/[~]/[ ]` state for every feature,
keyed to a named branch + date.

**Consequences.** Single file to update after each implementation session.
`openpoints.md` / `done.md` / `working.md` are deleted. The hand-maintained
"Implementation Status" section in `CLAUDE.md` is replaced with a one-line
pointer to `status.md`. See `MD/optimization_audit.md` for the audit that
produced this decision.

---

## ADR-003 — 2-player starting cash uses the without-concessions formula

- **Date:** pre-2026-04 (legacy decision; recorded retroactively)
- **Status:** ACCEPTED

**Context.** The Concession Phase is deferred (see ADR-004). Playbook §5.4
gives a separate without-concessions starting-cash formula because the normal
£5,400/n formula assumes concession holders pay 2× par at float, which is
revenue the bank would otherwise hold. Using £5,400/2 = £2,700 for the
2-player game gives a different balance than the rulebook intends.

**Decision.** `STARTING_CASH` returns £2,600 flat for the 2-player game (the
without-concessions value from Playbook §5.4) and £5,400/n rounded to nearest
£10 for 3–7 players.

**Consequences.** When the Concession Phase is implemented (see ADR-004),
`STARTING_CASH` will need to switch back to the standard formula for 3+
players who choose to play with concessions. The 2-player without-concessions
value stays as-is.

---

## ADR-004 — Defer the Concession Railroad Phase

- **Date:** pre-2026-04 (legacy decision; recorded retroactively)
- **Status:** ACCEPTED

**Context.** The Concession Phase requires a distinct round type (10 numbered
float actions in CON1–CON10 order), a queue management mechanism, and
obligation-transfer rules if a holder cannot pay. Implementing it before
core mechanics work is fragile — any bug in float ordering blocks playtest.

**Decision.** Define the 10 concession cards as entities (so the auction
includes them) but skip the Concession Phase itself; after the Auction Phase
the game proceeds directly to Regional/Minor Phase.

**Consequences.** All 10 CON1–CON10 cards are auctionable but their float
obligation is never triggered. The 2-player game uses the without-concessions
starting cash (ADR-003). When this is unblocked, the work is `MD/status.md` §5.

---

## ADR-005 — `WA-5` (silent `skip!` in `ConvertToNational`) is permanent, not a workaround

- **Date:** 2026-04-29 (recorded after the workaround was reviewed)
- **Status:** ACCEPTED

**Context.** `Step::ConvertToNational#skip!` is a no-op when the national
formation queue is empty, and `process_pass` uses the queue head as
`current_entity` rather than `action.entity`. This looked like a workaround
worth removing — but it's actually correct behaviour for a step that
conditionally blocks based on a queue state.

**Decision.** Document `WA-5` in `MD/status.md` §18 as `KEEP PERMANENTLY`
rather than `PENDING` (the default for workaround tags). Do not "fix" it.

**Consequences.** Future code reviewers won't waste time trying to refactor
this. If the formation queue mechanism changes, this ADR may need to be
revisited; the entry serves as a tripwire.

---

## ADR-006 — Reserved 2+2 obligation tracked via `Set`, not `trains.empty?`

- **Date:** 2026-04-28 (recorded retroactively)
- **Status:** ACCEPTED

**Context.** A floated company in Phases 2–3 must buy a 2+2 train on its first
OR. The naïve check is `entity.trains.empty?` — if you have no train, you
must buy. But this re-fires after a train rusts, after a buy-across, and
after consolidation reclaim — all situations where the obligation has
already been satisfied and shouldn't trigger again.

**Decision.** Track obligation fulfilment in a `Set` (`@fulfilled_train_obligation`)
on `Game::Base`. `must_buy_train?` returns `true` only when the entity is
floated, not in the Set, and the current phase has the `train_obligation`
status flag. `process_buy_train` snapshots phase status before `super` so a
phase change during the purchase doesn't cause a missed fulfilment mark.

**Consequences.** Obligation correctly fires once per company, ever — even
across rusting events. Phase transition during buy is handled cleanly.
`MD/status.md` §8g 3.1 is the implementation reference. Any future
"obligation"-style mechanic should use the same Set pattern.

---

## ADR-007 — Ferry route engine override deferred to a Layer 2 patch

- **Date:** 2026-04 (recorded retroactively)
- **Status:** ACCEPTED — implementation pending

**Context.** The base engine's tile placement validator rejects exits toward
blue (sea) hexes. 18OE needs ferries — tiles on land cities must be allowed
to exit toward specific blue hexes that carry pre-printed ferry paths.

**Decision.** Use a Layer 2 override in `g_18_oe/game.rb` (likely
`check_tile_edges` or `check_other`) that whitelists exits toward blue hexes
when the blue hex carries a matching pre-printed path. Two cases must be
covered: (1) forced upgrade where the city has a pre-printed path facing the
ferry hex; (2) optional connection where the player chooses to connect.

**Status of implementation.** Pre-printed ferry edges added to N31 Lille,
M28 London, AA82 Constantinople, I20 Dublin, O28 Le Havre, X33 Marseille.
Lille↔London ferry (N31→N29→M28) is open for playtesting because both cities
have forced upgrade edges. All other ferry routes remain blocked pending the
override. See `MD/status.md` §2b for the current state.

**Consequences.** Ferry mechanics, sea-zone costs, and OE bonus all
ultimately depend on this override. It is upstream of the OE first-run
detection.

---

## ADR-008 — Coding-guideline line length: 130 characters

- **Date:** 2026-04 (recorded retroactively from CLAUDE.md guidance)
- **Status:** ACCEPTED

**Context.** The upstream tobymao/18xx repo uses default Ruby style with no
explicit line length cap; some files run very long. Reading and reviewing
patches becomes painful past ~140 columns.

**Decision.** Cap `.rb` files at 130 characters per line for all 18OE
changes. Existing code that exceeds 130 is not retroactively reformatted
(would create unreviewable diffs); only new and modified lines are subject
to the limit.

**Consequences.** Rubocop config in the 18OE directory may need a
`Layout/LineLength: max: 130` override; otherwise the project-wide rubocop
default applies (typically 120). When that mismatch causes rubocop to fail,
revisit and align (this ADR or rubocop config).

---

## ADR-009 — Regional closure fires on 18th float, not on joint minors+regionals condition

- **Date:** 2026-05-14
- **Status:** ACCEPTED

**Context.** The rules (§8.2) state the Regional/Minor Phase ends "immediately when all 12 minors AND 18 of the regionals have floated" — both conditions simultaneously. The implementation has two separate triggers: `process_par` fires the regional-closure + `pass!` when `@regional_corps_floated == 18`, while `major_phase?` requires both 18 regionals and all minors floated. If the 18th regional is floated before all 12 minors, the 6 remaining regionals are removed but `major_phase?` stays false until every minor floats.

**Decision.** Accept the decoupled triggers. Merging them into a single atomic check would require `process_par` to know the minor count and delay the closure — adding complexity for a case that is unusual in no-concessions play (a player with a minor can float a regional on their turn, but they cannot pass until they float their minor, so all minors will eventually float in the same SR).

**Consequences.** In edge-case play order (player floats 18th regional before their own minor), the 6 un-floated regionals are removed from the board before the official phase transition text fires. `major_phase?` then correctly gates all downstream behaviour (secondary share purchases, conversions, inter-RR train trades). No functional gameplay difference results. If the Concession Phase (ADR-004) is implemented, revisit this decision — parred-only regionals that survive the close loop (BUG-012) could interact with this ordering.

---

## How to add a new ADR

1. Pick the next available ID (e.g. `ADR-009`).
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

3. If the new ADR replaces or supersedes an old one, update the old entry's
   status to `SUPERSEDED-BY ADR-NNN`. Don't delete the old entry.
4. Commit from `~/18xx-docs/` (see `MD/commands.md`).
