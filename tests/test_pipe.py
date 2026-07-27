from plumber.pipe import Pipe


def test_append_and_read_from(tmp_path):
    pipe = Pipe(tmp_path, "raw")

    offset = pipe.append([{"a": 1}, {"a": 2}])

    drops = list(pipe.read_from(0))
    assert [d for d, _ in drops] == [{"a": 1}, {"a": 2}]
    assert drops[-1][1] == offset


def test_read_from_resumes_at_last_offset(tmp_path):
    pipe = Pipe(tmp_path, "raw")

    pipe.append([{"a": 1}])
    mid_offset = pipe.append([{"a": 2}])
    pipe.append([{"a": 3}])

    drops = list(pipe.read_from(mid_offset))
    assert [d for d, _ in drops] == [{"a": 3}]


def test_truncate_removes_partial_write(tmp_path):
    pipe = Pipe(tmp_path, "raw")

    good_offset = pipe.append([{"a": 1}])
    with open(pipe.path, "ab") as f:
        f.write(b'{"a": incomplete')  # simulate a crash mid-write

    pipe.truncate(good_offset)

    drops = list(pipe.read_from(0))
    assert [d for d, _ in drops] == [{"a": 1}]