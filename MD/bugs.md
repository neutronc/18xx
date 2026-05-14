# 1862 Golden Spike — Bug Log

Curated list of known defects and their fixes. Entries are immutable IDs (`BUG-NNN`);
status changes over time but the ID and original description do not.

**Status values:** `OPEN` (unfixed), `FIXED` (with commit hash + date), `WONTFIX` (with reason), `INVESTIGATING` (under triage).
**Severity:** HIGH (blocks correct gameplay), MEDIUM (rule violation in edge case), LOW (cosmetic or low-impact).

When you fix a bug, change `Status:` to `FIXED <date> <commit>` and move the entry to the **Resolved** section.
Do not delete entries — the history is the value.

---

## Summary

```
Open: 0   Fixed: 0   Won't fix: 0   Total: 0
```

---

## Open

*(none yet)*

---

## Resolved

*(none yet)*

---

## Conventions

- **One ID per defect, ever.** If a bug recurs after being fixed, open a new entry linking back: `Status: REOPENED — superseded by BUG-NNN`.
- **Rule citations are mandatory** for HIGH/MEDIUM bugs.
- **Fix sections must include the diff direction**, not just the new code.
