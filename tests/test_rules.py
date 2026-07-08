"""Unit tests for the workflow best-practice rules."""

from cicd_toolkit.rules import (
    check_concurrency,
    check_job_timeouts,
    check_least_privilege,
    check_pinned_actions,
)

HARDENED = {
    "permissions": {"contents": "read"},
    "concurrency": {"group": "ci-${{ github.ref }}", "cancel-in-progress": True},
    "jobs": {
        "build": {
            "timeout-minutes": 15,
            "steps": [{"uses": "actions/checkout@v4"}],
        }
    },
}

RISKY = {
    "jobs": {
        "build": {
            "steps": [{"uses": "actions/checkout"}],
        }
    },
}


def test_hardened_workflow_has_no_findings():
    assert check_pinned_actions(HARDENED, "wf") == []
    assert check_least_privilege(HARDENED, "wf") == []
    assert check_job_timeouts(HARDENED, "wf") == []
    assert check_concurrency(HARDENED, "wf") == []


def test_unpinned_action_is_flagged_as_error():
    findings = check_pinned_actions(RISKY, "wf")
    assert len(findings) == 1
    assert findings[0].severity == "error"
    assert findings[0].rule == "pinned-actions"


def test_missing_permissions_is_warning():
    findings = check_least_privilege(RISKY, "wf")
    assert findings and findings[0].severity == "warning"


def test_missing_timeout_is_flagged():
    assert check_job_timeouts(RISKY, "wf")[0].rule == "job-timeouts"


def test_missing_concurrency_is_info():
    findings = check_concurrency(RISKY, "wf")
    assert findings and findings[0].severity == "info"
