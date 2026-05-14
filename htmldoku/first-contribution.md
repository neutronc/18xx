# Your First Contribution

One small change, one pull request, merged. This guide walks the whole loop end-to-end.

No prior experience with this codebase is required. You need Docker running (see [Development Setup](getting-started.html)) and a GitHub account.

---

## What makes a good first task

The safest first contributions are **L1** — changes to constants only. No new files, no logic, nothing that can cascade. The result is immediately visible in the browser, and if something breaks it breaks obviously.

Good L1 tasks:
- Add or correct a location name on the map
- Fix a tile quantity (physical game has 6 of tile #57; the code says 4)
- Correct a corporation colour, token layout, or starting cash value
- Add a missing `GAME_RULES_URL` to a title's `meta.rb`
- Add a missing logo SVG

Pick **one thing**. A first PR should be small enough for a reviewer to confirm in two minutes.

---

## Find something to fix

Open any title at `http://localhost:9292/map/<TITLE>` and compare it against the physical game or published rules.

Some reliable places to look:

```bash
# Titles missing a rules URL
grep -rL 'GAME_RULES_URL' lib/engine/game/*/meta.rb

# Location names left as empty strings
grep -rn "=> ''" lib/engine/game/*/map.rb | grep -i location

# Tile counts that differ from a known manifest
grep -n "'57'" lib/engine/game/g_1830/map.rb
```

You can also browse the [Implementation Tracker](status.html) and filter for **L1** items — those are the lowest-risk changes on an active title.

---

## Worked example — adding a missing location name

We'll add a city name that shows blank on the map. The change lives in one line of the title's `map.rb`.

**1. Find the hex coordinate** from the browser map or the physical board. In this example, hex `K22` in game 1830 shows no name.

**2. Check what is currently in the file:**

```bash
grep 'K22' lib/engine/game/g_1830/map.rb
```

**3. Open `lib/engine/game/g_1830/map.rb` and find `LOCATION_NAMES`:**

```ruby
LOCATION_NAMES = {
  'A10' => 'Montreal',
  'A20' => 'Burlington',
  # ...
  'K22' => '',          # blank — physical board says 'Providence'
}.freeze
```

**4. Fill it in:**

```ruby
  'K22' => 'Providence',
```

**5. Check the result in the browser** — `http://localhost:9292/map/1830` should now show the name on that hex. No restart needed; `lib/` changes are picked up automatically by the running container.

---

## Run the tests

```bash
# Fast check: fixtures for your title only
docker compose exec rack bundle exec rspec spec/lib/engine/game/fixtures_spec.rb -e "1830"

# Before opening a PR: full suite
docker compose exec rack bundle exec parallel_rspec spec/
```

L1 data changes very rarely break a fixture. If one does fail, the output tells you exactly which field changed — fix it or ask in **#18xxgamesdev** on Slack.

---

## Commit and push

```bash
# Branch name: what changed, not the mechanic
git checkout -b fix/1830-providence-location-name

# Stage only your file
git add lib/engine/game/g_1830/map.rb

# Subject under 50 chars; say what was wrong
git commit -m "fix(1830): add missing location name for Providence (K22)"

git push -u origin fix/1830-providence-location-name
```

---

## Open the PR

Go to `https://github.com/tobymao/18xx` — GitHub will offer a **Compare & pull request** banner for your branch.

A good description for an L1 fix is short:

> **Problem:** hex K22 showed no location name on the 1830 map.
>
> **Change:** added `'K22' => 'Providence'` to `LOCATION_NAMES`.
>
> **Source:** 1830 rulebook p. 4 / physical board.

Reviewers want three things: what was wrong, what you changed, where you confirmed it. That's all.

---

## Before you click Submit

- [ ] Map renders correctly at `http://localhost:9292/map/<TITLE>`
- [ ] No tile errors at `http://localhost:9292/tiles/<TITLE>/all`
- [ ] Fixtures pass for the affected title
- [ ] Full suite still green
- [ ] PR description cites the source (rulebook page, scan, or physical board)
- [ ] Diff contains only the one change — no unrelated edits

---

## What to expect

**Review turnaround** is usually a few days for a clean L1 change. Maintainers are volunteers; if you haven't heard back after a week, leave a polite comment.

**Common feedback** on a first PR:
- *"Can you cite a source for this?"* — add a rulebook reference to your PR description.
- *"Fixtures need updating"* — re-record the affected fixture (see [Testing Your Game](testing.html)).

**After it merges**, your contribution is live on 18xx.games. Pull `master` and the name is there.

---

## What's next

| You want to… | Read |
|---|---|
| Tackle another L1 task | [Implementation Tracker](status.html) → filter L1 |
| Understand how the pieces fit | [Understanding the Engine](engine-concepts.html) |
| Implement a full new title | [Development Setup](getting-started.html) → [Title Checklist](title-checklist.html) |
| Ask a question | Slack **#18xxgamesdev** |

---
*Version: 2026-05-08.*
