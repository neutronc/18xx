# 18xx Ruby Engine — Mechanics Reference for 18OE

Extracted from 18xx engine analysis. Covers only Ruby engine mechanics relevant to the
18OE implementation. All JavaScript / rendering content has been removed.

---

## 1. Implementation Layer Taxonomy

The engine organises game logic into four layers. Knowing which layer a mechanic lives
in tells you how hard it is to implement and where the code goes.

### Layer 1 — Pure Configuration (constants only)

No custom Ruby methods needed — only values in `TRAINS`, `PHASES`, `COMPANIES`,
`CORPORATIONS`, `MINORS`, or scalar game constants.

**TRAINS entries capture:**
- Train roster: name, distance, price, count
- Rust triggers: `rusts_on:`, `obsolete_on:`
- Availability gate: `available_on:` (train only appears after another is bought)
- Purchase discounts: `discount: {'2' => 30}` hash
- Variants: `variants:` array (sub-types selectable at buy time; each can have own `rusts_on:`)
- Revenue multipliers on variants: `multiplier:` int
- Phase-transition events: `events: [{'type' => 'xxx'}]` — dispatched to `event_xxx!`
- Multi-node distance specs: `distance:` as array of `{'nodes'=>[...], 'pay'=>N, 'visit'=>N}`

**PHASES entries capture:**
- Train limit per phase (scalar or `{minor: N, major: N, national: N}` hash)
- Available tile colours
- Operating rounds per phase
- Status flags: string array mapping to `STATUS_TEXT`
- Phase-trigger events: same `events:` key as trains

**COMPANIES entries capture:**
- All standard ability types via `abilities:` array (see ABILITIES_REFERENCE.md)

**CORPORATIONS/MINORS entries capture:**
- Type field: `:minor` / `:major` / `:national`
- Token stack and costs
- Home coordinates + city index
- Float percent

**Scalar game constants capture:**
- `CAPITALIZATION` (`:full`, `:incremental`, `:none`)
- `SELL_BUY_ORDER`, `SELL_AFTER`, `SELL_MOVEMENT`, `POOL_SHARE_DROP`
- `MUST_BUY_TRAIN`, `MUST_SELL_IN_BLOCKS`, `EBUY_FROM_OTHERS`, `EBUY_PRES_SWAP`
- `HOME_TOKEN_TIMING`, `TILE_RESERVATION_BLOCKS_OTHERS`, `TRACK_RESTRICTION`
- `BANK_CASH`, `STARTING_CASH`, `CERT_LIMIT`, `CURRENCY_FORMAT_STR`
- `GAME_END_CHECK` hash of reason → timing
- `BANKRUPTCY_ENDS_GAME_AFTER`, `BANKRUPTCY_ALLOWED`
- `TILE_LAYS` array of lay-slot hashes for default entity type
- `ALLOW_REMOVING_TOWNS` boolean
- `STATUS_TEXT`, `EVENTS_TEXT`, `MARKET_TEXT`, `GAME_END_REASONS_TEXT`

**g_1830 is the gold standard for Layer 1**: 95% of its mechanics live in constants.

---

### Layer 2 — Hook Overrides (named `Game::Base` method overrides)

These require Ruby code but follow a clear template: override a named method, replace
its return value or behaviour.

| Hook method | What it controls | 18OE relevance |
|---|---|---|
| `tile_lays(entity)` | Lay budget per entity type and/or phase | Minor/Regional=3pt, Major=6pt, National=9pt |
| `revenue_for(route, stops)` | Route revenue bonus additions | OE bonus, D-train doubling |
| `float_corporation(corp)` | When/how corp receives IPO cash | Standard incremental cap |
| `must_buy_train?(entity)` | Whether corp is forced to buy | `phase.status.include?('train_obligation')` |
| `upgrades_to?(from, to, ...)` | Custom tile upgrade validation | Label restrictions (L, B, S, A, Y, N, C) |
| `check_distance(route, visits)` | Route validity rules | OE route (Constantinople + terminus) |
| `check_other(route)` | Extra route validity rules | OE mandatory run rule |
| `operating_order` | Order entities operate | Share-value sort; nationals in bucket |
| `next_round!` | Inter-round sequencing | Consolidation trigger, national formation |
| `event_xxx!` | Any named phase/train event | National formation, train rusting |
| `num_trains(train)` | Override train count | Level 8 gated after 4th Level 7 purchase |
| `buying_power(entity)` | Available spending budget | President contribution |
| `can_par?(corp, parrer)` | Whether a corp can be parred | Regional float rules |
| `setup` | One-time game initialization | `@minor_available_regions`, obligation sets |
| `new_auction_round` / `operating_round` | Round factory overrides | Consolidation round |
| `action_processed(action)` | Post-action side effects | OE marker placement |
| `sold_out_increase?` | Stock market UP movement | Major/national only |

---

### Layer 3 — Custom Step and Round Classes

These require new Ruby files. They represent mechanics that change which *actions*
are available inside a round, or the order in which entities take those actions.

**Custom Step categories relevant to 18OE:**

| Step category | What it changes | 18OE use |
|---|---|---|
| Waterfall auction | How privates/minors are allocated | `step/waterfall_auction.rb` ✓ exists |
| Minor acquisition | OR step for major to absorb a minor | `step/consolidate.rb` (stub) |
| Merger/conversion | Corp merges and reduction | Phase 5 consolidation |
| Emergency issue/buy | Emergency train purchase flow | Insolvency logic |
| Nationalization (auto-step) | National corp auto-operates | National formation |
| Custom Operating | Extended start_operating / skip logic | `round/operating.rb` ✓ exists |

**Custom Round categories relevant to 18OE:**

| Round type | What it replaces | 18OE use |
|---|---|---|
| Waterfall Auction round | Initial auction round | `step/waterfall_auction.rb` ✓ |
| Consolidation round | New round at Phase 5 | `round/operating.rb` → Consolidation |
| Custom Stock | `sold_out_stock_movement` tracking | UP movement for major/national only |

---

### Layer 4 — Structural Divergence

Mechanics that fundamentally rewire the engine. **18OE has no Layer 4 mechanics.**

The National Revenue system (virtual tokens via `Graph.new(home_as_token: true,
no_blocking: true)`) is unusual but within Layer 3 — it overrides `national_revenue`
and uses an alternative graph rather than rewiring the entire share ownership model.

---

## 2. Event Handler Library

These are method names dispatched from `TRAINS` or `PHASES` `events:` arrays via
`@game.send("event_#{type}!")`. They must exist in game.rb or `base.rb`.

| Event name | What it does | Source |
|---|---|---|
| `close_companies` | Closes all companies with no owner or qualifying criteria | `base.rb` |
| `remove_reservations` | Removes all unsold home reservations | `1846 game.rb` |
| `remove_bonuses` | Removes east-west / bonus tokens | `1846 game.rb` |
| `float_30` / `float_40` / `float_60` | Changes float threshold | `1880 game.rb` |
| `green_minors_available` | Minors can buy green trains | `1867/1861` |
| `majors_can_ipo` | Major corps open for IPO | `1867/1861` |
| `minors_cannot_start` | Minors blocked from starting | `1867/1861` |
| `minors_nationalized` | All remaining minors nationalize | `1867/1861` |
| `trainless_nationalization` | Trainless entities nationalize | `1867/1861` |
| `nationalize_companies` | Privates absorbed into national | `1867/1861` |
| `phase_revenue` | Changes private revenues by phase | `1822 family` |
| `full_capitalisation` | Full cap event | `1822, 1880` |
| `trigger_endgame` | Signals game-end countdown | `1868_wy` |

**18OE events wired:**
- `event_consolidation_triggered!` — fires from PHASES at Phase 5; sets `@consolidation_triggered`

**18OE events still needed:**
- National formation is not a standard `event_xxx!` — it is called directly from
  `Step::BuyTrain#process_buy_train` when the phase changes to 4/6/8.

---

## 3. `tile_lays` Mechanics (from `lib/engine/step/tracker.rb`)

`tile_lays(entity)` returns an **ordered array of lay-slot hashes**. Each slot is one
available lay action, consumed in sequence as `@round.num_laid_track` is incremented.

```ruby
# Slot hash keys:
{ lay: true,                    # true / false / :not_if_upgraded
  upgrade: true,                # true / false / :not_if_upgraded
  cost: 0,                      # extra cost for yellow lays
  upgrade_cost: 0,              # extra cost for upgrades (defaults to :cost)
  cannot_reuse_same_hex: false  # prevents laying on same hex twice
}
```

**18OE tile point system** (from rules §7):

| Entity type | Points/OR | Notes |
|---|---|---|
| Minor / Regional | 3 pts | Yellow = 1pt, Upgrade = 2pt, Metropolis yellow = 2pt, Metro upgrade = 4pt |
| Major | 6 pts | Same tile point costs |
| National | 9 pts | Same tile point costs; exempt from terrain costs |

Note: 18OE's `Step::Track` implements its own `@points_used` counter directly rather
than using the base `tile_lays` slot array. This works but bypasses the standard
`lay_tile_action` slot mechanism. The `get_tile_lay` method returns a point budget
integer rather than a slot array.

---

## 4. How Abilities Work in Ruby

### `when:` field taxonomy
(Complete reference in ABILITIES_REFERENCE.md §4)

- **OR step-scoped** (`'track'`, `'token'`, `'buy_train'`): active during that specific step
- **OR turn-scoped** (`'owning_corp_or_turn'`): active any time the owning corp operates
- **Event-triggered** (`'bought_train'`, `'ran_train'`): used only on `close` abilities

### `count:` enforcement (`lib/engine/ability/base.rb`)

`ability.use!` decrements `@count`. When count reaches zero and `@remove_when_used_up`
is true (default), the ability is removed. `TileLay#use!` tracks `lay_count` and
`upgrade_count` separately.

### `consume_tile_lay:` (on `tile_lay` abilities)

- `consume_tile_lay: true` → routes through `lay_tile_action`, increments
  `@round.num_laid_track`. Ability *consumes* one of the corporation's normal lay slots.
- Without `consume_tile_lay` → routes through `lay_tile` directly. Ability is *extra*
  on top of the normal budget.

---

## 5. OR Step Sequence (standard 18xx)

The base engine uses these steps in this order for each operating entity:

1. `Step::HomeToken` (if entity needs to place home token)
2. `Step::Track` (lay or upgrade tiles)
3. `Step::Token` (place station token)
4. `Step::Route` (run trains, calculate revenue)
5. `Step::Dividend` (pay / withhold / split)
6. `Step::BuyTrain` (buy trains)
7. `Step::BuySellParShares` (buy/sell shares — majors only in 18OE)

18OE adds / will add:
- After `Step::Token`: a Transfer Tokens step (majors only — not yet implemented)
- `Step::Consolidate` (during Consolidation round)
- `Step::ConvertToNational` (when national formation triggered — not yet created)

---

## 6. Share Ownership and Float

**Float condition**: `float_percent` determines when `float_corporation!` is called.
For regionals: 50% president share sold = float. Treasury receives 2× par.

**Stock market movement in base engine:**
- RIGHT on dividend ≥ share value: `share_price_change` returns `{share_direction: :right}`
- LEFT on zero dividend: `{share_direction: :left}`
- DOWN each share sold: `sell_shares_and_change_price` in base engine handles this
- UP on sold-out at SR end: `sold_out_increase?` + `finish_round` → `sold_out_stock_movement`

---

## 7. National Revenue (virtual tokens)

Nationals have virtual tokens in every city/town in their home zone. The engine
mechanism:

```ruby
# Create a national-aware graph:
Graph.new(game, home_as_token: true, no_blocking: true)
```

This treats each home zone hex as if the national has a token there, without placing
physical tokens. The revenue calculation must then:
1. Identify all linked cities/towns in zone via graph connectivity
2. Count linked stops at face value
3. Fill remaining capacity at £60/city or £10/town (no linkage required)

This requires `NATIONAL_REGION_HEXES` to enumerate exactly which hexes are in each zone —
which is now complete (`NATIONAL_REGION_HEXES_COMPLETE = true`). The blocker is that all
city revenues are currently 0, so the graph would compute £0 revenue regardless.

---

*Sources: EVAN_MECHANICS_BRIEF.md, lib/engine/game/base.rb, lib/engine/step/tracker.rb,
lib/engine/ability/base.rb, lib/engine/ability/tile_lay.rb*
