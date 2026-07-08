"""Tests for workflow discovery and evaluation."""

import textwrap

from cicd_toolkit.validator import (
    discover_workflows,
    evaluate,
    exceeds_threshold,
    max_severity,
)


def _write(tmp_path, name, content):
    path = tmp_path / name
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path


def test_discover_finds_yaml_files(tmp_path):
    _write(tmp_path, "a.yml", "jobs: {}")
    _write(tmp_path, "b.yaml", "jobs: {}")
    _write(tmp_path, "c.txt", "ignored")
    assert len(discover_workflows(tmp_path)) == 2


def test_evaluate_flags_unpinned_action(tmp_path):
    _write(
        tmp_path,
        "ci.yml",
        """
        jobs:
          build:
            steps:
              - uses: actions/checkout
        """,
    )
    findings = evaluate(discover_workflows(tmp_path))
    rules = {f.rule for f in findings}
    assert "pinned-actions" in rules
    assert max_severity(findings) == "error"
    assert exceeds_threshold(findings, "error") is True
