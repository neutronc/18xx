# 1862 Golden Spike — Done

Completed sprints (implemented + committed on `1862_GS`).
Not auto-loaded. Consult for historical context only.

---

## Sprint 1–4 — Stock market, map skeleton, entities, share-structure fixes

Stock market grid · starting cash · bank size · certificate limits · corporation groups (Group 1/2/3) · share structure · map skeleton from photos · entities (13 corps, 7 privates)

## Sprint 5 — Dividend step + private close triggers (PSC/FNY)

Dividend step · PSC closes when WP pays first dividend · FNY closes when NYC pays first dividend

## Sprint 6 — Bond (Schuldschein): issue, repay, director-sell block

Bond issue · bond repay · director cannot sell shares while bond outstanding · bonds at game end are director's personal liability

## Sprint 7 — E-trains, tile-lay "2 yellow OR 1 upgrade", phase fixes

E-train variants (pay N stops, visit unlimited) · tile-lay budget (2 yellow OR 1 upgrade) · phase fixes

## Sprint 8 — GHU token discount, CompanyPendingPar, NHSC par lock

GHU token discount · CompanyPendingPar mechanic · NHSC par locked until NYH floats

## Sprint 9 — Bonus markers (Bonusplättchen): state, revenue, activation

Bonus marker state tracking · revenue bonus on activation · placement rules

## Sprint 10 — SLC transcontinental bonus + Golden Spike event

Salt Lake City $30 bonus (reduced to $15 while SOC open) · Golden Spike event triggered on first SLC transcontinental bonus collection · SOC closes when CPR or UP floats · NHSC closes when NYH floats

## PR 10a — Bond state + director sell-block (PR #12634)

`@corp_bonds` / `@buyback_done` state · bond amount = 5 × market price rounded up to nearest $100 · one bond per corp ever · director sell-block in `BuySellParShares#can_sell?` · penalty cert (+1 cert limit) via `num_certs` override

## PR 10b — Share buyback cert transformation (PR #12636)

`halve_shares!` — 20%→10%, 10%→5%, 30%→10%+5% split · 50% non-buyable treasury cert · proportional pricing via `forced_share_percent=5` + `price_multiplier=0.5` · treasury cert earns revenue/2 back to corp · game-end bond penalty via `player.penalty`

## PR 11 — Impassable border edges (PR #12637)

Five impassable borders in Great Lakes / St. Lawrence area: C19–C21, C19–D20, C21–D20, E27–D26 (Ottawa), E27–D28 (Montreal) · browser verified ✓
