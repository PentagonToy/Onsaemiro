"""Console and Jupyter table rendering."""

import csv
from collections.abc import Callable, Iterable, Mapping, Sequence
import html as _html
from os import PathLike
import sys
from io import StringIO
from pathlib import Path
from typing import Any

from ._environment import _is_jupyter


_TABLE_MODES = ("static", "live", "dynamic")


class TableMaker:
    """Table for console / Jupyter with optional live updates."""

    def __init__(
        self,
        title: str = "Analysis",
        columns: Iterable[str] | None = None,
        mode: str = "static",
        *,
        formatters: (
            Mapping[str | int, str | Callable[[Any], Any]]
            | Sequence[str | Callable[[Any], Any] | None]
            | None
        ) = None,
    ) -> None:
        if mode not in _TABLE_MODES:
            raise ValueError(
                f"Unknown mode {mode!r}; expected one of {_TABLE_MODES}."
            )
        self.title = title
        self.columns = list(columns or ["Parameter", "Value", "Unit"])
        if not self.columns:
            raise ValueError("TableMaker requires at least one column.")
        self.data: list[list[str]] = []
        self.mode = mode
        self.formatters = formatters
        self._jupyter = _is_jupyter()
        self._handle = None
        self._console: Any = None
        self._live: Any = None
        self._closed = False

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

    def _render_rich_table(self):
        """Build the Rich table used by terminal renderers."""
        from rich.table import Table
        from rich.text import Text

        table = Table(
            title=Text(str(self.title))
        )

        for index, column in enumerate(
            self.columns
        ):
            table.add_column(
                Text(str(column)),
                justify=(
                    "left"
                    if index == 0
                    else "right"
                ),
            )

        for row in self.data:
            table.add_row(
                *[
                    Text(str(value))
                    for value in row
                ]
            )

        return table

    def _render_text(self):
        """Render a static Rich-formatted terminal table."""
        from rich.console import Console

        buffer = StringIO()

        Console(
            file=buffer,
            force_jupyter=False,
            force_terminal=sys.stdout.isatty(),
            width=120,
        ).print(
            self._render_rich_table()
        )

        return buffer.getvalue()

    # ── Row management ──

    def _normalise_row(self, values: tuple[Any, ...]) -> list[str]:
        if len(values) == 1 and isinstance(values[0], (list, tuple)):
            row = list(values[0])
        else:
            row = list(values)

        if len(row) != len(self.columns):
            raise ValueError(
                f"Expected {len(self.columns)} values, received {len(row)}."
            )

        formatted = []
        for index, value in enumerate(row):
            formatter = None
            if isinstance(self.formatters, dict):
                formatter = self.formatters.get(
                    self.columns[index],
                    self.formatters.get(index),
                )
            elif self.formatters is not None and index < len(self.formatters):
                formatter = self.formatters[index]

            if formatter is None:
                formatted.append(str(value))
            elif callable(formatter):
                formatted.append(str(formatter(value)))
            else:
                formatted.append(format(value, str(formatter)))

        return formatted

    def add_row(self, *values: Any) -> None:
        """Add a row to the table.
        Accepts either positional arguments or a single list/tuple:
            table.add_row("a", "b", "c")
            table.add_row(["a", "b", "c"])
        """
        self.data.append(self._normalise_row(values))
        if self.mode in ("live", "dynamic"):
            self._update()

    def update_row(self, index: int, *values: Any) -> None:
        """Replace an existing row and refresh live output."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("Row index must be an integer.")

        try:
            self.data[index] = self._normalise_row(values)
        except IndexError as error:
            raise IndexError(
                f"Row index out of range: {index}"
            ) from error

        if self.mode in ("live", "dynamic"):
            self._update()

    def sort(
        self,
        column: str | int = 0,
        *,
        reverse: bool = False,
        key: Callable[[str], Any] | None = None,
    ) -> "TableMaker":
        """Sort rows in place by a column name or index."""
        if isinstance(column, str):
            try:
                column = self.columns.index(column)
            except ValueError as error:
                raise KeyError(f"Unknown table column: {column!r}.") from error
        if not isinstance(column, int) or isinstance(column, bool):
            raise TypeError("column must be a name or integer index.")
        if not -len(self.columns) <= column < len(self.columns):
            raise IndexError(f"Column index out of range: {column}")

        value_key = key or (lambda value: value)
        self.data.sort(
            key=lambda row: value_key(row[column]),
            reverse=reverse,
        )
        if self.mode in ("live", "dynamic"):
            self._update()
        return self

    def to_csv(self, path: str | PathLike[str]) -> Path:
        """Export the table, including its header, to CSV."""
        destination = Path(path).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(self.columns)
            writer.writerows(self.data)
        return destination

    def to_latex(
        self,
        path: str | PathLike[str] | None = None,
        *,
        caption: str | None = None,
        label: str | None = None,
    ) -> str:
        """Return a booktabs LaTeX table and optionally write it to a file."""
        def escape(value: object) -> str:
            replacements = {
                "\\": r"\textbackslash{}",
                "&": r"\&",
                "%": r"\%",
                "$": r"\$",
                "#": r"\#",
                "_": r"\_",
                "{": r"\{",
                "}": r"\}",
            }
            return "".join(
                replacements.get(character, character)
                for character in str(value)
            )

        alignment = "l" + "r" * (len(self.columns) - 1)
        lines = [r"\begin{table}", r"\centering"]
        if caption is not None:
            lines.append(rf"\caption{{{escape(caption)}}}")
        if label is not None:
            lines.append(rf"\label{{{escape(label)}}}")
        lines.extend(
            [
                rf"\begin{{tabular}}{{{alignment}}}",
                r"\toprule",
                " & ".join(escape(value) for value in self.columns) + r" \\",
                r"\midrule",
            ]
        )
        lines.extend(
            " & ".join(escape(value) for value in row) + r" \\"
            for row in self.data
        )
        lines.extend(
            [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
        )
        output = "\n".join(lines) + "\n"

        if path is not None:
            destination = Path(path).expanduser()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output, encoding="utf-8")

        return output

    # ── Update logic ──

    def _update(self):
        if self._jupyter:
            self._update_jupyter()
        else:
            self._update_terminal()

    def _update_terminal(self):
        if not sys.stdout.isatty():
            return

        from rich.console import Console
        from rich.live import Live

        renderable = self._render_rich_table()

        if self._live is None:
            self._console = Console(
                file=sys.stdout,
                force_jupyter=False,
            )
            self._live = Live(
                renderable,
                console=self._console,
                auto_refresh=False,
                transient=False,
            )
            self._live.start(
                refresh=True
            )
        else:
            self._live.update(
                renderable,
                refresh=True,
            )

    def _update_jupyter(self):
        from IPython.display import display, HTML
        html = HTML(self._render_html())
        if self._handle is None:
            self._handle = display(html, display_id=True)
        else:
            self._handle.update(html)

    # ── Lifecycle ──

    def close(self):
        """Finish live output and preserve the final table."""
        if self._closed:
            return

        if self._live is not None:
            self._live.stop()
            self._live = None
            self._console = None
        elif (
            not self._jupyter
            and self.mode in ("live", "dynamic")
            and not sys.stdout.isatty()
        ):
            print(
                self._render_text(),
                end="",
            )

        self._closed = True

    # ── Static display ──

    def display(self):
        if self._jupyter:
            from IPython.display import display as ipy_display, HTML
            ipy_display(HTML(self._render_html()))
        else:
            print(self._render_text(), end="")
