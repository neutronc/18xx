# 1862 Golden Spike — Bug Log

Curated list of known defects and their fixes. Entries are immutable IDs (`BUG-NNN`);
status changes over time but the ID and original description do not.

**Status values:** `OPEN` (unfixed), `FIXED` (with commit hash + date), `WONTFIX` (with reason), `INVESTIGATING` (under triage).
**Severity:** HIGH (blocks correct gameplay), MEDIUM (rule violation in edge case), LOW (cosmetic or low-impact).

When you fix a bug, change `Status:` to `FIXED <date> <commit>` and move the entry to the **Resolved** section.
Do not delete entries — the history is the value.

---

## Summary

```
Open: 0   Fixed: 12   Won't fix: 0   Total: 12
```

---

## Open

### BUG-012 — Buying a share does not end the player's SR turn

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-17
- **Severity:** HIGH — rule violation; players can continue acting after buying a share

**Symptom.** After a player buys a share in the stock round, their turn did not
immediately pass to the next player. DONE button remained visible.

**Root cause.** `SELL_BUY_ORDER = :sell_buy_sell` in game.rb allows selling after
buying. The engine does not auto-pass when no actions remain; DONE must be clicked.

**Fix.** Changed `SELL_BUY_ORDER` to `:sell_buy`. Added explicit `pass!` calls at the
end of `process_buy_shares` and `process_par` overrides in `step/buy_sell_par_shares.rb`
so the turn advances immediately after either action, with no DONE button required.

---

## Resolved

### BUG-011 — Private companies sellable to corporations via BuyCompany step

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-16
- **Severity:** HIGH — rule violation; all privates are unsellable; close only on named triggers

**Symptom.** Corporations could buy private companies from players during the OR.
Per the rules, no private may ever be sold to a corporation; they close only on their
individual triggers (float, dividend, tile placement, or end of game).

**Root cause.** `Engine::Step::BuyCompany` appeared twice in the `operating_round` step
list — once non-blocking (start of turn) and once blocking (end of turn).

**Fix.** Removed both `Engine::Step::BuyCompany` entries from `operating_round`.
The stock round step list was already correct (no `BuyCompany`).

---

### BUG-010 — Capitalization set to :incremental; should be 100% (:full)

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-16
- **Severity:** HIGH — corporations receive wrong cash on float; all financial calculations incorrect

**Symptom.** Corporations drip in cash as shares are sold from the IPO pool. Per the
company sheet, capitalization should be 100%: the corporation receives the full par price
multiplied by all shares immediately when it floats.

**Root cause.** `CAPITALIZATION = :incremental` in game.rb.

**Fix.** Changed to `CAPITALIZATION = :full`. Removed `after_par` override entirely —
under `:full`, `float_corporation` pays `par_price × total_shares` from the bank
automatically, and the base `after_par` correctly handles `close_companies_on_event!`.
The SOC multi-corp-share workaround was only needed under `:incremental`.

---

## Resolved

### BUG-009 — Token placement costs wrong: should be $40 / $80 / $120 progression

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-16
- **Severity:** HIGH — rule violation; corporations overpay for later tokens

**Symptom.** Token costs in entities.rb did not follow the $40 / $80 / $120 progression.
Definitions used $40 / $100 / $100 for Group 1 and $40 / $100 for Groups 2–3.

**Fix.** Updated `tokens:` arrays in entities.rb:
- 4-token corps (NYH, NYC, CP): `[0, 40, 80, 120]`
- 3-token corps (CPR, UP, ATS, SP): `[0, 40, 80]`
- 2-token corps (NP, CN, TP, ORN, WP, GMO): `[0, 40]` (unchanged)

---

### BUG-008 — Route revenue display shows raw city stops only; bonuses invisible until submit

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-16
- **Severity:** HIGH — player sees wrong revenue on map ($40) then different value on submit ($100)

**Symptom.** When CPR runs a 3-train Sacramento → Salt Lake City → Omaha, the route
display shows $40 (raw city stops). The dividend submit step shows $100.

**Root cause.** Game-level bonuses were added in `routes_revenue` only; `revenue_for`
(called per-route for the map display) had no bonus logic.

**Fix.** Overrode `revenue_for(route, stops)` in game.rb to compute SLC and corp bonuses
per route. Removed bonus additions from `routes_revenue` (now just `super`). Both the route
display and the dividend total now agree.

---

### BUG-007 — Sacramento (G3) preprinted yellow tile missing correct revenue

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-16
- **Severity:** HIGH — incorrect revenue shown on preprinted tile; affects CPR and WP income from turn 1

**Symptom.** The preprinted yellow tile on hex G3 (Sacramento) showed $0 revenue for both cities.

**Root cause.** Both city entries in the G3 HEXES definition had `revenue:0`.

**Fix.** Changed to `revenue:20` for both cities in map.rb.

---

### BUG-006 — TOR private: tile-lay ability inaccessible to owning player's corporation

- **Date:** 2026-05-16
- **Status:** FIXED 2026-05-16
- **Severity:** HIGH — rule violation; the Toronto gray tile could never be placed

**Symptom.** When the owner of TOR operated their corporation, no tile-lay button appeared.

**Root cause.** TOR's `tile_lay` ability had `owner_type: 'corporation'`, requiring the
corporation itself to own TOR. Since TOR stays with the player, `ability_right_owner?`
always failed.

**Fix.** In entities.rb: changed `owner_type: 'corporation'` → `owner_type: 'player'`
and `when: 'any'` → `when: 'owning_player_or_turn'`.

---

### BUG-005 — Private companies closed on 3/3E train purchase

- **Date:** 2026-05-15
- **Status:** FIXED 2026-05-15 (pending commit)
- **Severity:** HIGH — rule violation; privates closed at wrong time, cert slot freed incorrectly

**Symptom.** Buying a 3-train or its 3E variant triggered the `close_companies` engine event,
closing all private companies immediately.

**Root cause.** The 3-train entry in TRAINS included `events: [{ 'type' => 'close_companies' }]`,
which is the standard 18xx engine hook. In 1862 Golden Spike, privates have individual,
named close triggers (SOC on CPR/UP float; NHSC on NYH float; PSC on WP first dividend;
FNY on NYC first dividend; TOR after use) and are never closed by a train purchase event.
Privates not triggered by end of game are worthless but remain as certificate-count liabilities.

**Fix.** Removed the `events:` key from the 3-train entry in TRAINS. All private close
logic remains handled by the individual trigger callbacks in game.rb and entities.rb.

---

### BUG-004 — E-trains not offered as alternatives; unlimited separate pool

- **Date:** 2026-05-15
- **Status:** FIXED 2026-05-15 (pending commit)
- **Severity:** HIGH — E-trains never appeared as purchase option; pool not shared with base

**Symptom.** E-trains (2E, 3E, …) were never shown in the buy-train UI as alternatives
to the base train. In addition, the 2E had `num: 99` making it a separate unlimited pool;
3E–7E had `available_on:` gating that delayed their appearance.

**Root cause.** Each E-train was defined as a separate entry in TRAINS rather than as a
`variants:` entry on its base train. The engine only shows variant choices when purchasing
a given train slot; standalone entries are presented as independent train types, and the
2E (no `available_on`) appeared as such but was never surfaced in practice.

**Fix.** Removed all standalone E-train rows. Added each E-train as a `variants:` entry
on its base train. The shared `num:` on the base entry now correctly limits the combined
pool. Buying either variant decrements the same counter; `train.sym` stays as the base
name so phase advances and rust triggers fire on either purchase.

---

### BUG-003 — Corp logo SVGs missing, tokens invisible on map

- **Date:** 2026-05-15
- **Status:** FIXED 2026-05-15 (pending commit)
- **Severity:** HIGH — tokens invisible in browser

**Symptom.** Home tokens placed but not rendered on the map or in the market.

**Root cause.** Directory `public/logos/1862_usa_canada/` did not exist; all 13 corporation
`logo:` and `simple_logo:` references resolved to missing files.

**Fix.** Created `public/logos/1862_usa_canada/` with 26 placeholder SVG files (main +
`.alt`) for all 13 corporations using corp color and abbreviation. Final artwork is
tracked as open FIXME #7 in game.rb.

---

### BUG-002 — Token placement prompt appears before track in OR

- **Date:** 2026-05-15
- **Status:** FIXED 2026-05-15 (pending commit)
- **Severity:** HIGH — wrong OR action order, confuses players

**Symptom.** Corp prompted to place a station token at OR turn start, before track laying.

**Root cause.** `G1862UsaCanada::Step::Token` appeared **twice** in the `operating_round`
step stack: once before `Engine::Step::Track` (wrong position, becomes active first) and
once after as `Engine::Step::Token` (missing the GHU discount override). The early
occurrence blocked track laying by presenting token placement first.

**Fix.** Removed the early duplicate; replaced the late `Engine::Step::Token` with
`G1862UsaCanada::Step::Token`. Step order is now: Track → Token → Route.

---

### BUG-001 — NYH home token missing in first OR, blocks track laying

- **Date:** 2026-05-15
- **Status:** FIXED 2026-05-15 (pending commit)
- **Severity:** HIGH — blocks initial operating round entirely

**Symptom.** NYH (and potentially NYC/CP) could not lay track in the first OR.

**Root cause.** With `HOME_TOKEN_TIMING = :operate` (engine default), each corp's home
token is placed at the start of its own OR turn via `place_home_token`. That method calls
`city.place_token` directly — bypassing the step layer — so `clear_graph_for_entity` is
never called. The graph cache therefore has no tokens when connectivity is first queried,
showing zero connected hexes and blocking all tile lays.

**Fix (revised 2026-05-16).** Kept `HOME_TOKEN_TIMING = :operate` (correct per rules:
token is placed automatically at the start of the corp's first OR turn). Added
`place_home_token` override in game.rb that calls `super` then
`clear_graph_for_entity(corporation)`, ensuring the graph cache is cleared immediately
after the token is placed and before any step queries connectivity.

---

## Conventions

- **One ID per defect, ever.** If a bug recurs after being fixed, open a new entry linking back: `Status: REOPENED — superseded by BUG-NNN`.
- **Rule citations are mandatory** for HIGH/MEDIUM bugs.
- **Fix sections must include the diff direction**, not just the new code.
