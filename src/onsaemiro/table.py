"""Console and Jupyter table rendering."""

import html as _html
import sys
from io import StringIO

from ._environment import _is_jupyter


_TABLE_MODES = ("static", "live", "dynamic")


class TableMaker:
    """Table for console / Jupyter with optional live updates."""

    def __init__(self, title="Analysis", columns=None, mode="static"):
        if mode not in _TABLE_MODES:
            raise ValueError(
                f"Unknown mode {mode!r}; expected one of {_TABLE_MODES}."
            )
        self.title = title
        self.columns = columns or ["Parameter", "Value", "Unit"]
        self.data = []
        self.mode = mode
        self._jupyter = _is_jupyter()
        self._prev_lines = 0
        self._handle = None

    # ── Renderers ──

    def _render_html(self):
        """
        Academic-style (Booktabs) table.
        Works perfectly in both Light and Dark modes using 'currentColor'.
        All text content is HTML-escaped to survive arbitrary data.
        """
        # ── Design Constants ──
        LINE_COLOR = "currentColor"
        TEXT_COLOR = "currentColor"
        FONT_FAMILY = "'Times New Roman', Times, serif"

        esc = _html.escape

        # Header cells (wrapped in a single <tr>)
        hdr_cells = ""
        for i, c in enumerate(self.columns):
            align = "left" if i == 0 else "right"
            hdr_cells += (
                f'<th style="padding:10px 14px; text-align:{align}; '
                f'font-weight:bold; color:{TEXT_COLOR}; '
                f'border-top:2.5px solid {LINE_COLOR}; '
                f'border-bottom:1.2px solid {LINE_COLOR}; '
                f'font-size:14px; background:none">{esc(str(c))}</th>'
            )
        hdr = f'<tr>{hdr_cells}</tr>'

        # Body rows
        body = ""
        for r, row in enumerate(self.data):
            cells = ""
            is_last = (r == len(self.data) - 1)
            bottom_border = f"2.5px solid {LINE_COLOR}" if is_last else "none"

            for i, c in enumerate(row):
                align = "left" if i == 0 else "right"
                cells += (
                    f'<td style="padding:8px 14px; text-align:{align}; '
                    f'font-size:13px; color:{TEXT_COLOR}; '
                    f'border-bottom:{bottom_border}; background:none">'
                    f'{esc(str(c))}</td>'
                )
            body += f'<tr>{cells}</tr>'

        return (
            f'<div style="margin:15px 0; display:inline-block; background:none">'
            f'<div style="font-family:{FONT_FAMILY}; font-weight:bold; color:{TEXT_COLOR}; '
            f'font-size:14px; margin-bottom:10px; text-align:left">{esc(str(self.title))}</div>'
            f'<table style="border-collapse:collapse; font-family:{FONT_FAMILY}; '
            f'border:none; line-height:1.5; color:{TEXT_COLOR}; background:none">'
            f'<thead>{hdr}</thead>'
            f'<tbody>{body}</tbody></table></div>'
        )

    def _render_text(self):
        """Rich-formatted text for terminal only. rich is imported lazily
        so it is not a hard dependency for users who never call display()
        or add_row() in live/dynamic mode."""
        from rich.console import Console
        from rich.table import Table
        from rich.text import Text

        buf = StringIO()
        # Text objects are always literal — square brackets in data can
        # never be misread as Rich console markup (e.g. "[phi=0.4]").
        t = Table(title=Text(str(self.title)))
        for i, col in enumerate(self.columns):
            t.add_column(Text(str(col)), justify="left" if i == 0 else "right")
        for row in self.data:
            t.add_row(*[Text(str(v)) for v in row])

        Console(
            file=buf,
            force_jupyter=False,
            force_terminal=sys.stdout.isatty(),
            width=120,
        ).print(t)
        return buf.getvalue()

    # ── Row management ──

    def add_row(self, *values):
        """Add a row to the table.
        Accepts either positional arguments or a single list/tuple:
            table.add_row("a", "b", "c")
            table.add_row(["a", "b", "c"])
        """
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            row = values[0]
        else:
            row = values

        self.data.append([str(v) for v in row])
        if self.mode in ("live", "dynamic"):
            self._update()

    # ── Update logic ──

    def _update(self):
        if self._jupyter:
            self._update_jupyter()
        else:
            self._update_terminal()

    def _update_terminal(self):
        if self._prev_lines > 0:
            sys.stdout.write(f"\033[{self._prev_lines}A\033[J")
        text = self._render_text()
        sys.stdout.write(text)
        sys.stdout.flush()
        self._prev_lines = text.count("\n")

    def _update_jupyter(self):
        from IPython.display import display, HTML
        html = HTML(self._render_html())
        if self._handle is None:
            self._handle = display(html, display_id=True)
        else:
            self._handle.update(html)

    # ── Static display ──

    def display(self):
        if self._jupyter:
            from IPython.display import display as ipy_display, HTML
            ipy_display(HTML(self._render_html()))
        else:
            print(self._render_text(), end="")
