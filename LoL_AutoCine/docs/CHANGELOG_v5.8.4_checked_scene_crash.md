# v5.8.4 - Checked scenes freeze/crash investigation

## Fixed
- v5.8.3 inserted CHECKED_STAGE capture_start markers in the **wrong handler** (single scene). v5.8.4 puts them into `_make_list`.
- Add stage logs **before and after** reading the current template and dispatching the background thread, plus source start/stop and job completion. These determine whether the crash is in Tk/UI, source startup, or render.
- Set busy state synchronously to prevent double-start.
- Reduce heavy UI preview image processing during render, while retaining mirror view at a lower refresh rate.
- Add periodic stack dumps to `diagnostics/fatal_python.log` for hangs during checked-scene rendering. Not guaranteed for native crashes.
- Protect the UI queue pump with logging on unexpected exceptions.
- Add `COLLECT_DIAGNOSTICS.bat` to package diagnostic files.

## Not changed
- Camera/target lock, LoL-only audio, render pipeline, selected clips logic, GPU effect choices.

## Testing and limitations
- Synthetic UI callback regression test and Python syntax checks are provided. Real LoL, Windows capture and GPU tests must be run on Windows. Windows native process exit `0xCFFFFFFF` is not diagnosable by a stage marker alone.
