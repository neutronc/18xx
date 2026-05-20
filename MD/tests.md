# 1862 Golden Spike — Pending Browser Tests

Tests that require manual browser verification. Check this list at the start of each session.
Mark tests `[x]` when passed. Add new tests here whenever a fix needs browser confirmation.

---

## Pending

### T-001 — Home token placed at corp's first OR turn (not OR start)
- **Bug fixed:** BUG-001 (revised)
- **Setup:** Float any Group 1 corp (NYH, NYC, or CP)
- **Test:** Start the first OR. Confirm the home token appears when that corp's turn begins (not before). Confirm the corp can immediately lay track after the token appears.
- **Also check:** Two corps sharing a hex (NYC + NYH on F28) — each token appears on its own turn, both end up in the correct city slot.

### T-002 — TOR tile-lay available to any director; SR on owner's turn
- **Rule:** TOR tile-lay fires (a) on TOR owner's SR turn, (b) at any point during TOR owner's corp OR turn, (c) at the start of any corp's OR turn before they act (any director can trigger it)
- **Setup:** Player wins TOR in auction. Advance to SR1 and then OR1.
- **Test A (SR):** On TOR owner's SR turn, confirm the Toronto tile-lay button appears.
- **Test B (OR as director):** When TOR owner's corp operates, confirm button appears at any point in their turn.
- **Test C (OR as non-director):** When a different corp operates, confirm the Toronto tile-lay button appears at the start of that corp's turn before they act; confirm placement closes TOR and logs the action.
- **Known gap:** Bold log and "private was used" notification to owner not yet implemented (needs frontend work).

### T-003 — Route revenue display matches submit total
- **Bug fixed:** BUG-008
- **Setup:** CPR runs a 3-train Sacramento → Salt Lake City → Omaha (first time through SLC).
- **Test:** Revenue shown on the map route display must match the amount shown on the dividend submit button. Both should reflect the SLC bonus ($30 or $15 while SOC open) and the CPR Omaha activation bonus.

### T-004 — Token costs follow $40 / $80 / $120 progression
- **Bug fixed:** BUG-009
- **Setup:** Any 4-token corp (NYH, NYC, CP) with treasury cash.
- **Test:** Second token costs $40, third token costs $80, fourth token costs $120. For 3-token corps (CPR, UP, ATS, SP): second $40, third $80.

### T-005 — Corporation receives full par × 10 on float
- **Bug fixed:** BUG-010
- **Setup:** Par a corp and sell shares until it floats (60%).
- **Test:** On float, corp treasury shows `par_price × 10` (e.g. par at $92 → $920). No money should drip in as subsequent IPO shares are sold.

### T-006 — Sacramento hex shows $20 revenue on both city slots
- **Bug fixed:** BUG-007
- **Setup:** Start any game with CPR or WP in Group 3 (or inspect the map before they float).
- **Test:** Hex G3 (Sacramento) preprinted yellow tile shows $20 on both city circles.

---

## Passed

- [x] 2026-05-16 **T-002 (partial)** — TOR button appears when owner operates as director (BUG-006). Full re-test needed for SR and or_between_turns cases after when: update.

---

## Conventions

- One entry per fix that needs visual confirmation.
- Test description must include setup state, action, and expected outcome.
- When a test passes, move it to **Passed** with date: `[x] YYYY-MM-DD`.
- If a test fails after a "pass", reopen with a new T-NNN entry linking back.
