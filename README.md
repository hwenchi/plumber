# plumber

Intentionally naive stream processing for non-distributed small data.

```python
@valve(outlet="raw")
def watch_directory():
    return [...]

@valve(inlet="raw", outlet="attached")
def attach_metadata(d):
    return [...]
```

## Example

`examples/vision/` — a source generates synthetic bouncing balls, a
transform renders each frame, another detects circles with OpenCV's Hough
transform, and a sink plays the stream live. Four processes, communicating
only through JSONL files.

```bash
uv run python examples/run_vision.py
```

## Vocabulary

- **stream → pipe.** The JSONL file carrying data between valves.
  Append-only, and truncated back to the last checkpoint on crash recovery.
- **filter → valve.** A processing step, written as a plain function with
  the `@valve` decorator. Source, transform, sink, stateless or stateful,
  all the same decorator.
- **record → drop.** One unit of data in a pipe.
- **accumulator → reservoir.** State a stateful valve carries from one drop
  to the next.
- **checkpoint → gauge.** The file holding a valve's progress and
  reservoir, so it resumes where it left off.
- **process handle → actuator.** Starts, stops, restarts, and
  pauses/resumes a valve's process. `Pipeline.run()` decides when to
  restart a crashed valve.

## Design

- **A valve function holds domain logic only.** Crash safety, process
  lifecycle, and data movement are the framework's job.
- **Valves don't reference each other.** Each one reads its inlet and
  returns drops, so adding a valve leaves the rest untouched. State lives
  on disk, so the process is disposable.
- **Fan-out only.** Each valve has at most one inlet. Any number of valves
  can read the same pipe.
- **One OS process per valve.** `attach`/`detach` pause and resume one
  valve at a time, and a blocked or crashing valve leaves the others
  running.
- **Checkpoints are atomic** (write, fsync, rename). A restarted valve
  rolls its outlet back to the last checkpoint, so the pipe holds no
  duplicate output. A downstream valve may already have read output written
  past that checkpoint.
- **Binary payloads stay out of the pipe.** A valve writes the bytes to
  disk and puts the path in the drop. The framework has no blob storage.
- **The pipeline graph runs on one machine.** A valve can call out to
  remote compute, such as an HPC job or a cloud API.
- **Pipes persist after being consumed**, so every intermediate result
  stays inspectable and replayable.