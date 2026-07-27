import importlib
import json
import os
import subprocess
import sys
import time


def test_run_module_runs_valve_end_to_end(tmp_path):
    module_file = tmp_path / "fake_pipeline.py"
    module_file.write_text(
        "from plumber.decorator import valve\n"
        "\n"
        "@valve(outlet='raw')\n"
        "def watch_directory():\n"
        "    return [{'n': 1}]\n"
    )

    sys.path.insert(0, str(tmp_path))
    try:
        fake_pipeline = importlib.import_module("fake_pipeline")
        flow_name = fake_pipeline.watch_directory.fn.__name__
    finally:
        sys.path.remove(str(tmp_path))

    data_dir = tmp_path / "data"
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join([str(tmp_path), env.get("PYTHONPATH", "")])

    proc = subprocess.Popen(
        [sys.executable, "-m", "plumber.run", "fake_pipeline", flow_name, str(data_dir)],
        env=env,
    )
    try:
        time.sleep(0.5)
    finally:
        proc.terminate()
        proc.wait(timeout=5)

    lines = (data_dir / "pipes" / "raw.jsonl").read_text().splitlines()
    assert len(lines) > 0
    assert [json.loads(line) for line in lines] == [{"n": 1}] * len(lines)