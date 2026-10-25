"""Tests for log file naming in the custom logging plugin."""

import re

import pytest

from execution_testing.cli.pytest_commands.plugins.custom_logging.plugin_logging import (  # noqa: E501
    get_log_stem,
)

TIMESTAMP = r"\d{8}-\d{6}"


@pytest.mark.parametrize(
    "argv0,argv1,expected",
    [
        pytest.param("/venv/bin/fill", None, "fill", id="no-args"),
        pytest.param("/venv/bin/fill", "-k", "fill", id="option"),
        pytest.param(
            "/venv/bin/consume", "engine", "consume-engine", id="subcommand"
        ),
        pytest.param(
            "/venv/bin/execute", "remote", "execute-remote", id="subcommand-2"
        ),
        pytest.param(
            "/venv/bin/fill",
            "tests/frontier/opcodes/test_dup.py",
            "fill",
            id="test-path",
        ),
        pytest.param(
            "/venv/bin/fill",
            "tests/frontier/opcodes/test_dup.py::test_dup[fork_Cancun]",
            "fill",
            id="test-node-id",
        ),
        pytest.param("__main__", "tests", "pytest-tests", id="pytest"),
    ],
)
def test_get_log_stem(argv0: str, argv1: str | None, expected: str) -> None:
    """A test path must not end up in the log file name."""
    stem = get_log_stem(argv0, argv1)
    assert re.fullmatch(rf"{re.escape(expected)}-{TIMESTAMP}", stem), stem
