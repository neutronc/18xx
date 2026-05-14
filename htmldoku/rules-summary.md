# 18OE — Game Rules Summary

Quick reference for the core rules of 18OE. Intended as a developer cheat-sheet alongside the full rulebook at `rules/18OE_Rulebook_v_1.0.txt`.

---

## Company Types

| Type | Certs | Par Values | Float Condition |
|---|---|---|---|
| Minor | 1 (100%) | £120 fixed | Selected in auction; floated in Regional/Minor Phase |
| Regional | 3 (50%+25%+25%) | £60/65/70/75/80/90 | Pay 2× par to treasury |
| Major | 9 (20%+8×10%) | £75/80/90/100/110/120 | Expand from floated regional |
| National | 9 (20%+8×10%) | Inherits major | Forms at Phase 4/6/8 start |

---

## Game Phases (Railroad)

1. **Auction** — buy privates, minors, concessions
2. **Concession** (Train Phase 1) — 10 float actions in numbered order *(deferred)*
3. **Regional/Minor** — until 18 regionals + all 12 minors floated; 6 regionals removed
4. **Major** — secondary shares available; majors can float; level-3 trains available
5. **Consolidation** — first SR after Phase 5; remaining minors/regionals merge or abandon

---

## Train Phases & Rusting

| Level | Type | Qty | Face Value | Rusts At |
|---|---|---|---|---|
| 2 | 2+2 / — | 30 | £100 | Phase 4 |
| 3 | 3+3 / 3 | 20 | £225 / £200 | Phase 6 |
| 4 | 4+4 / 4 | 10 | £350 / £300 | Phase 8 |
| 5 | 5+5 / 5 | 8 | £475 / £400 | — |
| 6 | 6+6 / 6 | 6 | £600 / £525 | — |
| 7 | 7+7 / 4D | 14 | £750 / £850 | — |
| 8 | 8+8 / 5D | 8 | £900 / £1000 | — |

Level 8 becomes available after the 4th Level 7 purchase (not at a fixed phase).

---

## Train Limits by Phase

| Phase | Minor/Regional | Major | National |
|---|---|---|---|
| 1–3 | 2 | 4 | — |
| 4 | 1 | 3 | 4 |
| 5–6 | — (must merge) | 2 | 3 |
| 7–8 | — | 3 | 4 |

---

## Stock Market Movement

- **RIGHT**: dividend ≥ share value (also +3 RIGHT on first OE run)
- **LEFT**: zero dividend paid
- **UP**: all shares in players' hands at end of SR
- **DOWN**: each share sold
- **No move**: dividend > 0 but < share value; or at £550

---

## Operating Round (per company)

1. Lay track (tile pts: minor/regional=3, major=6, national=9; nationals pay no terrain costs)
2. Place token (one per OR; regionals/minors restricted to home zone)
3. Run trains & calculate revenue
4. Pay/split/hold (nationals must pay ALL as dividends)
5. Transfer tokens (majors only — between same player's majors)
6. Buy trains
7. Buy or sell shares (majors only)

---

## Track Rights Zones

| Zone Code | Zone Name | Home Token Cost | Terrain Discount |
|---|---|---|---|
| UK | United Kingdom | £40 | None |
| PHS | Prussia/Holland/Switzerland | £40 | None |
| FR | France/Belgium | £20 | None |
| AH | Austria-Hungary | £20 | None |
| IT | Italy | £10 | 20% |
| SP | Spain/Portugal | £10 | 20% |
| RU | Russia | £10 | 20% |
| SC | Scandinavia | £10 | 20% |

---

## Orient Express

- Majors only; route must include Constantinople + one of Paris/London/Berlin/Madrid/Sankt-Peterburg; must include some land track
- Constantinople is on-map pre-printed yellow at **AA82** (eastern map terminus)
- First run bonus: £30 (Phase 2–4), £60 (Phase 5–6), £100 (Phase 7–8) + RIGHT×3
- Trains level ≤4 can be combined (combined level = sum); level 5+ cannot combine

---

## National Revenue (unique)

Nationals have virtual tokens in every city/town in their home zone:

1. Linked cities/towns in zone → counted at face value (D trains double)
2. Remaining capacity → filled at £60/city or £10/town (no linkage required)

Implementation: `Graph.new(home_as_token: true, no_blocking: true)` — see [Engine Concepts](engine-concepts.html).

---

## Cross-Water Costs

- Track: Ferry = +£5 × distance; Sea = +£10 × number of sea zones
- Tokens: Ferry = +£20 × distance; Sea = +£40 × number of sea zones
- 6 sea zones: North Sea, Baltic, Western Mediterranean, Adriatic, Aegean, Black Sea
