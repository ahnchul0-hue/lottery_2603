# Deferred Items - Phase 04

## Pre-existing Issues (Out of Scope)

1. **test_balance_strategy.py imports non-existent BalanceStrategy**
   - File: `backend/tests/test_balance_strategy.py`
   - Issue: Imports `app.strategies.balance.BalanceStrategy` which doesn't exist yet
   - Impact: `pytest -x` fails on collection before reaching actual tests
   - Resolution: Will be resolved when BalanceStrategy is implemented (likely 04-02 or 04-03)
   - Discovered during: Plan 04-01 execution
