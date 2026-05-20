# 1862 Golden Spike — In Work

Items currently in flight: `[~]` in development · `[t]` implemented, testing in progress · `[>]` all tests passed, needs PR.

Move items here from `MD/todo.md` at session start. Move to `MD/done.md` when complete + PR merged.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file
Branch tag: backtick-wrapped branch name at end of each item line; `?` = branch not yet recorded

---

## Sprint 01 — Data skeleton (upstream blocker for 10a/10b)

PR #12622 open on tobymao/18xx — must merge before 10a/10b can resubmit.
All review feedback addressed in commit `9cc1888` (`fix(1862gs): address PR #12622 review feedback`). Waiting for reviewer re-approval and merge.

`1862_usa_canada_p01_data`

---

## Sprint 10a — Bond state + director sell-block

- `[>]` Bond (Schuldschein) state, director sell-block, penalty cert — PR #12634 **CLOSED** (closed 2026-05-18; resubmit after #12622 merges) **[L2/L3]** `1862_usa_canada_p10a_bond_state`

---

## Sprint 10b — Cert transformation + game-end liability

- `[>]` Share buyback cert halving, 50% treasury cert, proportional pricing, game-end penalty — PR #12636 **CLOSED** (closed 2026-05-18; resubmit after #12622 merges) **[L2]** `1862_usa_canada_p10b_cert_transform`

---

## Sprint 11 — Active

- `[>]` CPR/UP SLC transcontinental mechanics: first-connection $20/share payout, Golden Spike route bonus 30→50, transcontinental route stock move, first permanent train stock move — all tests green **[L2]** `1862_usa_canada_p11_impassable_borders`
- `[~]` SLC tile-state marker — track which state the Salt Lake City hex is in (before/after Golden Spike event) **[L2]** `1862_GS`

---

## Sprint 12 — Connection targets on map

Add visual markers for each corporation's connection bonus targets (CORP_BONUSES hexes) to the fixed map so players can see at a glance which cities pay bonuses to which corporation.

- `[>]` Corp-colored badge icons on all unique-target hexes; VPSL hexes use 2-tier pie-chart group badges **[L2]** `1862_usa_canada_p12_connection_badges`
- Known visual issue: VPSL group badges overlap CPR/WP home tokens on G3 — deferred to `map_svg_extras` canvas overlay approach (future sprint)
- [ ] Add TP El Paso bonus to `CORP_BONUSES` once amount confirmed from rulebook (Sprint 17) **[L1]**

`1862_usa_canada_p12_connection_badges`

---

## Sprint 13 — Connection target bonus: playtest and rule finalisation

Test the full lifecycle of a corporation reaching its connection bonus target for the first time. Finalise the cash-vs-permanent choice mechanic based on the physical rulebook pictures.

- `[>]` Browser-test: corp reaches bonus hex for first time → cash-or-permanent prompt appears ✓ (game #21, re-confirmed game #24 after F20 fix) **[browser]**
- `[>]` Browser-test: choosing permanent → bonus appears in revenue every subsequent OR ✓ (game #21) **[browser]**
- `[>]` Browser-test: choosing cash → one-time payment, no further bonus ✓ (game #21) **[browser]**
- `[>]` Implement cash-vs-permanent choice prompt — Step::ChooseBonus, regression spec committed (116/116) **[L2/L3]**
- `[>]` Browser-test: VPSL activation — IRB confirmed (3/3 PASS); full activation visual deferred to first playtest reaching VPSL hex **[browser+IRB]**
- `[>]` Rule review: confirm bonus amounts and activation conditions from rulebook photos against CORP_BONUSES constants **[rules]** — confirmed all clear by user
- `[>]` fix(1862gs): Chicago F20 correct exits SW(edge 0→G19) and W(edge 1→F18) — committed 7ae053580 **[L1/map]**

`1862_usa_canada_p13_bonus_choice`

---

## Sprint 14 — Bond mechanic: playtest and rule verification

Test the full bond (Schuldschein) lifecycle end-to-end in the browser. Adjust implementation if any behaviour deviates from the rules.

- [ ] Browser-test: director issues bond → cash received, director cannot sell shares while bond outstanding **[browser]**
- [ ] Browser-test: director repays bond → director sell-block lifted **[browser]**
- [ ] Browser-test: bond outstanding at game end → deducted from director's personal score **[browser]**
- [ ] Rule review: confirm bond face value, issue conditions, and repayment rules against rulebook **[rules]**
- [ ] Adjust `RepayBond` step and game.rb bond logic as needed based on test findings **[L2/L3]**

`1862_GS`

---

## Sprint 15 — Share price movement on sales: with and without bond

Implement and test the rule that determines how the stock price moves when a player sells shares, depending on whether the corporation has an outstanding bond.

- [ ] Rule review: confirm exact price-drop rules for selling with vs. without bond from rulebook **[rules]**
- [ ] Implement share price movement override in game.rb or custom step (currently using engine default `SELL_MOVEMENT = :down_per_10`) **[L2]**
- [ ] Browser-test: sell shares on corp without bond → price drops by correct amount **[browser]**
- [ ] Browser-test: sell shares on corp with outstanding bond → price behaviour follows bond rule **[browser]**

`1862_GS`

---

## Sprint 16 — Bond: issue UI step + game-end director liability

The bond (Schuldschein) repay step and director sell-block are implemented. Two pieces are missing: there is no OR step that lets the director trigger bond issuance (`issue_bond!` exists in game.rb but is never called), and outstanding bonds at game end are not deducted from the director's personal score.

- [ ] Rule review: confirm bond issue conditions and face value from rulebook **[rules]**
- [ ] Implement `Step::IssueBond` (or extend existing OR step) so the director can issue a bond during an OR turn **[L3]**
- [ ] Wire `issue_bond!` call into the new step **[L2]**
- [ ] Implement game-end score deduction: outstanding bonds reduce director's personal cash score **[L2]**
- [ ] Browser-test: director can issue bond during OR → cash received, bond recorded **[browser]**
- [ ] Browser-test: game ends with bond outstanding → director score reduced by bond face value **[browser]**

`1862_GS`

---

## Sprint 17 — Rules verification: amounts and phase counts

Several constants remain unconfirmed against the physical rulebook.

- [ ] Confirm Golden Spike event bonus amount and update `GOLDEN_SPIKE_BONUS` constant **[L1]**
- [ ] Confirm TP El Paso connection bonus amount and add to `CORP_BONUSES` **[L1]**
- [ ] Confirm operating rounds per phase and update `PHASES` `operating_rounds:` values **[L1]**
- [ ] Confirm 3/3E and 6/6E rust triggers against rulebook and update `TRAINS` if needed **[L1]**

`1862_GS`

---

## Sprint 18 — Monopoly fee collection

Directors owning >60% of a corporation owe a monopoly fee of 20% of face value per share above the 60% threshold. A FIXME exists in `BuySellParShares` but the fee is not collected.

- [ ] Rule review: confirm monopoly fee formula, timing, and recipient (bank vs. treasury) from rulebook **[rules]**
- [ ] Implement monopoly fee deduction in `game.rb` or custom SR step **[L2]**
- [ ] Browser-test: player crosses 60% threshold → fee deducted immediately **[browser]**
- [ ] Browser-test: player already above 60% buys another share → incremental fee charged **[browser]**

`1862_GS`

---

## Sprint 19 — StockBuyback / Aktienrückkauf step

Corporations in phase 3+ may buy back their own shares from the market at 50% of face value. `buyback_available?` exists in game.rb but there is no `Step::StockBuyback` file; the step is referenced as a FIXME in the `operating_round` step list.

- [ ] Rule review: confirm buyback amount, timing (which OR action slot), and share destination from rulebook **[rules]**
- [ ] Create `step/stock_buyback.rb` implementing the buyback action **[L3]**
- [ ] Wire the step into the `operating_round` step list (replace the FIXME placeholder) **[L2]**
- [ ] Browser-test: phase 3+, corp with market shares → buyback action available in OR **[browser]**
- [ ] Browser-test: buyback executed → shares moved to treasury, corp cash reduced **[browser]**

`1862_GS`
