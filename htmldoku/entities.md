# Corporations & Companies

This page documents the fields for `CORPORATIONS` and `COMPANIES` — the two entity arrays that define who plays, who invests, and what special abilities are in the game. Both are defined in `entities.rb` and included into the main `Game` class.

For trains, phases, and market configuration see [Trains, Phases & Market](trains-phases.html).

---

## CORPORATIONS

`CORPORATIONS` is an array of hashes, one per major corporation. Each hash is read by `Engine::Game::Base` during initialisation to construct `Engine::Corporation` objects [`lib/engine/corporation.rb:1`].

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `sym` | String | Short identifier shown on share certificates (e.g. `'PRR'`) |
| `name` | String | Full display name |
| `logo` | String | Path under `public/logos/` without the `.svg` extension (e.g. `'1830/PRR'`) |
| `tokens` | Array\<Integer\> | Token cost at each city; first element is always `0` (home token is free) |
| `coordinates` | String | Hex coordinate for the home token (e.g. `'H12'`) |
| `color` | String | CSS colour string for the corporation card |

### Common optional fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `float_percent` | Integer | `60` | Percentage of shares sold before the corporation floats and receives treasury cash |
| `max_ownership_percent` | Integer | `60` | Maximum percentage of shares a single player may hold |
| `type` | Symbol | `:major` | Corporation type; affects which Steps are available and how revenue is split |
| `simple_logo` | String | — | Simplified logo path for small icon views |
| `shares` | Array\<Integer\> | default IPO spread | Custom share distribution percentages |
| `always_market_price` | Boolean | `false` | If `true`, all purchases use market price rather than IPO price |
| `capitalization` | Symbol | `CAPITALIZATION` constant | Per-corporation override for `:full` or `:incremental` capitalisation |
| `president_percent` | Integer | `20` | Size of the president's certificate |
| `par_via_exchange` | Boolean | `false` | Corporation is pared by exchanging a private company |
| `reservation_color` | String | — | Hex colour used for the IPO reservation |
| `city` | Integer | — | Which city slot on the home hex receives the home token (for multi-city hexes) |
| `second_city` | String | — | Second token coordinate for corporations that start with two tokens |
| `abilities` | Array | `[]` | Corporation-level abilities (same structure as company abilities) |

### Where to look for more options

Many titles add custom corporation types or fields. Before adding new fields, check:

- `lib/engine/corporation.rb` — full list of attributes read from the hash
- `lib/engine/game/g_1830/entities.rb` — canonical 1830 example
- `lib/engine/game/g_1867/entities.rb` — title with both minors and majors

### Example

```ruby
CORPORATIONS = [
  {
    float_percent: 60,
    sym:          'PRR',
    name:         'Pennsylvania Railroad',
    logo:         '1830/PRR',
    simple_logo:  '1830/PRR.alt',
    tokens:       [0, 40, 100, 100],
    coordinates:  'H12',
    color:        '#32763f',
  },
].freeze
```

---

## COMPANIES

`COMPANIES` is an array of hashes defining private companies (privates). Each hash becomes an `Engine::Company` object [`lib/engine/company.rb:1`]. Privates are auctioned or distributed at the start of the game.

### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | String | Full display name |
| `sym` | String | Short identifier (e.g. `'CS'`) |
| `value` | Integer | Face value / purchase price |
| `revenue` | Integer | Income collected each OR while player-owned |

### Common optional fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `desc` | String | `''` | Text description shown in the UI |
| `abilities` | Array | `[]` | Special abilities granted to the owner |
| `color` | String | `nil` | Card background colour (nil uses the default yellow) |
| `min_price` | Integer | `value / 2` rounded up | Minimum resale price to another player |
| `max_price` | Integer | `value * 2` | Maximum resale price |
| `type` | Symbol | — | Company type (used by some custom Steps to filter) |
| `treasury` | Integer | `value` | Starting cash inside the company (rare) |
| `discount` | Integer | `0` | Reduces the minimum auction bid |

### Abilities

Each ability is a hash with at least a `type:` key. Common types:

| Type | Key fields | Effect |
|------|-----------|--------|
| `blocks_hexes` | `owner_type:`, `hexes:` | Prevents corporations from placing tokens on listed hexes while condition holds |
| `tile_lay` | `owner_type:`, `hexes:`, `tiles:`, `when:`, `count:` | Grants a free or discounted tile lay on specified hexes |
| `teleport` | `owner_type:`, `tiles:`, `hexes:` | Allows token placement without connectivity |
| `exchange` | `corporation:`, `owner_type:`, `when:`, `from:` | Allows exchange for a share of the named corporation |
| `shares` | `shares:` | Purchaser automatically receives specified shares |
| `no_buy` | — | Company cannot be sold to corporations |
| `close` | `when:`, `corporation:` | Closes the company when the condition is met |
| `revenue_change` | `revenue:`, `when:` | Changes revenue at a phase trigger |

For the full ability vocabulary see [Ability Types](abilities.html).

### Example

```ruby
COMPANIES = [
  {
    name:    'Champlain & St.Lawrence',
    sym:     'CS',
    value:   40,
    revenue: 10,
    desc:    'The owning corporation may lay a free tile on B20.',
    abilities: [
      { type: 'blocks_hexes', owner_type: 'player', hexes: ['B20'] },
      {
        type: 'tile_lay',
        owner_type: 'corporation',
        hexes: ['B20'],
        tiles: %w[3 4 58],
        when: 'owning_corp_or_turn',
        count: 1,
      },
    ],
    color: nil,
  },
].freeze
```

---

## What's Next

- Train, phase, and market configuration: [Trains, Phases & Market](trains-phases.html)
- Map and hex layout: [Map Configuration](map.html)
- Complete ability type reference: [Ability Types](abilities.html)
- Step-by-step implementation guide: [Game Structure](game-implementation.html)

---
*Version: 2026-05-08 — derived from `lib/engine/corporation.rb`, `lib/engine/company.rb`, `lib/engine/game/g_1830/entities.rb`.*
