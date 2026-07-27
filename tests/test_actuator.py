import importlib
import os
import sys
import time

from plumber.actuator import Actuator


def make_fake_pipeline(tmp_path):
    module_name = "fake_pipeline"
    module_file = tmp_path / f"{module_name}.py"
    module_file.write_text(
        "from plumber.decorator import valve\n"
        "\n"
        "@valve(outlet='raw')\n"
        "def watch_directory():\n"
        "    return [{'n': 1}]\n"
    )

    sys.path.insert(0, str(tmp_path))
    try:
        fake_pipeline = importlib.import_module(module_name)
        flow = fake_pipeline.watch_directory
    finally:
        sys.path.remove(str(tmp_path))

    os.environ["PYTHONPATH"] = os.pathsep.join([str(tmp_path), os.environ.get("PYTHONPATH", "")])
    return flow


def test_start_spawns_a_running_process(tmp_path):
    flow = make_fake_pipeline(tmp_path)
    data_dir = tmp_path / "data"
    actuator = Actuator(flow, data_dir)

    actuator.start()
    try:
        assert actuator.is_running() is True
        assert actuator.pid is not None
    finally:
        actuator.stop()


def test_detach_stops_progress_and_attach_resumes(tmp_path):
    flow = make_fake_pipeline(tmp_path)
    data_dir = tmp_path / "data"
    actuator = Actuator(flow, data_dir)
    actuator.start()

    try:
        time.sleep(0.3)
        actuator.detach()
        pipe_path = data_dir / "pipes" / "raw.jsonl"
        count_while_detached = len(pipe_path.read_text().splitlines())
        time.sleep(0.3)
        assert len(pipe_path.read_text().splitlines()) == count_while_detached

        actuator.attach()
        time.sleep(0.3)
        assert len(pipe_path.read_text().splitlines()) > count_while_detached
    finally:
        actuator.stop()


def test_restart_replaces_the_process(tmp_path):
    flow = make_fake_pipeline(tmp_path)
    data_dir = tmp_path / "data"
    actuator = Actuator(flow, data_dir)
    actuator.start()

    try:
        old_pid = actuator.pid
        actuator.restart()

        assert actuator.pid != old_pid
        assert actuator.is_running() is True
    finally:
        actuator.stop()