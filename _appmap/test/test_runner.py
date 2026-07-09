import os
import re

import pytest


def test_runner_noargs(script_runner):
    result = script_runner.run(["appmap-python"])
    assert result.returncode != 0
    assert result.stdout.startswith("usage")


def test_runner_help(script_runner):
    result = script_runner.run(["appmap-python", "--help"])
    assert result.returncode == 0
    assert result.stdout.startswith("usage")


@pytest.mark.parametrize("recording_type", ["process", "remote", "requests", "tests"])
def test_runner_recording_type(script_runner, recording_type):
    result = script_runner.run(["appmap-python", "--record", recording_type])
    assert result.returncode == 0
    assert (
        re.search(f"(?m)^APPMAP_RECORD_{recording_type.upper()}=true$", result.stdout) is not None
    )

    result = script_runner.run(["appmap-python", "--no-record", recording_type])
    assert result.returncode == 0
    assert re.search(f"(?m)^APPMAP_RECORD_{recording_type.upper()}=true$", result.stdout) is None


@pytest.mark.parametrize("flag,expected", [("--record", 1), ("--no-record", 0)])
def test_runner_multi_recording_type(script_runner, flag, expected):
    types = "process,pytest"
    result = script_runner.run(["appmap-python", flag, types])
    assert result.returncode == 0
    assert len(re.findall("(?m)^APPMAP_RECORD_PROCESS=true$", result.stdout)) == expected
    assert len(re.findall("(?m)^APPMAP_RECORD_PYTEST=true$", result.stdout)) == expected


@pytest.mark.parametrize(
    "flags,expected",
    [
        ([], "true"),
        (["--no-enable-log"], "true"),
        (["--enable-log"], "false"),
    ],
)
def test_runner_log_file_disabled_by_default(script_runner, flags, expected):
    result = script_runner.run(["appmap-python", *flags, "--record", "process"])
    assert result.returncode == 0
    assert re.search(f"(?m)^APPMAP_DISABLE_LOG_FILE={expected}$", result.stdout) is not None


@pytest.mark.script_launch_mode("subprocess")
class TestEnv:
    def test_appmap_present(self, script_runner):
        result = script_runner.run(["appmap-python", "printenv", "APPMAP"])
        assert result.returncode == 0
        assert re.match(r"true", result.stdout) is not None

    def test_recording_type_present(self, script_runner):
        result = script_runner.run(
            ["appmap-python", "--record", "process", "printenv", "APPMAP_RECORD_PROCESS"]
        )
        assert result.returncode == 0
        assert re.match(r"true", result.stdout) is not None

    def test_internal_state_not_leaked_to_child(self, script_runner):
        # appmap-python is itself instrumented at interpreter startup (via
        # appmap.pth), which can set internal, process-scoped _APPMAP*
        # markers using whatever it inherited, before this script has
        # computed the environment the child command should actually run
        # with. Simulate that by pre-setting one such marker (the
        # once-per-process "startup messages already shown" guard) and
        # confirm it doesn't leak into the child's environment, which would
        # otherwise silently suppress the child's own startup logging.
        env = {**os.environ, "_APPMAP_MESSAGES_SHOWN": "true"}
        result = script_runner.run(
            ["appmap-python", "printenv", "_APPMAP_MESSAGES_SHOWN"], env=env
        )
        assert result.returncode != 0
        assert result.stdout == ""
