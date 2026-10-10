"""Coalesce bursts of Tk variable writes into one redraw of the final state."""


def request_redraw(widget, method="draw"):
    if getattr(widget, "_redraw_token", None) is not None:
        return

    def draw_latest():
        widget._redraw_token = None
        if widget.winfo_exists():
            getattr(widget, method)()

    widget._redraw_token = widget.after(20, draw_latest)
