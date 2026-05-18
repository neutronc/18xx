# Trains, Phases & Market

This page covers the three constants that drive a game's economic arc: `TRAINS`, `PHASES`, and `MARKET`. All three are declared in `game.rb`. Together they control how fast the game progresses, when older trains become worthless, and how the stock price grid is structured.

For the entities that run on trains — corporations and companies — see [Corporations & Companies](entities.html).

---

## How They Fit Together

```
Train purchase  →  Phase advances  →  Track colours unlock / Old trains rust / OR count changes
                                    →  Events fire (close_companies, etc.)
```

Every train purchase is checked against the `on:` field in `PHASES`. When the first copy of that train is bought, the phase advances and all consequences apply simultaneously.

The stock market is independent of phases — it moves on share buys and sells throughout the game.

---

## TRAINS

`TRAINS` is an array of hashes defining every train type in the game. The `Engine::Depot` reads it to populate the train supply [`lib/engine/depot.rb:7`].

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Train identifier shown in the UI (e.g. `'2'`, `'D'`) |
| `distance` | Integer or Array | Maximum cities/towns the train may count. Use an array for complex distance rules — see below. |
| `price` | Integer | Purchase price from the depot |

### Common optional fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `num` | Integer | `∞` | Copies in the supply |
| `rusts_on` | String | — | Train name whose first purchase causes this train to rust (removed from play) |
| `obsolete_on` | String | — | Train name whose first purchase makes this train obsolete (still usable, worth less on resale) |
| `available_on` | String | — | Train name that must be purchased before this train appears in the depot |
| `events` | Array\<Hash\> | `[]` | Events fired when the first copy is bought |
| `discount` | Hash | — | Trade-in discounts; keys are train names, values are discount amounts (e.g. `{ '4' => 300 }`) |
| `salvage` | Integer | — | Amount the depot pays back when the train is discarded |
| `variants` | Array\<Hash\> | — | Sub-types selectable at buy time; each variant can override `name:`, `price:`, `distance:`, `rusts_on:` |
| `unlimited` | Boolean | `false` | Train never runs out |
| `multiplier` | Integer | — | Revenue multiplier (some titles double revenue for E-trains) |
| `track_type` | Symbol | `:broad` | Track gauge (`:broad`, `:narrow`, `:dual`) |

### Complex distance arrays

When a train visits different node types with different counting rules, use an array of hashes:

```ruby
distance: [
  { 'nodes' => %w[city offboard], 'pay' => 2, 'visit' => 2 },
  { 'nodes' => ['town'],          'pay' => 99, 'visit' => 99 },
]
```

Each element specifies which node types count toward `pay` (revenue stops) and `visit` (traversal limit). This pattern is used for titles where towns are free to pass through but cities are limited.

### Train events

Events in `events:` are dispatched via `@game.send("event_#{type}!")` when the first copy is bought. Define a matching `event_*!` method in `game.rb` — or rely on a base class implementation.

Common event types defined in `Game::Base`:

| Type | Effect |
|------|--------|
| `close_companies` | Closes all open private companies |
| `remove_reservations` | Removes unsold home reservations |
| `remove_bonuses` | Removes east-west / route bonus tokens |
| `minors_cannot_start` | Blocks minors from starting |
| `majors_can_ipo` | Opens major corporations for IPO |

### Rusts vs Obsolete

- **rusts_on** — train is removed from the game entirely when the named train is first purchased. Corporations that only held rusted trains must buy a replacement (emergency buy).
- **obsolete_on** — train stays in play but is worth less when sold to another corporation. A corporation can still run it.

### Permanent trains

A **permanent train** is any train that has no `rusts_on` key (or `rusts_on: nil`). It stays in play for the rest of the game regardless of phase advances. Titles that need to detect permanent trains at runtime use:

```ruby
train.rusts_on.nil?   # true → permanent
```

Some titles reward the first purchase of a permanent train from the bank (e.g. a stock price bonus). Check `train.owner.is_a?(Engine::Depot)` before calling `buy_train` to distinguish a bank purchase from a corporation-to-corporation trade.

### Example

```ruby
TRAINS = [
  { name: '2', distance: 2, price: 80,  rusts_on: '4', num: 6 },
  { name: '3', distance: 3, price: 180, rusts_on: '6', num: 5 },
  { name: '4', distance: 4, price: 300, rusts_on: 'D', num: 4 },
  {
    name: '5',
    distance: 5,
    price: 450,
    num: 3,
    events: [{ 'type' => 'close_companies' }],
  },
  {
    name: 'D',
    distance: 999,
    price: 1_100,
    num: 20,
    available_on: '6',
    discount: { '4' => 300, '5' => 300, '6' => 300 },
  },
].freeze
```

---

## PHASES

`PHASES` is an array of hashes defining game phases in order. The engine advances through phases as trains are purchased [`lib/engine/phase.rb:19`]. The first phase in the array is the starting phase; it has no `on:` field.

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Phase identifier shown in the UI (e.g. `'2'`, `'D'`) |
| `train_limit` | Integer or Hash | Maximum trains a corporation may own. Use a hash to differentiate entity types: `{ minor: 2, major: 4 }` |
| `tiles` | Array\<Symbol\> | Track colours that may be laid: `:yellow`, `:green`, `:brown`, `:gray` |
| `operating_rounds` | Integer | Number of Operating Rounds between each Stock Round |

### Common optional fields

| Field | Type | Description |
|-------|------|-------------|
| `on` | String | Train name whose first purchase triggers this phase (omit for the initial phase) |
| `status` | Array\<String\> | Status flags that become active (shown in the UI; used by Steps to gate actions) |
| `events` | Array\<Hash\> | Events fired when this phase starts (same `type:` vocabulary as train events) |

### Status flags

Status strings are arbitrary — they appear in the phase indicator in the UI. The base engine recognises several:

| String | Effect |
|--------|--------|
| `'can_buy_companies'` | Corporations may buy companies from the bank |
| `'can_buy_companies_from_other_players'` | Players may trade companies between themselves |

Custom status strings can be added freely. Check them in Steps with `@game.phase.status.include?('my_flag')`.

### Common phase patterns

**Standard 18xx escalation** — one phase per train tier, each adding track colours and increasing OR count:

```ruby
PHASES = [
  { name: '2', train_limit: 4, tiles: [:yellow],              operating_rounds: 1 },
  { name: '3', on: '3', train_limit: 4, tiles: %i[yellow green],         operating_rounds: 2, status: ['can_buy_companies'] },
  { name: '4', on: '4', train_limit: 3, tiles: %i[yellow green],         operating_rounds: 2, status: ['can_buy_companies'] },
  { name: '5', on: '5', train_limit: 2, tiles: %i[yellow green brown],   operating_rounds: 3, events: [{ 'type' => 'close_companies' }] },
  { name: '6', on: '6', train_limit: 2, tiles: %i[yellow green brown],   operating_rounds: 3 },
  { name: 'D', on: 'D', train_limit: 2, tiles: %i[yellow green brown gray], operating_rounds: 3 },
].freeze
```

**Reducing train limit** — important for late-game engine pressure. Check production titles for the exact numbers that create interesting decisions.

---

## MARKET

`MARKET` is a two-dimensional array of strings representing the stock price grid [`lib/engine/stock_market.rb:7`]. Rows run top (high) to bottom (low); columns run left (low) to right (high).

### Cell format

Each cell is a price string optionally followed by suffix characters:

| Suffix | Meaning |
|--------|---------|
| `y` | Yellow zone — corporation may be liquidated (title-specific) |
| `p` | Par value row — valid par prices are marked with `p` |
| `b` | Ledge (brown zone) — corporation stays here; does not fall further |
| `o` | Orange — title-specific; often triggers an event |
| `j` | Black — corporation is closed or bankrupt |
| (none) | Normal cell |

### Par prices

A corporation's par price must land on a `p`-marked cell. The engine reads these automatically from the MARKET definition — no separate list needed.

### Example (1830 excerpt)

```ruby
MARKET = [
  %w[60y 67 71 76 82 90 100p 112 126 142 160 180 200 225 250 275 300 325 350],
  %w[53y 60y 66 70 76 82  90p 100 112 126 142 160 180 200 220 240 260 280 300],
  %w[46y 55y 60y 65 70 76  82p  90 100 112 126 142 160 180 200 220 240 260 280],
  %w[39y 48y 55y 60 65 70   76   82  90 100 112 126 142 160 180 200 220 240],
  %w[32y 41y 48y 55 60 65   70   76  82  90 100 112 126 142 160 180],
  %w[25y 34y 41y 48 55 60   65   70  76   82  90 100 112 126],
  %w[18y 27y 34y 41 48 55   60   65   70   76  82  90 100],
  %w[10y 20y 27y 34 41 48   55   60   65   70  76  82],
].freeze
```

### Market movement constants

These constants in `game.rb` control how the stock marker moves:

| Constant | Type | Description |
|----------|------|-------------|
| `SELL_MOVEMENT` | Symbol | Direction on sell: `:down_share` (one step per share sold), `:left_block` (one step per block), `:none` |
| `POOL_SHARE_DROP` | Symbol | Where market-pool shares go when sold: `:bank`, `:left`, `:down` |
| `SELL_BUY_ORDER` | Symbol | `:sell_buy_sell` — sell, buy, sell again; `:sell_buy` — sell then buy only |
| `SOLD_OUT_TOP_X_CREATES_WEDGE` | Integer | If all shares sold out and price is in top N, creates a price wedge |

---

## Financial Constants

These constants in `game.rb` control the economy.

| Constant | Type | Description |
|----------|------|-------------|
| `BANK_CASH` | Integer | Total bank cash; game may end when this reaches zero |
| `CERT_LIMIT` | Hash | Player count → maximum certificates per player, e.g. `{ 3 => 20, 4 => 16 }` |
| `STARTING_CASH` | Hash | Player count → starting cash per player |
| `CAPITALIZATION` | Symbol | `:full` — corporation receives all IPO proceeds at float; `:incremental` — proceeds added as shares are sold |
| `MUST_SELL_IN_BLOCKS` | Boolean | If `true`, player must sell all shares of a corporation at once in the SR |
| `CURRENCY_FORMAT_STR` | String | Format string: `'$%s'` for dollars, `'£%s'` for pounds, `'M%s'` for marks |
| `SELL_AFTER` | Symbol | When players may first sell: `:after_sr_floated`, `:operate`, `:p_any_operate` |
| `MUST_BUY_TRAIN` | Symbol | When corporations must buy a train: `:always`, `:route`, `false` |
| `EBUY_FROM_OTHERS` | Boolean | Whether a corporation can emergency-buy trains from other corporations |
| `GAME_END_CHECK` | Hash | End conditions, e.g. `{ bank: :full_or, stock_market: :immediate }` |

### Looking up reference values

Before inventing your own numbers, check a production title that plays similarly:

| If your game is like… | Check |
|----------------------|-------|
| Classic 18xx (1830-style) | `lib/engine/game/g_1830/game.rb` |
| Incremental capitalisation | `lib/engine/game/g_1846/game.rb` |
| Short, sharp (1889-style) | `lib/engine/game/g_1889/game.rb` |
| Large map with minors | `lib/engine/game/g_1867/game.rb` |

---

## What's Next

- Defining map hexes, tile supply, and location names: [Map Configuration](map.html)
- How Steps use phase status to gate actions: [Rounds & Steps](round-step-system.html)
- Ability types that interact with trains and phases: [Abilities](abilities.html)
- Testing the economic arc: [Testing Your Game](testing.html)

---
*Version: 2026-05-08 — derived from `lib/engine/depot.rb`, `lib/engine/phase.rb`, `lib/engine/stock_market.rb`, `lib/engine/train.rb`, `lib/engine/game/base.rb`, `lib/engine/game/g_1830/game.rb`.*
