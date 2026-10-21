# NexCord Demo Runbook

Target video length: **2:45–2:55**, public YouTube or Vimeo, English narration, and under three minutes. Show the actual functioning application. Do not use unlicensed music or footage.

## Demo goal

Show that NexCord responds to an operational incident with a simulated plan and requires human approval before performing a constrained action, then verifies the resulting state change.

## Before recording

- Open the deployed HTTPS URL or the local app that you have tested. The current public demo URL is `https://nexcord-manish.duckdns.org/`.
- Use the demo login; do not show or speak the password in the recording.
- Ensure a seeded Robotics Final event and projector-failure incident are available. Reuse the existing incident state or reset/reseed it through your normal development workflow so the demo starts in a known state.
- Confirm the app is not showing stale narration such as “No action has been taken yet” after a completed execution. If that text appears, do not hide it; either fix it or avoid claiming the UI state is consistent.
- Hide browser password managers, secret values, database endpoints, AWS account IDs, IAM identifiers and unrelated terminal output.
- Prepare the window/browser zoom so incident, candidate plan, simulation, approval and verification are readable.
- Do not use a real operational environment; present the seeded data as demo data.

## Timed shot list and narration

| Time | What to show | Suggested narration |
|---|---|---|
| 0:00–0:12 | NexCord dashboard and event | “Live events depend on rooms, people, vendors and equipment. One failure can cascade. NexCord helps an operator respond with context while keeping the human in control.” |
| 0:12–0:35 | Robotics Final and projector incident | “Here, a projector has failed. NexCord gathers the event and resource state before proposing a response.” |
| 0:35–1:00 | Generate and display backup-projector plan | “The agent proposes a concrete action and simulates the resource change before it touches operational state.” |
| 1:00–1:20 | Show simulation result and selected candidate | “The plan is evaluated against available resources and constraints. Generating a plan is not authorization to execute it.” |
| 1:20–1:35 | Explicit approval action | “A human approves the plan. That approval gate is central to NexCord.” |
| 1:35–2:05 | Execution status / MCP-backed action | “The approved action is dispatched through NexCord’s self-hosted MCP server.” |
| 2:05–2:25 | Verification and resulting resource assignment/history | “NexCord checks the resulting state instead of assuming a successful tool call means the operation succeeded.” |
| 2:25–2:42 | Brief architecture/CloudWatch evidence | “The stack combines a web frontend, stateful agent, FastAPI backend, MCP server, PostgreSQL and an ML service. The cloud deployment also used managed PostgreSQL and CloudWatch observability.” |
| 2:42–2:52 | Return to project title | “NexCord: propose, simulate, approve, execute, verify.” |

## After recording

- Watch the full video while signed out and confirm it is publicly accessible.
- Confirm duration is under 3:00 and narration is in English.
- Make sure the approval control and final verification result are clearly visible.
- Ensure the video contains no credentials, tokens, unlicensed soundtrack, third-party footage, or confidential event data.
- Add the public video URL to Devpost.
- Include test access credentials only in the appropriate testing-instructions field; do not put them in the repository or public project description.
