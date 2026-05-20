# 1862 Golden Spike — Todo (Backlog)

All items not yet started. Pull into `MD/inwork.md` at session start.
Completed items → `MD/done.md`.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file

---

## Open Bugs (to fix)

- [ ] **BUG-012** — `SELL_BUY_ORDER` wrong; buying a share must end the player's SR turn **[L1]**

---

## Open FIXMEs (priority order)

- [x] **Map verification** — hex coordinates confirmed against physical rulebook 2026-05-16; remaining open: TP El Paso bonus amount, Golden Spike bonus amount (Sprint 17), and visual connection bonus display (Sprint 12)
- [ ] **Toronto hex** — `TODO_TORONTO` placeholder in `entities.rb` TOR ability; assign real tile ID **[L1]** *(Sprint 11 active)*
- [ ] **Corporation home hexes** — all home hexes flagged as placeholders in `entities.rb`; verify against physical rulebook **[L1]**
- [ ] **`StockBuyback` step** — share-halving / 50% buyback action (phase 3+); referenced in `game.rb` OR step list as FIXME; file does not exist yet **[L3]** *(Sprint 19)*
- [ ] **Rust triggers** — 3/3E and 6/6E rust triggers unconfirmed against rulebook **[L1]** *(Sprint 17)*
- [ ] **Operating rounds per phase** — counts in `PHASES` unverified against rulebook **[L1]** *(Sprint 17)*
- [ ] **Corporation logos** — 13 corps need logo SVG assets **[asset]**
- [ ] **Implement special tiles and rework tile manifest** **[L1]**
- [ ] **Bond issue UI step** — `issue_bond!` exists but no step triggers it; director has no way to issue a bond **[L3]** *(Sprint 16)*
- [ ] **Game-end bond liability** — outstanding bonds not deducted from director's personal score at game end **[L2]** *(Sprint 16)*
- [ ] **Monopoly fee** — >60% ownership fee not collected; FIXME in `BuySellParShares` **[L2]** *(Sprint 18)*

---

## Sprints Done

| Sprint | Deliverable | Status |
|--------|-------------|--------|
| 1–4    | Stock market, map skeleton, entities, share-structure fixes | Done |
| 5      | Dividend step + private close triggers (PSC/FNY) | Done |
| 6      | Bond (Schuldschein): issue, repay, director-sell block | Done |
| 7      | E-trains, tile-lay "2 yellow OR 1 upgrade", phase fixes | Done |
| 8      | GHU token discount, CompanyPendingPar, NHSC par lock | Done |
| 9      | Bonus markers (Bonusplättchen): state, revenue, activation | Done |
| 10     | SLC transcontinental bonus + Golden Spike event | Done |
