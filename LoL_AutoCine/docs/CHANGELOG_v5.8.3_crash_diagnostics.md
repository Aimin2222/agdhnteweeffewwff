# v5.8.3

- Checked-scenes stage markers in diagnostics/runtime.log.
- Telemetry I/O failures no longer override render results.
- GPU sampling reduced to once per 3 seconds; telemetry thread join bounded.
- Existing camera, audio, and effects paths preserved.
- Windows native crash cause is not yet confirmed; inspect fatal_python.log and runtime.log after reproduction.
