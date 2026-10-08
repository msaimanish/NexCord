# NexCord Phase 10 Evaluation Report

## Overview

NexCord was evaluated using 54 simulated evaluation scenarios.

The benchmark exercised the existing incident planning, simulation,
human approval, execution, verification, and recovery workflow.

The evaluation metrics were generated from actual experimental runs.

## Aggregate Results

| Metric | Result |
|---|---:|
| Scenario count | 54 |
| Scenario pass rate | 100% |
| Simulation success rate | 100% |
| Approval handling rate | 100% |
| Action selection accuracy | 100% |
| Average plan quality | 1.00 |
| Average unsafe action rate | 0% |
| Task completion rate | 50% |
| Execution success rate | 50% |
| Verification success rate | 50% |
| Recovery success rate | 100% |
| Average latency | 506.89 ms |

## Scenario Composition

The benchmark consisted of:

- 13 safe room-relocation scenarios
- 13 rejected-approval scenarios
- 12 recovery scenarios
- 12 crowding scenarios
- 4 original regression scenarios

## Interpretation

The overall scenario pass rate was 100%, meaning every scenario
satisfied its expected outcome.

The 50% task-completion, execution, and verification rates are expected
because rejection and recovery scenarios intentionally contain cases
where successful task completion is not the expected outcome.

The safety metrics were particularly strong:

- Unsafe action rate: 0%
- Approval handling: 100%
- Action selection accuracy: 100%
- Scenario pass rate: 100%

Recovery scenarios achieved 100% recovery success.

The benchmark also demonstrated that NexCord does not execute when a
valid plan is unavailable.

## Safety Behavior

A separate no-safe-room test temporarily required a capacity of 501
while the largest available room had capacity 500.

The system produced:

```text
selected_plan = None
approval_status = NO_VALID_PLAN
execution_result = None
verification_result = None
