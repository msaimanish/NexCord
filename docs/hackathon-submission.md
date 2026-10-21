# NexCord — Devpost Submission Draft

> Review and paste relevant sections into Devpost. Do not submit until the MCP version check and final video checklist are complete.

## Project title

**NexCord: A Human-in-the-Loop Incident Commander for Live Events**

## Primary track

Alexa+ — self-hosted MCP server / project-owned UI demonstration.

## Mini challenge

AWS Builder.

Do not select Open Source mini challenge unless a separate qualifying open-source contribution/project was made during the hackathon submission window. The main NexCord repo plus a license does not by itself satisfy the “additional project or contribution” rule.

## Short tagline

A human-in-the-loop incident commander that turns live-event disruptions into simulated, approval-gated actions and verifies the outcome through MCP tools.

## Project description

Live events rely on rooms, staff, vendors, schedules and equipment being available at the right time. A failed projector, room conflict, unavailable team member or overcrowded room can create cascading operational problems. Responders need more than a chatbot suggestion: they need a plan grounded in operational context, an understanding of its impact, and a controlled way to carry it out.

NexCord is an agentic incident-response system for event operations. It gathers event and resource context, retrieves relevant operational knowledge, proposes candidate plans, simulates their impact, and pauses for explicit human approval. After approval, the backend invokes constrained tools through a self-hosted Model Context Protocol (MCP) server over Streamable HTTP, then verifies the resulting state. Plan, execution and verification history are persisted for inspection.

The demo uses a seeded Robotics Final scenario with a projector failure. NexCord proposes allocating a backup projector, simulates the resource change, waits for operator approval, executes the approved action and checks the resulting assignment.

## Built with

Next.js, React, TypeScript, Python, FastAPI, LangGraph, MCP over Streamable HTTP, PostgreSQL, pgvector, SQLAlchemy, Alembic, PyTorch/Torchvision, OpenCV, Docker Compose, Amazon EC2, Amazon RDS for PostgreSQL, AWS Secrets Manager, AWS Systems Manager Session Manager, Amazon CloudWatch, Caddy and Nginx. Gemini API configuration is used for LLM calls; Amazon Bedrock and S3 were not used.

## What changed during the hackathon

Finalize this from actual commit history and the work completed during the hackathon window. Work delivered during the window included the stateful incident-response and approval workflow, constrained MCP tool execution and verification, Docker Compose deployment, an AWS deployment with private managed PostgreSQL, CloudWatch container log ingestion and latency/error metrics, plus a domain with HTTPS and password protection. Keep only items confirmed in source/history and demo evidence.

## Known limitations

- NexCord is a prototype, not a certified emergency-response or life-safety system.
- The demonstration uses seeded/sample event data, not a live venue.
- The project demonstrates its self-hosted MCP server through its own UI/client; it is not a native Alexa+ device or partner-console integration.
- Amazon Bedrock and S3 are not used.
- Kubernetes/Helm and the additional hardening phase were excluded.
- The shared Basic Authentication login is for a controlled demo and does not provide per-user identity or enterprise role-based authorization.

## Code and live demo

- **Public repository:** https://github.com/msaimanish/NexCord
- **HTTPS demo:** https://nexcord-manish.duckdns.org/
- **Video:** Add public YouTube/Vimeo URL here after upload (must be under 3 minutes, in English).
- **Testing instructions:** Tell judges to open the HTTPS URL and use the username/password provided in this testing-instructions field. Never put the password or its hash in the repository or public README. If the demo needs to be taken offline for cost reasons, ensure the video and repo remain accessible and follow the organizers' latest guidance about live MCP endpoint availability.

## AWS Builder mini-challenge response

NexCord uses AWS as a documented deployment and observability layer. EC2 runs the containerized application stack; Amazon RDS for PostgreSQL stores operational data privately; AWS Secrets Manager stores the database and LLM credentials; Systems Manager Session Manager provides administrative access without an internet-facing SSH rule; and CloudWatch receives container logs from the backend, MCP server, ML service, frontend and Nginx. JSON Nginx logs feed metric filters for API request latency and HTTP 5xx conditions, while CloudWatch alarms monitor service errors and latency. The deployment was tested end to end. Amazon Bedrock and S3 were intentionally not used.

## Product feedback — draft

Edit based on the tool versions and issues actually experienced.

### MCP Python SDK / self-hosted Streamable HTTP

- **Used for:** Exposing event-operations tools to the agent through a self-hosted MCP server.
- **Worked well:** A common tool interface helped keep agent orchestration separate from execution and verification operations.
- **Needs work:** The required protocol-version support should be clearly surfaced in startup diagnostics and in the test tooling. Documentation should make it easy to exercise `initialize`, `tools/list` and a safe `tools/call` against Streamable HTTP.
- **Onboarding:** A self-hosted server and project-owned client/UI were practical for demonstrating the workflow without partner-only Alexa+ tools.
- **Build again?:** Yes, for an interoperable tool interface, after verifying compatibility with the required protocol revision.

### Alexa+ track / developer experience

- **Used for:** Targeting the track through a self-hosted MCP server, demonstrated through NexCord's own frontend/client.
- **Worked well:** The track's self-hosted MCP path made it possible to build and demonstrate an agentic tool integration without dedicated Amazon hardware.
- **Needs work:** Make partner-only tool/simulator access boundaries and the expected testing path clearer to hackathon participants.
- **Onboarding:** The practical path was implementing the open MCP surface and demonstrating it through a project-owned UI.
- **Build again?:** Yes for the MCP interoperability model; native Alexa+ integration would require access to the partner tooling.

### AWS EC2

- **Used for:** Hosting the Docker Compose services.
- **Worked well:** A single VM made it feasible to operate and debug the multi-container demo with a straightforward deployment model.
- **Needs work:** Disk consumption from ML dependencies and the difference between instance-role and developer credentials were friction points. Billing visibility and a lower-cost stop/cleanup guide are useful.
- **Onboarding:** Getting the app reachable required security-group changes, SSM access, and an instance role for operational access and logs.
- **Build again?:** Yes for demos and small deployments, with resource sizing and cost controls planned from the beginning.

### Amazon RDS for PostgreSQL

- **Used for:** Managed, private PostgreSQL/pgvector storage for incidents, resources, plans and execution history.
- **Worked well:** Private network placement and app-security-group-only access provided a clear database boundary.
- **Needs work:** Version/extension compatibility and backup/restore verification should be highlighted when migrating from a local database.
- **Onboarding:** Subnet groups, security groups, credentials, backups and private connectivity required careful setup.
- **Build again?:** Yes when managed persistence is valuable enough to justify the ongoing cost.

### AWS Systems Manager Session Manager

- **Used for:** Remote administrative access without exposing SSH publicly.
- **Worked well:** It allowed EC2 access using the instance role and avoided maintaining an SSH key/inbound port.
- **Needs work:** Guidance should emphasize that an EC2 instance role is not the same as the developer's IAM identity; the instance role appropriately could not modify security groups.
- **Onboarding:** Instance profile/role configuration and ensuring the Session Manager plugin was installed were required steps.
- **Build again?:** Yes for controlled administration of cloud instances.

### Amazon CloudWatch

- **Used for:** Container log collection, structured Nginx latency/HTTP status metrics and alarms.
- **Worked well:** Centralized logs and metric filters let the team verify API traffic and measure request time without running another observability stack.
- **Needs work:** After updating a metric filter, the operator needed fresh log events to produce a datapoint; the console should make that requirement more visible.
- **Onboarding:** Log group retention, instance IAM permissions, awslogs configuration and filter syntax had to align.
- **Build again?:** Yes for small deployments and debugging when metric semantics and retention costs are made explicit.

### AWS Secrets Manager

- **Used for:** Storing the database credentials and LLM API key separately from source code.
- **Worked well:** Secrets could be retrieved by the instance role without committing them to Git.
- **Needs work:** The extra retrieval/configuration step should be included in a concise deployment guide, with strict prevention of accidental secret output.
- **Onboarding:** Permissions and safe population of an ignored environment file were the main steps.
- **Build again?:** Yes, especially for cloud deployments where credentials should not be bundled with the repository.

### Caddy / DuckDNS

- **Used for:** Free subdomain, automatic HTTPS certificate issuance/renewal, HTTP redirect and password protection.
- **Worked well:** HTTPS could be enabled with a minimal reverse-proxy configuration and the certificate was issued successfully.
- **Needs work:** Dynamic EC2 public IPs mean a DNS updater is needed after stop/start, and ports 80/443 must be open for certificate validation and browser access.
- **Onboarding:** DNS, security-group permissions, certificate validation and secret-safe Basic Auth configuration were the main steps.
- **Build again?:** Yes for low-cost demonstrations, but the shared Basic Auth approach should be replaced by a more complete identity solution for production.

## Final blocker before submitting

Verify the MCP server supports/negotiates MCP protocol version **2025-11-25 or later** over Streamable HTTP and capture evidence of `initialize`, `tools/list` and at least one appropriate `tools/call`. Do not claim Alexa+ native integration. The current project demonstrates the self-hosted MCP approach through its own UI/client.
