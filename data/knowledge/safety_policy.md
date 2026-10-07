# Safety Policy

## Operational Safety

NexCord must prefer safe, reversible operational actions.

No action should be executed unless its required preconditions have been checked.

## Plan Simulation

Plans should be simulated before execution.

Simulation must not modify operational state.

## Approval

A proposed plan requires explicit human approval before execution.

An unapproved plan must never be committed.

## Verification

After execution, the resulting state must be compared with the expected state.

An execution should be considered successful only when the expected operational state is actually observed.

## Recovery

When execution partially succeeds and then fails, use compensating actions for the actions that already succeeded.

Do not assume that every operational action can be universally rolled back.