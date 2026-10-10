"""Tk-free asynchronous mirror lifecycle; results are applied by the UI pump."""
import threading


class MirrorCapture:
    def __init__(self, result_queue):
        self.queue = result_queue
        self.generation = 0
        self.pending = False
        self.source = None
        self.starting = None
        self.cancel = threading.Event()

    def start(self, source):
        if self.pending or self.source is not None:
            return
        self.generation += 1
        token = self.generation
        self.pending = True
        self.starting = source
        self.cancel = cancel = threading.Event()
        result_queue = self.queue

        def run():
            error = None
            try:
                if not cancel.is_set():
                    source.start()
            except Exception as exc:
                error = str(exc)
            finally:
                if cancel.is_set() or error is not None:
                    try:
                        source.stop()
                    except Exception as exc:
                        result_queue.put(('mirror_stop_error', str(exc)))
                result_queue.put(('mirror_ready', token, source, error))

        try:
            threading.Thread(target=run, daemon=True, name='AutoCine-mirror-start').start()
        except Exception:
            self.pending = False
            self.starting = None
            raise

    def accept(self, token, source, error):
        if token != self.generation:
            return False  # Cancelled or replaced attempt must not turn ON again.
        self.pending = False
        self.starting = None
        self.source = source if error is None else None
        return True

    def stop(self):
        self.cancel.set()
        self.generation += 1
        source = self.source or self.starting
        self.source = self.starting = None
        self.pending = False
        if source is None:
            return
        result_queue = self.queue

        def close():
            try:
                source.stop()
            except Exception as exc:
                result_queue.put(('mirror_stop_error', str(exc)))

        threading.Thread(target=close, daemon=True, name='AutoCine-mirror-stop').start()
