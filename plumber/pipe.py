import json
import os
import pathlib
import typing


class PipeLike(typing.Protocol):
    def tap(self, offset: int): ...

    def truncate(self, offset: int) -> None: ...

    def append(self, drops: list[dict]) -> int: ...


class NullPipe:
    def tap(self, offset: int):
        return None, offset

    def truncate(self, offset: int) -> None:
        pass

    def append(self, drops: list[dict]) -> int:
        return 0


class Pipe:
    def __init__(self, data_dir, name):
        self.path = pathlib.Path(data_dir) / "pipes" / f"{name}.jsonl"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch(exist_ok=True)

    def truncate(self, offset: int) -> None:
        with open(self.path, "r+b") as f:
            f.truncate(offset)
            f.flush()
            os.fsync(f.fileno())

    def append(self, drops: list[dict]) -> int:
        with open(self.path, "ab") as f:
            for drop in drops:
                f.write(json.dumps(drop).encode("utf-8") + b"\n")
            f.flush()
            os.fsync(f.fileno())
            return f.tell()

    def tap(self, offset: int):
        return next(self.read_from(offset), None)

    def read_from(self, offset: int):
        with open(self.path, "rb") as f:
            f.seek(offset)
            while True:
                line = f.readline()
                if not line:
                    return
                offset += len(line)
                if line.strip():
                    yield json.loads(line), offset
