"""Validate scanner output and publish an advisory-only dependency report."""

import argparse
import hashlib
import json
import os
from pathlib import Path


def load_report(path, status):
    if status not in (0, 1):
        raise ValueError(f"{path}: scanner exited {status}")
    return json.loads(Path(path).read_text())


def bun_findings(path, status):
    data = load_report(path, status)
    if not isinstance(data, dict):
        raise ValueError("Bun did not return an advisory object")
    findings = []
    for package, advisories in data.items():
        if not isinstance(advisories, list) or not advisories:
            raise ValueError(f"Invalid Bun advisories for {package}")
        for advisory in advisories:
            severity = advisory["severity"]
            url = advisory["url"]
            if severity not in ("critical", "high", "moderate", "low", "info"):
                raise ValueError(f"Unknown advisory severity: {severity}")
            if not url.startswith("https://github.com/advisories/GHSA-"):
                raise ValueError(f"Unexpected advisory URL: {url}")
            findings.append((severity, package, url.rsplit("/", 1)[1], url))
    if bool(findings) != (status == 1):
        raise ValueError("Bun exit status disagrees with advisory output")
    return findings


def write_report(findings, directory):
    priorities = {"critical": 0, "high": 1, "unrated": 2, "moderate": 3,
                  "low": 4, "info": 5}
    findings = sorted(set(findings), key=lambda row: (priorities[row[0]], row[1:]))
    lines = ["# Dependency advisory monitoring", "",
             "Advisory-only rollout: a successful job means the scanners completed, "
             "not that the application is vulnerability-free.", "",
             f"**{len(findings)} package/advisory matches** (not unique CVEs or proven exploits).", "",
             "Includes development dependencies.", "",
             "Managed runtimes, OS/container packages and native mobile binaries are not "
             "covered. This repository has no committed lockfile. This report scans a "
             "fresh resolution of manifest ranges, not deployed artifacts or reproducible "
             "installed versions.", ""]
    for severity in priorities:
        count = sum(row[0] == severity for row in findings)
        if count:
            lines.append(f"- {severity}: {count}")
    lines += ["", "## Findings (first 50; complete results in the workflow artifact)", ""]
    for severity, package, advisory_id, url in findings[:50]:
        safe_package = package.replace("`", "").replace("\n", " ")
        lines.append(f"- **{severity}** `{safe_package}` — [{advisory_id}]({url})")
    fingerprint = hashlib.sha256(json.dumps(findings).encode()).hexdigest()
    lines += ["", f"<!-- inventory-sha256: {fingerprint} -->"]
    report = "\n".join(lines) + "\n"
    Path(directory, "summary.md").write_text(report)
    for variable, content in (("GITHUB_STEP_SUMMARY", report),
                              ("GITHUB_OUTPUT", f"findings={len(findings)}\n")):
        if variable in os.environ:
            with open(os.environ[variable], "a") as output:
                output.write(content)
    if findings:
        print(f"::warning::{len(findings)} dependency advisory matches; see job summary")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", default="security-results")
    parser.add_argument("--bun-exit", type=int, required=True)
    args = parser.parse_args()
    findings = bun_findings(Path(args.directory, "bun.json"), args.bun_exit)
    write_report(findings, args.directory)


if __name__ == "__main__":
    main()
