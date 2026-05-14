# Co-developing a Game with Claude

This page describes the workflow used to implement 18OE on this engine collaboratively with Claude Code. The same pattern applies to any new title.

The core idea: keep Claude's context sharp by maintaining a small set of always-current reference files, load only what is needed for each session, and establish a documentation-first habit so Claude never has to rediscover how the engine works mid-session.

---

## Setting Up for a New Game with Claude

Everything below assumes your machine is running. If you are on Windows, use **VS Code + WSL2 + Docker Desktop** — see [Development Setup](getting-started.html#vs-code-in-wsl) for the one-time installation steps. All commands run in a WSL terminal.

### Step 1 — Fork and clone the engine

Fork `tobymao/18xx` on GitHub, then clone your fork inside WSL:

```bash
mkdir -p ~/18xx
git clone https://github.com/YOUR-USERNAME/18xx.git ~/18xx/18xx
cd ~/18xx/18xx
git remote add upstream https://github.com/tobymao/18xx.git
```

Verify the app boots:

```bash
docker compose up          # first build takes a few minutes
# → open http://localhost:9292
```

### Step 2 — Create the Documentation branch and worktree

The workflow keeps documentation on a separate branch so it is always accessible regardless of which feature branch you have checked out. A git worktree exposes the branch as a separate directory without a second clone.

```bash
# Create an orphan Documentation branch
git -C ~/18xx/18xx checkout --orphan Documentation
git -C ~/18xx/18xx rm -rf .          # clear the working tree
git -C ~/18xx/18xx commit --allow-empty -m "chore: init Documentation branch"
git -C ~/18xx/18xx push -u origin Documentation

# Return to master
git -C ~/18xx/18xx checkout master

# Mount the Documentation branch as a worktree
git -C ~/18xx/18xx worktree add ~/18xx-docs Documentation
```

Create the MD/ directory and seed the tracking files:

```bash
mkdir -p ~/18xx-docs/MD
touch ~/18xx-docs/MD/CLAUDE.md \
      ~/18xx-docs/MD/inwork.md \
      ~/18xx-docs/MD/todo.md \
      ~/18xx-docs/MD/done.md \
      ~/18xx-docs/MD/bugs.md \
      ~/18xx-docs/MD/decisions.md
```

Expose `MD/` and `CLAUDE.md` at the project root via symlinks:

```bash
ln -s ~/18xx-docs/MD           ~/18xx/MD
ln -s ~/18xx-docs/MD/CLAUDE.md ~/18xx/CLAUDE.md
```

Now `~/18xx/MD/` and `~/18xx/CLAUDE.md` are visible on every feature branch without any branch switching.

### Step 3 — Import the engine documentation

The engine documentation (all `htmldoku/` pages, the HTML generator, and the rendered HTML) lives on the `Documentation` branch of `Witzman/18xx`. Import it into your own Documentation branch by adding it as a git remote — no manual copying needed.

**From your Documentation worktree:**

```bash
cd ~/18xx-docs

# Add this repo as a remote named "engine-docs"
git remote add engine-docs https://github.com/Witzman/18xx.git
git fetch engine-docs Documentation

# Merge the engine docs into your Documentation branch
# --allow-unrelated-histories is needed because both branches are orphans
git merge engine-docs/Documentation --allow-unrelated-histories \
    -m "docs: import engine documentation from Witzman/18xx"

git push
```

This pulls in `htmldoku/*.md`, `htmldoku/generate-html.py`, `docs/18xx-Doku/*.html`, and `MD/` as a starting point. Your own `MD/CLAUDE.md`, `MD/inwork.md`, etc. will overlay on top — edit them after the merge to match your game.

Verify the generator works:

```bash
python3 htmldoku/generate-html.py
# → Done. 31 pages → docs/18xx-Doku/index.html
```

**Staying up to date**

When the engine documentation is updated (new pages, corrections), re-fetch and merge:

```bash
cd ~/18xx-docs
git fetch engine-docs Documentation
git merge engine-docs/Documentation \
    -m "docs: merge engine documentation updates"
git push
```

**Using GitHub's Pull Request UI instead**

If you prefer reviewing changes before merging, you can open a PR on GitHub:

1. Go to your fork on GitHub → **Pull requests** → **New pull request**
2. Click **compare across forks**
3. Set **base repository** to your fork, **base** to `Documentation`
4. Set **head repository** to `Witzman/18xx`, **compare** to `Documentation`
5. Review the diff, then merge

This works because both repos are forks of `tobymao/18xx` and share the same GitHub fork network. The PR shows exactly which htmldoku pages changed so you can review before accepting.

### Step 4 — Write your CLAUDE.md

`CLAUDE.md` is the single file Claude reads at the start of every session. It eliminates re-orientation cost: Claude knows what the project is, where every file lives, and how the engine works — before the first prompt is typed.

Minimum viable `CLAUDE.md`:

```markdown
# MyGame — Claude Context

Read this file then `MD/inwork.md`. Do not proceed until both are read.

## Project

**MyGame** — 18xx-style train game on the 18xx.games engine. In-progress.

- Engine: `~/18xx/18xx/`
- Rules: `~/18xx/18xx/rules/MyGame_Rulebook.txt`

## Physical Layout

    ~/18xx/
        18xx/       ← main git repo
        MD/         ← symlink → ~/18xx-docs/MD/
        CLAUDE.md   ← symlink → ~/18xx-docs/MD/CLAUDE.md
    ~/18xx-docs/    ← Documentation worktree

## Key Files

| What | Path |
|------|------|
| Base game | `~/18xx/18xx/lib/engine/game/g_mygame/game.rb` |
| In Work   | `MD/inwork.md` |

## Documentation Lookup

| Task | Read |
|------|------|
| Engine layers | `~/18xx-docs/htmldoku/engine-concepts.md` |
| Map / HEXES   | `~/18xx-docs/htmldoku/map.md` |
| Abilities     | `~/18xx-docs/htmldoku/abilities.md` |
| Code recipes  | `~/18xx-docs/htmldoku/common-patterns.md` |

## Layer Taxonomy

L1 — constants · L2 — Game::Base override · L3 — new Step/Round file

## Coding Rules

- 130-char line limit · no puts/p/pp · frozen_string_literal: true
```

Extend it as you learn more about your game's rules.

### Step 5 — Seed the backlog

`MD/todo.md` is your full backlog. Decompose your rulebook into discrete, layer-annotated items. Each item is a checkbox:

```markdown
# MyGame — Backlog

## Trains & Phases

- [ ] **TRAINS constant** — 2/3/4/5/6 train roster with rust triggers **[L1]**
- [ ] **PHASES constant** — 5 phases with tile colours and OR counts **[L1]**

## Track

- [ ] **Custom tile upgrades** — validate label restrictions **[L2]**
- [ ] **Tile point budget** — 3pt minor / 6pt major **[L2]**

## Revenue

- [ ] **OE bonus** — revenue_for override **[L2]**
```

Layer annotations (`[L1]`, `[L2]`, `[L3]`) tell Claude how much new code is needed before any session starts. Commit `todo.md` to the Documentation branch.

### Step 6 — Open Claude Code and start your first session

Install Claude Code if you haven't already:

```bash
npm install -g @anthropic-ai/claude-code
```

Open Claude Code from your project root:

```bash
cd ~/18xx/18xx
claude
```

Claude reads `CLAUDE.md` automatically and orients on your project. Tell it which item from `MD/todo.md` to start with. The session workflow ([How a Session Works](#how-a-session-works)) takes it from there.

### Using the HTML generator

The HTML generator at `~/18xx-docs/htmldoku/generate-html.py` converts your `.md` source files to rendered HTML pages. Run it after every documentation edit:

```bash
cd ~/18xx-docs
# 1. Edit htmldoku/somepage.md
python3 htmldoku/generate-html.py          # regenerates docs/18xx-Doku/*.html
git add htmldoku/somepage.md docs/18xx-Doku/somepage.html
git commit -m "docs: update somepage"
git push
```

The generator:
- Converts all `htmldoku/*.md` files to `docs/18xx-Doku/*.html`
- Rebuilds the sidebar navigation from the `SIDEBAR` list at the top of the script
- Rebuilds `search-index.json` for the in-page search

To add a new documentation page:
1. Create `htmldoku/mypage.md`
2. Add an entry to `SIDEBAR` in `generate-html.py`
3. Run the generator
4. Commit source `.md` **and** rendered `.html` together

---

## Physical Setup

```
~/
├── 18xx/                        ← project root (NOT a git repo)
│   ├── 18xx/                    ← main git repo  (branch: your feature branch)
│   ├── MD/   →  symlink         ← always points to ~/18xx-docs/MD/
│   └── CLAUDE.md  →  symlink    ← always points to ~/18xx-docs/MD/CLAUDE.md
└── 18xx-docs/                   ← git worktree, Documentation branch only
    ├── MD/                      ← session context files (CLAUDE.md, inwork.md, etc.)
    └── htmldoku/                ← this documentation (source .md files)
```

The symlinks are the key: `MD/` and `CLAUDE.md` are visible at the same path on every feature branch without switching branches or stashing. Documentation changes are committed separately from code, from the worktree directory.

### One-time setup

```bash
# Create the Documentation worktree
git -C ~/18xx/18xx worktree add ~/18xx-docs Documentation

# Expose MD/ and CLAUDE.md at the project root
ln -s ~/18xx-docs/MD           ~/18xx/MD
ln -s ~/18xx-docs/MD/CLAUDE.md ~/18xx/CLAUDE.md
```

### Committing docs vs code

```bash
# Code commits (from the main repo)
cd ~/18xx/18xx
git add lib/engine/game/g_18_oe/...
git commit -m "..."

# Documentation commits (from the worktree)
cd ~/18xx-docs
git add MD/ htmldoku/ docs/
git commit -m "..."
git push
```

---

## The Context Files

Context is loaded in three tiers to keep token cost per session low.

| Tier | File | When loaded | What it contains |
|------|------|-------------|-----------------|
| Always | `MD/CLAUDE.md` | Session start (auto) | Project identity, file locations, layer taxonomy, doc lookup table, coding rules |
| Always | `MD/inwork.md` | Session start | Items currently in flight — `[~]` in dev · `[t]` testing in progress · `[>]` needs PR |
| On demand | `MD/sparring.md` | Before first code task | Full sparring protocol and pre-code checklist |
| On demand | `MD/todo.md` | Planning sessions only | Full backlog — all `[ ]` items with layer annotations |
| On demand | `MD/bugs.md`, `MD/decisions.md`, etc. | When relevant | Bugs, architecture decisions, rules summary |
| Never | `MD/done.md` | — | Completed items for record-keeping only |

**`CLAUDE.md` is the file that makes sessions coherent.** It tells Claude what the project is, where every file lives, which layer a new task belongs to, and where to look for documentation — before the first prompt is typed. It is the symlink target for `~/18xx/CLAUDE.md`, so Claude Code loads it automatically on every session.

**`inwork.md` is the sprint board.** It contains only what is currently in flight. Each item carries a branch tag (backtick-wrapped name at the end of the line) so Claude always knows which branch to check out without asking:

```
- [~] **UP movement** — end-of-SR **[L2]** `18oe_testgame`
- [t] **Minor C** — OR-start prompt wired **[L3]** `18oe_abilities`
- [>] **Nationals formation** — all tests passed **[L2]** `18oe_testgame`
```

Use `?` when a branch hasn't been recorded yet. The item lifecycle follows a fixed pipeline:

```
[ ] todo.md  →  [~] developing  →  [t] testing  →  [>] needs PR  →  done.md
```

When you finish a task and merge the PR, move it to `done.md`. When you want to start something new, load `todo.md` and pick from the backlog.

---

## The Documentation-First Habit

Before writing any code, Claude reads the relevant `.md` source file from this documentation directly. The lookup table in `CLAUDE.md` maps every topic to the right file:

| You're about to implement… | Read first (source file) |
|---------------------------|--------------------------|
| A revenue bonus or route rule | `~/18xx-docs/htmldoku/revenue-routing.md` |
| An auction setup | `~/18xx-docs/htmldoku/auction-round.md` |
| A custom Step | `~/18xx-docs/htmldoku/round-step-system.md` |
| A new mechanic — which layer? | `~/18xx-docs/htmldoku/engine-concepts.md` |
| Something similar to an existing title | `~/18xx-docs/htmldoku/common-patterns.md` |

Reading `.md` source files instead of the generated HTML saves roughly 30–40% tokens per page. After reading the doc page, Claude greps the engine source for existing implementations before proposing new code.

---

## How a Session Works

**1. Orient** — Claude reads `CLAUDE.md` (auto) and `MD/inwork.md`, then presents in-work items grouped by readiness: `[t]` testing-in-progress first (resume immediately — re-run IRB, continue browser testing), then `[>]` needs-PR, then `[~]` in development. Quick wins highlighted. User selects one item before anything else happens.

**2. Branch** — each item in `MD/inwork.md` carries a branch tag (backtick-wrapped name at the end of the line). Claude reads this before touching git:

- **Named branch** → check it out directly, no new branch needed
- **`?`** → branch unknown; Claude asks before proceeding
- **No tag** → new item; Claude runs the divergence check and creates a branch

For new branches, Claude checks divergence against upstream and cross-references the **Outstanding Upstream PRs** table to recommend the base that keeps the branch as close to upstream as possible:

```bash
git fetch upstream && git fetch origin
git log --oneline upstream/master..origin/18oe_testgame | head -20
# → git checkout -b 18oe_featurename <recommended-base>
```

After creating a new branch, Claude immediately adds the branch tag to the item in `MD/inwork.md`.

**3. Discover** — Claude reads the relevant rules section from the rulebook and the matching `htmldoku/` documentation page, then greps the engine for existing implementations of the same mechanic.

**4. Consult until clear** — Claude and user work through every edge case, interaction, and ambiguity together. The phase ends with a **sign-off card** that must be confirmed before any code is written:

```
Rules cited:       §X.Y p.NN — <summary>
Edge cases:        <every one, explicitly named>
Interactions:      <which other features are affected and how>
Ambiguities:       <each one with its resolution and rule citation>
Layer:             L1 / L2 / L3
Comparator title:  <title read>
Test scenarios:    (see below)
Proceed? ✓ / ✗
```

The **test scenarios** are written as part of the sign-off and reused in step 6 — written once, not twice. Each gets a test method classification and, where applicable, an IRB setup snippet generated by Claude:

```
Scenario:     <game state prerequisite>
Action:       <what the player does>
Expect:       <exact outcome>
Test method:  IRB | Browser | Both
IRB setup:    <Ruby snippet — omitted for Browser-only scenarios>
```

Classification: **IRB** for pure logic (revenue, phase triggers, share movement, train rules); **Browser** for UI (tile rendering, route highlighting, step sequencing); **Both** for anything with both a logic assertion and a visual component. No coding until the user confirms the card.

**5. Implement** — one task per session. If an adjacent bug surfaces, log it in `MD/bugs.md` and finish the current task first.

**6. Test** — two phases, in order:

*6a — Automated (internal):* Claude runs every IRB snippet from the sign-off card autonomously via `docker compose exec rack irb`. The user sees nothing. Any failure triggers a silent fix-and-rerun cycle until all IRB tests pass. When 6a completes, the item is marked `[>]` if no browser testing remains, or `[t]` if browser scenarios are still pending.

*6b — Manual (browser), only after 6a is clean:* Claude presents only the `Browser` / `Both` scenarios:

> "All automated tests passed. N scenario(s) require browser verification:"

User performs each test and reports back per scenario:

- **"test XY passed"** → Claude commits `test(18oe): <scenario name> ✓`
- **Test fails** → fix code → re-run IRB → re-present browser scenario → commit when passing

When all browser scenarios pass the item is updated to `[>]`. If there are no Browser/Both scenarios, 6b is skipped entirely. No item moves to done until every scenario has a passing commit.

A session interrupted after 6a leaves the item as `[t]` in `inwork.md` — at the next session start Claude sees `[t]`, re-runs 6a to confirm still green, then resumes browser testing.

**7. Wrap up** — all test commits in place:
- Move item from `MD/inwork.md` to `MD/done.md`
- Update internal tracking: `MD/bugs.md` · `MD/decisions.md` as needed
- Ask: *"Does the documentation need updating?"* → edit `htmldoku/*.md`, run `generate-html.py`, commit both source and rendered HTML
- Commit all `~/18xx-docs/` changes separately from code commits

---

## The Sparring Partner Protocol

The full protocol lives in `MD/sparring.md` and is read at the start of any session that involves writing code. Key rules:

- **State the layer first.** Every task gets a layer classification (L1/L2/L3) with a reason before any code is discussed.
- **Name the comparator.** Before writing code, name and read the production title that handles the same mechanic.
- **Present one rejected alternative.** For every proposed approach, describe the alternative considered and why it was ruled out.
- **Cite the rules before coding.** If a mechanic is ambiguous, find the rule reference (`rules/18OE_Rulebook_v_1.0.txt`) before implementing.
- **Push back on style.** Magic numbers, duplicate expressions, lines over 130 characters — flag before the user has to.

This turns Claude from a code generator into a second reviewer who challenges assumptions at the design stage rather than after the code is written.

---

## Keeping Context Sharp

The biggest risk in a long-running project is context drift — Claude accumulating stale assumptions. The secondary risk is token bloat — always-loaded files growing as the project matures.

| Risk | Mitigation |
|------|-----------|
| Stale in-flight state | `MD/inwork.md` is the only always-loaded state file; it contains only active items |
| Wrong branch checked out | Branch tag on every item in `inwork.md` — Claude reads it before touching git |
| Resuming half-tested work | `[t]` status flags items where IRB passed but browser testing is incomplete |
| Backlog noise at session start | `MD/todo.md` is never auto-loaded; consulted only during planning |
| Re-litigating architecture decisions | `MD/decisions.md` records every non-obvious choice with the alternative rejected |
| Forgetting a rule fix | `MD/bugs.md` logs every bug with the rule citation and fix |
| Claude re-deriving engine patterns | `htmldoku/` pages are read before coding, not discovered mid-session |
| Drifting from upstream | Branch recommendation in step 2 checks upstream divergence + outstanding PRs |
| Documentation drifting from code | After-commit prompt: "does any MD/ or htmldoku/ page need updating?" |
| Token cost growing over time | Always-loaded files kept short; sparring protocol and backlog are on-demand |

---

## Reference

- Session context: `MD/CLAUDE.md`
- In-flight work: `MD/inwork.md`
- Backlog: `MD/todo.md`
- Sparring protocol: `MD/sparring.md`
- Completed features: `MD/done.md`
- Engine layer taxonomy: [Understanding the Engine](engine-concepts.html)
- Code patterns from PR review: [Coding Guidelines](coding-guidelines.html)
- Title readiness stages: [Title Checklist](title-checklist.html)

---
*Version: 2026-05-08 — branch tags on inwork items; [t] testing state; IRB-first test pipeline; item lifecycle pipeline.*
