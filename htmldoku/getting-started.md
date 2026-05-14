# Development Setup

Get Docker running, create a stub title, and confirm it loads — in about 15 minutes.

You need Docker, Docker Compose, and Make. No local Ruby or Node installation is required.

---

## VS Code in WSL

The recommended development environment for Windows users is **VS Code + WSL2 + Docker Desktop**. All development happens inside WSL — the Linux filesystem, terminal, and Docker daemon — and VS Code on Windows connects to it transparently via the Remote-WSL extension.

### Why this stack

| Component | Role |
|-----------|------|
| WSL2 | Full Linux environment inside Windows — no dual-boot, native I/O speed |
| Docker Desktop (WSL2 backend) | Runs the app containers; bind-mounts stay on the Linux filesystem |
| VS Code Remote-WSL | Editor, terminal, and file system all in the same Linux context — no path translation |

> **Do not clone inside `/mnt/c/`** (the Windows C: drive). Docker bind-mounts from the Windows filesystem are slow. Clone under `~/` in WSL for full Linux I/O speed.

### One-time setup

**1 — Install WSL2** (PowerShell as administrator):

```powershell
wsl --install
# Reboot when prompted. Ubuntu 22.04 is installed by default.
```

**2 — Install Docker Desktop** — download from [docker.com](https://www.docker.com/products/docker-desktop/). During install, enable *Use the WSL 2 based engine*. After install:

- Docker Desktop → Settings → General → ✓ Use the WSL 2 based engine
- Docker Desktop → Settings → Resources → WSL Integration → enable your distro

**3 — Install VS Code** and the **Remote - WSL** extension (extension ID: `ms-vscode-remote.remote-wsl`).

**4 — Open a WSL terminal** (search "Ubuntu" in the Start menu, or `wsl` in PowerShell) and clone the engine:

```bash
mkdir -p ~/18xx
git clone https://github.com/tobymao/18xx.git ~/18xx/18xx
```

**5 — Open VS Code from WSL:**

```bash
cd ~/18xx/18xx
code .
```

VS Code opens on Windows but connects to the WSL filesystem. The integrated terminal runs bash inside WSL. All git, Docker, and Ruby commands work natively from that terminal — no switching between environments.

### Verify Docker works from WSL

```bash
cd ~/18xx/18xx
docker compose up
# → rack container starts; open http://localhost:9292
```

If `docker` is not found, check that Docker Desktop is running and the WSL Integration is enabled for your distro.

---

## Before You Begin — Designer/Publisher Approval

**Implementing a game on this platform requires permission from the game's designer or publisher.**

Do not open a pull request for a new title without confirmation that the rights holder has approved it. Check the [18xx.games supported titles list](https://github.com/tobymao/18xx/blob/master/GAMES.md) to see if approval is already on record.

For questions about approval status, contact the community on Slack: **#18xxgamesdev**

---

## 1. Clone and Start

```bash
git clone https://github.com/tobymao/18xx.git
cd 18xx
make
```

`make` runs `docker compose up` with `docker-compose.dev.yml` as override. Four containers start:

| Container | Role |
|-----------|------|
| `rack` | Roda web server — `http://localhost:9292` |
| `queue` | Rufus-Scheduler background jobs |
| `db` | PostgreSQL on host port 5433 |
| `redis` | Redis on host port 6380 |

First build takes a few minutes. Open `http://localhost:9292` when the rack container logs `Listening on…`.

**Apple Silicon:** set `DEV_DOCKERFILE=Dockerfile.amd64` before every `make` or `docker compose` command, or persist it with [direnv](https://direnv.net/).

---

## 2. Create a Developer Account

Go to `http://localhost:9292/signup` and register. No confirmation email is sent — the local instance has no mail delivery.

---

## 3. Create Your Title Stub

Create the four required files. Replace `g_8888` and `G8888` with your title throughout.

```bash
mkdir -p lib/engine/game/g_8888/step lib/engine/game/g_8888/round
```

**`lib/engine/game/g_8888/meta.rb`**

```ruby
# frozen_string_literal: true

require_relative '../meta'

module Engine
  module Game
    module G8888
      module Meta
        include Game::Meta

        DEV_STAGE = :prealpha

        GAME_SUBTITLE  = 'My New Title'
        GAME_DESIGNER  = 'Your Name'
        GAME_LOCATION  = 'Somewhere'
        GAME_PUBLISHER = :self_published
        GAME_RULES_URL = 'https://example.com/rules'

        PLAYER_RANGE = [3, 5].freeze
      end
    end
  end
end
```

**`lib/engine/game/g_8888/entities.rb`** — start with 1830's corporations and trim later:

```ruby
# frozen_string_literal: true

module Engine
  module Game
    module G8888
      module Entities
        COMPANIES = [].freeze

        CORPORATIONS = [
          {
            sym: 'A', name: 'A Railroad', logo: '1830/PRR',
            tokens: [0, 40], coordinates: 'D4', color: '#0000cc',
          },
          {
            sym: 'B', name: 'B Railroad', logo: '1830/NYC',
            tokens: [0, 40], coordinates: 'B4', color: '#333333',
          },
        ].freeze
      end
    end
  end
end
```

**`lib/engine/game/g_8888/map.rb`**

```ruby
# frozen_string_literal: true

module Engine
  module Game
    module G8888
      module Map
        TILES = { '7' => 4, '8' => 8, '9' => 7, '57' => 4 }.freeze

        LOCATION_NAMES = { 'D4' => 'Alpha', 'B4' => 'Beta' }.freeze

        HEXES = {
          white: {
            %w[C3 D2 E3] => '',
            ['D4']       => 'city=revenue:0',
            ['B4']       => 'city=revenue:0',
          },
        }.freeze

        LAYOUT = :pointy
      end
    end
  end
end
```

**`lib/engine/game/g_8888/game.rb`**

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

        CURRENCY_FORMAT_STR = '$%s'
        BANK_CASH    = 6_000
        CERT_LIMIT   = { 3 => 16, 4 => 12 }.freeze
        STARTING_CASH = { 3 => 400, 4 => 300 }.freeze
        CAPITALIZATION   = :full
        MUST_SELL_IN_BLOCKS = false

        MARKET = [
          %w[60y 67 71 76 82 90 100p 112 126],
          %w[53y 60y 66 70 76 82  90p 100 112],
          %w[46y 55y 60y 65 70 76  82p  90 100],
        ].freeze

        PHASES = [
          { name: '2', train_limit: 4, tiles: [:yellow],           operating_rounds: 1 },
          { name: '3', on: '3', train_limit: 4, tiles: %i[yellow green], operating_rounds: 2 },
        ].freeze

        TRAINS = [
          { name: '2', distance: 2, price: 80, rusts_on: '4', num: 6 },
          { name: '3', distance: 3, price: 180, num: 5 },
        ].freeze
      end
    end
  end
end
```

---

## 4. Verify the Title Loads

```bash
docker compose exec rack irb
```

```ruby
require_relative 'lib/engine'
g = Engine::Game::G8888::Game.new(%w[Alice Bob Charlie])
g.current_round.class   # => Engine::Round::Auction or Engine::Round::Stock
```

If you get a `NameError` or `LoadError`, check:

- Module name in `game.rb` matches `Engine::Game::G8888` exactly
- `meta.rb` has a `module Meta` (not `class Meta`) with `include Game::Meta`
- All four files are saved and the container has picked up the changes (check `docker compose logs rack -f`)

Navigate to `http://localhost:9292/` → New Game → select "8888". If the title does not appear, restart the rack container: `docker compose restart rack`.

---

## 5. Inspect Your Tiles and Map

| URL | What it shows |
|-----|---------------|
| `http://localhost:9292/tiles/8888/all` | Every tile defined for your title |
| `http://localhost:9292/map/8888` | Your full hex map |
| `http://localhost:9292/tiles/57` | Standard tile 57 for reference |

Optional URL params: `r=<rotation>` (integer or `all`), `n=<location_name>`, `grid` (show triangular grid overlay).

---

## 6. Run the Test Suite

```bash
# Your title only (fast)
docker compose exec rack bundle exec rspec spec/lib/engine/game/fixtures_spec.rb -e "8888"

# Full suite in parallel (before submitting a PR)
docker compose exec rack bundle exec parallel_rspec spec/
```

There are no fixtures yet for a new title, so the first command just confirms there are no syntax errors. Add a fixture as soon as you have a complete game — see [Testing Your Game](testing.html).

---

## 7. Code → Reload Cycle

- Edit any file under `lib/`, `models/`, or `routes/`
- The `rack` container auto-restarts via `rerun` within a few seconds
- Refresh the browser — no manual restart needed
- IRB sessions do **not** auto-reload; `exit` and reopen to pick up changes

---

## Day-to-Day Commands

### Lint

```bash
docker compose exec rack bundle exec rubocop lib/engine/game/g_18_oe/
```

130-character line limit · no `puts`/`p` in committed code.

### IRB (logic testing)

```bash
docker compose exec rack irb -r ./lib/engine
```

### Smoke spec (recommended, not yet committed)

```ruby
# spec/games/g_18_oe/smoke_spec.rb
require 'spec_helper'
require 'engine/game/g_18_oe/game'

describe Engine::Game::G18OE do
  it 'initialises a 4-player game without errors' do
    expect { described_class.new(%w[A B C D]) }.not_to raise_error
  end
end
```

```bash
docker compose exec rack bundle exec rspec spec/games/g_18_oe/smoke_spec.rb
```

### Pre-commit hook (install once, after smoke spec is committed)

```bash
cat > ~/18xx/18xx/.git/hooks/pre-commit <<'SH'
#!/usr/bin/env bash
set -euo pipefail
bundle exec rspec spec/games/g_18_oe/smoke_spec.rb
bundle exec rubocop lib/engine/game/g_18_oe/
SH
chmod +x ~/18xx/18xx/.git/hooks/pre-commit
```

### Quick file lookups

```bash
# All 18OE Ruby files
ls ~/18xx/18xx/lib/engine/game/g_18_oe/{,step/,round/}

# Rules text
less ~/18xx/18xx/rules/18OE_Rulebook_v_1.0.txt
less ~/18xx/18xx/rules/18OE_Playbook_v_1.0.txt
```

---

## What's Next

Continue the tutorial in order:

1. [Game Structure](game-implementation.html) — all four files in detail with full examples
2. [Map Configuration](map.html) — hex grid, terrain costs, location names
3. [Corporations & Companies](entities.html) — full CORPORATIONS/COMPANIES field reference
4. [Trains, Phases & Market](trains-phases.html) — economic arc configuration
5. [Testing Your Game](testing.html) — fixtures, parallel_rspec, IRB debugging

---
*Version: 2026-05-08 — derived from `DEVELOPMENT.md`, `Makefile`, `docker-compose.yml`, `scripts/import_game.rb`.*
