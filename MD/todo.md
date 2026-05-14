# 18OE — Todo (Backlog)

All items not yet started. Load during planning sessions with sparring partner to pick the next sprint.
Items in progress → `MD/inwork.md`. Completed items → `MD/done.md`.

Layers: L1 constants · L2 Game::Base override · L3 new Step/Round file

---

## Status Dashboard

*Updated 2026-05-14*

```
Alpha milestone progress
──────────────────────────────────────────────────────────────────
§1  Game Setup             ████████████████████  Complete  ✅
§2a Companies / Entities   ████████████████████  Complete  ✅
§2b Map                    █████████████████░░░  ~85%  (OE tiles + ferry hexes pending)
§3  Track Rights           ████████████████████  Complete  ✅
§4  Auction Phase          ████████████████░░░░  ~80%  (all-pass reduction pending)
§6a Stock Market Grid      ████████████████████  Complete  ✅
§6b Share Price Movement   ████████████████████  Complete  ✅
§6c Stock Round            ██████████████░░░░░░  ~70%  (minor merge done; removal + reserved pending)
§6d Dividend Options       ████████████████████  Complete  ✅
§7a Train Data             ████████████████████  Complete  ✅
§7b Phase Structure        ████████████████████  Complete  ✅
§8a Operating Order        ████████████████████  Complete  ✅
§8b Track Laying           ██████████████████░░  ~90%  (first-OR exception)
§8c Token Placement        ████████████████████  Complete  ✅
§8f Pullman Cars           ░░░░░░░░░░░░░░░░░░░░  0%  (not started)
§8g Train Purchase         ████████████░░░░░░░░  ~60%  (obligation done; force-buy pending)
§8h OR Share Step          ████████████░░░░░░░░  ~60%  (DOWN done; Exchange TBD)
§9  Minor Abilities        ██████████████████░░  ~90%  (CIWL Pullman pending)
§10 Private Abilities      ████████████████░░░░  ~80%  (2 complex abilities)
§11 Nationals (base)       █████████████░░░░░░░  ~65%  (formation + rusted-train claim done; revenue beta)
§12A Track Rights Chit     ████████████████████  Complete  ✅
§13a Consolidation Scaffold ████████████████████  Complete  ✅
§14 Token Transfer         ░░░░░░░░░░░░░░░░░░░░  0%  (not started)
§15 End Game               ████████████████░░░░  ~80%  (abbreviated OR beta)
§16 Tests                  ░░░░░░░░░░░░░░░░░░░░  0%  (not started)

Bug tracker  ██████████████████░░  19 / 25 bugs closed  (76%)
Alpha bugs   ████████████████████  0 open alpha bugs  ✅

Branch status (rebased 2026-05-14 onto upstream/master after PRs #12578 + #12592 merged)
──────────────────────────────────────────────────────────────────
18oe_abilities    ██████████  rebased ✓  abilities wiring (C/D/J/L + privates)
18oe_gamefixes    ██████████  rebased ✓  10 bug fixes
18oe_mergers      ██████████  rebased ✓  minor merger · national formation · SR fixes
18oe_testing      ░░░░░░░░░░  pending    integration branch not yet updated
```

---

# Alpha Backlog

Target: auction · floating · minor-regional phase · major phase to game end · map complete (port icons displayed, no routing) · all minor/private abilities not gated on beta features.

---

## Art / Non-Code

- [ ] **Logo SVGs** — colors done; still missing: minors A/B/D/E/F/G/J/L; regionals BHB/POB/KSS/KBS/SB/MAV/SFAI/SFR/CHN/MZA/RCP/MSP/MKV/LRZD/WW/DSJ/BJV **[non-code]**

---

## Map

- [ ] OE9–OE11 — green double-town path edge orientations needed **[L1]**
- [ ] OE20–OE22 — brown double-town path edge orientations needed **[L1]**
- [ ] OE19 — tile type unknown; must be identified and defined **[L1]**
- [ ] Verify standard tile quantities against physical tile manifest **[L1]**
- [ ] Audit OE-specific tile upgrade paths against physical manifest **[L1]**

---

## §4 — Auction Phase

- [ ] All-pass price reduction — if all players consecutively pass before opening packet is sold, privates pay dividends then all items on topmost row reduce by £5; repeats; items reaching £0 must all be taken by next player **[L2]**

---

## §5 — Concession Railroad Phase *(DEFERRED — Out of Scope)*

Concession cards defined (§2.5). Phase skipped for now: current flow goes Auction → Regional/Minor Phase.
Requires a distinct round with queue management; deferred until core mechanics are stable.

- [ ] Define Concession round with ordered float actions (CON1–CON10) **[L3]**
- [ ] Wire concession cards to specific regional/major home tokens and par values **[L1]**
- [ ] Float obligation: holder pays 2× par; obligation transfers if holder cannot pay **[L3]**
- [ ] Round sequencing: Auction → Concession → Regional/Minor Phase **[L2]**
- [ ] 2-player without-concessions variant: skip Concession Phase (starting cash already correct) **[L2]**

---

## §6 — Stock Round

- [ ] Voluntary regional removal — player may remove one unfloated regional during Regional/Minor Phase; max 6 total **[L2/L3]**
- [ ] Reserved secondary shares — during Initial SR only, each player may designate one regional's secondary (25%) share as reserved; no other player may purchase it until the second SR; cancelled if regional expands to major before its first OR **[L2]**

*Change of Presidency — handled by base engine (`can_dump?` + `fit_in_bank?`); no custom code needed. Removed 2026-05-14.*

---

## §8b — Track Laying

- [ ] First-OR green tile exception (§11.1.9) — Phase 2 only, first OR after float: if RR cannot connect home token to any town/city via land or ferry without a sea crossing, it may lay one non-city green tile at cost of all remaining tile points; requires ≥1 tile point; cannot be exploited deliberately **[L2]**

---

*§8d Routing (Land) — local train town counting + combined train runs → beta. Shifted 2026-05-14.*

---

## §8f — Pullman Cars

No Pullman logic yet. Nationals' inherent Pullman bonus already in `national_revenue`.

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
- [ ] Remove `Engine::Step::Bankrupt` from OR step list — base bankruptcy fires game-end immediately; 18OE force-buy should route to national conversion (BUG-019/BUG-027); replace with a custom no-op or override **[L2]**

*Level 3 trains not available in first OR — implemented via `non_starter_trains_available? = major_phase? && @first_or_done`. Removed from todo 2026-05-14.*

---

## §8h — Major's OR Buy/Sell Shares Step (§11.7)

- [ ] Investigate `Engine::Step::Exchange` in OR step list — minor exchange abilities fire in SR only; confirm Exchange never triggers during OR and remove if vestigial **[L2]**

*§11.7 DOWN price movement on share issuance — fixed 2026-05-14 (BUG-022). Removed from todo.*

---

## §9 — Minor Special Abilities

- [ ] **7.13** Minor M (CIWL) — holds 10 Pullman cars (see §8f) **[L3]**

*Ability transfer on merge → beta. Minor A (Silver Banner) → beta. Shifted 2026-05-14.*

---

## §10 — Private Special Abilities

- [ ] **8.2** Barclay, Bevan, Barclay & Tritton — owner selects one of three abilities at time of use **[L3]**
- [ ] **8.8** Swift Metropolitan Line — from Phase 4, one controlled RR may keep one 2+2 outside train limit **[L3]**

---

*§12E Minor Merger Edge Cases → beta (all items). Shifted 2026-05-14.*

---

## §14 — Token Transfer Between Majors

- [ ] During major's OR Transfer Tokens step: controlling player transfers one token between two majors **[L2]**
- [ ] Cost: token value (paying major) + token value (receiving major, same zone) + transfer fee (Normal £20 / Grand £40 / Metropolis £60) **[L2]**
- [ ] Selling a token: returns to charter at highest-cost open position **[L2]**

---

## §15 — End Game Rules

- [ ] Second final OR: each company pays same revenue as first final OR; no track/token/train actions (BUG-026) `[BETA]` **[L3]**

*Bank-break timing (BUG-024), level-8 end trigger (BUG-025), remainder cash, and bankrupt:immediate removal (BUG-027) — all fixed 2026-05-14. Removed from todo.*

---

## §16 — Tests (Alpha)

- [ ] Smoke spec — `Engine::Game::G18OE.new(%w[A B C D])` does not raise
- [ ] Basic game flow (auction → regional/minor → major phase)
- [ ] Train phase transitions (rusting, limits)
- [ ] Stock market movement (right/left/up/down, edge cases)
- [ ] Minor ability transfer
- [ ] Pullman car revenue

---

---

# Beta Backlog

Target: sea zones · ports and ferry runs · Orient Express · minor→major mergers (full) · nationalization of companies · railroad formation (nationals) · abandoning minors.

---

## Map

- [ ] Ferry distance numbers — per-zone crossing distances needed for cross-water cost calculations (§8d); sea zone borders themselves are complete **[L1]**
- [ ] **Ferry sea hexes** — partial work exists; still needed: N29/G22/N25/I22/I24/AE12/AF13/AB21/AB23/AB25 **[L1]**
- [ ] Ferry route engine override — `game.rb` override to whitelist exits toward blue hexes that carry a matching pre-printed path **[L2]**
- [ ] **Lille↔London ferry** — tiles connect correctly; all other ferry routes blocked pending L2 engine override **[L2]**
- [ ] **Port sea stubs** `[BETA]` — blue tiles at port entry points use `junction;path=a:X,b:_0,terminal:1` as connectors between land port paths and sea ferry routes; model: land port → stub → sea ferry hexes → stub → land port; implement per port once ferry routing engine override is in place; public vs private port access distinction applies here (see §8d) **[L1/L2]**
- [ ] **G30 inland port** `[BETA]` — G30 currently has `junction;path=a:4,b:_0` (missing `terminal:1`); inland ports differ from coastal port stubs in routing rules — define and document the distinction before implementing; add `terminal:1` as part of this work **[L1]**

---

## §2 — Patronage Tiles (§11.1.8)

45 tiles placed randomly on the map at setup (pink/yellow/green/white groups). Data and payout mechanic both needed.

- [ ] Setup: randomise and place patronage tiles on map cities at game start (3 pink, 3 yellow, 3 white, 8 green drawn per group, rest discarded) **[L1]**
- [ ] Payout: when a RR first lays a track tile in a patronage hex during Lay Track step, bank pays one-time bonus equal to tile amount for the highest track color available in current Train Phase; patronage tile removed **[L2]**
- [ ] Float edge case: minor that places its home token on a patronage hex fulfils it immediately and receives the lowest payout shown on the tile **[L2]**

---

## §6 — Stock Round

- [ ] +3 RIGHT — on the first Orient Express run, share price moves 3 steps right (depends on §8e) **[L2]**

---

## §8d — Routing: Land + Cross-Water

- [ ] Local train town counting: towns beyond city limit fill to train level; express trains skip towns **[L2]**
- [ ] Combined train runs: Level ≤4 trains combine (sum); Level 5+, 4D, 5D cannot combine **[L2]**

Sea zones defined as data only; no routing logic yet.

- [ ] Cross-water costs: Ferry = +£5 track / +£20 token × distance; Sea = +£10 track / +£40 token × zones **[L2]**
- [ ] Ferry mechanics: distance counts against city limit; public ferry usable by any RR; enemy tokens block **[L2]**
- [ ] Port authority markers: each reduces sea zone count + ferry distance by 2; 16 total (8 North Sea, 8 Med) **[L2/L3]**
- [ ] Port authority purchase — majors only, one per major; £125 paid during OR at any point before Buy Trains step; North Sea covers light-blue zones, Mediterranean covers sea-green zones; also reduces cross-water track and token costs **[L2]**
- [ ] Port authority transfer — major may buy a PA marker from another major during its Transfer Tokens OR step; price exactly £125 to selling major's treasury **[L2]**
- [ ] Port types: public (any RR) vs private (owning RR only) **[L2]**
- [ ] Offshore port mechanics: train connects regardless of intervening hexes **[L2]**
- [ ] Channel passages at Copenhagen and Constantinople **[L2]**

---

## §8e — Orient Express

No OE logic yet. Prerequisite: all city revenues verified against physical map.

- [ ] Detect valid OE route: Constantinople (AA82) + one of Paris/London/Berlin/Madrid/Sankt-Peterburg + land track **[L2]**
- [ ] First-time bonus: £30 (Ph2–4), £60 (Ph5–6), £100 (Ph7–8); OE marker placed on major **[L2]**
- [ ] +3 RIGHT on first OE run (also §6b) **[L2]**
- [ ] Train combining: Level ≤4 combine; combined level = sum; city limit = combined level **[L2]**
- [ ] Subsequent OE runs: no bonus, no extra stock movement **[L2]**
- [ ] Mandatory OE: if OE route is best possible, president must run it **[L2]**
- [ ] OE blocked for nationals **[L2]**
- [ ] D-train bonus does NOT apply to OE first-time bonus **[L2]**

---

## §8h — Major's OR Buy/Sell Shares Step (§11.7)

- [ ] Major purchases one abandoned minor from Open Market for £60 (to bank); minor's charter + assets added as if merged but no share of major stock issued to former owner **[L2]**

---

## §9 — Minor Special Abilities

- [ ] **7.9** Minor H (Great Western Steamship) — reduces sea zones by 1 (Ph1–6) or 2 (Ph7–8) **[L2]**
- [ ] **D (Green Junction)** — sea/ferry variant: unreachable-city placement step where target city is accessible only via sea or ferry **[L3]**

---

## §10 — Private Special Abilities

- [ ] **Wien Südbahnhof** — sea-zone crossing cost modifier for tokens placed via this private; WCF interaction (paying WCF token placement cost from Wien Südbahnhof) **[L2/L3]**

---

## §9 — Railroad Formation (Nationals) + Abandoning a Minor

- [ ] Forming a national (trigger): phase 4/6/8 purchase → `trigger_nationals_formation!` → ordered queue **[L2]**
- [ ] Forming a national (steps): `Step::ConvertToNational` — cash→bank, treasury certs→OM, tokens removed, national placed, trains inherited **[L2/L3]**
- [ ] Abandoning a minor (§9.5): triggered by national formation or consolidation failure — `abandon_minor!`: charter→Open Market; trains→Open Market; tokens removed; cash→bank; track rights chit stays **[L2]**
- [ ] D minor token and L minor marker stay with their charters on abandonment **[L2]**
- [ ] M minor Pullman stays with charter on abandonment **[L2]**

---

## §11 — Nationals

- [ ] `national_revenue`: linked/unlinked split, best-first, D-train double, flat-rate fill; `[:payout]` only **[L2]**
- [ ] Inherent Pullman: `+£10 × highest non-rusted train level` **[L2]**
- [ ] No tokens / no terrain costs — `return 0 if entity.type == :national` in `upgrade_cost` (BUG-011); skip token step already done **[L2]**
- [ ] Train limit discard via `depot.reclaim_train` **[L2]**
- [ ] Merged minors abandoned at national formation (depends on `@minor_track_rights`) **[L3]**
- [ ] Track rights / OE markers / private markers removed at formation **[L3]**
- [ ] Exchange owned rusted train for higher-level unclaimed rusted train **[L2/L3]**
- [ ] Flip owned rusted train from express to local side **[L2/L3]**
- [ ] Upgrade rusted → non-rusted by purchasing from same-owner major **[L2/L3]**

---

## §10.5 — Minor SR Mergers (Full)

- [ ] Minor SR merge action — `can_merge_minors?` / `merge_minor!` / `transfer_minor_track_rights!` implemented on `18oe_testgame`; PR pending `[BETA]` **[L2/L3]**
- [ ] **7.1** Ability transfer — minor merges into regional/major; ability inherited; nationals cannot inherit **[L3]**
- [ ] **7.2** Minor A (Silver Banner) — bank pays major current share price at moment of merger **[L3]**
- [ ] No-stock connection check: merge only if unlimited-city train can reach minor's token to major's network **[L3]**
- [ ] Player choice on token conflict and train decline **[L3]**
- [ ] Cross-player personal cash side payment UI **[L3]**
- [ ] Solicit-offers rule for unmergeable minors **[L3]**
- [ ] Cannot pass in Consolidation Phase if owns unfloated minors/regionals not yet merged **[L2]**

---

## §12E — Minor Merger Edge Cases (Beta)

- [ ] Consolidation Round forced mergers (§10.6) — hook into `Step::Consolidate` **[L3]**

---

## §13 — Consolidation Phase

- [ ] Conditional merger: major/national may offer; if no offer, company is abandoned **[L3]**

---

## §14 — Token Transfer Between Majors

- [ ] Port authority transfer: major buys PA marker from another major during Transfer Tokens step; price exactly £125 to selling major's treasury (see also §8d) **[L2]**

---

## §16 — Tests (Beta)

- [ ] National revenue calculation
- [ ] Orient Express bonus (first run, subsequent runs)

---

---

# §17 — Variants & Scenarios *(Deferred — out of scope until full game ships)*

All UK-FR variant and scenario items are deferred. No work until the full 18OE base game reaches beta.

- Confirm UK-FR variant entities (4 minors: C/H/K/M; 7 regionals: BEL/GSWR/GWR/LNWR/MIDI/OU/PLM)
- UK-FR train rusting rules
- Validate UK-FR map hex definitions
- Other scenarios (medium/short) — reduced RR counts, modified OE destinations
