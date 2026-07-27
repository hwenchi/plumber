import json
import os
import pathlib


class Gauge:
    def __init__(self, data_dir, name):
        self.path = pathlib.Path(data_dir) / "gauges" / f"{name}.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict:
        if not os.path.exists(self.path):
            return {"read_offset": 0, "write_offset": 0, "reservoir": {}}
        with open(self.path, "rb") as f:
            return json.loads(f.read())

    def write(self, checkpoint: dict) -> None:
        tmp_path = f"{self.path}.tmp"
        with open(tmp_path, "wb") as f:
            f.write(json.dumps(checkpoint).encode("utf-8"))
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, self.path)
