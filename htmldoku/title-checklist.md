# New Title Checklist

Use this checklist to track progress from first commit to production release.

---

## Before First Run

- [ ] **Designer/publisher approval obtained** — implementing a title requires permission from the rights holder; confirm before opening any PR (questions → Slack **#18xxgamesdev**)
- [ ] `lib/engine/game/g_<name>/meta.rb` created with `DEV_STAGE = :prealpha`
- [ ] `lib/engine/game/g_<name>/entities.rb` — CORPORATIONS and COMPANIES defined
- [ ] `lib/engine/game/g_<name>/map.rb` — TILES, LOCATION_NAMES, HEXES, LAYOUT defined
- [ ] `lib/engine/game/g_<name>/game.rb` — includes meta/entities/map, TRAINS, PHASES, MARKET defined
- [ ] `Game.new(%w[Alice Bob Charlie])` runs without exception in IRB
- [ ] Title appears in the game creation list at `http://localhost:9292/`
- [ ] At least one complete game played locally (auction → OR → game end)

## Code Quality

- [ ] No hardcoded player names or game IDs
- [ ] All tile strings validated at `/tiles/<title>/all` — no rendering errors
- [ ] Map renders correctly at `/map/<title>` with no missing hexes
- [ ] SVG logos present at `public/logos/<title>/<SYM>.svg` for all corporations
- [ ] `frozen_string_literal: true` at the top of every `.rb` file
- [ ] No `puts` or `pp` left in game code (use `@log <<` for game messages)

## Testing

- [ ] At least one fixture exists in `public/fixtures/<TITLE>/`
- [ ] Fixture passes: `bundle exec rspec spec/lib/engine/game/fixtures_spec.rb -e "<TITLE>"`
- [ ] Full suite still green: `bundle exec parallel_rspec spec/`
- [ ] Fixture covers at least one complete game (status: "finished")

## Ready for `:alpha`

- [ ] DEV_STAGE set to `:alpha` in meta.rb
- [ ] At least three distinct complete-game fixtures
- [ ] At least three games played by people other than the implementer
- [ ] Rules URL set in `GAME_RULES_URL`
- [ ] GAME_DESIGNER, GAME_LOCATION filled in meta.rb
- [ ] Optional rules (if any) defined in `OPTIONAL_RULES` with descriptions

## Ready for `:beta`

- [ ] DEV_STAGE set to `:beta`
- [ ] At least five complete games played, covering different player counts
- [ ] Fixtures for 3-player, 4-player, and 5-player game (if applicable)
- [ ] No known rules-compliance issues
- [ ] All abilities tested with fixtures (blocks_hexes, tile_lay, exchange, teleport)
- [ ] Game-end condition tested with a fixture

## Ready for `:production`

- [ ] DEV_STAGE set to `:production`
- [ ] Ten or more complete games played without rules disputes
- [ ] Rules-compliance confirmed with the game designer or published rules
- [ ] PR reviewed and approved by a maintainer
- [ ] CHANGELOG or PR description lists any deviations from physical rules

---

## Quick Command Reference

```bash
# Run your title's fixtures
docker compose exec rack bundle exec rspec spec/lib/engine/game/fixtures_spec.rb -e "8888"

# Run the full suite in parallel
docker compose exec rack bundle exec parallel_rspec spec/

# Open an IRB console
docker compose exec rack irb

# Check logs for startup errors
docker compose logs rack -f

# Validate all tiles render
# Open: http://localhost:9292/tiles/8888/all

# Validate the map
# Open: http://localhost:9292/map/8888
```

---

## Common Mistakes

| Symptom | Likely cause |
|---------|-------------|
| Title missing from game creation list | Module name doesn't match `Engine::Game::G<name>` exactly, or `Meta` submodule is missing |
| `NoMethodError` on `process_action` | A Step's `ACTIONS` includes a type but `process_<type>` is not implemented |
| `GameError: No valid route` on first OR | Corporation has no token or no reachable track; check home coordinates and HEXES |
| Revenue mismatch in fixture replay | Phase-based revenue string changed without updating the fixture |
| Fixture fails with `result mismatch` | Engine logic changed since fixture was recorded; either fix the engine or re-record |
| `RouteTooLong` unexpected | `check_distance` or train `distance` doesn't match tile connectivity |

---

## What's Next

- Full tutorial from the beginning: [Understanding the Engine](engine-concepts.html)
- Testing in depth: [Testing Your Game](testing.html)
- Common rule patterns with code: [Common Patterns](common-patterns.html)

---
*Version: 2026-05-08.*
