# 18OE — In Work

Items currently in flight: `[~]` in development · `[t]` implemented, testing in progress · `[>]` all tests passed, needs PR.

Move items here from `MD/todo.md` at session start. Move to `MD/done.md` when complete + PR merged.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file
Branch tag: backtick-wrapped branch name at end of each item line; `?` = branch not yet recorded

Items without a milestone tag = **alpha**. `[BETA]` = deferred to beta milestone.

---

## Active Workarounds

**WA-1** *(BETA SCOPE)* — `national_revenue` linked/unlinked split unverified. To remove: confirm `Graph.new(home_as_token: true, no_blocking: true)` correctly identifies linked nodes in a test game. Not relevant until nationalization is implemented.

**WA-5** *(PERMANENT)* — Silent `skip!` in `ConvertToNational` when queue empty. Correct behaviour — do not remove. See `MD/decisions.md` ADR-005.

---

## Outstanding Fork PRs *(Witzman/18xx — staging for upstream)*

| Fork PR | Upstream PR | Title | Branch | Bugs |
|---------|-------------|-------|--------|------|
| #52 | tobymao#12601 | `[18OE] fix get_par_prices for regional companies` | `18oe_fix_par_prices` | par prices |
| #53 | tobymao#12602 | `[18OE] implement §4.4 three-way OR share price movement` | `18oe_fix_share_price_movement` | BUG-013/014 |
| #54 | tobymao#12603 | `[18OE] president pool purchase above 60% at 2× price` | `18oe_fix_president_overcap` | BUG-021 |
| #55 | tobymao#12604 | `[18OE] stock round fixes + zone-based terrain discount` | `18oe_fix_stock_terrain` | BUG-008/009/010/015/022 |
| #56 | tobymao#12605 | `[18OE] level-8 train gate + game-end timing` | `18oe_fix_level8_gameend` | BUG-018/024/025/027 |

**Note:** Ability stubs (`assign_krasnaya_strela!`, `event_d_token_phase_change!`, `assign_d_token!`, `cheap_upgrade?`, `pay_mail_contract!`, `d_corp_hex_bonus` + their constants) were stripped from #50 — they belong in `18oe_abilities` PR. Verify these are all present in `18oe_abilities` before submitting that PR upstream. `[TODO]`

---

## Branch Status *(updated 2026-05-14)*

| Branch | Base | Status | Contents |
|--------|------|--------|----------|
| `18oe_abilities` | upstream/master | rebased ✓ | Minor C/D/J/L + private abilities wiring |
| `18oe_gamefixes` | upstream/master | closed (split) | superseded by PRs #47–51 |
| `18oe_mergers` | upstream/master | rebased ✓ | Minor SR merger · national formation · SR fixes |
| `18oe_testing` | upstream/master | rebased ✓ | Integration: gamefixes + abilities + mergers |
| `18oe_fix_par_prices` | upstream/master | fork #52 / upstream #12601 open | par price fix |
| `18oe_fix_share_price_movement` | upstream/master | fork #53 / upstream #12602 open | BUG-013/014 |
| `18oe_fix_president_overcap` | upstream/master | fork #54 / upstream #12603 open | BUG-021 |
| `18oe_fix_stock_terrain` | upstream/master | fork #55 / upstream #12604 open | BUG-008/009/010/015/022 |
| `18oe_fix_level8_gameend` | upstream/master | fork #56 / upstream #12605 open | BUG-018/024/025/027 |
