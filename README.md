# plumber

Stream processing for small data on a single machine.

```python
# squares.py
from plumber.decorator import valve


@valve(outlet="ticks", throttle=1)
def count_up(_, reservoir):
    n = reservoir.get("n", 0)
    return [{"n": n}], {"n": n + 1}


@valve(inlet="ticks", outlet="squares")
def square(d):
    return [{**d, "square": d["n"] ** 2}]


@valve(inlet="squares")
def report(d):
    print(d["n"], d["square"])
```

```python
# run.py
from plumber.pipeline import Pipeline
from squares import count_up, report, square

if __name__ == "__main__":
    Pipeline([count_up, square, report], "data/").run()
```

A valve takes the incoming drop, plus a reservoir if it keeps state, and
returns a list of drops and the next reservoir. Each valve runs in a fresh
process that imports its module, so valves live in an importable file,
separate from the script that runs the pipeline.

Two knobs set a valve's pace. `backoff` is how long it waits after finding
its inlet empty. `throttle` is the minimum time between drips, for a valve
that always has work.

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

- **The data path isn't distributed.** Where and how a valve computes is
  not plumber's concern. Pipes and gauges live on one machine's disk, and
  every drop funnels through it.
- **A valve doesn't read two pipes.** No fan-in. Any number of valves can
  read the same pipe.
- **A valve doesn't do plumbing.** Crash safety, process lifecycle, and
  data movement are the framework's job. The function carries domain logic.
- **A restart doesn't duplicate output.** Checkpoints are atomic (write,
  fsync, rename), and a restarted valve rolls its outlet back to the last
  one. A downstream valve may already have read past that point.
- **Reading a pipe doesn't empty it.** Every intermediate result stays on
  disk, inspectable and replayable.
- **Valves don't share a process.** `attach`/`detach` pause one valve at a
  time, and a blocked or crashing valve leaves the others running.
- **A valve doesn't know the others.** It reads its inlet and returns
  drops, so adding one leaves the rest untouched. State lives on disk, so
  the process is disposable.
- **A pipe doesn't carry bytes.** A valve writes binary payloads to disk
  and puts the path in the drop. The framework has no blob storage.