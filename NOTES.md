# Notes

## Approach
Business rules live in `Group` (no printing or input), the CLI is a thin layer on top.
This keeps the rules easy to test and the CLI easy to swap for an API.

## Money
All amounts are `decimal.Decimal` with exactly 2 decimal places. Floats are rejected
on purpose. Inputs with more than 2 decimal places (e.g. `1.234`) are rejected rather
than silently rounded, so no money is ever created or lost.

## Assumptions and decisions
1. **Adding members:** only allowed before the first contribution is recorded (week 1
   not yet started). Adding later would change the pot size and payout order mid-cycle
   and make earlier weeks unfair.
2. **Names:** trimmed and compared case-insensitively ("Ama" and " ama " are duplicates).
   The name as first entered is kept for display.
3. **Contributions only for the current week.** Past weeks are closed; future weeks
   cannot be pre-paid. The optional `week` argument is validated against this.
4. **Overpayment** is rejected (as required), so there are no credits to carry forward.
5. **Payout order** = join order. Week N pays member N.
6. **End of cycle:** once every member has received the pot once, the group is
   complete. Further payments and closes are rejected with a clear message.
7. **Closing an empty group** is rejected (nobody to pay).
8. **Failed close** changes no state: nothing is paid, the week does not advance,
   and the payments already made stay recorded.
9. Pot = weekly amount x number of members. Because every member must be paid in
   full to close, the pot always equals the money collected that week.

## Known limitations / with more time
- State is in memory only; add JSON/SQLite persistence.
- Support multiple groups and an HTTP API (FastAPI) on top of `Group`.
- Allow a documented late-join policy (e.g. join at end of queue between cycles).
- Payment timestamps and a full audit log of contributions.
- Start a new cycle after completion.
- More tests for the CLI layer.
