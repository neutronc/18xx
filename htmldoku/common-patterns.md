# Common Implementation Patterns

Short recipes for the most frequently needed game mechanics. Each pattern names the hook to override, shows a minimal implementation, and points to a production title that uses it.

---

## Revenue Patterns

### Hex revenue bonus

A route that visits a specific hex earns extra revenue.

```ruby
# In game.rb
BONUSES = { 'F8' => 20, 'D4' => 30 }.freeze

def revenue_for(route, stops)
  super + stops.sum { |s| BONUSES.fetch(s.hex.id, 0) }
end
```

Reference: `lib/engine/game/g_18co/game.rb`

---

### East-west route bonus

A corporation earns a bonus when its route set collectively spans east and west edges.

```ruby
EAST_HEXES = %w[A3 A5 A7].freeze
WEST_HEXES = %w[M3 M5 M7].freeze

def routes_revenue(routes)
  base = routes.sum(&:revenue)
  all_stops = routes.flat_map(&:stops).map { |s| s.hex.id }
  bonus = (all_stops & EAST_HEXES).any? && (all_stops & WEST_HEXES).any? ? 80 : 0
  base + bonus
end
```

Reference: `lib/engine/game/g_1830/game.rb`

---

### Revenue multiplier for a special train

Double the revenue of E-trains or other high-tier trains.

```ruby
def revenue_for(route, stops)
  base = super
  route.train.name == 'E' ? base * 2 : base
end
```

---

## Route Validation Patterns

### Mandatory home-city inclusion

Every route must pass through the corporation's home city.

```ruby
def check_other(route)
  home = route.corporation.coordinates
  return if route.stops.any? { |s| s.hex.id == home }
  raise GameError, "#{route.corporation.name} must include its home city"
end
```

Reference: `lib/engine/game/g_18chesapeake/game.rb`

---

### Route must reach an off-map hex

```ruby
REQUIRED_EXIT = %w[A1 A3].freeze   # at least one route must end here

def check_route_combination(routes)
  exits = routes.flat_map(&:stops).select { |s| s.hex.offboard? }.map { |s| s.hex.id }
  return if (exits & REQUIRED_EXIT).any?
  raise GameError, 'At least one route must reach an off-map space'
end
```

---

### Limit on routes sharing the same city

Standard 18xx rules prohibit two of the same corporation's routes from counting the same city twice.

```ruby
def check_route_combination(routes)
  # Base engine already checks path overlap; add city-level check:
  city_stops = routes.flat_map { |r| r.stops.select(&:city?) }
  dupes = city_stops.group_by(&:itself).select { |_, v| v.size > 1 }.keys
  raise GameError, "Route shares city #{dupes.first.hex.id}" if dupes.any?
end
```

---

## Dividend Patterns

### Half-pay dividend type

Add a "half" option alongside payout and withhold.

```ruby
# In step/dividend.rb (or a title-specific subclass)
DIVIDEND_TYPES = %i[payout half withhold].freeze

def dividend_types
  DIVIDEND_TYPES
end

def half(entity, revenue)
  per_share = (revenue / 2 / entity.total_shares).floor
  { corporation: revenue - (per_share * entity.total_shares), per_share: per_share }
end
```

Then register your step in `operating_round`:

```ruby
require_relative 'step/dividend'

def operating_round(round_num)
  Round::Operating.new(self, [
    # ... other steps ...
    G8888::Step::Dividend,
    # ...
  ], round_num: round_num)
end
```

Reference: `lib/engine/game/g_1822/step/dividend.rb`

---

### Stock price holds on half-pay

```ruby
# In the custom Dividend step
def share_price_change(entity, revenue)
  case @dividends_paid
  when :payout  then { share_direction: :right, share_times: 1 }
  when :half    then {}   # no movement
  when :withhold then { share_direction: :left, share_times: 1 }
  end
end
```

---

## Tile Lay Patterns

### Extra free tile lay via company ability

Give a private company the ability to lay one free tile on a specific hex. No custom Step needed — the `tile_lay` ability and `Step::SpecialTrack` handle it automatically.

```ruby
# In entities.rb COMPANIES
{
  name:    'Bavarian Central Railway',
  sym:     'BCR',
  value:   80,
  revenue: 15,
  abilities: [
    { type: 'blocks_hexes', owner_type: 'player', hexes: ['D8'] },
    {
      type:       'tile_lay',
      owner_type: 'corporation',
      hexes:      ['D8'],
      tiles:      %w[3 4 58],
      when:       'owning_corp_or_turn',
      count:      1,
    },
  ],
  color: nil,
}
```

The owning corporation gets one free tile lay on D8 per OR. `Step::SpecialTrack` must be in your `operating_round` step list (it is in the default list).

---

### `tile_lays` slot mechanics

`tile_lays(entity)` returns an **ordered array of lay-slot hashes**. Each slot is one available lay action, consumed in sequence as `@round.num_laid_track` is incremented.

```ruby
# Slot hash keys:
{ lay: true,                    # true / false / :not_if_upgraded
  upgrade: true,                # true / false / :not_if_upgraded
  cost: 0,                      # extra cost for yellow lays
  upgrade_cost: 0,              # extra cost for upgrades (defaults to :cost)
  cannot_reuse_same_hex: false  # prevents laying on same hex twice
}
```

`ability.use!` on a `tile_lay` ability routes through `lay_tile_action` when `consume_tile_lay: true` (consumes a slot) or through `lay_tile` directly when omitted (extra on top of the normal budget).

---

### Corporation gets two tile lays per OR

```ruby
# In game.rb
TILE_LAYS = [
  { lay: true, upgrade: true },
  { lay: :not_if_upgraded, upgrade: false, cost: 20 },
].freeze
```

The second element is the second lay: `lay: :not_if_upgraded` means the second action may only lay a new tile (not upgrade an existing one). `cost: 20` charges $20 for the second lay.

Reference: `lib/engine/game/g_1849/game.rb`

---

## Token Patterns

### Free token placement via teleport ability

A private company grants the owning corporation a free token placement anywhere on the board, bypassing connectivity.

```ruby
# In entities.rb COMPANIES
{
  name: 'Steamboat Company',
  sym:  'SBC',
  value: 30,
  revenue: 5,
  abilities: [
    {
      type:       'teleport',
      owner_type: 'corporation',
      tiles:      %w[57 14 15],
      hexes:      [],          # empty = any hex
    },
  ],
  color: nil,
}
```

`Step::SpecialToken` must be in your `operating_round` step list.

---

### Corporation starts with two home tokens

```ruby
# In entities.rb CORPORATIONS
{
  sym:         'PRR',
  coordinates: 'H12',
  second_city: 'F14',   # second home token placed here at game start
  # ...
}
```

---

## Phase & Event Patterns

### Custom event method

When a train fires an event, the engine calls `game.send("event_#{type}!")`. Define the method in `game.rb`:

```ruby
# Fired when the first 5-train is purchased
def event_close_companies!
  @log << '-- Event: Private companies close --'
  super
end
```

Call `super` to run the base class logic (closing companies, etc.) before or after your additions.

---

### Phase-gated action in a Step

Check the current phase status inside a Step's `actions` method to enable or disable options:

```ruby
def actions(entity)
  return [] unless @game.phase.status.include?('can_buy_companies')
  super
end
```

---

## Operating Order Patterns

### Custom operating order

Override `operating_order` in `game.rb`:

```ruby
# Corporations with destination tokens operate before others
def operating_order
  without_dest, with_dest = super.partition { |c| !destination_reached?(c) }
  without_dest + with_dest
end
```

Reference: `lib/engine/game/g_1889/game.rb`

---

### Minors operate before majors

The default `operating_order` already does this. To reverse it:

```ruby
def operating_order
  floated_majors = corporations.select { |c| c.type == :major && c.floated? }
  floated_minors = minors.select(&:floated?)
  (floated_majors + floated_minors).sort_by { |c| [c.share_price.price, c.share_price.corporations.index(c)] }.reverse
end
```

---

## Bond / Director Liability Patterns

### Director personal bond (Schuldschein)

A director takes on a personal debt (bond) tied to a corporation. The bond blocks the director from selling that corporation's shares and reduces their end-game score if unpaid.

```ruby
# In game.rb

def setup
  @corp_bonds = {}   # corp_id => Integer (outstanding amount)
  @buyback_done = {} # corp_id => player entity (original director)
end

# Bond amount: 5 × market price, rounded up to nearest $100.
def buyback_bond_amount(corporation)
  (corporation.share_price.price * 5).ceil(-2)
end

def bond?(corporation)
  (@corp_bonds[corporation.id] || 0).positive?
end

def bond_amount(corporation)
  @corp_bonds[corporation.id] || 0
end

# Record the bond — safe to call only once per corporation (no-op thereafter).
def record_bond!(corporation)
  return if @buyback_done.key?(corporation.id)

  amount = buyback_bond_amount(corporation)
  director = corporation.owner
  @corp_bonds[corporation.id]   = amount
  @buyback_done[corporation.id] = director
  @log << "#{corporation.name}: #{director.name} takes #{format_currency(amount)} bond"
end

# Full repayment only; no-op if corp cash is insufficient.
def repay_bond!(corporation)
  owed = bond_amount(corporation)
  return unless owed.positive? && corporation.cash >= owed

  corporation.spend(owed, @bank)
  @corp_bonds[corporation.id] = 0
end

# Penalty cert: director who issued a bond loses 1 cert slot for the game.
def num_certs(entity)
  super + (@buyback_done || {}).values.count { |d| d == entity }
end

# Game-end: apply bond as personal score penalty.
def end_game!(reason = nil)
  @corp_bonds.each do |corp_id, amount|
    next unless amount.positive?

    director = @buyback_done[corp_id]
    next unless director.respond_to?(:penalty)

    director.penalty = (director.penalty || 0) + amount
  end
  super
end
```

Block the director from selling while the bond is active in the stock-round step:

```ruby
# In step/buy_sell_par_shares.rb
def can_sell?(entity, bundle)
  return false if bundle && bundle.corporation.president?(entity) &&
                  @game.bond?(bundle.corporation)

  super
end
```

`player.penalty` is already subtracted in `Player#value`, so no further score hook is needed.

Reference: `lib/engine/game/g_1862_usa_canada/game.rb`, `step/buy_sell_par_shares.rb`

---

### Share halving — cert transformation on buyback

When a corporation executes a buyback, halve all outstanding certs and create a non-reissuable 50% treasury cert. Update `forced_share_percent` and `price_multiplier` so proportional pricing stays correct.

```ruby
# In game.rb
def halve_shares!(corporation)
  # Guard: already halved if the 50% non-buyable cert exists.
  return if corporation.shares_of(corporation).any? { |s| s.percent == 50 && !s.buyable }

  all_shares = @_shares.values.select { |s| s.corporation == corporation }
  corporation.share_holders.clear

  next_idx    = all_shares.map(&:index).max + 1
  split_certs = []

  all_shares.each do |share|
    if share.percent == 30
      # 30% president → 10% cert + new 5% cert (same owner)
      share.percent = 10
      extra = Share.new(corporation, owner: share.owner, percent: 5, index: next_idx)
      next_idx += 1
      split_certs << extra
    else
      share.percent /= 2  # 20→10, 10→5
    end
    corporation.share_holders[share.owner] += share.percent
  end

  split_certs.each do |cert|
    cert.owner.shares_by_corporation[corporation] << cert
    corporation.share_holders[cert.owner] += cert.percent
    @_shares[cert.id] = cert
  end

  # Proportional pricing: a 5% cert now costs market_price × 0.5.
  corporation.forced_share_percent = 5
  corporation.instance_variable_set(:@price_multiplier, 0.5)

  # Non-reissuable 50% treasury cert.
  treasury = Share.new(corporation, owner: corporation, percent: 50, index: next_idx)
  treasury.buyable = false
  treasury.counts_for_limit = false
  corporation.share_holders[corporation] += 50
  corporation.shares_by_corporation[corporation] << treasury
  @_shares[treasury.id] = treasury

  update_cache(:shares)
end
```

Route the treasury cert's dividends back into the corporation by overriding `corporation_dividends` in the title's Dividend step:

```ruby
# In step/dividend.rb
def corporation_dividends(entity, per_share)
  # Non-buyable holdings (the 50% buyback cert) earn revenue back into the corp.
  # Returns 0 for corporations that have never done a buyback.
  treasury_units = entity.shares_of(entity)
                         .reject(&:buyable)
                         .sum { |s| s.num_shares(ceil: false) }
  super + (treasury_units * per_share).ceil
end
```

**Key invariants after halving:**
- `share_holders` values still sum to 100
- `total_shares` doubles (100 / 5 = 20)
- Each 5% cert costs `market_price / 2`; the 10% president cert costs `market_price`
- Treasury cert (10 share-units out of 20) earns `revenue / 2` back to corp each OR

Reference: `lib/engine/game/g_1862_usa_canada/game.rb`, `step/dividend.rb`; see also `g_1873/game.rb` for the `share_holders.clear` + rebuild pattern.

---

## Finding More Examples

The fastest way to find a production example of any pattern:

```bash
# Find titles that override revenue_for:
grep -rl "def revenue_for" lib/engine/game/

# Find titles that define a half-pay step:
grep -rl "half" lib/engine/game/*/step/

# Find all titles that use a specific ability type:
grep -rl "type: 'teleport'" lib/engine/game/
```

---

## What's Next

- Revenue hook reference: [Revenue & Routing](revenue-routing.html)
- Ability field reference: [Abilities](abilities.html)
- Writing a custom Step from scratch: [Rounds & Steps](round-step-system.html)
- Verifying patterns with fixtures: [Testing Your Game](testing.html)

---
*Version: 2026-05-17 — derived from production game titles in `lib/engine/game/`, `lib/engine/step/`, `lib/engine/game/base.rb`.*
