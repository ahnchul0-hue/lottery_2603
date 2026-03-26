---
phase: 02-time-decay-engine
verified: 2026-03-26T14:45:00Z
status: passed
score: 6/6 must-haves verified
re_verification: false
documentation_note:
  - issue: "REQUIREMENTS.md DECAY-02 still says 'halflife default 50' but user decision D-02 changed it to 30"
    recommendation: "Update REQUIREMENTS.md DECAY-02 description to say halflife=30 to match CONTEXT.md, ROADMAP.md, and implementation"
    severity: info
    blocking: false
---

# Phase 2: Time Decay Engine Verification Report

**Phase Goal:** A reusable time-decay weighting module that assigns exponentially decaying weights to historical draws
**Verified:** 2026-03-26T14:45:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Given a list of draws, the newest draw receives weight 1.0 and older draws receive progressively lower weights | VERIFIED | `decay_engine.py:36` formula `0.5 ** ((n - 1 - i) / self.halflife)` where i=n-1 yields 1.0; test `test_newest_draw_highest_weight` passes: weights[-1]==1.0, weights[0]<1.0 |
| 2 | A draw exactly halflife positions before the newest draw receives weight 0.5 | VERIFIED | Test `test_halflife_gives_half_weight` passes: weights[-31]==approx(0.5), weights[-61]==approx(0.25) for halflife=30 |
| 3 | Weight values follow the formula 0.5^(draws_since / halflife) exactly | VERIFIED | `decay_engine.py:36` implements `0.5 ** ((n - 1 - i) / self.halflife)` which is equivalent; pure Python exponentiation, no numpy |
| 4 | compute_weighted_frequencies returns a dict covering all 45 numbers (1-45) with float values | VERIFIED | `decay_engine.py:54` initializes `{n: 0.0 for n in range(1, 46)}`; test `test_weighted_frequencies_all_numbers` passes: keys=={1..45}, all float, all >=0 |
| 5 | The halflife defaults to 30 and can be changed via constructor parameter without modifying core logic | VERIFIED | `decay_engine.py:17` reads `settings.DECAY_HALFLIFE` when no arg; `config.py:9` sets `DECAY_HALFLIFE: int = 30`; test `test_default_halflife_from_config` passes; test `test_custom_halflife` passes with halflife=10 vs halflife=50 |
| 6 | DECAY_HALFLIFE is defined in config.py Settings class with default value 30 | VERIFIED | `config.py:9` contains `DECAY_HALFLIFE: int = 30` |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `backend/app/services/decay_engine.py` | DecayEngine class with compute_weights and compute_weighted_frequencies methods | VERIFIED | 60 lines (min 25), exports DecayEngine class, both methods present, pure Python math |
| `backend/app/config.py` | Settings class with DECAY_HALFLIFE field | VERIFIED | Contains `DECAY_HALFLIFE: int = 30` on line 9 |
| `backend/tests/test_decay_engine.py` | 8 test cases covering decay curve, frequencies, config, and integration | VERIFIED | 125 lines (min 80), exactly 8 `def test_` functions, all 8 pass |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `decay_engine.py` | `schemas/lottery.py` | `from app.schemas.lottery import LotteryDraw` | WIRED | Line 2, type annotation on compute_weights and compute_weighted_frequencies |
| `test_decay_engine.py` | `services/decay_engine.py` | `from app.services.decay_engine import DecayEngine` | WIRED | Line 5, used in all 8 test functions |
| `config.py` | `services/decay_engine.py` | `DECAY_HALFLIFE = 30` read via `settings.DECAY_HALFLIFE` | WIRED | config.py:9 defines it, decay_engine.py:17 reads it in constructor |

### Data-Flow Trace (Level 4)

Not applicable -- DecayEngine is a computational module (not a UI component rendering dynamic data). Its data flow is verified through unit tests and the integration test with real DataLoader data.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 8 decay engine tests pass | `uv run pytest tests/test_decay_engine.py -v` | 8 passed in 0.01s | PASS |
| Full backend suite passes without regression | `uv run pytest -x -q` | 24 passed in 0.04s | PASS |
| No numpy/pandas imports in decay_engine.py | grep for numpy/pandas imports | No matches found | PASS |
| Formula uses pure Python exponentiation | grep for `0.5 **` | Found on line 36 | PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| DECAY-01 | 02-01-PLAN | Apply exponential decay weights (recent = high, old = low) | SATISFIED | Formula `0.5^(draws_since/halflife)` implemented; newest=1.0, monotonically decreasing; 3 tests verify curve shape |
| DECAY-02 | 02-01-PLAN | Halflife parameter defaults to 30, adjustable at code level | SATISFIED | `config.py` DECAY_HALFLIFE=30; constructor accepts override; `test_default_halflife_from_config` and `test_custom_halflife` both pass. Note: REQUIREMENTS.md text says "50" but user decision D-02 changed to 30; ROADMAP.md Success Criteria confirms 30. |

**Orphaned Requirements:** None. All requirement IDs mapped to Phase 2 in the traceability table (DECAY-01, DECAY-02) are accounted for in the plan's `requirements` field.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `decay_engine.py` | 32 | `return []` | Info | Empty-draws guard clause, correct behavior, not a stub |

No TODO, FIXME, HACK, PLACEHOLDER, or stub patterns found in any of the three artifacts.

### Human Verification Required

None required. All phase deliverables are backend computational code with comprehensive test coverage. No visual, UX, or real-time behaviors to verify.

### Documentation Note

REQUIREMENTS.md line 21 states: `**DECAY-02**: 감쇠 파라미터(halflife)는 기본값 50으로 설정되며 코드 레벨에서 조정 가능하다`

The implementation uses halflife=30, which matches:
- User decision D-02 in CONTEXT.md (halflife=30, aggressive)
- ROADMAP.md Success Criteria #2 ("defaults to 30")
- DISCUSSION-LOG.md (user selected 30 over 50 and 100)

The RESEARCH.md (line 316-318) recommended updating REQUIREMENTS.md to reflect halflife=30 as part of this phase, but this was not done. This is a documentation inconsistency only -- the implementation correctly follows the user's decision. Recommend updating REQUIREMENTS.md DECAY-02 to say "기본값 30" in a future cleanup.

### Gaps Summary

No gaps found. All 6 must-have truths verified. All 3 artifacts pass all 4 verification levels (exists, substantive, wired, behavioral). All key links confirmed. Both requirements satisfied. All 8 tests pass. Full backend suite of 24 tests passes with zero regressions.

---

_Verified: 2026-03-26T14:45:00Z_
_Verifier: Claude (gsd-verifier)_
