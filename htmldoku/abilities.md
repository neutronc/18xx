# Ability Types Reference

Company and corporation abilities are defined as hashes in `entities.rb` files. The engine processes them via `lib/engine/ability/` and evaluates their legality through `Game::Base#ability_right_time?`. This page is an exhaustive reference for ability types, their fields, and the `when:` vocabulary.

---

## Ability Type Frequency

Frequencies extracted from analysis of 112 `entities.rb` files (1,111 COMPANIES, 1,241 CORPORATIONS) across the engine.

| Type | Occurrences | Games | Key fields |
|------|-------------|-------|------------|
| `exchange` | 260 | 31 | `corporations:`, `from:`, `when:` |
| `tile_lay` | 232 | 59 | `count:`, `when:`, `free:`, `tiles:`, `hexes:`, `consume_tile_lay:`, `closed_when_used_up:` |
| `blocks_hexes` | 180 | 40 | `hexes:` |
| `no_buy` | 175 | 35 | (no extra fields) |
| `shares` | 124 | 43 | `shares:` |
| `close` | 108 | 38 | `when:`, `corporation:`, `on_phase:` |
| `revenue_change` | 92 | 14 | `revenue:`, `on_phase:` |
| `assign_hexes` | 82 | 34 | `hexes:` |
| `reservation` | 78 | 11 | `hexes:` |
| `hex_bonus` | 54 | 10 | `hexes:`, `amount:` |
| `token` | 53 | 27 | `price:`, `count:`, `corporation:` |
| `base` | 50 | 8 | `description:` |
| `tile_discount` | 44 | 28 | `terrain:`, `discount:` |
| `assign_corporation` | 34 | 21 | `corporations:` |
| `blocks_hexes_consent` | 32 | 4 | (blocking released on owner consent) |
| `description` | 21 | 8 | `description:` |
| `choose_ability` | 19 | 6 | (no standard fields) |
| `manual_close_company` | 19 | 1 | (no standard fields) |
| `sell_company` | 19 | 2 | (no standard fields) |
| `train_discount` | 16 | 12 | `discount:`, `trains:` |
| `teleport` | 16 | 12 | `hexes:`, `tiles:` |
| `tile_income` | 10 | 9 | (no standard fields) |
| `train_limit` | 9 | 6 | (no standard fields) |
| `generic` | 8 | 1 | `desc:` |
| `additional_token` | 7 | 7 | (no standard fields) |
| `train_buy` | 6 | 6 | (no standard fields) |
| `acquire_company` | 6 | 2 | (no standard fields) |
| `borrow_train` | 2 | 2 | (no standard fields) |
| `blocks_partition` | 2 | 2 | (no standard fields) |
| `train_scrapper` | 1 | 1 | (no standard fields) |
| `purchase_train` | 1 | 1 | (no standard fields) |

---

## Ability Structure

Standard ability hash in `entities.rb`:

```ruby
{
  type: 'tile_lay',           # required
  owner_type: 'player',       # 'player' | 'corporation'
  when: 'track',              # string or array; see When: Field section
  count: 2,                   # number of uses; omit = unlimited
  hexes: %w[A1 B2],           # hex restriction
  tiles: %w[57 58],           # tile number restriction
  free: true,                 # waives tile cost
  closed_when_used_up: true,  # close company when count reaches 0
  reachable: true,            # must be reachable from home token
  consume_tile_lay: true,     # consumes one of the corporation's normal lay slots
  terrain: 'mountain',        # (on tile_discount) terrain type
  discount: 20,               # (on tile_discount / train_discount) amount
  trains: %w[2+2 3+3],        # (on train_discount) train types
  corporations: %w[GWR LNWR], # (on exchange / token / assign_corporation)
  from: 'par',                # (on exchange) source
  description: 'text',        # (on base / description / generic)
  price: 0,                   # (on token) placement cost
  corporation: 'GWR',         # (on token / close) specific corporation
  on_phase: 'Phase 4',        # (on close / revenue_change) phase trigger
  revenue: 20,                # (on revenue_change) new value
  amount: 30,                 # (on hex_bonus) bonus amount
}
```

### `count:` enforcement

`ability.use!` decrements `@count` [`lib/engine/ability/base.rb:1`]. When count reaches zero and `@remove_when_used_up` is true (the default), the ability is removed from the entity. `TileLay#use!` tracks `lay_count` and `upgrade_count` separately.

### `consume_tile_lay:` on `tile_lay` abilities

- `consume_tile_lay: true` — routes through `lay_tile_action`; increments `@round.num_laid_track`. The ability *consumes* one of the corporation's normal lay slots.
- Without `consume_tile_lay` — routes through `lay_tile` directly. The ability is *extra* on top of the normal budget.

### `blocks_hexes` vs `blocks_hexes_consent`

- `blocks_hexes` — unconditional; blocked until the company is purchased or closed.
- `blocks_hexes_consent` — blocking released when the owning player consents. Used for concession cards (released when the concession is transferred or the major is parred). Reference: 1822 family.

---

## `when:` Field Complete Vocabulary

649 occurrences across 75 games; 27 distinct values. Source: `Game::Base#ability_right_time?` [`lib/engine/game/base.rb`].

### OR Step-Scoped

Active only during the named Step class:

| Value | Active when | Typical ability types |
|-------|-------------|-----------------------|
| `'track'` | `Step::Track` | `tile_lay`, `tile_discount` |
| `'special_track'` | `Step::SpecialTrack` | `tile_lay`, `teleport` |
| `'token'` | `Step::Token` | `token` |
| `'special_token'` | `Step::SpecialToken` | `token`, `teleport` |
| `'route'` | `Step::Route` | `generic` |
| `'track_and_token'` | `Step::TrackAndToken` | `tile_lay`, `token` |
| `'buy_train'` | `Step::BuyTrain` | `train_discount` |
| `'buying_train'` | During train purchase (alias) | `train_discount` |
| `'single_depot_train_buy'` | Variant buy-train step | `train_discount` |
| `'dividend'` | `Step::Dividend` | `generic`, `revenue_change` |
| `'exchange'` | SR `Step::Exchange` | `exchange` |

### OR Turn-Scoped

Active at any point during the owning entity's OR turn:

| Value | Condition |
|-------|-----------|
| `'owning_corp_or_turn'` | OR active AND current operator owns the ability (155 occurrences) |
| `'owning_player_or_turn'` | OR active AND the president is the ability's player |
| `'owning_player_track'` | OR active AND president == ability's player AND in Track step |
| `'owning_player_token'` | OR active AND president == ability's player AND in Token step |
| `'or_between_turns'` | OR active AND `!current_operator_acted` |
| `'or_start'` | OR active AND `@round.at_start` |

### SR Turn-Scoped

| Value | Condition |
|-------|-----------|
| `'owning_player_sr_turn'` | SR active AND current entity is ability's player (155 occurrences) |
| `'stock_round'` | SR active, any player, any turn |

### Event-Triggered (on `close` abilities only)

| Value | Triggered by |
|-------|--------------|
| `'bought_train'` | `base.rb#buy_train` → `close_companies_on_event!` |
| `'ran_train'` | `step/dividend.rb` → `close_companies_on_event!` |
| `'operated'` | `step/dividend.rb#pass!` → `close_companies_on_event!` |
| `'par'` | `base.rb#after_par` → `close_companies_on_event!` |
| `'sold'` | `step/buy_company.rb` fires `'sold'` abilities |
| `'auction_end'` | Game-specific auction step |
| `'has_train'` | Revenue-change at OR start when the corporation has trains |

### Meta / Any-Round

| Value | Meaning |
|-------|---------|
| `'any'` | Usable at any time. Short-circuits all other checks. |

**Always-valid values** (no step prerequisite): `any`, `owning_corp_or_turn`, `owning_player_or_turn`, `owning_player_track`, `owning_player_token`, `owning_player_sr_turn`, `stock_round`, `or_between_turns`, `or_start`.

---

## `exchange` Ability — `from:` Values

| Value | Meaning |
|-------|---------|
| `'par'` | Concession pattern — company exchanged to float a corporation at par |
| `'ipo'` | Exchange for a share from the IPO pool |
| `'market'` | Exchange for a share from the secondary market |
| `%w[ipo market]` | Either source |
| `%i[reserved]` | Reserved share |

Concessions use `from: 'par'` per the 1822/1866 concession pattern.

---

## `description` Ability

Used to associate a minor with a major and to hold the human-readable rulebook ability text:

```ruby
# In CORPORATIONS for a minor:
abilities: [{ type: 'description', description: 'Associated minor for GWR' }]
```

The `par_via_exchange` field handles the mechanical association; the `description` ability is UI display only.

---

## 18OE Ability Mapping

### Minor special abilities

| Minor | Rule description | Ability types needed |
|-------|-----------------|----------------------|
| A — Silver Banner | Bank pays major treasury = share value on merge | `base` + custom hook in `merge_minor` |
| B — Orange Scroll | Track upgrades cost 1 tile point (not cities/grand/metro) | `tile_discount` + `tile_lay` extra slot |
| C — Golden Bell | President chooses operating position each OR | `choose_ability` + custom `operating_order` |
| D — Green Junction | Token in non-metro city; £20/£40 bonus by phase; removed at Phase 5 | `token` (free) + `hex_bonus` (phase-conditional) |
| E — Blue Coast | 33% discount on blue terrain; +1 tile pt in blue hexes | `tile_discount` (terrain: water) + `tile_lay` |
| F — White Peak | 33% discount on green terrain; +1 tile pt in green hexes | `tile_discount` (terrain: mountain) + `tile_lay` |
| G — Indigo Foundry | +2 tile points per OR | Custom `tile_lays` returning extra slots |
| H — Great Western Steamship | Reduces sea zones counted by 1 (Phase 1–6) or 2 (Phase 7–8) | Custom game hook; no standard type |
| J — Grey Locomotive Works | 10% discount on all train purchases | `train_discount` |
| K — Vermilion Seal | Mail contract pays revenue to treasury at OR start | `extra_revenue` hook or `hex_bonus` |
| L — Krasnaya Strela | +1+1 marker adds 1 city limit and 1 town count to assigned train | Custom game hook; no standard type |
| M — CIWL | 10 Pullman cars | Custom Pullman asset; no standard type |

### Private special abilities

| Private | Rule description | Ability types needed |
|---------|-----------------|----------------------|
| Wien Südbahnhof | Free station token placement | `token` (price: 0, when: 'token') |
| Barclay, Bevan, Barclay & Tritton | Three selectable options (re-set par / reserve share / prevent DROP) | `choose_ability` |
| Star Harbor Trading Co. | Port token in port city (doesn't consume slot) | `token` + `assign_hexes` |
| Central Circle Transport Corp. | Token in non-port city as town (£10–£60 by phase) | `token` + `hex_bonus` |
| White Cliffs Ferry | Lille (N31) token at Phase 5; enables ferry | `tile_lay` + phase-trigger logic |
| Hochberg Mining & Lumber | Token in rough terrain hex; track restricted to owner | `assign_hexes` + custom hook |
| Brandt & Brandau, Engineers | 4 tokens, up to 2/OR, free yellow tile; closes on last token | `tile_lay` (free: true, count: 4, closed_when_used_up: true) |
| Swift Metropolitan Line | Protects one 2+2 from train limit | Custom game hook; no standard type |

---

## What's next

- How abilities are evaluated at runtime: [Game Engine](game-engine.html)
- OR step order in which ability `when:` values become active: [Round/Step System](round-step-system.html)
- Tile lay mechanics: [Tile Reference](tiles.html)

---
*Version: 2026-05-08 — derived from `lib/engine/ability/base.rb`, `lib/engine/ability/tile_lay.rb`, `lib/engine/game/base.rb`.*
