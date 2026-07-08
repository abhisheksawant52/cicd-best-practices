"""Best-practice rules for GitHub Actions workflows.

Each rule is a callable ``(document, source) -> list[Finding]``. Rules are pure
functions over the parsed YAML document so they are trivial to unit test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Matches ``owner/repo@ref``; a pinned ref is either a 40-char SHA or a version
# tag. Unpinned references (``owner/repo`` with no ``@``) are flagged.
_ACTION_REF = re.compile(r"^(?P<action>[\w.-]+/[\w.-]+)(?:@(?P<ref>.+))?$")


@dataclass(frozen=True)
class Finding:
    """A single rule violation."""

    rule: str
    severity: str  # "info" | "warning" | "error"
    message: str
    source: str


def _jobs(document: dict) -> dict:
    jobs = document.get("jobs")
    return jobs if isinstance(jobs, dict) else {}


def check_pinned_actions(document: dict, source: str) -> list[Finding]:
    """Every ``uses:`` reference must be pinned to a tag or commit SHA."""
    findings: list[Finding] = []
    for job_name, job in _jobs(document).items():
        for step in job.get("steps", []) or []:
            uses = step.get("uses") if isinstance(step, dict) else None
            if not uses or uses.startswith("./") or uses.startswith("docker://"):
                continue
            match = _ACTION_REF.match(uses)
            if match and not match.group("ref"):
                findings.append(
                    Finding(
                        rule="pinned-actions",
                        severity="error",
                        message=f"job '{job_name}': action '{uses}' is not pinned to a ref",
                        source=source,
                    )
                )
    return findings


def check_least_privilege(document: dict, source: str) -> list[Finding]:
    """A top-level ``permissions`` block should be declared (ideally read-only)."""
    if "permissions" not in document:
        return [
            Finding(
                rule="least-privilege-permissions",
                severity="warning",
                message="no top-level 'permissions' block; token defaults to write access",
                source=source,
            )
        ]
    return []


def check_job_timeouts(document: dict, source: str) -> list[Finding]:
    """Every job should set ``timeout-minutes`` to avoid runaway runners."""
    findings: list[Finding] = []
    for job_name, job in _jobs(document).items():
        if isinstance(job, dict) and "timeout-minutes" not in job:
            findings.append(
                Finding(
                    rule="job-timeouts",
                    severity="warning",
                    message=f"job '{job_name}' has no 'timeout-minutes'",
                    source=source,
                )
            )
    return findings


def check_concurrency(document: dict, source: str) -> list[Finding]:
    """A ``concurrency`` group prevents redundant/overlapping runs."""
    if "concurrency" not in document:
        return [
            Finding(
                rule="concurrency-control",
                severity="info",
                message="no 'concurrency' group; overlapping runs are not cancelled",
                source=source,
            )
        ]
    return []


ALL_RULES = (
    check_pinned_actions,
    check_least_privilege,
    check_job_timeouts,
    check_concurrency,
)
