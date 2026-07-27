import json
import os
import signal
import subprocess
import sys
import time


def read_lines(path):
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_pipeline_run_detects_crash_and_restarts(tmp_path):
    module_file = tmp_path / "crash_pipeline.py"
    module_file.write_text(
        "import os\n"
        "from plumber.decorator import valve\n"
        "\n"
        "@valve(outlet='raw')\n"
        "def counter(_, reservoir):\n"
        "    n = reservoir.get('n', 0) + 1\n"
        "    return [{'n': n, 'pid': os.getpid()}], {'n': n}\n"
    )

    runner_file = tmp_path / "run_crash_pipeline.py"
    runner_file.write_text(
        "from crash_pipeline import counter\n"
        "from plumber.pipeline import Pipeline\n"
        "\n"
        "Pipeline([counter], 'data').run()\n"
    )

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(tmp_path), env.get("PYTHONPATH", "")])

    proc = subprocess.Popen(
        [sys.executable, str(runner_file)],
        cwd=tmp_path,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    raw_pipe = tmp_path / "data" / "pipes" / "raw.jsonl"

    try:
        for _ in range(50):
            if read_lines(raw_pipe):
                break
            time.sleep(0.1)
        else:
            raise AssertionError("valve never produced a drop")

        original = read_lines(raw_pipe)
        original_pid = original[-1]["pid"]
        original_n = original[-1]["n"]

        os.kill(original_pid, signal.SIGKILL)

        for _ in range(50):
            time.sleep(0.1)
            lines = read_lines(raw_pipe)
            if lines and lines[-1]["pid"] != original_pid:
                break
        else:
            raise AssertionError("valve was never restarted")

        final = read_lines(raw_pipe)
        assert final[-1]["pid"] != original_pid
        assert final[-1]["n"] > original_n
    finally:
        proc.terminate()
        proc.wait(timeout=5)
