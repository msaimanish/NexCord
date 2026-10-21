# NexCord — Hackathon Friction Log Draft

These entries are based on issues encountered while building/deploying NexCord. Review each entry for accuracy and adjust wording to match the exact steps you personally performed before submitting it to Devpost.

## 1. CPU-only ML image build pulled larger CUDA dependencies

- **Task:** Build the ML/backend images for a CPU-only EC2 deployment.
- **Steps:** Built the AWS Docker images with the general dependency sync configuration, then inspected the installed PyTorch build and Docker disk usage.
- **Expected:** CPU-only configuration would result in compact CPU images.
- **Actual:** The dependency install pulled CUDA-related packages despite intending a CPU-only build, consuming most of the host disk.
- **Severity:** High — build/disk pressure threatened to block deployment.
- **Workaround:** Used AWS-specific Dockerfiles with an explicit PyTorch CPU package index/source, rebuilt, and cleaned unused Docker images.
- **Actionable suggestion:** Clarify in package/tool docs which environment variables do and do not influence dependency resolvers, and document the supported CPU-only install mechanism in a minimal reproducible example.

## 2. Broad Git ignore rule omitted backend model source files

- **Task:** Deploy the FastAPI backend from a clean Git clone.
- **Steps:** Pulled the repository on EC2 and started the service.
- **Expected:** Required SQLAlchemy model modules would be present in the clone.
- **Actual:** A broad `models/` ignore pattern had prevented nested backend model files from being tracked, resulting in `ModuleNotFoundError: No module named 'backend.models'`.
- **Severity:** High — the deployed backend could not start correctly.
- **Workaround:** Anchored the ignore rule to the repository-root `/models/` path, explicitly tracked the required backend model modules, committed the correction, and pulled it onto EC2.
- **Actionable suggestion:** Provide a CI/release check that detects required imports whose source files are ignored or absent from the tracked repository before building deployment images.

## 3. CloudWatch metric filter needed post-change log events

- **Task:** Create an API-only latency metric from structured Nginx logs.
- **Steps:** Created a JSON metric filter, narrowed it to `/api/*`, generated API requests, and queried CloudWatch metric statistics.
- **Expected:** A metric query immediately after changing the filter would make it obvious whether the new filter matched.
- **Actual:** An early query returned an older datapoint from before the filter update; fresh requests were needed to validate the updated filter.
- **Severity:** Medium — validation was delayed, but application functionality was not blocked.
- **Workaround:** Generated five new API requests, confirmed their JSON access log entries, and verified a fresh metric datapoint: average latency 4.4 ms, maximum 5 ms, sample count 5.
- **Actionable suggestion:** Improve the console/tooling to distinguish post-filter-change datapoints and make initial filter-match validation easier to discover.

## 4. EC2 application role lacked permissions to change security groups

- **Task:** Open inbound ports 80 and 443 for HTTPS certificate issuance and browser access.
- **Steps:** Attempted `ec2:AuthorizeSecurityGroupIngress` from the EC2 Systems Manager session.
- **Expected:** The AWS CLI command would add the web rules.
- **Actual:** AWS returned `UnauthorizedOperation` because the instance role intentionally lacked security-group modification permissions.
- **Severity:** Medium — required network setup was blocked from the instance.
- **Workaround:** Exited the SSM session and ran the rule update from the developer laptop's IAM identity, which had the required permission.
- **Actionable suggestion:** Make the distinction between instance-role permissions and administrator/deployer credentials more prominent in EC2 + SSM deployment guidance, with a secure recommended workflow for modifying network policy outside the instance.
