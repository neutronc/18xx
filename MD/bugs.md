# 18OE — Bug Log

Curated list of known defects and their fixes. Entries are immutable IDs (`BUG-NNN`);
status changes over time but the ID and original description do not.

**Status values:** `OPEN` (unfixed), `FIXED` (with commit hash + date), `WONTFIX`
(with reason), `INVESTIGATING` (under triage).

**Severity:** HIGH (blocks correct gameplay), MEDIUM (rule violation in edge case or
narrow window), LOW (cosmetic or low-impact).

When you fix a bug, change `Status:` to `FIXED <date> <commit>` and move the entry
to the **Resolved** section. Do not delete entries — the history is the value.

---

## Summary

```
Open (alpha): 0   Open (beta): 6   Fixed: 17   Won't fix: 2   Total: 25
Bugs closed  ██████████████████░░  19 / 25  (76%)
Alpha bugs   ████████████████████  0 open alpha bugs  ✅
```

---

## Open

> All remaining open bugs are **beta scope** — none block the alpha milestone.

### BUG-026 — Final two ORs (abbreviated second OR) not implemented

- **Status:** OPEN
- **Severity:** HIGH (beta scope — level-8 trigger now in place via BUG-025; abbreviated OR logic deferred)
- **File:** `lib/engine/game/g_18_oe/round/operating.rb` (new FinalOperating round)
- **Rule:** §13 — Second final OR: each RR pays the same revenue as first final OR; no track/token/train. If a train was acquired in Final OR 1, that RR may recalculate.

**Symptom.** Both final ORs run as normal ORs. Second OR is not abbreviated.

**Additional edge case.** When level-8 is purchased in OR 2 of a set, rule requires 3 more ORs but `:one_more_full_or_set` yields 2 (off by 1 — also deferred to this bug).

**Fix needed.** Custom `FinalOperating` round that skips track/token/train steps and replays stored revenue. Must also handle the OR-2 trigger case (extend final set to 3 ORs).

---

### BUG-023 — §11.7 abandoned-minor purchase by major in OR not implemented

- **Status:** OPEN
- **Severity:** MEDIUM (beta scope — deferred until minor abandonment and Open Market are implemented)
- **File:** `lib/engine/step/issue_shares.rb` (needs 18OE override)
- **Rule:** §11.7 — *"In addition to buying or selling shares, the major may also purchase one abandoned minor from the Open Market (see 9.5). The price of £60 is paid directly to the bank."*

**Symptom.** The `IssueShares` OR step has no mechanism for purchasing an abandoned minor. The action is entirely absent.

**Fix needed.** Override `IssueShares` in 18OE to add a `buy_company` action when abandoned minors are in the Open Market, charge £60 to bank, and trigger the merger path (§10.5) without conferring a share.

---

### BUG-020 — Orient Express first-run bonus (§12.2) not implemented

- **Status:** OPEN
- **Severity:** HIGH (beta scope — OE routing is a beta feature)
- **File:** `lib/engine/game/g_18_oe/step/dividend.rb`, `lib/engine/game/g_18_oe/game.rb`
- **Rule:** §12.2 — First time a major runs the OE, president chooses: (a) move RIGHT × 3 and treasury receives total OE train revenue, or (b) keep normal dividend + extra revenue by phase (£30/£60/£100). OE run must include land track, not only sea.

**Symptom.** No OE marker is awarded, no bonus revenue is calculated, no first-run choice is presented. The OE route runs as a normal train.

**Root cause.** No implementation exists. Requires: OE-route detection (train passes through the OE tile chain), per-major first-run marker, choice prompt, and the two bonus paths.

**Fix needed.** Layer 2/3: track OE first-run per major, detect when a route uses OE tiles, extend dividend step to offer the choice, implement both bonus paths including the RIGHT×3 stock market movement.

---

### BUG-019 — Force-buy mechanics not implemented (president cash contribution + national conversion)

- **Status:** OPEN
- **Severity:** HIGH (beta scope — requires president cash contribution + insolvency path; deferred until base force-buy flow is verified reachable in alpha testing)
- **File:** `lib/engine/game/g_18_oe/step/buy_train.rb`
- **Rule:** §11.6.4 — When a major force-buys, president pays the difference between treasury and train cost. §11.6.5 — When a minor/regional force-buys and president can't pay, president surrenders all cash, cert goes to Open Market at face value, RR is insolvent.

**Symptom.** `must_buy_train?` correctly forces the buy but the engine has no mechanism to draw on the president's personal cash when the treasury is short. A major or minor with an empty treasury and a forced buy obligation will be unable to complete its turn correctly.

**Root cause.** No `emergency_issuable_bundles` or president-contribution flow in 18OE's `BuyTrain` step. The base engine's forced-buy path (if any) is not customised for 18OE's president-pays and national-conversion rules.

**Fix needed.** Implement `emergency_issuable_bundles` / president cash contribution for majors; implement first-round insolvency path (cash transfer, cert to market, RR suspended) for minors/regionals.

---

### BUG-011 — Nationals not exempt from terrain costs

- **Status:** OPEN
- **Severity:** HIGH (beta scope — not reachable until nationalization is implemented)
- **File:** `lib/engine/game/g_18_oe/game.rb` (`upgrade_cost`), `lib/engine/game/g_18_oe/step/track.rb`
- **Rule:** §11.1.5 — *"Nationals are exempt from all tile placement expenses; they may always lay track at no cost."*

**Symptom.** A national operating in a rough-terrain hex would pay the full terrain cost; no exemption exists in `upgrade_cost` or `Track#lay_tile_action`.

**Root cause.** `upgrade_cost` in 18OE only short-circuits for entities with a `tile_discount` terrain ability. Nationals have none, so they fall through to `super` which charges the full terrain cost.

**Fix needed.** Add `return 0 if entity.type == :national` (or check `spender`) at the top of `upgrade_cost` in game.rb. Also verify `tile_cost_with_discount` for any non-terrain costs.

---

### BUG-012 — `close_corporation` skips parred-but-not-floated regionals at phase end

- **Status:** OPEN
- **Severity:** MEDIUM (beta scope — only reachable once Concession Phase is implemented, ADR-004)
- **File:** `lib/engine/game/g_18_oe/step/buy_sell_par_shares.rb` (`process_par`)
- **Rule:** §8.2 — *"The six remaining un-floated regionals are removed from play when the 18th regional is floated."* Un-floated includes parred-but-not-floated.

**Symptom.** When the 18th regional is floated, the cleanup loop skips any regional whose `ipoed` flag is `true`. A regional that was parred during the Concession Phase (president's share placed in the Open Market) has `ipoed = true` but is not floated. It would survive the cleanup and remain in play incorrectly.

**Root cause.** The filter `next if corp.ipoed` conflates "parred" with "floated". `ipoed` is set to `true` the moment the president's share is purchased (`share_pool.rb:53`), which happens at par time — before the regional is floated.

**Fix needed.** Replace `corp.ipoed` with `corp.floated?` (or an equivalent check on `corp.share_price && corp.president`) so the filter correctly identifies floated corps regardless of par state. Verify that `close_corporation` for a parred-only regional correctly returns its president's share to the Open Market or removes it.

---

---

## Resolved

### — Fixed 2026-05-14 —

### BUG-025 — Level-8 train purchase end trigger not implemented

- **Status:** FIXED 2026-05-14 `d9a71f932` (testing) / `0e236a65c` (gamefixes)
- **Severity:** HIGH
- **Rule:** §13 — first 8+8 purchase triggers game end + remainder cash injection.

**Fix landed.** Added `events: [{ 'type' => 'level8_train_purchased' }]` to the 8+8 train. `event_level8_train_purchased!` is idempotent, injects `REMAINDER_CASH = 100_000` (20×£5,000) into bank cash directly, sets `@level8_train_purchased`. `game_end_check_final_phase?` returns that flag, wiring `final_phase: :one_more_full_or_set` end timing.

---

### BUG-024 — Bank `full_or` timing wrong; remainder cash not implemented

- **Status:** FIXED 2026-05-14 `d9a71f932` (testing) / `0e236a65c` (gamefixes)
- **Severity:** HIGH
- **Rule:** §13 — bank-break: finish current OR only (mid-OR) or one more OR (mid-SR).

**Fix landed.** Changed `GAME_END_CHECK` bank timing from `:full_or` to `:current_or`. Engine's `:current_or` correctly handles both mid-OR and mid-SR bank-break cases. Remainder cash (`REMAINDER_CASH = 100_000`) injected at level-8 event (BUG-025, same commit). Priority ordering ensures `:current_or` beats `:one_more_full_or_set` when both fire simultaneously.

---

### BUG-021 — Above-60% president pool purchase at 2× price not implemented

- **Status:** FIXED 2026-05-14 `737db0a94` (testing) / `113b54bea` (gamefixes)
- **Severity:** MEDIUM
- **File:** `lib/engine/game/g_18_oe/step/buy_sell_par_shares.rb`
- **Rule:** §10.2 — *"The president of a major or national may purchase shares of that RR from the Open Market (not from the treasury!), paying the bank double the current share value per share."*

**Fix landed.** Added `president_pool_overcap_buy?` helper (bundle from pool + major/national type + is president + holds ≥60%). `can_buy?` short-circuits before `super` when this is true, bypassing `holding_ok?` while still enforcing `bought?`, 2× cash, and cert limit. `process_buy_shares` passes `exchange_price: bundle.price * 2` to charge the correct amount.

---

### BUG-018 — Level-8 trains available before 4th level-7 is purchased

- **Status:** FIXED 2026-05-14 `672197d3f` (testing) / `a0a00b4e2` (gamefixes)
- **Severity:** MEDIUM
- **File:** `lib/engine/game/g_18_oe/step/buy_train.rb`
- **Rule:** §11.6 — *"Level 8 trains may be purchased after the fourth level 7 train is purchased."*

**Fix landed.** Override `buyable_trains` in `G18OE::Step::BuyTrain`: injects the first `8+8` train from `depot.upcoming` into the buyable list once `level8_train_available?` returns true (≥4 level-7 trains sold). Defensively rejects `8+8` when gate is closed. Counts sold level-7s as `(total 7+7+4D in depot.trains) − (7+7 still in depot.upcoming)`, correctly handling the `4D` variant rename on purchase. Predicate lives in `game.rb` as `level8_train_available?` per Guideline 17.

---

### BUG-008 — Zone-based 20% terrain discount (SP / IT / SC / RU) not implemented

- **Status:** FIXED 2026-05-14 `996c6685e` (testing) / `2d57d1446` (gamefixes)
- **Severity:** HIGH
- **Rule:** §11.1.5 — entities with track rights in SP/IT/SC/RU get 20% discount in those zones.

**Fix landed.** Rewrote `upgrade_cost`: compares `entity_track_rights_zone` against `region_for_hex(hex)`; if zone matches and is in `ZONE_DISCOUNT_ZONES`, applies 20% (`cost = (base_cost * Rational(4,5)).floor`). E/F detection augments to 50% when terrain matches. Removed `TERRAIN_DISCOUNT_RATE`. See BUG-009, BUG-010.

---

### BUG-009 — Minor E/F terrain discount: wrong rate and wrong activation condition

- **Status:** FIXED 2026-05-14 `996c6685e` (testing) / `2d57d1446` (gamefixes)
- **Severity:** MEDIUM
- **Rule:** §11.1.5 — E/F augments zone discount to 50%; gives no standalone discount.

**Fix landed.** E/F `tile_discount` abilities retained in entities.rb (with `discount: 0` to suppress base-engine application). `upgrade_cost` checks for E/F via `terrain_discount_ability` only after confirming zone match; applies 50% rate when ability terrain matches hex tile. Standalone E/F (no zone match) falls through to `super` → no discount.

---

### BUG-010 — Terrain cost discount rounding favours bank, not RR

- **Status:** FIXED 2026-05-14 `996c6685e` (testing) / `2d57d1446` (gamefixes)
- **Severity:** LOW
- **Rule:** §11.1.5 — round fractions in favour of RR; cost rounds DOWN.

**Fix landed.** Changed formula from `base_cost - (base_cost * rate).floor` (cost rounds up) to `(base_cost * (1 - rate)).floor` (cost rounds down). Example: £45 at 50% → 22 ✓.

---

### BUG-022 — §11.7 share issuance by major does not move stock price DOWN

- **Status:** FIXED 2026-05-14 `ccc92c665` (testing) / `1079d58e2` (gamefixes)
- **Severity:** HIGH
- **Rule:** §11.7 / §10.1 — issue is subject to selling rules; DOWN per share.

**Fix landed.** Created `G18OE::Step::IssueShares` overriding `process_sell_shares` to call `@game.sell_shares_and_change_price(bundle)` instead of `@game.share_pool.sell_shares(bundle)`. Routes through the standard sell path which applies `SELL_MOVEMENT = :down_share`. Wired in place of `Engine::Step::IssueShares` in `operating_round`.

---

### BUG-015 — Sold-out UP movement at SR end uses alphabetical order, not share-price order

- **Status:** FIXED 2026-05-14 `b78a4baa6` (testing) / `570311b81` (gamefixes)
- **Severity:** LOW
- **Rule:** §4.4 — markers moved highest to lowest share value.

**Fix landed.** Created `G18OE::Round::Stock` with `finish_round` override replacing `.sort` with `.sort_by { |c| -c.share_price.price }`. Wired into `game.rb#stock_round`. The sort must live in `finish_round` because `corporations_to_move_price.sort` in the base round would re-sort any pre-sorted array alphabetically.

---

### BUG-027 — `bankrupt: :immediate` end trigger does not apply to 18OE

- **Status:** FIXED 2026-05-14 `b2e020610` (testing) / `fa366bdd9` (gamefixes)
- **Severity:** MEDIUM
- **File:** `lib/engine/game/g_18_oe/game.rb`
- **Rule:** §11.6.4, §11.6.5 — no player-bankruptcy game-end in 18OE.

**Fix landed.** Added `GAME_END_CHECK = { bank: :full_or }.freeze` to drop `bankrupt: :immediate` from the inherited base-engine check. Bank-break timing (`bank: :full_or`) is a separate concern addressed by BUG-024.

---

### BUG-013 — OR share price movement ignores share-price threshold

- **Status:** FIXED 2026-05-14 `efd0c50a4` (testing) / `e09ca23b6` (gamefixes)
- **Severity:** HIGH
- **File:** `lib/engine/game/g_18_oe/step/dividend.rb` (`share_price_change`)
- **Rule:** §4.4 — *"A major's or national's marker moves RIGHT if … dividend equal to or greater than its share value … does not move if … less than its share value but greater than zero … moves LEFT if … zero."*

**Symptom.** Any positive dividend moved a major or national RIGHT regardless of threshold. A major at £150 paying £100 incorrectly moved RIGHT instead of staying put.

**Root cause.** `share_price_change` called `super` for majors/nationals; base engine returns `:right` for any `revenue.positive?` with no share-price comparison.

**Fix landed.** Override `share_price_change` in `G18OE::Step::Dividend` with the three-way rule: LEFT if zero, no move if below price, RIGHT if at or above price. Dead `game.rb#change_share_price` removed (BUG-014).

---

### BUG-014 — `game.rb#change_share_price` is dead code and should be removed

- **Status:** FIXED 2026-05-14 `efd0c50a4` (testing) / `e09ca23b6` (gamefixes)
- **Severity:** LOW
- **File:** `lib/engine/game/g_18_oe/game.rb` (`change_share_price`)

**Symptom.** Method contained correct three-way OR movement logic but was never called. OR movement is driven by `Step::Dividend#share_price_change` returning a direction hash, not by an imperative game-level method.

**Fix landed.** Method removed as part of BUG-013 fix. Correct logic now lives in the step override.

---

### — Fixed before 2026-05-14 —

### BUG-007 — `can_sell?` allows secondary regional share sales (rule violation)

- **Status:** FIXED 2026-05-05 `645a87b20` (testgame) / `70d3fde6c` (fullmap)
- **Severity:** HIGH
- **File:** `lib/engine/game/g_18_oe/step/buy_sell_par_shares.rb` (`can_sell?`)
- **Rule:** §10.1 — *"A player may never sell a share of a regional."*

**Symptom.** On `18oe_testgame` and `18oe_fullmap`, `can_sell?` only blocked the president's certificate of a regional (`bundle.presidents_share`). Secondary (25%) regional shares could be sold, violating §10.1.

**Root cause.** Guard was narrowed during BUG-004 investigation on the mistaken assumption that secondary regional shares are sellable in Major Phase. §10.1 is unconditional.

**Fix landed.** Reverted to `return false if bundle.corporation.type == :regional` — blocks all regional cert sales regardless of phase or cert type.

---

### BUG-001 — `can_buy?` blocks non-presidents from secondary shares in Major Phase

- **Status:** FIXED 2026-04-26 `6ade8434d` (testgame) / `6162d3717` (fullmap)
- **Severity:** HIGH
- **File:** `lib/engine/game/g_18_oe/step/buy_sell_par_shares.rb:60–72`
- **Rule:** §8.3 — *"Secondary shares of regionals are available [in the Major RR Phase]."* No president-only restriction.

**Symptom.** When no conversion is in progress (normal Major Phase) and a non-president player tries to buy a secondary share of a regional from its IPO, `can_buy?` returns `false`. Only the president can buy, contradicting §8.3.

**Root cause.** The guard intended to enforce §9.3 step 1 (president-only, one share before converting) was too broad — fired in normal Major Phase too.

**Fix landed.** Replaced single `@converted` state with a two-variable state machine (`@converting` = conversion triggered but not complete; `@converted` = conversion complete). The president-only guard now lives inside `if @converting` so it only fires in the pre-conversion window, not in normal play.

---

### BUG-002 — `@bought` ivar removed but still referenced; double-buy not blocked

- **Status:** FIXED 2026-04-26 `6ade8434d` (testgame) / `6162d3717` (fullmap)
- **Severity:** HIGH
- **File:** `lib/engine/game/g_18_oe/step/buy_sell_par_shares.rb:68`
- **Rule:** §9.3 step 1 — *"the player may purchase ONE share prior to step 2."*

**Symptom.** During pre-conversion, a president could buy multiple treasury shares before triggering conversion, violating the one-share rule.

**Root cause.** `@bought` was nil after a refactor; the one-share cap guard always evaluated `nil == corp` → `false`.

**Fix landed.** Replaced `@bought` with `bought_corporation` helper (reads last `BuyShares` action from `@round.current_actions`). Cap guard now lives inside `if @converting` alongside BUG-001 fix.

---

### BUG-004 — `can_sell?` blocks all regional share selling, including in Major Phase

- **Status:** WONTFIX — rule-correct
- **Rule:** §10.1 — *"A player may never sell a share of a regional."*

The full `:regional` type block in `can_sell?` is correct. Investigating this bug revealed the opposite problem on `18oe_testgame`/`18oe_fullmap` (see BUG-007).

---

### BUG-006 — Minors always pay half dividend (no choice offered)

- **Status:** WONTFIX — rule-correct
- **Severity:** N/A
- **Rule:** §6d — minors are restricted to half-pay only; no other option exists.

`dividend_types` returns `[:half]` for minors on `18oe_testgame` and `18oe_rulechanges`. The single button is correct behaviour, not a bug.

---

### BUG-005 — RCP cannot lay track

- **Status:** FIXED (confirmed by user 2026-05-05; specific commit not identified)
- **Severity:** HIGH
- **Source:** Original short note in `bugs.md` ("rcp cant lay track").

**Symptom.** RCP (Spanish regional, SP zone) could not lay any track tile when operating.

**Root cause (suspected).** `Step::Track#tracker_available_hex` calls `hex_within_national_region?(entity, hex)`; a nil-guard or incorrect zone assignment caused it to reject all SP-zone hexes for RCP.

---

### BUG-003 — Post-conversion sell window skipped when player is already president

- **Status:** FIXED 2026-05-03 `b4b9d4e37` (testgame) / `2a57076b0` (fullmap)
- **Severity:** MEDIUM
- **File:** `lib/engine/game/g_18_oe/step/buy_sell_par_shares.rb:267–273`
- **Rule:** §9.3 — *"Optional — the active player may sell any number of shares of any RR they already own (not the newly floated major)."*

**Symptom.** When the converting player was already the regional's president, `pass!` completed conversion and ended the turn in the same call — no sell or buy window offered.

**Root cause.** `pass!` fell straight through to `super` after `complete_conversion`.

**Fix landed.** `pass!` now `return`s after `complete_conversion` (leaving `@converting` nil and `@converted` set), giving the player a sell+buy window. A second `pass!` call (with `@converted` set) enforces the president check and ends the turn.

---

## Conventions

- **One ID per defect, ever.** If a bug recurs after being fixed, open a new entry that links back: `Status: REOPENED — superseded by BUG-NNN`.
- **Rule citations are mandatory** for HIGH/MEDIUM bugs. If a bug is "wrong but rules are silent," that's a `decisions.md` ADR, not a bug.
- **Fix sections must include the diff direction**, not just the new code, so that future readers can see what the change does.
