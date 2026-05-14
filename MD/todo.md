# 1862 Golden Spike — Todo (Backlog)

All items not yet started. Pull into `MD/inwork.md` at session start.
Completed items → `MD/done.md`.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file

---

## Open FIXMEs (priority order)

- [ ] **Map verification** — all hex coordinates in `map.rb` are approximations from photos; verify every hex against physical rulebook before any map-dependent work **[L1]**
- [ ] **Toronto hex** — `TODO_TORONTO` placeholder in `entities.rb` TOR ability; assign real tile ID **[L1]** *(Sprint 11 active)*
- [ ] **Corporation home hexes** — all home hexes flagged as placeholders in `entities.rb`; verify against physical rulebook **[L1]**
- [ ] **`StockBuyback` step** — share-halving / 50% buyback action (phase 3+); referenced in `game.rb` OR step list as FIXME; file does not exist yet **[L3]**
- [ ] **Rust triggers** — 3/3E and 6/6E rust triggers unconfirmed against rulebook **[L1]**
- [ ] **Operating rounds per phase** — counts in `PHASES` unverified against rulebook **[L1]**
- [ ] **Corporation logos** — 13 corps need logo SVG assets **[asset]**

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
