# 1862 Golden Spike — In Work

Items currently in flight: `[~]` in development · `[t]` implemented, testing in progress · `[>]` all tests passed, needs PR.

Move items here from `MD/todo.md` at session start. Move to `MD/done.md` when complete + PR merged.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file
Branch tag: backtick-wrapped branch name at end of each item line; `?` = branch not yet recorded

---

## Sprint 01 — Data skeleton ✓ MERGED

PR #12622 merged 2026-05-19. Sprint 10a/10b can now be resubmitted.

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
- `[>]` fix(1862gs): use connection_hexes fallback for deserialized routes in bonus checks — Route#visited_stops always [] for JSON-replayed routes; add route_hex_ids helper falling back to connection_hexes.flatten; spec updated to 2E-train / G19 path (120/120) — committed 35247e40b **[L2]**

`1862_usa_canada_p13_bonus_choice`

---

## Sprint 14 — Bond + Stock Buyback: full lifecycle implementation and test

Bond (Schuldschein) is issued as part of the Stock Buyback (Aktienrückkauf): the corporation takes on the debt, director receives a permanent −1 cert-limit marker, and the director is personally liable for any unrepaid bond at game end.

Rules confirmed 2026-05-20:
- Bond and buyback are one combined action (buyback triggers the bond)
- Director gets a permanent penalty marker: cert limit −1 forever, even after bond is repaid
- Director cannot sell shares of that corporation while bond is outstanding
- If bond not repaid by game end: director pays from personal cash; forced end-game share sales do not drop share price

- `[>]` Rule review: buyback amount = 50% market cap (5×price ⌈nearest $100⌉); StockBuyback in early OR slot; RepayBond after Dividend; confirmed 2026-05-20 **[rules]**
- `[>]` IRB-test: `record_bond!` sets corp debt; `buyback_done?` true; director cert count reflects `@buyback_done` permanent marker (120/0 spec) **[IRB]**
- `[>]` IRB-test: `bond?` true after `record_bond!`; `bond?` false after `repay_bond!`; `buyback_done?` still true (permanent) **[IRB]**
- `[>]` IRB-test: `director_bond_blocks_sale?` true for bonded corp director; false after repayment **[IRB]**
- `[>]` IRB-test: `apply_bond_penalties!` deducts bond amount from director cash at game end **[IRB]**
- `[>]` Create `step/stock_buyback.rb` — triggers buyback + bond issuance in one action — committed bb4968358 **[L3]**
- `[>]` Wire `Step::StockBuyback` into `operating_round` step list — committed bb4968358 **[L2]**
- `[>]` Create `step/repay_bond.rb` — OR action to repay the bond — committed bb4968358 **[L3]**
- `[>]` Wire `Step::RepayBond` into `operating_round` step list — committed bb4968358 **[L2]**
- `[>]` Fix `record_bond!` to transfer bond amount from bank to corp treasury — committed bb4968358 **[L2]**
- `[>]` `execute_buyback_payout!`: pays each shareholder 50% market price per cert, calls `halve_shares!` — committed bb4968358 **[L2]**
- [ ] Implement end-game forced share sale without share price drop **[L2]**
- `[>]` Browser-test: phase 3+, corp with market shares → buyback action available in OR; bond issued, cert limit reduced ✓ 2026-05-22 **[browser]**
- `[>]` Browser-test: corp repays bond → financial debt cleared, cert limit still reduced ✓ 2026-05-22 **[browser]**
- [ ] Browser-test: game ends with bond outstanding → director score reduced **[browser]**

`1862_usa_canada_p14_bond_buyback`

---

## Sprint 15 — Share price movement on sales: with and without bond

Implement and test the rule that determines how the stock price moves when a player sells shares, depending on whether the corporation has an outstanding bond.

- [ ] Rule review: confirm exact price-drop rules for selling with vs. without bond from rulebook **[rules]**
- [ ] Implement share price movement override in game.rb or custom step (currently using engine default `SELL_MOVEMENT = :down_per_10`) **[L2]**
- [ ] Browser-test: sell shares on corp without bond → price drops by correct amount **[browser]**
- [ ] Browser-test: sell shares on corp with outstanding bond → price behaviour follows bond rule **[browser]**

`1862_GS`

---

## Sprint 16 — Rules verification: amounts and phase counts

Several constants remain unconfirmed against the physical rulebook.

- [ ] Confirm Golden Spike event bonus amount and update `GOLDEN_SPIKE_BONUS` constant **[L1]**
- [ ] Confirm TP El Paso connection bonus amount and add to `CORP_BONUSES` **[L1]**
- [ ] Confirm operating rounds per phase and update `PHASES` `operating_rounds:` values **[L1]**
- [ ] Confirm 3/3E and 6/6E rust triggers against rulebook and update `TRAINS` if needed **[L1]**

`1862_GS`

---

## Sprint 17 — Monopoly fee collection

Directors owning >60% of a corporation owe a monopoly fee of 20% of face value per share above the 60% threshold. A FIXME exists in `BuySellParShares` but the fee is not collected.

- [ ] Rule review: confirm monopoly fee formula, timing, and recipient (bank vs. treasury) from rulebook **[rules]**
- [ ] Implement monopoly fee deduction in `game.rb` or custom SR step **[L2]**
- [ ] Browser-test: player crosses 60% threshold → fee deducted immediately **[browser]**
- [ ] Browser-test: player already above 60% buys another share → incremental fee charged **[browser]**

`1862_GS`

---

