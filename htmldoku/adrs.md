# Architecture Decision Records

This page documents the key architectural decisions that shaped 18xx.games. Each ADR explains the context, the decision taken, and its consequences.

---

## ADR-001 — Shared Ruby/Opal Engine

**Status:** Accepted

**Context:** The game engine must run both server-side (for authoritative state) and client-side (for immediate UI feedback). Maintaining two implementations in different languages is error-prone.

**Decision:** The engine is written in Ruby and transpiled to JavaScript by [Opal](https://opalrb.com/) [`Gemfile:9`]. The identical codebase runs in both environments. Each game title is compiled to its own JS bundle [`api.rb:70`].

**Consequences:**
- Single source of truth for rules logic.
- Client-side validation is always in sync with server-side validation.
- The engine must avoid Ruby features that Opal does not support (native C extensions, filesystem I/O).
- Build time increases with the number of game titles.

---

## ADR-002 — Action Replay Instead of Snapshots

**Status:** Accepted

**Context:** Game state could be persisted either as a full snapshot after every move or as an append-only action log that is replayed on load.

**Decision:** Only Actions (JSON) are stored. The full game state is reconstructed by replaying all Actions on every load [`lib/engine/game/base.rb:819-837`].

**Consequences:**
- The `actions` table schema never needs to migrate when game objects change.
- Any historical game state is reproducible by replaying a prefix of the action list.
- Load time grows linearly with the number of actions; acceptable for 18xx game lengths.
- A breaking engine change can invalidate old replays — the pinning mechanism mitigates this for running games [`lib/engine/game/base.rb:688-694`].

---

## ADR-003 — PostgreSQL Advisory Locks for Concurrency

**Status:** Accepted

**Context:** Two simultaneous requests for the same game could both replay the action list, produce diverging states, and both attempt to insert action N+1.

**Decision:** The API acquires a PostgreSQL Advisory Lock keyed on the game ID before loading any actions [`routes/game.rb:56`]. This serialises requests per game at the database level.

**Consequences:**
- No additional distributed lock service is needed.
- Lock acquisition is handled by the `sequel-pg_advisory_lock` gem [`Gemfile:17`].
- Concurrent requests for the *same* game queue behind the lock; throughput is limited to one action per game per round-trip.

---

## ADR-004 — Redis MessageBus for Real-Time Updates

**Status:** Accepted

**Context:** In live mode, all players need to see the board update after each action without polling.

**Decision:** After persisting each action, the API publishes the updated game state to Redis channel `/game/:id` using MessageBus [`lib/bus.rb:1`]. All browser clients receive the push via Server-Sent Events.

**Consequences:**
- Real-time updates without browser polling.
- Redis is a required infrastructure component.
- MessageBus backlog is capped (`max_backlog_size = 1`); only the latest state is relevant.

---

## ADR-005 — Game Pinning for Breaking Changes

**Status:** Accepted

**Context:** Fixing a rule bug sometimes requires changing engine behaviour in a way that would make existing games non-replayable with the new code.

**Decision:** When a breaking change is deployed, running games are *pinned* to an older JavaScript bundle [`lib/engine/game/base.rb:688-694`]. Pinned games continue uninterrupted but cannot be debugged, and Beta-title pins expire after 7 days.

**Consequences:**
- Players are never stranded mid-game by a developer fix.
- Old JS bundles must be retained until all pinned games finish.
- The system complexity includes bundle versioning and pin expiry logic.

---

## ADR-006 — Argon2 Password Hashing

**Status:** Accepted

**Context:** Passwords must be stored securely.

**Decision:** Passwords are hashed with Argon2 via the `argon2` gem [`Gemfile:3`]. Plain-text passwords are never stored or logged.

**Consequences:**
- Strong resistance to brute-force attacks.
- Argon2 parameters (memory, iterations) can be tuned in `routes/user.rb`.

---

## ADR-007 — Ordered Step List for Action Dispatch

**Status:** Accepted

**Context:** 18xx game titles have deeply varying action sequences. A single large dispatch method in `Game::Base` would become unmaintainable as the number of titles grew. A flat map from action type to handler would not express priority or the concept of a Step blocking others from acting.

**Decision:** Each Round holds an ordered list of `Step` objects [`lib/engine/round/base.rb:22`]. Every Step declares, via the `ACTIONS` constant, which action type strings it can process. When the Round receives an action, it iterates the Step list in order, calls `blocking?` on each Step, and delegates to the first blocking Step whose `ACTIONS` includes the incoming type. If no Step claims the action, a `GameError` is raised [`lib/engine/round/base.rb:75-95`].

Steps are composed per title by passing a custom array to the Round factory method (`new_operating_round`, `new_stock_round`). A title adds a mechanic by inserting a Step; it removes one by omitting it.

**Consequences:**
- Adding a new mechanic requires a new Step class and a single array entry — no changes to existing steps or the round.
- The order of Steps expresses priority implicitly: earlier Steps shadow later ones for the same action type.
- Steps contribute state to the Round via `round_state`, avoiding direct coupling between Step classes.
- The UI derives which buttons to enable by taking the union of all active Steps' `ACTIONS` lists — engine model and UI are in sync without a separate mapping layer.
- The `blocking?` vs `blocks?` distinction (whether a Step prevents others from acting vs whether it auto-skips for a given entity) adds complexity that requires care when writing new Steps.
- Inter-Step dependencies must be expressed through shared Round state rather than direct calls, which is less obvious than a sequential algorithm.

---

## What's next

- System topology: [Architecture Overview](architecture.html)
- How actions flow: [Core Flow](kernablauf.html)
- Round and Step design: [Round/Step System](round-step-system.html)

---
*Version: 2026-05-08 — derived from `lib/engine/game/base.rb`, `routes/game.rb`, `lib/bus.rb`, `api.rb`, `Gemfile`, `lib/engine/round/base.rb`.*
