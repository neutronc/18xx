# 18OE — Open for Alpha

All remaining work scoped to the alpha milestone. Items marked `[/]` are partially implemented (branch exists, some code wired); items marked `[ ]` are not yet started.

Pick from this list at the start of a development session. Quick wins (L1, well-scoped) are highlighted.

---

## Art / Non-Code

- [ ] **Logo SVGs** — missing: minors A/B/D/E/F/G/J/L; regionals BHB/POB/KSS/KBS/SB/MAV/SFAI/SFR/CHN/MZA/RCP/MSP/MKV/LRZD/WW/DSJ/BJV ⭐ *non-code, independent*

---

## Map

- [ ] OE9–OE11 — green double-town path edge orientations **[L1]** ⭐ *quick win*
- [ ] OE20–OE22 — brown double-town path edge orientations **[L1]** ⭐ *quick win*
- [ ] OE19 — tile type unknown; must be identified and defined **[L1]**
- [ ] Verify standard tile quantities against physical tile manifest **[L1]**
- [ ] Audit OE-specific tile upgrade paths against physical manifest **[L1]**

---

## §4 — Auction Phase

- [ ] All-pass price reduction — if all players consecutively pass before opening packet sold, privates pay dividends then all items on topmost row reduce £5; repeats; items reaching £0 must all be taken by next player **[L2]**

---

## §6 — Stock Round

- [ ] Voluntary regional removal — player may remove one unfloated regional during Regional/Minor Phase; max 6 total **[L2/L3]**
- [ ] Reserved secondary shares — during Initial SR only, each player may designate one regional's 25% share as reserved; no other player may purchase until second SR; cancelled if regional expands to major before first OR **[L2]**

---

## §8b — Track Laying

- [ ] First-OR green tile exception (§11.1.9) — Phase 2 only, first OR after float: if RR cannot connect home token to any town/city via land or ferry without a sea crossing, may lay one non-city green tile at cost of all remaining tile points **[L2]**

---

## §8f — Pullman Cars *(0% — not started)*

- [ ] Pullman asset type — does not count against train limit; max 1 per non-national company **[L3]**
- [ ] Revenue bonus: +£10 × assigned train level, once per OR **[L2/L3]**
- [ ] Purchase from Minor M: £150 + £15 royalty; J-minor discount on price only **[L3]**
- [ ] Purchase from Open Market: £150, no royalty; available Phase 4+ **[L3]**
- [ ] Purchase from another RR: negotiated price **[L3]**
- [ ] Minor M free Pullman: if Minor M not closed at Phase 4 start, places free Pullman **[L2/L3]**
- [ ] Discard order: rusted trains first; Pullman voluntarily returnable to Open Market **[L3]**
- [ ] Company with zero trains but holds Pullman: retain until next train acquired **[L3]**

---

## §8g — Train Purchase

- [ ] Forced purchase — president covers shortfall; else national conversion (majors) or insolvency (minors/regionals) **[L3]**
- [ ] First-round insolvency: president cash → treasury; company receives reserved 2+2; presidential cert → Open Market; president paid face value **[L3]**
- [ ] Remove `Engine::Step::Bankrupt` from OR step list — replace with custom no-op or override **[L2]**

---

## §8h — Major's OR Buy/Sell Shares Step

- [ ] Investigate `Engine::Step::Exchange` in OR step list — confirm Exchange never triggers during OR and remove if vestigial **[L2]** ⭐ *quick investigation*

---

## §9 — Minor Special Abilities

- [ ] **7.13** Minor M (CIWL) — holds 10 Pullman cars (see §8f) **[L3]**
- [/] **C** (Golden Bell) — `choose_ability`/`@golden_bell_position`/`operating_order` wired; **still needed**: OR-start choice-prompt step **[L3]** `18oe_abilities`
- [/] **D** (Green Junction) — `hex_bonus`/`event_d_token_phase_change!`/`assign_d_token!` wired; **still needed**: unreachable-city placement step (land cities only) **[L3]** `18oe_abilities`
- [/] **J** (Grey Locomotive Works) — `train_discount` (0.1) wired; **needs PR** **[L1]** `18oe_abilities` ⭐ *quick win — PR only*
- [/] **L** (Krasnaya Strela) — `assign_krasnaya_strela!`/`restore_krasnaya_strela!` wired; **still needed**: train-choice step + D-train exception **[L3]** `18oe_abilities`

---

## §10 — Private Special Abilities

- [ ] **8.2** Barclay, Bevan, Barclay & Tritton — owner selects one of three abilities at time of use **[L3]**
- [ ] **8.8** Swift Metropolitan Line — from Phase 4, one controlled RR may keep one 2+2 outside train limit **[L3]**
- [/] **Central Circle** — `token` (extra_slot, special_only) wired; **still needed**: town revenue scoring (£10/£20/£40/£60 by phase), SR window **[L3]** `18oe_abilities`
- [/] **Hochberg Mining** — `assign_hexes` wired; **still needed**: routing exclusion + placement eligibility (cost ≥ £45) **[L3]** `18oe_abilities`
- [/] **Brandt & Brandau** — `tile_lay` (free, count: 4) wired; **still needed**: per-OR cap (max 2/OR) **[L3]** `18oe_abilities`

---

## §14 — Token Transfer Between Majors *(0% — not started)*

- [ ] During major's OR Transfer Tokens step: controlling player transfers one token between two majors **[L2]**
- [ ] Cost: token value (paying major) + token value (receiving major, same zone) + transfer fee (Normal £20 / Grand £40 / Metropolis £60) **[L2]**
- [ ] Selling a token: returns to charter at highest-cost open position **[L2]**

---

## §16 — Tests *(0% — not started)*

- [ ] Smoke spec — `Engine::Game::G18OE.new(%w[A B C D])` does not raise
- [ ] Basic game flow (auction → regional/minor → major phase)
- [ ] Train phase transitions (rusting, limits)
- [ ] Stock market movement (right/left/up/down, edge cases)
- [ ] Minor ability transfer
- [ ] Pullman car revenue

---

## PRs Pending Upstream Review

The following items are implemented and awaiting merge into `tobymao/18xx`:

| Item | Branch | Upstream PR |
|------|--------|-------------|
| fix get_par_prices for regional companies | `18oe_fix_par_prices` | [tobymao#12601](https://github.com/tobymao/18xx/pull/12601) |
| §4.4 three-way OR share price movement | `18oe_fix_share_price_movement` | [tobymao#12602](https://github.com/tobymao/18xx/pull/12602) |
| President pool purchase above 60% | `18oe_fix_president_overcap` | [tobymao#12603](https://github.com/tobymao/18xx/pull/12603) |
| Stock round fixes + zone-based terrain discount | `18oe_fix_stock_terrain` | [tobymao#12604](https://github.com/tobymao/18xx/pull/12604) |
| Level-8 train gate + game-end timing | `18oe_fix_level8_gameend` | [tobymao#12605](https://github.com/tobymao/18xx/pull/12605) |

---

*Updated 2026-05-14. Source: `MD/todo.md` Alpha Backlog.*
