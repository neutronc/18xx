# Fixture Testing

Fixtures are JSON snapshots of complete or in-progress games. The test suite replays every fixture and asserts that the final result matches the recorded outcome. Adding a fixture for your title gives you regression coverage without writing a single explicit test assertion.

---

## How Fixtures Work

When the test suite loads a fixture it:

1. Reads the `actions` array from the JSON file.
2. Initialises a fresh engine instance with the fixture's `title` and `players`.
3. Replays every action in order via `Game::Base#process_action`.
4. Compares the final player scores against the `result` hash in the file.

A failing fixture means the engine no longer produces the same outcome from the same sequence of moves — a regression.

The spec that runs all fixtures is `spec/lib/engine/game/fixtures_spec.rb`. It discovers fixture files automatically; no registration is required.

---

## Fixture File Location

Place fixture files under:

```
public/fixtures/<title>/
```

For example:

```
public/fixtures/1830/1830_game_end_bank.json
public/fixtures/1830/26855.json
```

The directory name must exactly match the game's `GAME_TITLE` string (the canonical title, e.g. `'1830'`).

---

## Creating a Fixture

### 1. Play or import a complete game

The easiest source is a finished game from production. Import it into your local instance:

```bash
docker compose exec rack irb
```

```ruby
load 'scripts/import_game.rb'
import_game(12345)   # replace with the production game ID
```

All player passwords are reset to `password` after import.

Alternatively, play a game to completion on your local instance.

### 2. Export the game JSON

Open the game in the browser and navigate to:

```
http://localhost:9292/api/game/<id>
```

Save the JSON response as a file. Or use the export link in the game UI (⋮ menu → Export).

### 3. Anonymise and clean the file

The fixture spec enforces several format requirements. Edit the JSON to meet them:

| Requirement | What to change |
|-------------|---------------|
| `"status"` must be `"finished"` | Do not use in-progress games |
| Player names must be anonymised | Replace with `"Player 1"`, `"Player 2"`, etc. |
| `"description"` must be empty | Set to `""` |
| All action IDs must be integers | Verify no string IDs |
| File must be single-line | See compression step below |

Remove or scrub chat messages — `"message"` actions expose real player usernames.

### 4. Compress to a single line

The spec checks that fixtures are stored compressed (single line with no extra whitespace). Use `jq`:

```bash
jq -c . my_game.json > public/fixtures/1865/my_game.json
```

Or use the project's make target if available:

```bash
make fixture_format
```

---

## Fixture JSON Structure

```json
{
  "id": 12345,
  "description": "",
  "user": { "id": 0, "name": "You" },
  "players": [
    { "id": 1, "name": "Player 1" },
    { "id": 2, "name": "Player 2" },
    { "id": 3, "name": "Player 3" }
  ],
  "min_players": 2,
  "max_players": 6,
  "title": "1830",
  "settings": {
    "seed": 1879860849,
    "is_async": true,
    "optional_rules": []
  },
  "status": "finished",
  "turn": 9,
  "round": "Operating Round",
  "result": {
    "1": 13048,
    "2": 12109,
    "3": 12025
  },
  "actions": [
    { "type": "bid",  "entity": 1, "entity_type": "player", "id": 1, "company": "CA", "price": 165 },
    { "type": "par",  "entity": 2, "entity_type": "player", "id": 5, "corporation": "PRR", "share_price": "100,0,6" },
    { "type": "pass", "entity": 3, "entity_type": "player", "id": 6 },
    ...
  ]
}
```

The `result` hash maps **player ID strings** to their final scores. The engine calculates scores by summing cash, share values, and any other title-specific scoring. The fixture spec asserts the replay produces exactly these values.

---

## Running Fixture Tests

Run all fixtures:

```bash
docker compose exec rack bundle exec rspec spec/lib/engine/game/fixtures_spec.rb
```

Run only fixtures for one title:

```bash
docker compose exec rack bundle exec rspec spec/lib/engine/game/fixtures_spec.rb \
  -e "1830"
```

Run in parallel (recommended for the full suite):

```bash
docker compose exec rack bundle exec parallel_rspec spec/
```

---

## Debugging a Failing Fixture

### Identify the failing action

The spec error message includes the action ID where replay diverged. Find that action in the fixture JSON and examine the game state immediately before it.

### Load the fixture in IRB

```bash
docker compose exec rack irb
```

```ruby
require_relative 'lib/engine'

raw = JSON.parse(File.read('public/fixtures/1830/26855.json'))

# Replay all actions
g = Engine::Game::G1830::Game.new(
  raw['players'].map { |p| p['name'] },
  id: raw['id'],
  actions: raw['actions']
)

# Inspect state
g.current_round.class           # => Engine::Round::Operating
g.current_entity.name           # => "PRR"
g.corporations.map { |c| [c.name, c.cash] }.to_h
g.players.map { |p| [p.name, p.cash] }.to_h
```

To replay only up to action N:

```ruby
g = Engine::Game::G1830::Game.new(
  raw['players'].map { |p| p['name'] },
  id: raw['id'],
  actions: raw['actions'].first(42)   # replay first 42 actions
)
```

### Add a breakpoint

```ruby
# In your step or game file:
require 'pry-byebug'
binding.pry   # execution pauses here when hit during replay
```

Then replay the fixture in IRB — the pry prompt will open at the breakpoint.

---

## Readable Diffs with jq

Fixture files are compressed to single lines, which makes git diffs unreadable. Configure git to expand them before diffing:

Add to `.git/config` (or `~/.gitconfig` to apply globally):

```ini
[diff "json"]
  textconv = bash -c 'jq . "$0" -'
```

Add to `.gitattributes` in the project root:

```
public/fixtures/**/*.json diff=json
```

Now `git diff` shows properly indented JSON.

---

## Fixture Format Options

An optional `fixture_format` key controls how the formatting make-target processes the file:

```json
"fixture_format": {
  "keep_user": false,
  "keep_description": false,
  "chat": "scrub"
}
```

| Key | Values | Effect |
|-----|--------|--------|
| `keep_user` | `true` / `false` | Preserve or clear the `user` field |
| `keep_description` | `true` / `false` | Preserve or clear `description` |
| `chat` | `"scrub"` / `"keep"` / omit | Replace message content with `""`, keep as-is, or remove message actions entirely |

---

## Updating a Fixture After an Intentional Engine Change

When you intentionally change engine behaviour (fix a rules bug, implement a missing rule), existing fixtures may fail because the new code produces different final scores. Do not simply re-record the fixture — first decide which is correct:

| Situation | Action |
|-----------|--------|
| The old fixture was wrong (the engine had a bug) | Fix the engine, then re-record the fixture |
| The fixture was correct and the change broke it | Fix the change so it doesn't regress the existing game |
| The rules genuinely changed (errata) | Re-record the fixture and note the rules change in the PR |

### Re-recording a fixture

1. Play or import a new complete game that exercises the new behaviour.
2. Export and anonymise as described in [Creating a Fixture](#creating-a-fixture).
3. Replace the old fixture file or add a new one alongside it.
4. Confirm the spec passes with the new fixture before deleting the old one.

If the change affects many fixtures, run the full suite first to see the scope:

```bash
docker compose exec rack bundle exec rspec spec/lib/engine/game/fixtures_spec.rb \
  --format documentation 2>&1 | grep "FAILED\|passed"
```

---

## CI and Parallel Execution

The full fixture suite covers hundreds of games and takes several minutes sequentially. Always run in parallel before submitting a PR:

```bash
# Run all specs in parallel (uses all available CPU cores)
docker compose exec rack bundle exec parallel_rspec spec/

# Run only fixture specs in parallel
docker compose exec rack bundle exec parallel_rspec spec/lib/engine/game/

# Set explicit process count
docker compose exec rack bundle exec parallel_rspec -n 4 spec/
```

`parallel_rspec` splits spec files across worker processes. Output is buffered per worker and printed at the end. A failing fixture prints the action ID and expected vs actual result hash.

### Checking only your title before a PR

```bash
# Fast: syntax + your fixtures only
docker compose exec rack bundle exec rspec \
  spec/lib/engine/game/fixtures_spec.rb -e "8888"

# Then full parallel suite to catch regressions
docker compose exec rack bundle exec parallel_rspec spec/
```

---

## What's Next

- Step-by-step game title setup: [Game Structure](game-implementation.html)
- Running the dev environment: [Development Setup](getting-started.html)
- Common rules patterns with test examples: [Common Patterns](common-patterns.html)
- Title readiness checklist: [Title Checklist](title-checklist.html)

---
*Version: 2026-05-08 — derived from `public/fixtures/README.md`, `spec/lib/engine/game/fixtures_spec.rb`, `DEVELOPMENT.md`.*
