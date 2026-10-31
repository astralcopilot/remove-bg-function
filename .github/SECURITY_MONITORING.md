# Dependency security monitoring

> **Inventory limitation:** This repository has no committed `bun.lock`. The
> workflow generates a fresh temporary resolution of the `package.json` ranges
> with `bun install --lockfile-only --ignore-scripts`. This is not a scan of
> deployed artifacts or a reproducible installed dependency set; do not commit
> the generated lockfile.

The security workflow audits that resolved Bun dependency inventory daily at
08:23 UTC, on relevant pull requests, and on manual dispatch. It does not install
or execute application packages.

## Rollout and ownership

- Merge this workflow to the repository's **default branch** to activate its
  schedule and Dependabot. Until then, only PR validation runs.
- The initial rollout is **advisory-only**: existing findings do not block PRs.
  A green job means scanning completed, not zero vulnerabilities. Scanner/network
  errors, malformed reports and skipped Python packages fail the job.
- Scheduled/default-branch manual runs create or refresh one GitHub backlog issue.
  Subscribe to that issue and enable Actions failure notifications. Assign a human
  security owner to triage it. PRs have a read-only token and never write issues.
- Full JSON and logs are kept as a workflow artifact for 14 days. The summary and
  issue show the first 50 matches, prioritized by severity; Python is **unrated**,
  not low priority. Counts are package/advisory matches, not unique CVEs.
- Dependabot proposes weekly Bun and Actions updates with three open PRs
  per ecosystem. Nothing here enables auto-merge. GitHub dependency graph,
  Dependabot alerts and security updates must also be enabled in repository
  Settings → Security; a config file does not enable those settings.
- Upgrade production-reachable packages first. Validate affected code paths,
  lesson access/generation and mobile compatibility before deploying fixes.

## Coverage boundaries

This is dependency monitoring, not a SIEM, exploit test or deployed-asset scan.
It includes dev/build dependencies and does not prove production reachability.
No student data, application secrets or runtime logs are read by this workflow.

Node/Bun executable CVEs, managed Vercel/Trigger runtime patch versions, OS/native
libraries in deployed containers, CocoaPods/Gradle and already-installed mobile
binaries need separate inventory and scanning. Do not infer deployed versions
from `engines.node` or a local executable. Capture deployed image digests and
runtime patch versions before adding image/runtime gates. Rebuilding or
redeploying is required to apply fixes to already-running workers and binaries.

## Local verification

Run `python .github/scripts/security_report.test.py`. Run
`bun install --lockfile-only --ignore-scripts` before `bun audit --json` to
collect the fresh range-resolution advisories. Do not commit the generated
lockfile. Exit 1 means findings only when the JSON validates; it can also
accompany a failed scanner. The report validator checks both.
