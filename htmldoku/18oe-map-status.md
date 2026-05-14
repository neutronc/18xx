# 18OE — Map Implementation Status

Current state of `lib/engine/game/g_18_oe/map.rb`. Tracks what is implemented, what is verified against the physical map, and what is still outstanding.

Map orientation: `LAYOUT = :pointy`, `AXES = { x: :number, y: :letter }`
Coordinate system: rows A–Z then AA–AH (34 rows); columns 2–88.

---

## Overall Status

| Area | Status |
|------|--------|
| Grid coverage | ✓ 651 blue hexes |
| Regional home city coordinates | ✓ All 24 |
| National region hex lists | ✓ All 8 (UK, SC, FR, PHS, AH, IT, SP, RU) — `NATIONAL_REGION_HEXES_COMPLETE = true` |
| Location names | ✓ All 255 |
| Sea zones | ✓ 19 named zones with hex lists; borders encoded as `type:province`; port stubs on 37 sea tiles |
| Custom tile codes | ✓ OE1–OE8, OE12–OE18, OE23–OE44 |
| Standard tile quantities | ✓ Complete |
| Terrain costs | ✓ UK, FR, SP, SC, Alps, IT, Adriatic, Carpathians, Balkans, Caucasus, river crossings |
| Station revenues | ✓ All 255 named locations have correct starting revenue |
| Pre-printed yellows | ✓ Liverpool J25, Manchester J27, Athinai AE72 |
| Pre-printed whites (path edges) | ~ Several cities missing path edges — see §3 |
| Ferry paths / distances | ? Outstanding |
| Double-town tile orientations | ? OE9–11, OE20–22 outstanding |

---

## Grid Bounds

```
A:  42-52, 66-74          B:  43-57, 63-81
C:  42-58, 64-66, 72-82   D:  41-57, 67-85
E:  24-28, 42-44, 48-58, 66-86
F:  23-29, 49-55, 69-85   G:  16-20, 24-28, 44-46, 50-56, 64-86
H:  15-21, 25-29, 43-47, 51-55, 63-87
I:  14-20, 26-28, 44-52, 64-86
J:  13-19, 23-29, 45-49, 63-87
K:  22-30, 40-50, 54-86   L:  23-31, 37-87
M:  22-30, 34-86          N:  31-85
O:  24, 28-86             P:  19-87
Q:  20-86                 R:  23-87
S:  24-86                 T:  23-81
U:  6-12, 22-80           V:  5-47, 51-79
W:  6-48, 54-78           X:  5-29, 33-37, 43-49, 55-77
Y:  2-28, 44-50, 56-78    Z:  3-27, 41, 45-51, 61-79
AA: 2-22, 48-54, 62-86    AB: 1-19, 27, 39-41, 51-57, 63-71, 77, 83-85
AC: 6-20, 38-40, 54-58, 64-68, 76-86
AD: 5-17, 39, 55, 65-71, 79-87
AE: 52, 68-72, 80-86      AF: 49-53, 67-69, 81-87
AG: 50-52, 68-70
```

---

## Red (Off-Board) Hexes

19 red hexes. (A40 → blue/Skagerrak; E88 → removed entirely; AH87 → blue/no zone.)

```
A:54 A:56    North Sweden (×2)         B:41 B:83    Bergen, Arkhangelsk
D:25         Scottish Highlands        F:87 G:88    Moskva (×2; G88 = gray through-track)
N:1 N:87     New York, Kharkov         S:88 T:87    Sevastopol (×2; S88 = gray through-track)
Z:1          Lisboa (2 station slots)  AB:87        Levant
AD:1         North Africa & Americas   AF:5 AF:11 AF:25   Casablanca, Melilla, Alger
AG:40 AG:88  Tunis, Alexandria & Suez
```

### Off-Board Revenue Values

All best-guess — verify against physical map.

| Hex | Name | Revenues (y/g/b/gray) | Path edges | Notes |
|-----|------|-----------------------|------------|-------|
| A54 | ~~North Sweden~~ | — | 1→4 | Gray through-track hex |
| A56 | North Sweden | 30/50/80/100 | 0, 1, 4, 5 | |
| B41 | Bergen | 30/60/80/120 | 1, 3, 4 | |
| B83 | Arkhangelsk | 30/50/60/60 | none | confirm isolated or needs edge |
| D25 | Scottish Highlands | 20/40/50/50 | 0, 5 | |
| F87 | Moskva | 30/50/80/100 | 0, 1, 2, 5 | |
| G88 | ~~Moskva~~ | — | 0→2 | Gray through-track hex |
| N1 | New York | —/60/100/160 | 5 | no yellow phase |
| N87 | Kharkov | 30/40/60/80 | 0, 1, 2 | |
| S88 | ~~Sevastopol~~ | — | 0→1 | Gray through-track hex |
| T87 | Sevastopol | 30/40/60/80 | 1 | |
| Z1 | Lisboa (2 slots) | 30/40/60/80 | 3, 4 | `city=revenue:0 ×2` also set |
| AB87 | Levant | 30/50/80/120 | 1, 2 | |
| AD1 | North Africa & Americas | —/40/80/120 | 4 | no yellow phase |
| AF5 | Casablanca | 30/40/60/80 | 3 | |
| AF11 | Melilla | 30/40/40/40 | 4 | |
| AF25 | Alger | 30/40/60/100 | 2, 3 | |
| AG40 | Tunis | 30/40/50/80 | 3, 4 | |
| AG88 | Alexandria & Suez | —/50/80/120 | 1 | no yellow phase |

---

## Pre-Printed Tiles

### ✓ Complete

| Hex | City | Tile string |
|-----|------|-------------|
| J25 | Liverpool | `city=revenue:30;label=Y;path=a:2,b:_0;path=a:_0,b:4` |
| J27 | Manchester | `city=revenue:20;upgrade=cost:30,terrain:mountain;path=a:1,b:_0;path=a:_0,b:4` |
| AE72 | Athinai | `city=revenue:20;path=a:1,b:_0;path=a:5,b:_0` |

### ~ Partial (revenue set, path edges missing)

| Hex | City | Current string | Missing |
|-----|------|----------------|---------|
| M28 | London | `city=revenue:30;label=L;upgrade=cost:30,terrain:water` | both edges |
| AA82 | Constantinople | `city=revenue:20;city=revenue:20;upgrade=cost:45,terrain:water;label=C` | both edges |
| N31 | Lille | `city=revenue:10;label=Y;border=edge:2,type:impassable;path=a:1,b:_0` | edge 0 |
| I20 | Dublin | `city=revenue:10` | both edges |
| O28 | Le Havre | `city=revenue:10` | both edges |
| X33 | Marseille | `city=revenue:20;label=Y` | both edges |
| U24 | Bordeaux | `city=revenue:10` | both edges |

Once both edges are confirmed, move each hex from `white:` to `yellow:` section in `map.rb`.

---

## Sea Zones

19 named zones implemented. Zone borders encoded as `border=edge:X,type:province` on all boundary edges. Port-entry stubs on 37 sea tiles (`junction;path=a:X,b:_0,terminal:1`).

✓ All zones: Celtic Sea, North Atlantic Ocean, North Atlantic Silver Coast, Bay of Biscay, English Channel, North Sea, Skagerrak (incl. A40), German Bight, Gulf of Finland, Baltic Sea, Strait of Gibraltar, Balearic Sea, Sea of Sardinia, Tyrrhenian Sea, Adriatic Sea, Aegean Sea, Levantine Sea, Black Sea, Karkinitsky Bay.

**Outstanding:**
- ? Ferry paths — start hex+edge, end hex+edge, distance number
- ? Sea zone distance numbers for cost calculation

---

## National Zone Boundaries

All 8 zones defined. `NATIONAL_REGION_HEXES_COMPLETE = true`.
`CITY_NATIONAL_ZONE` overrides: Q38 → FR, O52 → PHS.
`MINOR_EXCLUDED_HOME_CITIES` defined.

⚠️ Two stale entries to fix:
- `NATIONAL_REGION_HEXES['SC']` still contains `A40` (now blue) — remove
- `NATIONAL_REGION_HEXES['RU']` still contains `E88` (removed hex) — remove

---

## Terrain Costs

### Carpathians (rows P–T, cols 55–75)

- £30: R51, Q70, O50, O68, P57
- £45: Q60, Q62, Q64, Q68, R61, R69, N45, O62, P55, T67, T71, T73
- £60: O54, R71, S52, S54, T49, T51

### Balkans (rows X–AG, cols 55–80)

- £30: X65, Z63, Z69, Z75, AA68, AB53, AC66, AD65, AF69, AG50
- £45: X57, X61, X63, X67, Y62, Y68, Z61, Z65, Z71, AA64, AA72, AB67, AC54
- £60: X67, Z67, AA66, AA86, AB65

### Caucasus (rows AA–AF, cols 80–88)

- £45: AD81, AD83, AE80, AF83
- £60: AA86, AB85, AE82, AE84

### River Crossings

- £5: E78
- £30: N39, P41, K64, K66, L69, L71, L75, L77, M74, M76, M78, M80, N69–N79
- £45: K44, N81, O82, AE52
- £60: M34, T23, AB77, AC76, AD71, AG70

? **Verify against physical map:** Caucasus at AA86/AD81–AE84; river routing accuracy; combined terrain hexes (mountain + water).

---

## Custom Tile Codes

✓ Implemented: OE1–OE8, OE12–OE18, OE23–OE44

? **Outstanding — orientations unknown (double-town tiles, commented out):**

| Code | Colour | Qty | Missing |
|------|--------|-----|---------|
| OE9 | green | 3 | edge pair |
| OE10 | green | 3 | edge pair |
| OE11 | green | 3 | edge pair |
| OE20 | brown | 3 | edge pair |
| OE21 | brown | 2 | edge pair |
| OE22 | brown | 6 | edge pair |
| OE19 | ? | ? | tile type (gap between OE18 green and OE20 brown) |

? Do OE9–11 upgrade directly to OE20–22?

---

## Ports and Ferry Routes

| Item | Status |
|------|--------|
| Port city hexes (public light-blue / private red anchor) | ? |
| Ferry route paths (start hex+edge → end hex+edge, distance) | ? |
| North Sea port authority positions (8) | ? |
| Mediterranean port authority positions (8) | ? |
| White Cliffs Ferry token slot near Lille N31 | ? |
| Patronage tiles — fixed city list or game logic only? | ? |

---

## Outstanding Bugs

| Bug | Location | Fix |
|-----|----------|-----|
| Constantinople AA82 no path edges | `map.rb white:` | Add edges, move to `yellow:` |
| London M28 no path edges | `map.rb white:` | Add edges, move to `yellow:` |
| SC zone contains A40 | `game.rb NATIONAL_REGION_HEXES` | Remove A40 |
| RU zone contains E88 | `game.rb NATIONAL_REGION_HEXES` | Remove E88 |

---

## Open Issues Summary

| Priority | Item |
|----------|------|
| **High** | Pre-printed path edges for M28, AA82, N31, I20, O28, X33, U24 |
| **High** | Verify all 19 red hex revenues and edges against physical map |
| **High** | Remove A40/E88 from national zone hex lists |
| **Medium** | Ferry paths and distance numbers (sea zone borders done) |
| **Medium** | Port markers, ferry routes, distances |
| **Medium** | Verify Caucasus terrain; river routing accuracy |
| **Low** | Confirm Venezia V47 town vs city |
| **Low** | OE9–11, OE20–22 edge pairs; OE19 tile type |
| **Low** | Patronage — fixed list or game logic only |
