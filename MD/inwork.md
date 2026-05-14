# 18OE — In Work

Items currently in flight: `[~]` in development · `[t]` implemented, testing in progress · `[>]` all tests passed, needs PR.

Move items here from `MD/todo.md` at session start. Move to `MD/done.md` when complete + PR merged.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file
Branch tag: backtick-wrapped branch name at end of each item line; `?` = branch not yet recorded

Items without a milestone tag = **alpha**. `[BETA]` = deferred to beta milestone.

---

## Stock Round

- [>] **Minor SR merge action** `[BETA]` — `can_merge_minors?` / `minor_by_id` / `mergeable_entity/entities` / `process_merge` / `merge_minor!` / `transfer_minor_track_rights!` implemented **[L2/L3]** `18oe_mergers`

## Minor Abilities

- [~] **C** (Golden Bell) — `choose_ability`/`@golden_bell_position`/`operating_order` wired; **still needed**: OR-start choice-prompt step **[L3]** `18oe_abilities`
- [~] **D** (Green Junction) — `hex_bonus`/`event_d_token_phase_change!`/`assign_d_token!` wired; **still needed**: unreachable-city placement step (land cities only; sea/ferry variant → beta todo) **[L3]** `18oe_abilities`
- [>] **J** (Grey Locomotive Works) — `train_discount` (0.1) wired; removed `owner_type`/TODO; ability-transfer to major → beta **[L1]** `18oe_abilities`
- [~] **L** (Krasnaya Strela) — `assign_krasnaya_strela!`/`restore_krasnaya_strela!` wired; **still needed**: train-choice step + D-train exception **[L3]** `18oe_abilities`

## Private Abilities

- [~] **Central Circle** — `token` (extra_slot, special_only) wired; **still needed**: town revenue scoring (£10/£20/£40/£60 by phase), SR window **[L3]** `18oe_abilities`
- [~] **Hochberg Mining** — `assign_hexes` wired; **still needed**: routing exclusion + placement eligibility (cost ≥ £45) **[L3]** `18oe_abilities`
- [~] **Brandt & Brandau** — `tile_lay` (free, count: 4) wired; **still needed**: per-OR cap (max 2/OR) **[L3]** `18oe_abilities`

---

## Beta

### Train Purchase

- [>] **Nationals claim rusted trains** `[BETA]` — `spend_minmax [0,0]`, fast-path in `process_buy_train`, `trigger_nationals_formation!` implemented **[L2/L3]** `18oe_mergers`

### Private Abilities

- [~] **Wien Südbahnhof** `[BETA]` — `token` (price: 0, teleport_price: 0, extra_action: true) wired; **still needed**: Token step zone-bypass for free placement anywhere + sea-zone crossing costs **[L2→L3]** `18oe_abilities`
- [~] **Star Harbor** `[BETA]` — `token` (extra_slot, special_only) wired; **still needed**: port routing, revenue exclusion, SR window **[L3]** `18oe_abilities`
- [~] **White Cliffs Ferry** `[BETA]` — `token` (hexes: ['N31']) wired; **still needed**: Phase 5 start event hook + ferry routing **[L3]** `18oe_abilities`

---

## Active Workarounds

**WA-1** *(BETA SCOPE)* — `national_revenue` linked/unlinked split unverified. To remove: confirm `Graph.new(home_as_token: true, no_blocking: true)` correctly identifies linked nodes in a test game. Not relevant until nationalization is implemented.

**WA-5** *(PERMANENT)* — Silent `skip!` in `ConvertToNational` when queue empty. Correct behaviour — do not remove. See `MD/decisions.md` ADR-005.

---

## Outstanding Fork PRs *(Witzman/18xx — staging for upstream)*

| PR | Title | Branch | Bugs |
|----|-------|--------|------|
| #47 | `[18OE] fix get_par_prices for regional companies` | `18oe_fix_par_prices` | par prices |
| #48 | `[18OE] implement §4.4 three-way OR share price movement` | `18oe_fix_share_price_movement` | BUG-013/014 |
| #49 | `[18OE] president pool purchase above 60% at 2× price` | `18oe_fix_president_overcap` | BUG-021 |
| #50 | `[18OE] stock round fixes + zone-based terrain discount` | `18oe_fix_stock_terrain` | BUG-008/009/010/015/022 |
| #51 | `[18OE] level-8 train gate + game-end timing` | `18oe_fix_level8_gameend` | BUG-018/024/025/027 |

**Note:** Ability stubs (`assign_krasnaya_strela!`, `event_d_token_phase_change!`, `assign_d_token!`, `cheap_upgrade?`, `pay_mail_contract!`, `d_corp_hex_bonus` + their constants) were stripped from #50 — they belong in `18oe_abilities` PR. Verify these are all present in `18oe_abilities` before submitting that PR upstream. `[TODO]`

---

## Branch Status *(updated 2026-05-14)*

| Branch | Base | Status | Contents |
|--------|------|--------|----------|
| `18oe_abilities` | upstream/master | rebased ✓ | Minor C/D/J/L + private abilities wiring |
| `18oe_gamefixes` | upstream/master | closed (split) | superseded by PRs #47–51 |
| `18oe_mergers` | upstream/master | rebased ✓ | Minor SR merger · national formation · SR fixes |
| `18oe_testing` | upstream/master | rebased ✓ | Integration: gamefixes + abilities + mergers |
| `18oe_fix_par_prices` | upstream/master | PR #47 open | par price fix |
| `18oe_fix_share_price_movement` | upstream/master | PR #48 open | BUG-013/014 |
| `18oe_fix_president_overcap` | upstream/master | PR #49 open | BUG-021 |
| `18oe_fix_stock_terrain` | upstream/master | PR #50 open | BUG-008/009/010/015/022 |
| `18oe_fix_level8_gameend` | upstream/master | PR #51 open | BUG-018/024/025/027 |
