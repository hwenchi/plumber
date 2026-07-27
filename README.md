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

- **stream → pipe.** A stream is a sequence of data between processing
  steps — traditionally an ephemeral kernel buffer. Ours is a durable log
  file, append-only in normal operation but truncated back to the last
  checkpoint on crash recovery.
- **filter → valve.** A filter consumes and produces a stream. A valve is a
  plain function decorated with `@valve` — source, transform, sink,
  stateless or stateful, all the same decorator.
- **record → drop.** One unit of data flowing through a pipe.
- **accumulator → reservoir.** State a stateful valve carries from one drop
  to the next.
- **checkpoint → gauge.** The file tracking a valve's progress and
  reservoir, so it resumes exactly where it left off.
- **process handle → actuator.** Starts, stops, restarts, and
  pauses/resumes a valve's process — a control interface only. Deciding
  *when* to restart a crashed valve is `Pipeline.run()`'s job.

## Philosophy

> The competent programmer is fully aware of the strictly limited size of
> his own skull; therefore he approaches the programming task in full
> humility, and among other things he avoids clever tricks like the plague.
>
> — Dijkstra, *The Humble Programmer* (1972)

This is a framework for the sanity of application programmers.

1. **The Unix philosophy, generalized** (McIlroy; VTK's filter pipeline;
   Rx's composable streams). A valve does one thing well; valves work
   together over pipes; the pipe is the universal interface — upgraded from
   an ephemeral kernel buffer to a durable, inspectable file, and
   generalized from text streams to JSON. By convention, large binary
   payloads (e.g. images) are written to disk separately and referenced by
   a plain path field in the drop, which a valve opens explicitly to get
   the bytes — the framework itself has no built-in blob storage.
2. **Mechanism belongs to the framework; policy belongs to your code**
   (Hydra, the X Window System; the same reason Spark, Hadoop, and Storm
   exist). Crash safety, process lifecycle, and data movement are the
   framework's job. A valve function carries only domain logic.
3. **Functional core, imperative shell** (Gary Bernhardt, *Boundaries*,
   2012). Valve functions are pure and mutually unaware of each other, so a
   pipeline's complexity never compounds — a 50-valve pipeline is as easy to
   reason about, valve-by-valve, as a 2-valve one. State lives outside the
   process, so the process itself is disposable.

## Key decisions

- **Fan-out only, never fan-in.** Each valve has at most one inlet. Multiple
  downstream valves can read the same pipe independently at no cost.
  Apparent needs for multi-input joins have always turned out to be
  sequential enrichment instead, solved by cascading single-inlet valves.
- **Each valve is its own OS process**, mainly for job control: pausing one
  valve (`attach`/`detach`) has to target it individually, and POSIX
  signals can't address a single thread inside a shared process. A blocking
  or crashing valve can't stall or take down any other.
- **Crash safety by construction.** Every valve checkpoints its progress
  atomically (write, fsync, rename), and on restart rolls its outlet back
  to the last checkpoint before resuming, so its own reprocessing is
  exactly-once. A downstream valve that already tapped output written
  after that checkpoint but before the crash will still have seen it,
  since fan-out readers are independent of the producer's rollback.
- **Single-machine orchestration.** A valve can call out to remote or
  distributed compute — an HPC job, a cloud API — but the pipeline graph
  itself, the valves and pipes, always runs on one machine.
- **Durable pipes double as lineage.** Every intermediate result is written
  to disk and persists after being consumed, so a pipeline's full data
  lineage is there for free, inspectable and replayable after the run.