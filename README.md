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

## Philosophy

> The competent programmer is fully aware of the strictly limited size of
> his own skull; therefore he approaches the programming task in full
> humility, and among other things he avoids clever tricks like the plague.
>
> — Dijkstra, *The Humble Programmer* (1972)

This is a framework for the sanity of application programmers.

1. **The Unix philosophy, generalized** (McIlroy). A valve does one thing
   well; valves work together over pipes; the pipe is the universal
   interface. The pipe itself is upgraded from an ephemeral kernel buffer to
   a durable, inspectable file, and the interface is generalized from text
   streams to JSON, plus binary data by reference (PostgreSQL TOAST-style: a
   drop holds a path; the bytes stay untouched on disk).
2. **Mechanism belongs to the framework; policy belongs to your code**
   (Hydra, the X Window System; the same reason Spark, Hadoop, and Storm
   exist; also VTK's pipeline model and Rx's composable streams). Crash
   safety, process lifecycle, and data movement are the framework's job. A
   valve function carries only domain logic.
3. **Functional core, imperative shell** (Gary Bernhardt, *Boundaries*,
   2012). Valve functions are pure and mutually unaware of each other, so a
   pipeline's complexity never compounds — a 50-valve pipeline is as easy to
   reason about, valve-by-valve, as a 2-valve one. State lives outside the
   process, so the process itself is disposable.

## Vocabulary

- **drop** — one record flowing through a pipe.
- **valve** — a processing step, written as a plain function and decorated
  with `@valve`. Source, transform, sink, stateless or stateful — all the
  same decorator, no boilerplate for the common case.
- **reservoir** — state a stateful valve carries from one drop to the next.
- **pipe** / **gauge** — the durable log connecting valves, and the
  checkpoint tracking a valve's progress through it.
- **actuator** — starts, stops, restarts, and pauses/resumes a valve's
  process, mirroring the mechanical distinction between a valve and the
  actuator that operates it from outside.

## Key decisions

- **Fan-out only, never fan-in.** Each valve has at most one inlet. Multiple
  downstream valves can read the same pipe independently at no cost.
  Apparent needs for multi-input joins have always turned out to be
  sequential enrichment instead, solved by cascading single-inlet valves.
- **Each valve is its own OS process**, mainly for job control: pausing one
  valve (`attach`/`detach`) has to target it individually, and signals
  address a process, not a thread. A blocking or crashing valve can't stall
  or take down any other.
- **Crash safety by construction.** Every valve atomically checkpoints its
  progress alongside its output, so a crash at any point is harmless, and
  reprocessing after a restart is exactly-once — no downstream
  deduplication needed.
- **Single-machine orchestration, not a distributed system.** A valve can
  call out to remote or distributed compute — an HPC job, a cloud API — but
  the pipeline graph itself, the valves and pipes, always runs on one
  machine.
- **Durable pipes double as lineage.** Every intermediate result is a file
  on disk, not a value that vanishes once consumed — so a pipeline's full
  data lineage is there for free, inspectable and replayable after the run.