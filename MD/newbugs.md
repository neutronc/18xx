# Auto-play script findings — engine API notes
# 2026-05-13

These are observations from writing `~/18xx/scripts/auto_play_18oe.rb`.
Not bugs in the 18OE game logic — bugs/gotchas in the engine API that
bit the scripting work. Useful for future test tooling and for any IRB scripts.

---

## Engine API gotchas found

### 1. `g.current_round` does not exist — use `g.round`
`Engine::Game::Base` exposes the round via `g.round`, not `g.current_round`.
Same for `g.finished` (no `?` variant).

### 2. Route step is hard-blocking when entity has trains
`Engine::Step::Route::ACTIONS = %w[run_routes]` — no `pass` in the list.
When `g.can_run_route?(entity)` is true the step is blocking and will raise
`"Blocking step Run Routes cannot process action pass"` if you pass.
Fix: submit `Engine::Action::RunRoutes.new(entity, routes: [])` for a 0-revenue
run when you don't want to compute real routes.

### 3. BuyTrain step is hard-blocking under train obligation (Phase 2–3)
`G18OE::Step::BuyTrain#must_buy_train?` returns true for any floated entity
with no trains. `pass` is not in `actions(entity)` when this is true.
Using `g.depot.upcoming.first` may return a train object that does not match
`step.buyable_trains(entity)` (different filtering). Always use
`step.buyable_trains(entity).first` to get the correct train for the entity.

### 4. `can_par?` does not exist on BuySellParShares — iterate prices directly
There is no `step.can_par?(entity, corp)` method. To check whether a regional
can be parred, call `step.get_par_prices(entity, corp)` and test for any price
the entity can afford. The cost for the president's 50% share is `par_price × 5`
in standard 18xx math (50% / 10% × price).

### 5. `get_par_prices` for regionals — unknown if cash-filtered
`G18OE::Step::BuySellParShares#get_par_prices` for minors returns all
`@game.stock_market.par_prices`. For non-minors it calls `super`. The base
implementation behaviour (whether it filters by entity cash) was not verified
during this session — needs a follow-up IRB check.

---

## Current state of auto_play_18oe.rb (~/18xx/scripts/)

- Auction: works cleanly, all 20 companies sold in ~22 actions
- SR1: all 12 minors floated with home tokens placed
- OR1.1 / OR1.2: tiles laid (cheapest-terrain first), trains bought, empty routes run
- SR2 / SR3: players pass (regional parring still broken — see issue 4 above)
- JSON output: `~/18xx/testgames/18OE_mid_game.json` — usable for map/track/token
  testing but no regionals or share trading visible

## Next steps to fix the script
1. Debug why `step.get_par_prices(entity, corp)` returns empty for regionals in SR1/SR2
   (add an explicit IRB probe after completing auction)
2. Once regionals par: HomeToken for regional goes to `corp.coordinates` automatically,
   but verify no pending_tokens are added
3. SR buy_shares: filter to only non-president shares of floated corps
4. Consider computing simple 1-train routes instead of empty runs to see revenue flow
