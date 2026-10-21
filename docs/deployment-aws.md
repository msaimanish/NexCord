# AWS Deployment Notes

This document records the NexCord AWS deployment approach. It intentionally contains no account IDs, private database endpoints, tokens, passwords, or secret values.

## Deployment shape

The AWS deployment uses Docker Compose on an Ubuntu EC2 instance. The Compose file is `docker-compose.aws.yml`; AWS-specific CPU-only Dockerfiles are used for the backend and ML services. The public edge consists of Caddy and Nginx. Application data lives in private Amazon RDS for PostgreSQL with pgvector.

Services in the Compose deployment:

- `caddy` — public ports 80/443, automatic HTTPS, HTTP-to-HTTPS redirection and Basic Authentication.
- `nginx` — routes `/api/` and `/health` to FastAPI, and other paths to the frontend; structured request logs go to stdout.
- `frontend` — Next.js production UI.
- `backend` — FastAPI application and agent orchestration; applies Alembic migrations on startup.
- `mcp-server` — self-hosted MCP service over Streamable HTTP.
- `ml` — ML/computer-vision HTTP service.

RDS is not a Compose service. The application uses a private RDS endpoint supplied via environment configuration.

## Prerequisites

- AWS CLI credentials with permission to manage the relevant resources.
- EC2 instance role for Systems Manager and CloudWatch log delivery.
- The required CloudWatch log groups already created.
- Secrets in AWS Secrets Manager for the database connection and LLM API key.
- An `.env.aws` file on EC2 with `DATABASE_URL`, `GEMINI_API_KEY`, and `NEXCORD_BASIC_AUTH_HASH`. Keep this file root/user restricted and never commit it.
- A DuckDNS subdomain pointing to the EC2 public IP.

## Deploy or update from EC2

Connect from a trusted machine using Session Manager:

```bash
aws ssm start-session --region ap-south-1 --target <EC2_INSTANCE_ID>
```

Then, on the instance:

```bash
cd /home/ssm-user/NexCord
git pull origin main
sudo docker compose --env-file .env.aws -f docker-compose.aws.yml config -q
sudo docker compose --env-file .env.aws -f docker-compose.aws.yml up -d --build
sudo docker compose --env-file .env.aws -f docker-compose.aws.yml ps
```

Do not paste or print `.env.aws`. The Basic Auth hash must be present in that file for Compose to interpolate the Caddy environment variable.

## Domain, HTTPS and authentication

The documented demo hostname is `nexcord-manish.duckdns.org`. Caddy obtains and renews a Let's Encrypt certificate automatically when DNS points to the instance and inbound ports 80/443 are reachable. Caddy's data and configuration directories are persisted in named Docker volumes.

The EC2 host has a systemd timer that runs a DuckDNS update script periodically and after boot, so the free DNS hostname follows the dynamic public IP when it changes. The token is stored in a root-only file under `/etc/duckdns/`; do not copy it into Git.

Caddy applies HTTP Basic Authentication to the whole public hostname. For judging, provide the login details only in the private/appropriate testing instructions field; never put the password or hash in this repository or in the public README. The configured shared login is for a demo only.

## Network and data protection

- Public inbound web traffic is allowed on ports 80 and 443 so Caddy can redirect HTTP and complete certificate validation.
- Do not expose PostgreSQL 5432, FastAPI 8000, MCP 8001 or ML 8100 directly to the public internet.
- RDS should remain non-public and accept traffic only from the app security group.
- Use Session Manager for administration rather than an internet-facing SSH rule.
- Do not publish database dumps, `.env`, `.env.aws`, secrets, AWS account/instance identifiers, private endpoints, or unredacted logs.

## Observability

Application logs are sent to CloudWatch log groups under `/nexcord/prod/`. The groups cover backend, MCP server, ML, frontend and Nginx. Nginx JSON logs contain request path, status, request time and upstream response time. The `NexCord/Production` namespace includes API request latency and HTTP 5xx metrics, along with service error metrics and alarms.

The API-only latency metric was observed with five requests in one minute: average latency 4.4 ms and maximum 5 ms. The HTTP 5xx/error alarms were in `OK` state when checked, with some showing no datapoints and missing data treated as non-breaching; that state is not proof that each alarm's triggering path was exercised.

## Useful operational checks

```bash
# Container status
sudo docker compose --env-file .env.aws -f docker-compose.aws.yml ps

# Recent Caddy logs
sudo docker compose --env-file .env.aws -f docker-compose.aws.yml logs --tail=100 caddy

# Recent backend logs
aws logs tail /nexcord/prod/backend --region ap-south-1 --since 10m

# Public HTTPS check from a trusted client
curl -sS -o /dev/null -w '%{http_code}\n' https://nexcord-manish.duckdns.org/
```

Unauthenticated public requests should receive `401`; authenticated frontend/API requests should return a successful response for valid routes.

## Cost and lifecycle notes

Stopping EC2 stops its compute charges while stopped, but attached EBS storage and other resources may still cost money. RDS instance compute/storage and CloudWatch resources have their own billing behavior; stopping EC2 does not stop RDS billing. RDS stopped-state behavior is temporary. Before retiring the demo, preserve a verified local database backup and demo evidence, then explicitly remove unneeded billable resources.
