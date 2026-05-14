# Game Engine Reference

The 18xx engine is a collection of plain Ruby classes under `lib/engine/`. The same code runs server-side in MRI Ruby and client-side as JavaScript compiled by Opal. This page lists the major classes and their responsibilities.

## Core Classes

### `Engine::Game::Base` [`lib/engine/game/base.rb:91`]

The root game object. Holds every other engine object and drives the game flow. Key responsibilities:

| Method / constant | Purpose |
|-------------------|---------|
| `initialize` (`:566`) | Builds all objects; replays saved Actions on startup |
| `initialize_actions` (`:819`) | Loads persisted Actions and applies them in order |
| `process_action` (`:838`) | Entry point for a new player move; delegates to the active Round |
| `next_round!` (`:2921`) | Transitions to the next Round after the current one finishes |
| `game_end_check` (`:2970`) | Tests all end conditions after every Action |
| `new_stock_round` (`:3177`) | Factory method for a new Stock Round |
| `new_operating_round` (`:3192`) | Factory method for a new Operating Round |

Every game title overrides constants in this class: `TRAINS`, `CORPORATIONS`, `PHASES`, `HEXES`, `COMPANIES`, `PLAYER_RANGE`, and many others.

### `Engine::Round::Base` [`lib/engine/round/base.rb:12`]

Container for a turn segment. Holds an ordered list of Steps and the Entity queue.

| Method | Purpose |
|--------|---------|
| `initialize` (`:22`) | Builds Steps; merges `DEFAULT_STEPS` with title-specific steps |
| `process_action` (`:75`) | Finds the first active, blocking Step that handles the action and calls it |
| `active_step` (`:136`) | Returns the first blocking, non-finished Step |

Concrete subclasses: `Round::Stock`, `Round::Operating`, `Round::Auction`.

### `Engine::Step::Base` [`lib/engine/step/base.rb:8`]

Atomic decision unit. Each Step declares which action types it handles and processes them.

| Method | Purpose |
|--------|---------|
| `actions(_entity)` (`:31`) | Returns the list of action-type strings this Step allows |
| `blocking?` (`:84`) | Returns true if this Step prevents lower-priority Steps from acting |
| `process_*` | Handler called by the Round — e.g. `process_buy_shares`, `process_lay_tile` |

### `Engine::Phase` [`lib/engine/phase.rb:6`]

Tracks the current game phase. Advances when a train of the triggering type is purchased [`lib/engine/phase.rb:19`]. Controls which track types are legal, the number of Operating Rounds per set, and which trains rust.

### `Engine::Bank` [`lib/engine/bank.rb:8`]

Central cash reserve. `broken?` (`:38`) returns true when cash drops to zero or below; this may trigger the `bank` end condition depending on the title.

### `Engine::Depot` [`lib/engine/depot.rb:7`]

Supply of available trains. `available` (`:114`) returns trains purchasable by a given Corporation. Handles train export and reclaiming.

### `Engine::StockMarket` [`lib/engine/stock_market.rb:7`]

Two-dimensional price grid. Movement methods (`move_right`, `move_up`, `move_down`, `move_left`, diagonal variants) adjust a Corporation's price marker. Special cells (top row, right ledge) can trigger game-end or Corporation closure.

### `Engine::Graph` [`lib/engine/graph.rb:6`]

Computes the routing graph from the current tile layout. `connected_hexes` (`:98`) and `connected_nodes` (`:103`) return the set of Hexes/nodes reachable from a Corporation's tokens. Used by route-validation Steps.

### `Engine::Action::Base` [`lib/engine/action/base.rb:1`]

Base class for all persisted moves. Every concrete action (e.g. `Action::BuyShares`, `Action::LayTile`) stores an entity reference, an action type string, and type-specific parameters as JSON.

## Key Supporting Classes

| Class | File | Role |
|-------|------|------|
| `Player` | `lib/engine/player.rb:1` | Cash, certificates, name |
| `Corporation` | `lib/engine/corporation.rb:1` | Shares, tokens, trains, cash, president |
| `Company` | `lib/engine/company.rb:1` | Private company; grants special abilities |
| `Minor` | `lib/engine/minor.rb:1` | Subsidiary; owns shares, runs routes |
| `SharePrice` | `lib/engine/share_price.rb:1` | A cell on the StockMarket; holds par and current price |
| `Hex` | `lib/engine/hex.rb:1` | One hexagon on the map; holds a Tile |
| `Tile` | `lib/engine/tile.rb:1` | Track layout, cities, towns |
| `Token` | `lib/engine/token.rb:1` | Corporation presence on a city |
| `Train` | `lib/engine/train.rb:1` | Reach (distance), phase trigger |

## Title Registration

`lib/engine.rb:17-24` builds `GAME_META_BY_TITLE`, a hash that maps title strings (e.g. `"1830"`) to `Meta` modules. The API and frontend use this map to instantiate the correct game class.

---

## Implementation Layer Taxonomy

When adding mechanics to a game title, use this four-layer model to identify where the code lives and how much effort is required.

### Layer 1 — Pure Configuration (constants only)

No custom Ruby methods — only values in `TRAINS`, `PHASES`, `COMPANIES`, `CORPORATIONS`, or scalar game constants. `g_1830` is the gold standard; 95% of its mechanics live in constants.

**`TRAINS` entries capture:**

| Field | Purpose |
|-------|---------|
| `name:`, `distance:`, `price:`, `count:` | Train identity and roster |
| `rusts_on:`, `obsolete_on:` | Rust/obsolete triggers |
| `available_on:` | Gate — train only appears after another is bought |
| `discount:` | Hash of discounts, e.g. `{'2' => 30}` |
| `variants:` | Sub-types selectable at buy time; each can have own `rusts_on:` and `multiplier:` |
| `events:` | Phase-transition events dispatched to `event_xxx!` |
| `distance:` (array) | Multi-node specs: `[{'nodes'=>[...], 'pay'=>N, 'visit'=>N}]` |

**`PHASES` entries capture:** train limit (scalar or `{minor: N, major: N}` hash), available tile colours, operating rounds per phase, status flag strings, and phase-trigger `events:`.

**Key scalar game constants:**

| Constant | Controls |
|----------|---------|
| `CAPITALIZATION` | `:full`, `:incremental`, `:none` |
| `SELL_BUY_ORDER`, `SELL_AFTER`, `SELL_MOVEMENT`, `POOL_SHARE_DROP` | Share sale mechanics |
| `MUST_BUY_TRAIN`, `EBUY_FROM_OTHERS`, `EBUY_PRES_SWAP` | Emergency buy rules |
| `HOME_TOKEN_TIMING` | When home tokens are placed |
| `TILE_RESERVATION_BLOCKS_OTHERS`, `TRACK_RESTRICTION` | Tile lay restrictions |
| `BANK_CASH`, `STARTING_CASH`, `CERT_LIMIT` | Financial limits |
| `GAME_END_CHECK` | Hash of reason → timing pairs |
| `TILE_LAYS` | Default lay-slot array for each entity type |
| `STATUS_TEXT`, `EVENTS_TEXT`, `MARKET_TEXT` | UI text for phases and events |

### Layer 2 — Hook Overrides (named `Game::Base` method overrides)

Require Ruby code but follow a clear template: override a named method, replace its return value or behaviour.

| Hook method | What it controls |
|-------------|-----------------|
| `tile_lays(entity)` | Lay budget per entity type and/or phase |
| `revenue_for(route, stops)` | Route revenue bonus additions |
| `float_corporation(corp)` | When/how a corporation receives IPO cash |
| `must_buy_train?(entity)` | Whether a corporation is forced to buy a train |
| `upgrades_to?(from, to, ...)` | Custom tile upgrade validation |
| `check_distance(route, visits)` | Route validity rules |
| `check_other(route)` | Extra route validity rules |
| `operating_order` | Order entities operate in an OR |
| `next_round!` | Inter-round sequencing (see Guideline 12) |
| `event_xxx!` | Named phase/train event handler |
| `num_trains(train)` | Override train count |
| `buying_power(entity)` | Available spending budget |
| `can_par?(corp, parrer)` | Whether a corporation can be parred |
| `setup` | One-time game initialisation |
| `action_processed(action)` | Post-action side effects |
| `sold_out_increase?` | Stock market UP movement on sold-out |

### Layer 3 — Custom Step and Round Classes

Require new Ruby files. Used when a mechanic changes which *actions* are available or the order in which entities take them.

**Custom Step categories:**

| Category | 18xx use case |
|----------|--------------|
| Waterfall auction | Initial private/minor allocation |
| Minor acquisition | OR step for a major to absorb a minor |
| Merger/conversion | Corporation merges and conversion |
| Emergency issue/buy | Emergency train purchase flow |
| Nationalisation (auto-step) | National corporation auto-operates |

**Custom Round categories:**

| Category | Replaces |
|----------|---------|
| Waterfall auction round | Initial auction round |
| Consolidation round | New round triggered at a phase boundary |
| Custom Stock round | Extended SR with special movement tracking |

### Layer 4 — Structural Divergence

Mechanics that fundamentally rewire the engine. Rare; avoid unless no other approach is possible.

---

## Event Handler Library

Event method names are dispatched from `TRAINS` or `PHASES` `events:` arrays via `@game.send("event_#{type}!")`. They must exist in `game.rb` or `base.rb`.

| Event name | What it does |
|------------|-------------|
| `close_companies` | Closes all companies with no owner or qualifying criteria |
| `remove_reservations` | Removes all unsold home reservations |
| `remove_bonuses` | Removes east-west / bonus tokens |
| `float_30` / `float_40` / `float_60` | Changes float threshold during the game |
| `green_minors_available` | Allows minors to buy green trains |
| `majors_can_ipo` | Opens major corporations for IPO |
| `minors_cannot_start` | Blocks minors from starting |
| `minors_nationalized` | All remaining minors nationalise |
| `trainless_nationalization` | Trainless entities nationalise |
| `nationalize_companies` | Privates are absorbed into a national |
| `phase_revenue` | Changes private revenues by phase |
| `full_capitalisation` | Full capitalisation event |
| `trigger_endgame` | Signals game-end countdown |

---

## `tile_lays` Mechanics

`tile_lays(entity)` [`lib/engine/step/tracker.rb`] returns an **ordered array of lay-slot hashes**. Each slot is one available lay action, consumed in sequence as `@round.num_laid_track` is incremented.

```ruby
# Lay-slot hash keys:
{
  lay: true,                    # true / false / :not_if_upgraded
  upgrade: true,                # true / false / :not_if_upgraded
  cost: 0,                      # extra cost for yellow lays
  upgrade_cost: 0,              # extra cost for upgrades (defaults to :cost)
  cannot_reuse_same_hex: false  # prevents laying on the same hex twice
}
```

The `TILE_LAYS` constant defines the default slots for the base entity type. Override `tile_lays(entity)` in `game.rb` to return a different array based on entity type or current phase.

---

## Share Ownership and Float

**Float condition:** `float_percent` determines when `float_corporation!` is called. For most entities: when the combined sold shares reach the threshold, the treasury receives the capitalisation.

**Stock market movement triggers:**

| Trigger | Direction |
|---------|-----------|
| Dividend ≥ share price | RIGHT (`share_direction: :right`) |
| Zero dividend | LEFT (`share_direction: :left`) |
| Each share sold | DOWN — handled by `sell_shares_and_change_price` |
| Sold out at SR end | UP — triggered by `sold_out_increase?` + `finish_round` → `sold_out_stock_movement` |

Override `sold_out_increase?` in `game.rb` to restrict the UP movement to specific entity types (e.g., majors and nationals only).

---

## National Revenue — Virtual Tokens

Nationals in some titles have virtual tokens in every city/town in their home zone. The engine mechanism:

```ruby
# Create a national-aware graph (no physical tokens needed):
Graph.new(game, home_as_token: true, no_blocking: true)
```

This treats each home zone hex as if the national has a token there. Revenue calculation then:

1. Identifies all linked cities/towns in the zone via graph connectivity.
2. Counts linked stops at face value.
3. Fills remaining train capacity at flat rates for unlinked stops (game-specific).

Requires a `NATIONAL_REGION_HEXES` constant enumerating exactly which hexes belong to each national's zone.

---

## What's next

- How an action travels through the engine: [Core Flow](kernablauf.html)
- Round and Step interaction in depth: [Round/Step System](round-step-system.html)
- Ability types and `when:` vocabulary: [Ability Types Reference](abilities.html)
- Tile DSL and development routes: [Tile Reference](tiles.html)
- Coding patterns and guidelines: [Coding Guidelines](coding-guidelines.html)
- System topology: [Architecture Overview](architecture.html)

---
*Version: 2026-05-08 — derived from `lib/engine/game/base.rb`, `lib/engine/round/base.rb`, `lib/engine/step/base.rb`, `lib/engine/step/tracker.rb`, `lib/engine/phase.rb`, `lib/engine/bank.rb`, `lib/engine/depot.rb`, `lib/engine/stock_market.rb`, `lib/engine/graph.rb`.*
