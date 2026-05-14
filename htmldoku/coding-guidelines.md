# Coding Guidelines

Patterns distilled from pull-request feedback on the 18xx engine. Read these before making any code changes. Each guideline includes the rationale and a concrete example.

---

## Reference Games — Study Before Implementing a Mechanic

Find a production game that does something similar before writing new code. These are well-established reference implementations.

| Mechanic | Reference game / file |
|----------|-----------------------|
| Minor/major conversion, waterfall auction | `g_1822/game.rb` |
| Merger round, regional → national | `g_1867/game.rb` |
| Coal exchange, coalitions, receivership | `g_1837/game.rb` |
| Phase/event system, `event_` methods | `g_18_royal_gorge/game.rb` |
| Complex events, multi-company types | `g_1868_wy/game.rb` |
| Company mergers and conversion | `g_1841/game.rb` |
| Merger round mechanics | `g_18_mag/game.rb` |
| Receivership, insolvency | `g_1860/game.rb` |
| Train obligation, forced purchase | `g_1862_ea/game.rb` |
| National railway with special revenue | `g_1873/game.rb` |
| Clean minimal baseline | `g_18_ny/game.rb`, `g_1837/game.rb` |
| National companies (state-owned mid-game) | `g_1844/game.rb`, `g_1854/game.rb` |
| Mergers with stock conversion | `g_1828/game.rb`, `g_1841/game.rb` |
| Combining trains (level ≤4 OE-style) | `g_1862/game.rb` |
| Ferries / port tokens | `g_18_mex/game.rb`, `g_18_scan/game.rb` |
| Sea zones / province crossing | `g_18_oe/game.rb` |

| Feature | File |
|---------|------|
| Waterfall auction | `g_1822/step/waterfall_auction.rb` |
| Minor/major conversion | `g_1822/game.rb` (conversion section) |
| Merger round | `g_1841/game.rb`, `g_18_mag/game.rb` |
| National revenue | `g_1873/game.rb` |
| Forced train purchase | `g_1860/game.rb`, `g_1862_ea/game.rb` |
| Custom event flow | `g_18_royal_gorge/game.rb` |
| Phase status patterns | `g_18_eu/game.rb` |
| Minors as Corporation (no par), auto-dividend | `g_1837/game.rb` L675, `g_1837/step/minor_half_pay.rb` |
| Assign/hex tokens (ferry, port) | `lib/engine/step/assign.rb`, `g_18_mex/step/` |

---

## 1. Extract helpers when a method has distinct phases

When a public method contains multiple `if`/`return` blocks that each represent a distinct state, pull each block into its own named private helper. The top-level method becomes a clean dispatch.

**Bad:**
```ruby
def actions(entity)
  if @converting
    actions = []
    ipo_bundle = @converting.ipo_shares.first&.to_bundle
    actions << 'buy_shares' if ipo_bundle && can_buy?(entity, ipo_bundle)
    actions << 'pass'
    return actions
  end
  # ... more phases inline ...
end
```

**Good:**
```ruby
def actions(entity)
  return converting_actions(entity) if @converting
  return converted_actions(entity) if @converted
  # normal actions ...
end

private

def converting_actions(entity)
  actions = []
  ipo_bundle = @converting.ipo_shares.first&.to_bundle
  actions << 'buy_shares' if ipo_bundle && can_buy?(entity, ipo_bundle)
  actions << 'pass'
  actions
end
```

Aim for 5–20 lines per method; guard clauses at the top; early return on rejection.

---

## 2. No magic numbers — use named constants

Replace bare literals with named constants in `game.rb`. Reference them in step files via `@game.class::CONSTANT`.

**Bad:**
```ruby
6.times do |index|
  share = Share.new(corporation, ..., index: 4 + index)
end
```

**Good:**
```ruby
# In game.rb:
CONVERSION_NEW_SHARES = 6

# In step file:
@game.class::CONVERSION_NEW_SHARES.times do |index|
  share = Share.new(corporation, ..., index: 4 + index)
end
```

Use `Set` for membership checks. Use descriptive names: `ROYAL_GORGE_HEXES_TO_TILES`, not `SPECIAL_HEXES`. Group constants near thematically related ones.

---

## 3. No duplicated expressions — extract shared private helpers

If the same expression appears in two or more methods, extract it to a private helper.

**Bad:**
```ruby
def help
  zones = @game.minor_available_regions.map { |zone, count| "#{zone}(#{count})" }.join(', ')
  "Available zones: #{zones}."
end

def float_minor(action)
  zones = @game.minor_available_regions.map { |zone, count| "#{zone}(#{count})" }.join(', ')
  @log << "Available zones: #{zones}"
end
```

**Good:**
```ruby
def help
  "Available zones: #{zones_display}."
end

def float_minor(action)
  @log << "Available zones: #{zones_display}"
end

private

def zones_display
  @game.minor_available_regions.map { |zone, count| "#{zone}(#{count})" }.join(', ')
end
```

---

## 4. Compound guard conditions — multi-line for separate rule clauses

Multiple single-condition `return false` guards are clearer than one compound boolean when each guard encodes a distinct rule clause.

```ruby
# Clearer — each condition is independently debuggable:
if @converting
  return false if bundle.corporation != @converting
  return false unless bundle.corporation.president?(entity)
  return false if bought_corporation == bundle.corporation
end

# Shorter but harder to scan:
return false if @converting && (bundle.corporation != @converting ||
                                !bundle.corporation.president?(entity) ||
                                bought_corporation == bundle.corporation)
```

Use the one-liner only when the conditions form a single logical unit.

---

## 5. Phase conditions — use status strings, never phase name integers

**Bad:**
```ruby
return false if @phase.name.to_i >= 4
```

Phase names are not guaranteed to be integers; variant games can rename them. `.to_i` silently returns 0 for non-numeric names. Phase comparisons are also invisible to the game info page.

**Good:**
```ruby
# In PHASES (game.rb):
{ name: '4', ..., status: ['can_buy_trains_from_others'] }

# In game.rb:
def can_buy_train_from_others?
  @phase.status.include?('can_buy_trains_from_others')
end

def must_buy_train?(entity)
  return false unless entity.trains.empty?
  return false unless @phase.status.include?('train_obligation')
  entity.floated?
end
```

Note: `entity.corporation?` is a class check (is this object a Corporation instance?), not a type check. In OR methods, the entity is always a corporation — players and the bank never reach them. The meaningful discriminator is `entity.type` (`:minor`, `:major`, `:national`, etc.).

For one-shot state changes, use train events:
```ruby
# In TRAINS (game.rb):
{ name: '5', ..., events: [{ 'type' => 'consolidation_triggered' }] }

# In game.rb:
def event_consolidation_triggered!
  @consolidation_triggered = true
  @log << '-- Event: Consolidation phase triggered --'
end
```

Reference: `g_18_eu/game.rb` `can_par?`, `g_18_royal_gorge/game.rb` event methods.

---

## 6. Array emptiness — `.empty?` not `.any?` without a block

**Bad:**
```ruby
return false if entity.trains.any?   # always truthy — guard never fires
```

**Good:**
```ruby
return false unless entity.trains.empty?
entity.trains.any? { |t| t.distance > 2 }  # predicate with block — fine
```

Reserve `.any?` / `.none?` / `.all?` for block predicates only.

---

## 7. Class references in steps — `@game.class::` not the literal class name

**Bad:**
```ruby
G18OE::Game::CITY_NATIONAL_ZONE[hex.name.to_s]
```

This locks the step to the concrete class; variant subclasses that override the constant are silently ignored.

**Good:**
```ruby
@game.class::CITY_NATIONAL_ZONE[hex.coordinates]
```

Also applies to constants referenced from `game.rb` itself — use `self.class::CONSTANT` so subclass overrides take effect.

---

## 8. Hex keys — `coordinates` for data, `name` for display

```ruby
# Data lookups:
@game.class::CITY_NATIONAL_ZONE[hex.coordinates]

# Log strings and UI display only:
@log << "Token placed at #{hex.name}"
```

---

## 9. Value deletion — `.delete(value)` not `.delete_at(index)`

**Bad:**
```ruby
idx = @game.minor_available_regions.index(region)
@game.minor_available_regions.delete_at(idx) if idx
```

**Good:**
```ruby
@game.minor_available_regions.delete(region)
```

`.delete(value)` removes by identity and returns `nil` if not found — safe. `.delete_at(index)` is for positional removal only.

---

## 10. No in-repo feature flags

**Bad:**
```ruby
NATIONAL_REGION_HEXES_COMPLETE = false
return true unless self.class::NATIONAL_REGION_HEXES_COMPLETE
```

Flag constants accumulate and become dead code. Reviewers cannot tell which flags are active or permanent.

**Good:** Remove the constant when the feature is complete. During development, use a plain TODO comment:
```ruby
# TODO: restrict to home zone once all NATIONAL_REGION_HEXES lists are filled
```

For player-selectable behaviour, use `optional_rules` instead.

---

## 11. Round inheritance — inherit from the closest engine round class

**Bad:**
```ruby
class Consolidation < Engine::Round::Base
```

Inheriting from `Base` forces re-implementation of stock round behaviour.

**Good:**
```ruby
class Consolidation < Engine::Round::Stock
  # override only what differs: select_entities, finished?, finish_round
end
```

Stock-like rounds → `Engine::Round::Stock`. Merger-like rounds → `Engine::Round::Merger`.

Reference: `g_18_eu` FinalExchange, `g_1867` Merger, `g_18_mag` merger round.

---

## 12. `next_round!` — use a case statement, not if/return chains

**Bad:**
```ruby
def next_round!
  if @round.is_a?(Round::Operating) && @consolidation_triggered && !@consolidation_done
    @round = new_consolidation_round
    return
  end
  super
end
```

**Good:**
```ruby
def next_round!
  @round =
    case @round
    when Round::Stock
      @operating_rounds = @phase.operating_rounds
      reorder_players
      new_operating_round
    when Round::Operating
      if @round.round_num < @operating_rounds
        or_round_finished
        new_operating_round(@round.round_num + 1)
      elsif @consolidation_triggered && !@consolidation_done
        @turn += 1
        or_round_finished
        or_set_finished
        new_consolidation_round
      else
        @turn += 1
        or_round_finished
        or_set_finished
        new_stock_round
      end
    when Round::G18OE::Consolidation
      @consolidation_done = true
      new_stock_round
    when init_round.class
      init_round_finished
      reorder_players
      new_stock_round
    end
end
```

Rules: assign `@round` once at the top via `case @round`; no `return` statements; no `super`; each `when` branch returns the new round object.

Reference: `g_18_mag/game.rb`, `g_1841/game.rb`, `g_1867/game.rb`.

---

## 13. Event architecture

Each game event has a dedicated `event_foo!` method. Event methods log their own messages and delegate complex logic to private helpers.

```ruby
def event_green_phase!
  @log << '-- Event: Green Phase --'
  setup_green_phase_companies
  @companies.each { |c| close_company(c) if c.sym =~ /^P/ }
end

private

def setup_green_phase_companies
  # focused helper
end
```

- Guard clauses at the top: `return unless condition`
- Log with `@log << "-- Event: #{description} --"`
- Use `round_state` in step files to declare and initialise step-level state.

Reference: `g_18_royal_gorge/game.rb` lines 327–379.

---

## 14. Disable actions via `actions()`, never via `raise` in `process_*`

If a player shouldn't be able to take an action, don't offer it in `actions()`. Don't offer it and then raise a `GameError` inside `process_*`.

**Bad:**
```ruby
def converted_actions(entity)
  actions = []
  actions << 'pass'   # always offered
  actions
end

def pass!
  raise GameError, "Must become president" unless @converted.president?(current_entity)
end
```

**Good:**
```ruby
def converted_actions(entity)
  actions = []
  actions << 'pass' if @converted.president?(entity)   # only when allowed
  actions
end

def pass!
  if @converted
    @round.current_actions.clear
    @converted = nil
  end
  super
end
```

### Step file structure

- One concern per step file (`bankrupt.rb`, `coal_exchange.rb` — not one giant file).
- Inherit from the closest base step; override only what differs.
- Declare step-level state in `round_state`, not in instance variables set outside `setup`.

---

## 15. Commenting style

Write no comment if the method name explains the intent. Write a short comment only when the rule being encoded is non-obvious to someone reading without the rulebook.

Never write multi-line comment blocks or docstrings. Use short explanatory comments only for non-obvious domain logic.

---

## 16. Commit hygiene

- One logical change per commit.
- Do not mix feature work, file deletions, and merge commits.
- Do not push accidental deletions.
- Prefer multiple small focused PRs over one large PR.
- PRs that build on each other must be merged in order; document this in the PR description.

---

## 17. Keep logic in the game class — expose simple predicates to steps

Steps should call simple named methods on `@game`. The preconditions and implementation details belong in `game.rb`.

**Bad:**
```ruby
# step encodes multi-part condition:
def buyable_trains(entity)
  return [] if !@game.major_phase? || !@game.first_or_done
end
```

**Good:**
```ruby
# game.rb exposes a single named predicate:
def non_starter_trains_available?
  major_phase? && first_or_done
end

# step:
def buyable_trains(entity)
  return [] unless @game.non_starter_trains_available?
end
```

If a predicate has a phase precondition, encode the phase check inside the predicate, not at every call site:

```ruby
# game.rb — predicate encodes its own precondition:
def fulfilled_train_obligation?(entity)
  !phase.status.include?('train_obligation') || @fulfilled_train_obligation.include?(entity.id)
end
```

---

## 18. Method naming conventions — `!` for mutation, `?` for boolean predicates

```ruby
def fulfill_train_obligation!(entity)   # mutates state
  @fulfilled_train_obligation.add(entity.id)
end

def fulfilled_train_obligation?(entity) # boolean query
  !phase.status.include?('train_obligation') || @fulfilled_train_obligation.include?(entity.id)
end
```

---

## 19. Understand what base step methods gate before overriding

Some base step methods do more than their name implies. Before overriding, read the base implementation and every call site.

**Example — `can_entity_buy_train?`:**

This method gates the entire `actions` method, including the emergency-buy sell-shares path for the president. If it returns `false` for a player, the president can never be asked to sell shares to fund an emergency purchase.

```ruby
# base Engine::Step::BuyTrain#actions:
def actions(entity)
  return [] unless can_entity_buy_train?(entity)            # gates everything
  return ['sell_shares'] if entity == current_entity&.owner # president e-buy path
  # ...
end
```

Only return `true` for players from `can_entity_buy_train?` when the rules allow the president to sell shares to fund a train purchase.

Before writing any override, verify what the base class already returns for every entity type in the game. If the base already returns the same value for all types your game uses, the override is dead code — delete it.

---

## 20. Auto-process steps with a single valid choice — `actions` + `skip!`

When an entity type has only one valid option for a step (e.g., minors always half-pay), do not present the choice to the player.

**Bad:**
```ruby
def dividend_types
  case current_entity.type
  when :minor then [:half]
  # ...
  end
end
```

**Good:**
```ruby
def actions(entity)
  return [] if %i[minor national].include?(entity.type)
  super
end

def skip!
  case current_entity.type
  when :minor
    kind = total_revenue.zero? ? 'withhold' : 'half'
  when :national
    kind = total_revenue.zero? ? 'withhold' : 'payout'
  else
    return super
  end
  process_dividend(Action::Dividend.new(current_entity, kind: kind))
end
```

`dividend_types` must include every kind `process_dividend` may be called with, including `:withhold` as a fallback for the zero-revenue case:

```ruby
def dividend_types
  case current_entity.type
  when :minor   then %i[half withhold]
  when :national then %i[payout withhold]
  else %i[withhold half payout]
  end
end
```

Reference: `g_1837/step/minor_half_pay.rb` `skip!` pattern.

---

## 21. `buyable_trains` — trust the depot; never filter by price

**Bad:**
```ruby
def buyable_trains(entity)
  trains = super
  depot_trains = trains.select(&:from_depot?)
  unless depot_trains.empty?
    min_price = depot_trains.map(&:price).min
    trains = trains.reject { |t| t.from_depot? && t.price > min_price }
  end
  trains
end
```

`Depot#available_upcoming_trains` already returns only the current level. The custom block is dead weight. Also wrong: filtering out trains the entity cannot afford. The UI handles affordability — unaffordable trains appear greyed-out. `buyable_trains` controls which trains are *eligible*, not which are *payable*.

**Good:**
```ruby
def buyable_trains(entity)
  super  # or add game-specific eligibility rules only
end
```

Only filter by game eligibility rules (e.g., minors cannot buy trains at all). Leave price and depot-level gating to the depot and the UI.

---

## 22. Round `select_entities` — broad list; step `blocks?` handles skipping

**Bad:**
```ruby
def select_entities
  @game.players.select do |p|
    p.shares.map(&:corporation).any? { |c| %i[minor regional].include?(c.type) }
  end
end
```

A player whose last minor is merged mid-round is still in `@entities` from the initial selection but can no longer act.

**Good:**
```ruby
def select_entities
  @game.players  # all non-bankrupt players
end
```

The step's `blocks?` returns `false` when the player has nothing to do; the round auto-skips them. `select_entities` determines who *participates*; `blocks?` determines whether their turn is *active* right now.

---

## 23. `dividend_types` — no parameter, no `&` operator

`dividend_types` is defined in the base step as `def dividend_types` (no argument).

**Bad:**
```ruby
def dividend_types
  case current_entity&.type   # & is unnecessary
```

**Good:**
```ruby
def dividend_types
  case current_entity.type
```

If `current_entity` is `nil` when `dividend_types` is called, something has gone wrong upstream. Use `&.` only where `nil` is a legitimate value — not to suppress real bugs.

---

## 24. Delete empty override files

If a step or round file inherits from its parent but adds no methods of its own, delete it. Empty override files accumulate silently and suggest the subclass has its own behaviour when it doesn't.

**Bad:**
```ruby
# lib/engine/game/g_1880_romania/round/stock.rb
module Engine
  module Game
    module G1880Romania
      module Round
        class Stock < G1880::Round::Stock
        end
      end
    end
  end
end
```

**Good:** Delete the file. Point the game's `GAME_ROUNDS` or `new_stock_round` directly at the parent class.

The same applies to `buy_sell_par_shares.rb`, `company_pending_par.rb`, or any other step file that does nothing beyond `< ParentStep`.

---

## 25. Only define constants that differ from the engine default

Don't copy default constant values from the base class into your game file. Only define constants you are actually overriding. Reviewers cannot tell at a glance whether a constant is intentional or copied noise.

**Bad (copied defaults — noise):**
```ruby
BANKRUPTCY_ALLOWED = false    # already false in Game::Base
MUST_BUY_TRAIN = :route       # already :route
MAX_LOANS = 0                 # already 0
```

**Good (only overrides):**
```ruby
MAX_TOKENS = 3                # overrides default of 4
SELL_AFTER = :operate         # overrides default of :first_turn
```

Check `lib/engine/game/base.rb` for the real default before adding a constant.

---

## 26. Ruby collection idioms — first, include?, Array.new with a block

Three patterns reviewers flag consistently:

**`Array#first` over `[0]`:**
```ruby
row.first == company   # preferred
row[0] == company      # avoid
```

**`include?` over `index` for membership:**
```ruby
row.include?(company)  # preferred — returns bool, intent is clear
row.index(company)     # avoid for membership — returns index or nil
```

**`Array.new(n) { [] }` for 2D arrays:**
```ruby
# Bad — all 4 elements share the same Array object:
@tiers = Array.new(4, [])

# Good — each element is a distinct Array:
@tiers = Array.new(4) { [] }
```

The second form is required whenever you mutate the inner arrays independently.

---

## 27. Minor companies — use `MINORS`, not `CORPORATIONS`

Minor companies that have no share price belong in the `MINORS` constant (entities array), not `CORPORATIONS`. `Corporation` objects carry a market position; `Minor` objects do not. Using the wrong type causes share-price-related logic to fire where it shouldn't.

```ruby
# Correct for entities without a share price:
MINORS = [
  { sym: 'M1', name: 'Minor 1', type: :minor, ... },
].freeze

# Wrong — only use CORPORATIONS for entities with share prices:
CORPORATIONS = [
  { sym: 'M1', ... },   # minor company placed here by mistake
].freeze
```

For minors accessible by ID: `@game.minor_by_id('M1')` (not `@game.corporation_by_id`).

---

## 28. No debug logging or dead code in PRs

Remove all debug artefacts before opening a PR:

- `LOGGER.debug { ... }` blocks added during development
- `puts`, `p`, `pp` statements
- Commented-out code blocks
- Methods that exist but are never called from within the game

If a method might be needed later, leave a TODO in `MD/todo.md` and delete it now. Reviewers treat dead code as a signal that the PR wasn't reviewed before submission.

---

## 29. Named entity accessors over hardcoded symbol lookups

When game logic repeatedly references a specific entity by its symbol string, add a named accessor to `game.rb`. This removes the coupling to the symbol string and makes variant subclasses easy to override.

**Bad:**
```ruby
# scattered through steps and game.rb:
company = @game.companies.find { |c| c.sym == 'BCR' }
return if company.nil?
```

**Good:**
```ruby
# game.rb:
def bcr_company
  @bcr_company ||= companies.find { |c| c.sym == 'BCR' }
end

# steps call @game.bcr_company — one lookup, one place to override
```

The same pattern applies to corporations, privates, and minors. Cache with `||=` if the object is stable; skip the cache if it can be closed or transferred.

---

## 30. Data-driven flags over name-string matching in variant filtering

When limiting which train variants are purchasable, put a flag in the variant definition rather than matching by name string. Name-string matching breaks silently when train names change.

**Bad:**
```ruby
def buyable_train_variants(train, entity)
  variants = super
  variants.select { |v| v[:name] == train.name }  # fragile name match
end
```

**Good:**
```ruby
# In TRAINS definition (game.rb):
variants: {
  '4n'   => { name: '4n', ... },
  '4n-1' => { name: '4n-1', ..., event_downgrade_variant: true },
}

# In step:
def buyable_train_variants(train, entity)
  variants = super
  return variants unless variants.any? { |v| v[:event_downgrade_variant] }
  variants.select { |v| v == train.variant }
end
```

The flag makes the intent visible in the data and is safe to rename.

---

## 31. `Array.intersect?` over `(a & b).empty?`

`(a & b)` builds an intermediate array before testing emptiness. `Array#intersect?` avoids the allocation.

**Bad:**
```ruby
return false if (actions & %w[buy_train scrap_train]).empty?
```

**Good:**
```ruby
return false unless actions.intersect?(%w[buy_train scrap_train])
```

Available since Ruby 3.1 (the engine's minimum). Use it anywhere you would have written `(a & b).any?` or `!(a & b).empty?`.

---

## 32. No redundant `return` at end of method

Ruby returns the last expression automatically. An explicit `return` as the final statement is noise — reviewers flag it consistently.

**Bad:**
```ruby
def zones_display
  result = @game.minor_available_regions.map { |z, c| "#{z}(#{c})" }.join(', ')
  return result
end
```

**Good:**
```ruby
def zones_display
  @game.minor_available_regions.map { |z, c| "#{z}(#{c})" }.join(', ')
end
```

`return` is correct and expected for early-exit guard clauses. The anti-pattern is only at the tail.

---

## 33. Call `super` instead of duplicating base class code

Do not copy-paste methods from base step or game classes. Call `super` and override only the delta. Duplicated code drifts silently when the base is updated.

**Bad:**
```ruby
def payout_shares
  # 12 lines that are identical to Engine::Step::Dividend#payout_shares
  per_share = revenue / total_shares
  entity.player_shares.each { |s| ... }
end
```

**Good:**
```ruby
def payout_shares
  super
  do_extra_step
end
```

Also applies to step files that repeat checks the base step already performs (`can_exchange?` calling `can_exchange?`, duplicate `require_relative` that the parent already loads, etc.).

---

## 34. `choices` must be a hash, not an array

When a step exposes choices to the player, always use a hash. Array choices store the button label as the key in the saved game JSON — future label changes silently break all in-progress games.

**Bad:**
```ruby
def choices
  %w[Left Right Stay]
end
```

**Good:**
```ruby
def choices
  { 'left' => 'Move Left', 'right' => 'Move Right', 'stay' => 'Stay' }
end
```

The hash key is what gets stored. The value is display-only and can be changed freely.

---

## 35. Use `def help` for player guidance — not `@log`

`@log` is permanent game history. Transient guidance ("available zones: …", "select one of…") belongs in the step's `help` method. It appears below the log in the UI and disappears when the step ends.

**Bad:**
```ruby
def float_minor(action)
  @log << "Available zones: #{zones_display}. Select one."
end
```

**Good:**
```ruby
def help
  "Available zones: #{zones_display}."
end
```

Log only actions that actually happened: *"Minor A placed token in UK zone."* Guide the player through `help`.

---

## 36. Per-round state belongs in `round_state`, not game instance variables

State that is only meaningful within the current round — players who have acted, shares bought this SR, companies parred — must be declared in the step's `round_state` method. It resets automatically when the round changes.

**Bad:**
```ruby
def setup
  @parred_this_sr = []   # survives across rounds
end
```

**Good:**
```ruby
def round_state
  super.merge({ parred_this_sr: [] })
end

# accessed from any step in the same round as:
@round.parred_this_sr
```

Game-class instance variables (`@game.foo`) persist for the whole game. Use `round_state` for anything that should be fresh each round.

---

## 37. Graph invalidation — `Graph#clear`, not `nil`; also implement `clear_graph_for_entity`

Never assign `nil` to a custom graph to force recalculation. Call `@custom_graph.clear` instead — `nil` will cause `NoMethodError` at the next access.

When overriding `clear_graph_for_corporation`, also override `clear_graph_for_entity` with the same body. The engine calls both depending on context; missing one leaves the graph stale.

**Bad:**
```ruby
def clear_graph_for_corporation(corporation)
  @narrow_gauge_graph = nil
end
```

**Good:**
```ruby
def clear_graph_for_corporation(corporation)
  @narrow_gauge_graph.clear
end

def clear_graph_for_entity(entity)
  @narrow_gauge_graph.clear
end
```

---

## 38. `route.hexes` not `route.stops` for non-station hex checks

`route.stops` contains only revenue centers (cities, towns, off-boards). Plain track hexes in the middle of a route appear only in `route.hexes`. Bonus detection based on passing through a specific hex must use `route.hexes`.

**Bad:**
```ruby
# misses the hex if the bonus marker moves to a plain track tile:
route.stops.any? { |s| s.hex.coordinates == @bonus_hex }
```

**Good:**
```ruby
route.hexes.any? { |hex| hex.coordinates == @bonus_hex }
```

Use `route.stops` only when you need the revenue-center objects themselves (e.g., to read slot count or revenue value).

---

## 39. Subclass variants — `.dup` before mutating shared constants; `.deep_freeze` in base

When a subgame overrides an array or hash constant inherited from a parent game, calling `super` returns the *same object* held in the parent constant. Mutating it without `.dup` silently corrupts the parent game's data — a hard-to-reproduce bug that only appears when both games are loaded in the same process.

**Bad:**
```ruby
# g_18_rhineland/map.rb — modifies the parent class's TILES array in-place:
def self.tiles
  super << { ... }
end
```

**Good:**
```ruby
def self.tiles
  super.dup << { ... }
end
```

For nested structures (hash of arrays), deep-dup both layers:
```ruby
map = self.class::HEXES.to_h { |k, v| [k, v.to_h { |k2, v2| [k2.dup, v2] }] }
```

**Base class:** freeze constants with `.deep_freeze` instead of `.freeze` so any inadvertent mutation raises immediately rather than silently corrupting state:
```ruby
TILES = [...].deep_freeze
```

---

## 40. Boolean keyword arguments for optional flags

When a method has an optional boolean that affects behaviour, use a keyword argument with a default rather than a positional parameter. It reads clearly at call sites and is easy to override selectively in subclasses.

**Bad:**
```ruby
def set_par(corporation, share_price, true)  # true — what does this mean?
```

**Good:**
```ruby
def set_par(corporation, share_price, place_token: true)
  place_token!(corporation, share_price) if place_token
  # ...
end

# subgame that needs to skip token placement:
@stock_market.set_par(corporation, price, place_token: false)
```

The flag name doubles as documentation; the default keeps all existing callers working without changes.

---

## 41. Mark partial rule implementations with an explicit TODO comment

When a rule is deliberately left incomplete — the engine is mid-development, a corner case is deferred, or a variant interaction isn't handled yet — add a plain TODO comment in the code. Silent partial implementations cause reviewers and future contributors to assume the rule is fully modelled.

```ruby
def home_token_locations(corporation)
  # TODO: FEC corner case — if all slots in the city are full, FEC may use a
  # 'cheater' token. Not yet implemented; see §3.2 of the 18Cuba rulebook.
  return MINOR_VALID_CITIES if corporation.type == :minor
  super
end
```

The comment must name the specific case that's missing, not just say "TODO". A reviewer reading the code should understand exactly what is unfinished without opening the rulebook.

---

## 42. `attr_accessor` — only for state that external code touches

Use `attr_accessor` only when another class (a step, a round, a view) needs to read or write the value. If a variable is only ever set and read within `game.rb` itself, use `@var` directly. An unnecessary accessor implies a public API that isn't there and makes it harder to tell what is genuinely shared state.

**Bad:**
```ruby
attr_accessor :consolidation_triggered, :consolidation_done, :first_or_done
# first_or_done is only read inside non_starter_trains_available? in game.rb itself
```

**Good:**
```ruby
attr_accessor :consolidation_triggered, :consolidation_done
# @first_or_done accessed directly via @first_or_done in non_starter_trains_available?
```

Grep every accessor name for external usages before adding it to `attr_accessor`.

---

## 43. 18OE entity identity — `entity.minor?` is not `entity.type == :minor`

`Engine::Minor#minor?` returns `true`. `Engine::Corporation#minor?` inherits from `Entity` and returns `false`.

18OE "minors" are `Engine::Corporation` instances with `type: :minor`, not `Engine::Minor` instances. So `entity.minor?` is always `false` for them.

| Check | 18OE minor (Corporation, type: :minor) |
|---|---|
| `entity.minor?` | `false` — it is a Corporation, not a Minor |
| `entity.corporation?` | `true` |
| `entity.type == :minor` | `true` — use this to discriminate by game type |

Consequence: the base step `can_entity_buy_train?` (`!entity.minor?`) already returns `true` for 18OE minors. An override that simply returns `entity.corporation?` adds nothing — drop it.

---

## 44. Type casting for DSL values — normalize at construction, keep it consistent

**The existing convention:** The tile DSL parser (`tile.rb:76`) splits on `:` and produces plain String values. Game ability definitions also use strings (`partition_type: 'water'`). These flow into object constructors as strings.

**Normalize to Symbol/Float at construction — not at every use site.** The view compares partition types against symbol literals (`:province`, `:divider`, etc.) and does float arithmetic with `length`. Without normalization at construction, these comparisons silently fail and the map does not render.

```ruby
# partition.rb — normalize once here
@type = type&.to_sym     # nil stays nil; 'province' → :province
@length = length&.to_f   # nil stays nil; '0.5' → 0.5
```

**Normalize at the data source, not defensively in the class.** `partition.type` is now a Symbol. Any ability that compares against it must also use a Symbol — but the right place to ensure that is in the entity definition, not in the ability class:

```ruby
# entities.rb — correct: declare as symbol literal
{ type: 'blocks_partition', partition_type: :water }

# entities.rb — wrong: string will silently fail the blocks? comparison
{ type: 'blocks_partition', partition_type: 'water' }
```

Adding `&.to_sym` inside `BlocksPartition#setup` papers over a bug in the entity definition and belongs in a separate fix PR, not in the ability class itself. Fix the root cause (the string literal in entities.rb), not the symptom.

**`&.` is correct when `nil` is legitimate** — the DSL omits `type` for untyped partitions, so `nil&.to_sym` → `nil` is the right result.

**Do not remove these casts based on Opal assumptions.** The upstream maintainer suggested removing `to_sym` on the grounds that Opal (Ruby→JS) makes string/symbol comparison transparent. We removed them. The map stopped loading. We restored them. The conversions are load-bearing regardless of Opal's behaviour — always verify in the browser before removing defensive normalization.

**What the cascade looks like when you skip normalization:**
```ruby
# partition.rb stores a string:
@type = type   # "province"

# view skip condition — with string type, '!= :province' may not behave
# as expected depending on Opal version and context:
next if partition.type != :divider && partition.type != :province && ...

# province partitions silently stop rendering → map does not load
```

---

## What's next

- Implementation layer taxonomy: [Game Engine](game-engine.html)
- Round and Step patterns: [Round/Step System](round-step-system.html)
- Ability implementation: [Ability Types Reference](abilities.html)

---
*Version: 2026-05-14 — §44 revised: blocks_partition root cause is entity definition (symbol literal), not ability class; to_sym/to_f in partition.rb are load-bearing.*
