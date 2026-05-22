# 1862 Golden Spike — Pending Browser Tests

Tests that require manual browser verification. Check this list at the start of each session.
Mark tests `[x]` when passed. Add new tests here whenever a fix needs browser confirmation.

---

## Pending

---

## Passed

- [x] 2026-05-22 **T-001** — Home token placed at corp's first OR turn (not OR start); two corps sharing F28 each token on own turn, correct city slot (BUG-001)
- [x] 2026-05-22 **T-002** — TOR tile-lay: SR turn button ✓, OR as director ✓, OR as non-director (before they act) ✓ (BUG-006; full re-test)
- [x] 2026-05-22 **T-003** — Route revenue display matches submit total including SLC bonus and CPR Omaha activation bonus (BUG-008)
- [x] 2026-05-22 **T-004** — Token costs $40/$80/$120 for 4-token corps; $40/$80 for 3-token corps (BUG-009)
- [x] 2026-05-22 **T-005** — Corporation receives par × 10 on float; no drip from subsequent IPO sales (BUG-010)
- [x] 2026-05-22 **T-006** — Sacramento hex G3 shows $20 on both city slots (BUG-007)
- [x] 2026-05-16 **T-002 (partial)** — TOR button appears when owner operates as director (BUG-006). Superseded by full T-002 pass above.

---

## Conventions

- One entry per fix that needs visual confirmation.
- Test description must include setup state, action, and expected outcome.
- When a test passes, move it to **Passed** with date: `[x] YYYY-MM-DD`.
- If a test fails after a "pass", reopen with a new T-NNN entry linking back.
