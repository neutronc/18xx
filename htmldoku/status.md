# 18OE — Implementation Tracker

Current milestone progress and branch/PR status. Updated 2026-05-14.

---

## Alpha Milestone Progress

Target: auction · floating · minor-regional phase · major phase to game end · map complete (port icons displayed, no routing) · all minor/private abilities not gated on beta features.

| Section | Topic | Status | Notes |
|---------|-------|--------|-------|
| §1 | Game Setup | ✅ Complete | |
| §2a | Companies / Entities | ✅ Complete | |
| §2b | Map | ~85% | OE custom tiles + remaining ferry hexes pending |
| §3 | Track Rights | ✅ Complete | |
| §4 | Auction Phase | ~80% | All-pass price reduction pending |
| §6a | Stock Market Grid | ✅ Complete | |
| §6b | Share Price Movement | ✅ Complete | Three-way rule implemented (BUG-013/014 fixed) |
| §6c | Stock Round | ~70% | Minor merge done; voluntary removal + reserved shares pending |
| §6d | Dividend Options | ✅ Complete | |
| §7a | Train Data | ✅ Complete | |
| §7b | Phase Structure | ✅ Complete | |
| §8a | Operating Order | ✅ Complete | |
| §8b | Track Laying | ~90% | First-OR green tile exception pending |
| §8c | Token Placement | ✅ Complete | |
| §8f | Pullman Cars | 0% | Not started |
| §8g | Train Purchase | ~60% | Obligation done; force-buy pending |
| §8h | OR Share Step | ~60% | DOWN on issuance done (BUG-022); Exchange step TBD |
| §9 | Minor Special Abilities | ~90% | C/D/J/L partial; M (CIWL Pullman) not started |
| §10 | Private Special Abilities | ~80% | 5 partial; 2 not started |
| §11 | Nationals (base) | ~65% | Formation + rusted-train claim done; revenue → beta |
| §12A | Track Rights Chit | ✅ Complete | |
| §13a | Consolidation Scaffold | ✅ Complete | |
| §14 | Token Transfer | 0% | Not started |
| §15 | End Game | ~80% | Bank/level-8/remainder done; second final OR → beta |
| §16 | Tests | 0% | Not started |

---

## Beta Milestone Progress

Target: sea zones · ports and ferry runs · Orient Express · minor→major mergers (full) · nationalization · railroad formation (nationals) · abandoning minors.

| Section | Topic | Status | Notes |
|---------|-------|--------|-------|
| §8d | Routing: Land + Cross-Water | 0% | Sea zone data defined; no routing logic yet |
| §8e | Orient Express | 0% | Prerequisite: all city revenues verified |
| §9 | Minor D (sea/ferry variant) | 0% | Land variant partial (alpha); sea/ferry → beta |
| §9 | Minor H (Great Western Steamship) | 0% | |
| §10 | Wien Südbahnhof | Partial | Token wired; zone-bypass + sea costs pending |
| §10 | Star Harbor | Partial | Token wired; port routing + SR window pending |
| §10 | White Cliffs Ferry | Partial | Token wired; Phase 5 hook + ferry routing pending |
| §10.5 | Minor SR Mergers (full) | Partial | Core action done (needs PR); edge cases + ability transfer pending |
| §11 | Nationals claim rusted trains | Partial | Implemented (needs PR) |
| §11 | National revenue | 0% | linked/unlinked split, D-train double, flat-rate fill |
| §12E | Minor Merger Edge Cases | 0% | |
| §13 | Consolidation Phase (full) | 0% | |
| §15 | Second Final OR | 0% | |
| Map | Ferry sea hexes + routing | Partial | Lille↔London tiles done; engine override pending |
| §2 | Patronage Tiles | 0% | |

---

## Bug Tracker

| Metric | Value |
|--------|-------|
| Total bugs | 25 |
| Closed | 19 (76%) |
| Open alpha bugs | **0** ✅ |
| Open beta bugs | 6 |

---

## Open PRs

### Fork PRs *(Witzman/18xx — staging for upstream)*

| Fork PR | Upstream PR | Branch | Contents |
|---------|-------------|--------|----------|
| [#52](https://github.com/Witzman/18xx/pull/52) | [tobymao#12601](https://github.com/tobymao/18xx/pull/12601) | `18oe_fix_par_prices` | Fix get_par_prices for regional companies |
| [#53](https://github.com/Witzman/18xx/pull/53) | [tobymao#12602](https://github.com/tobymao/18xx/pull/12602) | `18oe_fix_share_price_movement` | §4.4 three-way OR share price movement (BUG-013/014) |
| [#54](https://github.com/Witzman/18xx/pull/54) | [tobymao#12603](https://github.com/tobymao/18xx/pull/12603) | `18oe_fix_president_overcap` | President pool purchase above 60% at 2× price (BUG-021) |
| [#55](https://github.com/Witzman/18xx/pull/55) | [tobymao#12604](https://github.com/tobymao/18xx/pull/12604) | `18oe_fix_stock_terrain` | Stock round fixes + zone-based terrain discount (BUG-008/009/010/015/022) |
| [#56](https://github.com/Witzman/18xx/pull/56) | [tobymao#12605](https://github.com/tobymao/18xx/pull/12605) | `18oe_fix_level8_gameend` | Level-8 train gate + game-end timing (BUG-018/024/025/027) |

---

## Branch Status

| Branch | Base | Status | Contents |
|--------|------|--------|----------|
| `18oe_abilities` | upstream/master | rebased ✓ | Minor C/D/J/L + private abilities wiring |
| `18oe_mergers` | upstream/master | rebased ✓ | Minor SR merger · national formation · SR fixes |
| `18oe_testing` | upstream/master | rebased ✓ | Integration: gamefixes + abilities + mergers |
| `18oe_fix_par_prices` | upstream/master | PR open | par price fix |
| `18oe_fix_share_price_movement` | upstream/master | PR open | BUG-013/014 |
| `18oe_fix_president_overcap` | upstream/master | PR open | BUG-021 |
| `18oe_fix_stock_terrain` | upstream/master | PR open | BUG-008/009/010/015/022 |
| `18oe_fix_level8_gameend` | upstream/master | PR open | BUG-018/024/025/027 |

---

*Source of truth: `MD/todo.md` (backlog), `MD/inwork.md` (in-flight), `MD/bugs.md` (bug tracker).*
