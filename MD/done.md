# 18OE — Done

Completed items (implemented in `18oe_testgame` + at least one upstream PR merged).
Not auto-loaded. Consult for historical context only.

---

## §1 — Game Setup
Player range 2–7 · starting cash formula · bank £54,000 · certificate limits · three-tier hierarchy · incremental capitalisation · regional float condition · regional dump restriction

## §2a — Company Definitions
All 24 regionals · all 12 minors · all 10 privates · all 12 minor auction cards · all 10 concession cards · charter colors for all 12 minors

## §2b — Map
Full 651-hex grid · 19 red off-board hexes · all terrain costs · 255 LOCATION_NAMES · 255 station slots with revenues · pre-printed yellow tiles (J25/J27/AE72/L37/I50/I48) · all pre-printed revenues · pre-printed ferry paths (N31/M28/AA82/I20/O28/X33) · NATIONAL_REGION_HEXES (8 zones) · stale entries removed · SEA_ZONES (19 zones) · city revenues set

## §3 — Track Rights Zones
All 8 zones defined · zone fee on par · zone token restriction · minor zone assignment · asterisked-zone cap (UK/PHS/FR, max 4) · `@minor_available_regions` dynamic · `home_token_locations` filtered · 20% terrain discount (IT/SP/RU/SC)

## §4 — Auction Phase
Waterfall auction with tiered rows · minor card → float right + £120 par

## §6a — Stock Market Grid
8×17 grid with correct prices · par colour bands (blue regional / red major)

## §6b — Share Price Movement
LEFT (zero dividend) · no movement (below price) · RIGHT (at/above price) · minors/regionals exempt from movement

## §6c — Stock Round Structure
Sell-then-buy order · home token placement during SR · regional→major conversion · share issuance for majors

## §6d — Dividend Options
Minors: half-pay only · Nationals: full payout only · Majors/regionals: all three options

## §7a — Train Data
7-level roster · rust triggers (L4/L6/L8) · L8 unlock after 4th L7

## §7b — Phase Structure
8 named phases with train limits · tile colour by phase · status flags · consolidation event on first L5 · national corp type · NATIONAL_REGION_HEXES_COMPLETE / CITY_NATIONAL_ZONE / MINOR_EXCLUDED_HOME_CITIES

## §8a — Operating Order
Float order: minors/regionals first (home-token order), then majors/nationals by share price

## §8b — Track Laying
OE1–OE3 (yellow double-town) · OE4–OE8 (yellow city) · OE12–OE18 (green city) · OE23–OE33 (brown city) · OE34–OE44 (gray city) · tile point budgets · tile point costs · TILE_UPGRADES_MUST_USE_MAX_EXITS · metropolis upgrade labels · nationals pay no terrain

## §8c — Token Placement
Zone restriction · connectivity check · nationals skip token step

## §8g — Train Purchase
Reserved 2+2 obligation (Set flag, phase-status check, depot gating, `process_buy_train` snapshot) · obligation waived if Phase 4 before first OR · depot level gating · inter-RR purchase Phase 4+

## §9 — Minor Ability Descriptions
All 12 minor ability texts entered (A–M)

## §10 — Private Ability Descriptions
All 10 private ability texts entered

## §11 — Nationals (base)
National type `:national` in train limits · NATIONAL_REGION_HEXES · `@minor_available_regions`

## §12A — Track-Rights Chit System
`MINOR_TRACK_RIGHTS_CHITS` · `ASTERISKED_ZONES` cap · `region_available?` / `track_rights_cost` / `claim_region!` · `HomeToken#process_place_token` · `major_phase?`

## §6e — Share Price: UP Movement + Post-Conversion Window
UP movement at end of SR for majors/nationals with no bank-pool shares (`sold_out_increase?`) · post-conversion sell window: sell-then-buy window after regional→major conversion, before mandatory president purchase (`@converted` flow in `BuySellParShares`)

## §9b — Minor Abilities: B E F G K
B (Orange Scroll): 1-point cheap upgrade via `CHEAP_UPGRADE_CORPORATIONS` + Track step · E (Blue Coast): 33% water terrain discount + extra tile lay (`upgrade_cost` + `terrain_discount_ability`) · F (White Peak): same pattern for mountain terrain · G (Indigo Foundry): +2 tile points (`EXTRA_TILE_POINTS`) · K (Vermilion Seal): mail contract revenue paid at OR start (`pay_mail_contract!` in `Operating#after_setup`)

## §13a — Consolidation Phase Scaffold
First L5 purchase → `consolidation_triggered` event → Consolidation Round (once, via `@consolidation_done`) · `Round::G18OE::Consolidation` + `Step::Consolidate`: pass-only scaffold

## §12A — Track-Rights Chit System (upstream PR #12542, merged 2026-05-10)
`MINOR_TRACK_RIGHTS_CHITS` · `ASTERISKED_ZONES` cap · `region_available?` / `track_rights_cost` / `claim_region!` · zone cap enforcement upstream

## §8g — Train Purchase Obligation (upstream PR #12543, merged 2026-05-12)
§8g 3.1/3.4–3.6 reserved 2+2 obligation · depot level gating · inter-RR purchase Phase 4+

## §6c — Stock Round: can_buy? guard + share issuance (upstream PR #12544, merged 2026-05-12)
`can_buy?` guard · share issuance for majors

## §2b — Port icons on map (upstream PR #12558, merged 2026-05-10)
§2a zone colors · §2b port icons on map hexes (alpha); port routing → beta

## §6d — Dividend types + HalfPay (upstream PR #12561, merged 2026-05-07)
`dividend_types` · `HalfPay` step for minors · full-pay only for nationals

## §6b — OR Share Price Movement: threshold rule + dead code removal (2026-05-14)
Three-way `share_price_change` override in `G18OE::Step::Dividend`: LEFT on zero, no move below price, RIGHT at or above price (BUG-013). Dead `game.rb#change_share_price` removed (BUG-014).

## §6b — Sold-out UP: share-price order at SR end (2026-05-14)
`G18OE::Round::Stock` with `finish_round` override — replaces alphabetical `.sort` with `.sort_by { |c| -c.share_price.price }` so highest-priced corps move first (BUG-015).

## §6c — Zone-based terrain discounts + E/F augmentation + rounding (2026-05-14)
`upgrade_cost` rewrite: 20% zone discount for SP/IT/SC/RU zone-matched track rights (`Rational(4,5)`); E/F ability augments to 50% when zone matches; all rounding `.floor` on cost so RR pays less on fractions (BUG-008, BUG-009, BUG-010).

## §6c — President above-60% pool purchase at 2× price (2026-05-14)
`president_pool_overcap_buy?` helper in `BuySellParShares`; `can_buy?` short-circuits before `super` to bypass `holding_ok?`; `process_buy_shares` charges `bundle.price * 2` via `exchange_price:` keyword (BUG-021, §10.2).

## §7a — Level-8 train gate (2026-05-14)
`buyable_trains` override in `G18OE::Step::BuyTrain` injects first `8+8` from `depot.upcoming` once `game.level8_train_available?` is true (≥4 level-7 trains sold); rejects `8+8` until gate opens. Gate predicate lives in `game.rb` as `level8_train_available?` (BUG-018, §11.6).

## §8h — OR share issuance DOWN movement (2026-05-14)
`G18OE::Step::IssueShares` overrides `process_sell_shares` to call `sell_shares_and_change_price` (triggering `SELL_MOVEMENT = :down_share`) instead of bare `share_pool.sell_shares` (BUG-022, §11.7).

## §2b — Province borders + partition engine (upstream PRs #12578 + #12592, merged 2026-05-14)
`type:province` partition engine (`partition.rb` −1 sentinel, `len` anchor param) · orange dashed border renderer (`partitions.rb`) · RU South hexes (Arkhangelsk + Black Sea approach hexes) · TILES.md partition DSL docs

## §13/§15 — Game-end timing: bank-break + level-8 trigger + remainder cash (2026-05-14)
`GAME_END_CHECK = { bank: :current_or, final_phase: :one_more_full_or_set }` · `bankrupt: :immediate` dropped (BUG-027) · `event_level8_train_purchased!` idempotent event injects `REMAINDER_CASH = 100_000` (20×£5,000 notes, §13) into bank via ivar and sets `@level8_train_purchased`; `game_end_check_final_phase?` returns that flag (BUG-024, BUG-025, §13).
