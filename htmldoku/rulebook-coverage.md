# 18OE — Rulebook Coverage

Coverage of the 18OE Rulebook v1.0 by section. Each row shows the alpha and beta implementation status and the primary code location.

**Status key:** ✅ Complete · 🔵 Partial · ⬜ Not started · ➡️ Deferred / out of scope

---

## Part 1 — Setup

| § | Title | Alpha | Beta | Notes |
|---|-------|-------|------|-------|
| §1 | Game Setup (bank, certs, starting cash) | ✅ | — | `game.rb` constants |
| §2.1 | Minor companies | ✅ | — | `entities.rb` |
| §2.2 | Regional companies | ✅ | — | `entities.rb` |
| §2.3 | Major companies | ✅ | — | `entities.rb` |
| §2.4 | National companies | ✅ | — | `entities.rb` |
| §2.5 | Concession cards | ➡️ | ➡️ | Defined in entities; Concession Phase deferred |
| §2.6 | Private companies | ✅ | — | `entities.rb` |
| §2b | Map configuration | 🔵 | 🔵 | ~85% alpha; ferry hexes + OE tiles pending |

---

## Part 2 — Rounds and Phases

| § | Title | Alpha | Beta | Notes |
|---|-------|-------|------|-------|
| §3 | Track rights chits | ✅ | — | Zone constants + `track_rights` method |
| §4 | Auction Phase | 🔵 | — | ~80%; all-pass price reduction pending |
| §5 | Concession Railroad Phase | ➡️ | ➡️ | Deferred until core mechanics stable |
| §6a | Stock market grid | ✅ | — | `MARKET` constant |
| §6b | Share price movement (three-way rule) | ✅ | — | `Step::Dividend#share_price_change` (BUG-013/014 fixed) |
| §6c | Stock round — par, buy, sell | 🔵 | — | ~70%; voluntary removal + reserved shares pending |
| §6d | Dividend options | ✅ | — | Pay / withhold / split |
| §7a | Train roster | ✅ | — | `TRAINS` constant |
| §7b | Phase structure | ✅ | — | `PHASES` constant |

---

## Part 3 — Operating Round

| § | Title | Alpha | Beta | Notes |
|---|-------|-------|------|-------|
| §8a | Operating order | ✅ | — | `operating_order` override |
| §8b | Track laying | 🔵 | — | ~90%; first-OR green tile exception pending |
| §8c | Token placement | ✅ | — | Zone cost + `home_token_locations` |
| §8d | Routing — land trains | ⬜ | 🔵 | Local/express counting → beta |
| §8d | Routing — cross-water (ferry + sea) | ⬜ | ⬜ | Sea zone data defined; no routing logic |
| §8e | Orient Express | ⬜ | ⬜ | Not started; city revenues must be verified first |
| §8f | Pullman cars | ⬜ | — | Not started |
| §8g | Train purchase + force-buy | 🔵 | — | ~60%; force-buy + insolvency pending |
| §8h | Major OR buy/sell shares step | 🔵 | 🔵 | DOWN on issuance done; Exchange + abandoned minor purchase → beta |
| §9 | Minor special abilities | 🔵 | 🔵 | C/D/J/L partial (alpha); H + sea variant → beta |
| §10 | Private special abilities | 🔵 | 🔵 | 5 partial, 2 not started (alpha); 3 partial + 1 not started (beta) |

---

## Part 4 — Companies

| § | Title | Alpha | Beta | Notes |
|---|-------|-------|------|-------|
| §10.5 | Minor SR mergers (core action) | ✅ | 🔵 | Core merge done (needs PR); ability transfer + edge cases → beta |
| §11.1–11.5 | National revenue + train rules | 🔵 | 🔵 | Formation done; revenue calculation → beta |
| §11.6 | Train purchase rules (nationals claim rusted) | 🔵 | 🔵 | Partially implemented (needs PR) |
| §11.7 | Major OR share step (issue + price DOWN) | ✅ | 🔵 | Issuance DOWN done (BUG-022); abandoned minor purchase → beta |
| §12A | Track rights chit mechanics | ✅ | — | `transfer_minor_track_rights!` |
| §12E | Minor merger edge cases | — | ⬜ | All items → beta |
| §13 | Consolidation Phase | 🔵 | ⬜ | Scaffold + step list done; conditional merge logic not started |

---

## Part 5 — End Game

| § | Title | Alpha | Beta | Notes |
|---|-------|-------|------|-------|
| §14 | Token transfer between majors | ⬜ | — | Not started |
| §15 | End game triggers (bank break, level-8) | ✅ | 🔵 | Bank/level-8/remainder all done; second final OR → beta |
| §16 | Tests | ⬜ | ⬜ | Not started |

---

## Part 6 — Deferred / Variants

| § | Title | Status | Notes |
|---|-------|--------|-------|
| §5 | Concession Railroad Phase | ➡️ Deferred | Deferred until core mechanics stable |
| §17 | UK-FR variant | ➡️ Deferred | No work until full base game ships |
| — | Scenarios (medium/short) | ➡️ Deferred | |

---

## Coverage Summary

| Milestone | Sections complete | Sections partial | Sections not started |
|-----------|-----------------|-----------------|---------------------|
| Alpha | 14 | 9 | 5 |
| Beta | — | 10 | 8 |
| Deferred | 3 | — | — |

---

*Rule reference: `rules/18OE_Rulebook_v_1.0.txt`. Updated 2026-05-14.*
