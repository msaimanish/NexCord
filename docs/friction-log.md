# NexCord — Development Friction Log

## 1. Building CPU-only PyTorch containers

**Severity:** High

**Task attempted:** Build the ML and backend Docker images for the AWS deployment using CPU-only PyTorch.

**Steps:** Initially built the AWS images using the existing dependency configuration and attempted to avoid CUDA dependencies through environment configuration.

**Expected result:** Compact images containing CPU-only PyTorch, suitable for an EC2 instance without a GPU.

**Actual result:** The build downloaded large CUDA-related dependencies and filled the EC2 root disk to approximately 97% capacity.

**Workaround:** Added an explicit PyTorch CPU package index to the AWS-specific Dockerfiles, rebuilt the images, verified that CUDA was unavailable in the CPU build, and removed unused Docker artifacts.

**Actionable suggestion:** Document the recommended CPU-only PyTorch installation and package-index configuration in the container deployment guides. A pre-build image-size or disk-space check would also help developers avoid exhausting instance storage.

## 2. Python model modules missing from the AWS deployment

**Severity:** High

**Task attempted:** Start the deployed backend after pulling the latest application code.

**Steps:** Pulled the repository and started the Docker Compose services.

**Expected result:** The backend would import its SQLAlchemy models and start normally.

**Actual result:** The backend reported `ModuleNotFoundError` for `backend.models`. A broad `.gitignore` pattern had caused required source files under model directories to be ignored.

**Workaround:** Narrowed the ignore rule to the intended root-level directory, explicitly tracked the required model modules, pushed the fix, and pulled it on EC2.

**Actionable suggestion:** Use root-anchored ignore patterns when ignoring directories with common names, and add a repository check that verifies required Python source files are tracked before deploying.

## 3. Docker Compose couldn't find AWS environment variables

**Severity:** Medium

**Task attempted:** Rebuild only the frontend on EC2.

**Steps:** Invoked Docker Compose with the AWS Compose file but without explicitly loading the deployment environment file.

**Expected result:** The frontend would rebuild without requiring unrelated application configuration to be entered manually.

**Actual result:** Compose failed during interpolation because `DATABASE_URL` and `GEMINI_API_KEY` were not available to it.

**Workaround:** Used the existing private `.env.aws` file with the `--env-file` option and avoided printing any secret values.

**Actionable suggestion:** Put the required Compose invocation in the deployment documentation and make it clear which environment file is required for AWS commands.

## 4. Docker socket permissions inside Systems Manager

**Severity:** Medium

**Task attempted:** Rebuild and restart a container through an SSM Session Manager shell.

**Steps:** Ran Docker Compose as the default SSM user.

**Expected result:** The command would access the Docker daemon and rebuild the frontend.

**Actual result:** The shell reported permission denied on `/var/run/docker.sock`. Switching to a root shell also changed the meaning of `~`, causing an incorrect project path.

**Workaround:** Used `sudo docker compose` and explicit paths under `/home/ssm-user/NexCord`.

**Actionable suggestion:** Document the required permissions and supported Docker command pattern for SSM sessions, and prefer absolute paths in privilege-escalated deployment commands.

## 5. Updating an AWS security group from the EC2 role

**Severity:** Medium

**Task attempted:** Allow public web traffic on ports 80 and 443 so Caddy could obtain a certificate and serve HTTPS.

**Steps:** Tried to modify the application security group using AWS CLI from the EC2 SSM session.

**Expected result:** The security group would be updated by the command.

**Actual result:** AWS denied `ec2:AuthorizeSecurityGroupIngress` because the instance role did not have that permission.

**Workaround:** Ran the security-group change from the local terminal using the configured IAM user, keeping the EC2 application role limited.

**Actionable suggestion:** Clearly distinguish instance-role permissions from operator permissions in AWS CLI guidance and provide a least-privilege deployment checklist for security-group changes.

## 6. Caddy validation through Docker Compose

**Severity:** Low

**Task attempted:** Validate the Caddyfile before exposing the HTTPS service.

**Steps:** Ran the Compose `run` command with `validate` as the command argument.

**Expected result:** Caddy would validate the configuration.

**Actual result:** Docker tried to execute `validate` as the container's executable and returned `exec: "validate": executable file not found in $PATH`.

**Workaround:** Used `--entrypoint caddy` to invoke the Caddy executable explicitly, after which the configuration validated successfully.

**Actionable suggestion:** Include tested Docker Compose examples for running one-off Caddy validation and formatting commands.

## 7. DuckDNS initially pointed at the wrong IP

**Severity:** Medium

**Task attempted:** Make NexCord reachable through a free DuckDNS subdomain.

**Steps:** Created `nexcord-manish.duckdns.org` and checked its DNS resolution.

**Expected result:** The hostname would resolve to the EC2 public IP.

**Actual result:** DNS initially resolved to the laptop's public IP instead of EC2.

**Workaround:** Updated the DNS record to the current EC2 address and installed a root-protected DuckDNS updater script with a systemd timer that refreshes the record periodically.

**Actionable suggestion:** Add a deployment checklist that compares the hostname's resolved address with the current EC2 address before configuring TLS.

## 8. Shell differences in password setup

**Severity:** Low

**Task attempted:** Prompt for a password without displaying the characters and store only its hash in the private environment file.

**Steps:** Used Bash's `read -s` command inside the default SSM shell.

**Expected result:** The shell would hide typed password input.

**Actual result:** The session used `sh`, which rejected the `-s` option.

**Workaround:** Started a Bash shell, then reran the command successfully without exposing the password.

**Actionable suggestion:** Identify the shell expected by scripts that use Bash-specific features and use an explicit Bash shebang where appropriate.

## 9. Verifying CloudWatch latency metrics

**Severity:** Medium

**Task attempted:** Turn structured Nginx request logs into an API latency metric and confirm the metric was receiving data.

**Steps:** Created a metric filter, generated API requests, and queried CloudWatch metric statistics.

**Expected result:** Recent `/api/` request latency would appear in the metric.

**Actual result:** The initial filter was too broad, and the first query after narrowing it showed no new datapoint. CloudWatch metric filters apply to incoming log events, so requests and query time windows had to be aligned.

**Workaround:** Restricted the filter to API URIs, generated five fresh API requests, and verified a datapoint with a 4.4 ms average and 5 ms maximum request time.

**Actionable suggestion:** Document the relationship between metric-filter creation time, incoming log events, time-window selection, and alarm evaluation. Provide a smoke-test query for each custom metric.
