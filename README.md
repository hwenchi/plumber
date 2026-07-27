# plumber

Stream processing for small data on a single machine.

```python
@valve(outlet="raw")
def watch_directory():
    return [...]

@valve(inlet="raw", outlet="attached")
def attach_metadata(d):
    return [...]
```

## Example

`examples/vision/` — four valves chained over three pipes:

- `generate_positions` — a stateful source. The reservoir carries each
  ball's position and velocity from one frame to the next.
- `draw_frame` — draws the balls, writes the PNG to disk, and puts the path
  in the drop.
- `detect_circles` — finds the balls again with a Hough transform and
  annotates the frame. Crashes on purpose on ~0.2% of drops, so restart and
  recovery show up in a normal run.
- `play_video` — a sink. Labels the frame with its detections and displays
  it.

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