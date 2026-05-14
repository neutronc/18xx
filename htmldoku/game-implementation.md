# Implementing a New Game Title

This tutorial walks through adding a new 18xx game title from an empty directory to a working, registered title. It uses an imaginary title "8888" as the running example. After completing this tutorial you can run the title locally, play through a full auction round, and lay the first tiles.

Before starting, ensure your local Docker stack is running — see [Getting Started](getting-started.html).

## File Structure

Every title lives under `lib/engine/game/g_<fs_name>/`. The directory name is lowercase, using underscores. For 8888:

```
lib/engine/game/g_8888/
├── meta.rb       — Title metadata: designer, rules URL, player range
├── entities.rb   — Companies and corporations (included as modules)
├── map.rb        — Tile supply, location names, hex layout
└── game.rb       — Phases, trains, market grid, round configuration
```

Custom Steps and Rounds go in subdirectories:

```
lib/engine/game/g_8888/
├── round/
│   └── special_auction.rb
└── step/
    └── bid.rb
```

The engine discovers the title automatically at startup: `lib/engine.rb` scans for every `Engine::Game::G*` module that contains a `Meta` submodule. No explicit registration is needed.

## Step 1 — meta.rb

`meta.rb` describes the title to the platform: who designed it, where the rules live, and how many players may participate.

```ruby
# frozen_string_literal: true

require_relative '../meta'

module Engine
  module Game
    module G8888
      module Meta
        include Game::Meta

        DEV_STAGE = :prealpha

        GAME_SUBTITLE = 'Railways of the German Empire'
        GAME_DESIGNER = 'Example Designer'
        GAME_LOCATION = 'Germany'
        GAME_PUBLISHER = :self_published
        GAME_RULES_URL = 'https://example.com/8888-rules'
        GAME_INFO_URL  = 'https://github.com/tobymao/18xx/wiki/8888'

        PLAYER_RANGE = [3, 5].freeze
      end
    end
  end
end
```

**`DEV_STAGE` controls the warning banner and archival behaviour:**

| Value | Meaning |
|-------|---------|
| `:prealpha` | Active development; shown only to the implementer |
| `:alpha` | Testing with a small group; warning banner shown |
| `:beta` | Broader testing; warning banner shown |
| `:production` | Released; no warning banner |

Start at `:prealpha`. Move to `:beta` only after at least five complete games have been played.

**Optional fields you may also set:**

| Constant | Purpose |
|----------|---------|
| `GAME_TITLE` | Override the canonical title string (defaults to module name without the `G` prefix) |
| `GAME_DISPLAY_TITLE` | Override the UI display name |
| `GAME_ALIASES` | Array of alternate title strings that the engine recognises |
| `OPTIONAL_RULES` | Array of rule variant hashes (`sym:`, `short_name:`, `desc:`) |
| `MUTEX_RULES` | Array of rule symbol groups that are mutually exclusive |
| `KEYWORDS` | Array of search keywords |

## Step 2 — entities.rb

`entities.rb` defines private companies and major corporations as a module that `game.rb` includes.

```ruby
# frozen_string_literal: true

module Engine
  module Game
    module G8888
      module Entities
        COMPANIES = [
          {
            name: 'Rhine Valley Railway',
            sym:  'RVR',
            value: 20,
            revenue: 5,
            desc: 'Blocks hex C7 while owned by a player.',
            abilities: [{ type: 'blocks_hexes', owner_type: 'player', hexes: ['C7'] }],
            color: nil,
          },
          {
            name: 'Bavarian Central Railway',
            sym:  'BCR',
            value: 80,
            revenue: 15,
            desc: 'The owning corporation may lay one free tile on D8.',
            abilities: [
              { type: 'blocks_hexes', owner_type: 'player', hexes: ['D8'] },
              {
                type: 'tile_lay',
                owner_type: 'corporation',
                hexes: ['D8'],
                tiles: %w[3 4 58],
                when: 'owning_corp_or_turn',
                count: 1,
              },
            ],
            color: nil,
          },
        ].freeze

        CORPORATIONS = [
          {
            sym:          'KBR',
            name:         'Königlich Bayerische Staatsbahnen',
            logo:         '8888/KBR',
            simple_logo:  '8888/KBR.alt',
            tokens:       [0, 40, 100],
            coordinates:  'D8',
            color:        '#0000cc',
            float_percent: 60,
          },
          {
            sym:          'PR',
            name:         'Preußische Staatsbahnen',
            logo:         '8888/PR',
            simple_logo:  '8888/PR.alt',
            tokens:       [0, 40, 100, 100],
            coordinates:  'B4',
            color:        '#333333',
            float_percent: 60,
          },
        ].freeze
      end
    end
  end
end
```

**Key corporation fields:**

| Field | Required | Notes |
|-------|----------|-------|
| `sym` | Yes | Short identifier shown on share certificates |
| `name` | Yes | Full display name |
| `logo` | Yes | Path under `public/logos/` (without `.svg` extension) |
| `tokens` | Yes | Array of token costs; first element is always `0` (home token is free) |
| `coordinates` | Yes | Starting hex for the home token |
| `color` | Yes | CSS colour string |
| `float_percent` | No | Percent sold before the corporation floats; default `60` |

For the complete field list see [Corporations & Companies](entities.html).

## Step 3 — map.rb

`map.rb` provides three things: the tile supply, location name labels, and the hex grid definition.

```ruby
# frozen_string_literal: true

module Engine
  module Game
    module G8888
      module Map
        TILES = {
          '3'  => 2,
          '4'  => 2,
          '7'  => 4,
          '8'  => 8,
          '9'  => 7,
          '14' => 3,
          '15' => 3,
          '57' => 4,
          '58' => 2,
        }.freeze

        LOCATION_NAMES = {
          'D8' => 'Munich',
          'B4' => 'Berlin',
          'C5' => 'Leipzig',
          'E7' => 'Nuremberg',
          'A5' => 'Hamburg',
        }.freeze

        HEXES = {
          red: {
            ['A3'] => 'offboard=revenue:yellow_30|brown_60;path=a:4,b:_0;path=a:5,b:_0',
          },
          gray: {
            ['A5'] => 'city=revenue:30;path=a:3,b:_0;path=a:4,b:_0',
          },
          white: {
            %w[C5 E7]       => 'city=revenue:0',
            %w[B6 D6 C7 D4] => 'town=revenue:0',
            %w[C3 D2 E5 F8] => '',
            %w[B2 C1 E3]    => 'upgrade=cost:80,terrain:mountain',
            ['D8']          => 'city=revenue:0;upgrade=cost:40,terrain:water',
          },
          yellow: {
            ['B4'] => 'city=revenue:30;city=revenue:30;path=a:0,b:_0;path=a:3,b:_1;label=OO',
          },
        }.freeze

        LAYOUT = :pointy
      end
    end
  end
end
```

**Hex colour convention:**

| Colour | Meaning |
|--------|---------|
| `white` | Empty; players lay and upgrade tiles here |
| `yellow` | Pre-printed yellow tile; upgradeable during play |
| `gray` | Fixed tile; never upgradeable |
| `red` | Off-map revenue space; never upgradeable |

For the complete tile string syntax see [Map Configuration](map.html).

## Step 4 — game.rb

`game.rb` is the main game class. It includes the other three modules, declares game mechanics as constants, and overrides the Round factory methods.

```ruby
# frozen_string_literal: true

require_relative 'entities'
require_relative 'map'
require_relative 'meta'
require_relative '../base'

module Engine
  module Game
    module G8888
      class Game < Game::Base
        include_meta(G8888::Meta)
        include Entities
        include Map

        CURRENCY_FORMAT_STR = 'M%s'
        BANK_CASH = 8_000
        CERT_LIMIT   = { 3 => 16, 4 => 12, 5 => 10 }.freeze
        STARTING_CASH = { 3 => 500, 4 => 375, 5 => 300 }.freeze
        CAPITALIZATION = :full
        MUST_SELL_IN_BLOCKS = false

        MARKET = [
          %w[60y 67 71 76 82 90 100p 112 126 142 160 180 200 220],
          %w[53y 60y 66 70 76 82  90p 100 112 126 142 160 180 200],
          %w[46y 55y 60y 65 70 76  82p  90 100 112 126 142],
          %w[39y 48y 55y 60 65 70   76   82  90 100],
          %w[32y 41y 48y 55 60 65   70   76  82],
          %w[25y 34y 41y 48 55 60   65   70],
        ].freeze

        PHASES = [
          {
            name: '2',
            train_limit: 4,
            tiles: [:yellow],
            operating_rounds: 1,
          },
          {
            name: '3',
            on: '3',
            train_limit: 4,
            tiles: %i[yellow green],
            operating_rounds: 2,
            status: ['can_buy_companies'],
          },
          {
            name: '5',
            on: '5',
            train_limit: 2,
            tiles: %i[yellow green brown],
            operating_rounds: 3,
            events: [{ 'type' => 'close_companies' }],
          },
        ].freeze

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

        def operating_round(round_num)
          Round::Operating.new(self, [
            Engine::Step::Bankrupt,
            Engine::Step::Exchange,
            Engine::Step::SpecialTrack,
            Engine::Step::SpecialToken,
            Engine::Step::BuyCompany,
            Engine::Step::HomeToken,
            Engine::Step::Track,
            Engine::Step::Token,
            Engine::Step::Route,
            Engine::Step::Dividend,
            Engine::Step::DiscardTrain,
            Engine::Step::BuyTrain,
            [Engine::Step::BuyCompany, { blocks: true }],
          ], round_num: round_num)
        end

        def stock_round
          Round::Stock.new(self, [
            Engine::Step::DiscardTrain,
            Engine::Step::Exchange,
            Engine::Step::SpecialTrack,
            Engine::Step::BuySellParShares,
          ])
        end
      end
    end
  end
end
```

The two Round factory methods define which Steps are active in each round. Omitting either method falls back to the `Game::Base` default. Override only when you need a Step that the default does not include.

## Step 5 — Add Logos

Each corporation needs an SVG logo at `public/logos/<title>/<sym>.svg`. For the example above, create `public/logos/8888/KBR.svg`. Without it the UI shows a placeholder; the game still runs.

## Step 6 — First Run

Start the Docker stack and open `http://localhost:9292/`. Create a new game and select "8888". If the title does not appear, confirm the module name matches `Engine::Game::G8888` exactly and contains a `Meta` submodule.

If the game fails to load, check the container log or open a console:

```bash
docker compose logs rack -f
```

```bash
docker compose exec rack irb
```

```ruby
require_relative 'lib/engine'
g = Engine::Game::G8888::Game.new(%w[Alice Bob Charlie])
g.current_round   # => should return a Round::Auction or Round::Stock instance
```

## Which Layer Does My Rule Belong To?

Before writing code, find the least-invasive layer that handles your rule. Work top-down:

```
Does a constant cover it?
  YES → add/change a value in game.rb, entities.rb, or map.rb
  NO  ↓
Does an event hook cover it?
  YES → override event_*! or operating_order in game.rb
  NO  ↓
Does an existing Step's behaviour differ only slightly?
  YES → subclass the Step, override one method
  NO  ↓
Does an entirely new action type need to exist?
  YES → write a new Step (and possibly a new Round)
```

**Layer examples:**

| Rule | Layer | What to change |
|------|-------|---------------|
| Different bank size | Constant | `BANK_CASH` in game.rb |
| Companies close on 5-train | Constant | `events: [{ 'type' => 'close_companies' }]` on the train |
| Custom log message when companies close | Event hook | override `event_close_companies!` in game.rb |
| Hex revenue bonus | Method override | override `revenue_for` in game.rb |
| Minor always half-pays | Step subclass | subclass `Step::Dividend`, override `actions` + `skip!` |
| Entirely new auction mechanic | New Step + Round | `step/bid.rb` + `round/auction.rb` |

When in doubt, search `lib/engine/game/` for a production title that already implements something similar. The [Common Patterns](common-patterns.html) page has grep commands for this.

## When to Add Custom Steps

The default Step set in `Round::Operating` and `Round::Stock` covers the mechanics of most 18xx titles. Add a custom Step only when:

- A new action type must be introduced that no existing Step handles
- The decision sequence for a corporation type differs from the default OR order
- An existing Step's logic cannot be expressed through `tile_lays`, abilities, or hook overrides alone

Before writing a new Step, see the walkthrough in [Rounds & Steps](round-step-system.html) and look for a production title that already implements something similar.

## Reference Games

| Mechanic | Reference title |
|----------|----------------|
| Waterfall auction | 1822 |
| Minor conversion to major | 1867 |
| Full capitalisation | 1830 |
| Incremental capitalisation | 1846 |
| Multiple track-lays per OR | 1849 |
| Loan system | 1817 |
| Receivership | 1860 |
| Nationalisation | 18ZOO |
| Destination token | 1889 |
| Hex bonus revenue | 18CO |

## What's Next

- CORPORATIONS and COMPANIES field reference: [Corporations & Companies](entities.html)
- TRAINS, PHASES, MARKET reference: [Trains, Phases & Market](trains-phases.html)
- Hex grid and tile string syntax: [Map Configuration](map.html)
- Short code recipes for common rules: [Common Patterns](common-patterns.html)
- Testing your title with fixtures: [Testing Your Game](testing.html)
- Writing a custom Step with a worked example: [Rounds & Steps](round-step-system.html)
- PR patterns and code style: [Coding Guidelines](coding-guidelines.html)

---
*Version: 2026-05-08 — derived from `lib/engine/game/g_1830/`, `lib/engine/game/meta.rb`, `lib/engine/game/base.rb`.*
