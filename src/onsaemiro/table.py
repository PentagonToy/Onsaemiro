"""Portable table rendering for terminals and notebooks."""

import csv
from collections.abc import Callable, Iterable, Mapping, Sequence
import html
from os import PathLike
from pathlib import Path
import shutil
import sys
import textwrap
from typing import Any

from ._environment import _is_jupyter


_TABLE_MODES = ("static", "live", "dynamic")


class Table:
    """A small scientific table with plain-text and HTML representations."""

    def __init__(self, title: str = "Analysis", columns: Iterable[str] | None = None, mode: str = "static", *, formatters: Mapping[str | int, str | Callable[[Any], Any]] | Sequence[str | Callable[[Any], Any] | None] | None = None) -> None:
        if mode not in _TABLE_MODES:
            raise ValueError(f"Unknown mode {mode!r}; expected one of {_TABLE_MODES}.")
        self.title = title
        self.columns = list(columns or ["Parameter", "Value", "Unit"])
        if not self.columns:
            raise ValueError("Table requires at least one column.")
        self.data: list[list[str]] = []
        self.mode = mode
        self.formatters = formatters
        self._jupyter = _is_jupyter()
        self._handle = None
        self._finished = False
        self._rendered_lines = 0

    def _normalise_row(self, values: tuple[Any, ...]) -> list[str]:
        row = list(values[0]) if len(values) == 1 and isinstance(values[0], (list, tuple)) else list(values)
        if len(row) != len(self.columns):
            raise ValueError(f"Expected {len(self.columns)} values, received {len(row)}.")
        result = []
        for index, value in enumerate(row):
            formatter = None
            if isinstance(self.formatters, dict):
                formatter = self.formatters.get(self.columns[index], self.formatters.get(index))
            elif self.formatters is not None and index < len(self.formatters):
                formatter = self.formatters[index]
            if formatter is None:
                result.append(str(value))
            elif callable(formatter):
                result.append(str(formatter(value)))
            else:
                result.append(format(value, str(formatter)))
        return result

    def add_row(self, *values: Any) -> None:
        """Add a row and refresh live output."""
        self.data.append(self._normalise_row(values))
        if self.mode in {"live", "dynamic"}:
            self._update()

    def update_row(self, index: int, *values: Any) -> None:
        """Replace a row and refresh live output."""
        if not isinstance(index, int) or isinstance(index, bool):
            raise TypeError("Row index must be an integer.")
        try:
            self.data[index] = self._normalise_row(values)
        except IndexError as error:
            raise IndexError(f"Row index out of range: {index}") from error
        if self.mode in {"live", "dynamic"}:
            self._update()

    def sort(self, column: str | int = 0, *, reverse: bool = False, key: Callable[[str], Any] | None = None) -> "Table":
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
        self.data.sort(key=lambda row: value_key(row[column]), reverse=reverse)
        if self.mode in {"live", "dynamic"}:
            self._update()
        return self

    def to_text(self, width: int | None = None) -> str:
        """Return a terminal-width-aware Unicode table."""
        rows = [self.columns, *self.data]
        widths = [max(len(str(row[index])) for row in rows) for index in range(len(self.columns))]
        available = width or shutil.get_terminal_size((120, 20)).columns
        available = max(20, available)
        minimums = [min(value, max(6, len(str(self.columns[index])))) for index, value in enumerate(widths)]
        while sum(widths) + 3 * len(widths) + 1 > available:
            candidates = [index for index, value in enumerate(widths) if value > minimums[index]]
            if not candidates:
                break
            widest = max(candidates, key=lambda index: widths[index] - minimums[index])
            widths[widest] -= 1

        numeric = []
        for index in range(len(self.columns)):
            try:
                for row in self.data:
                    float(row[index])
            except ValueError:
                numeric.append(False)
            else:
                numeric.append(bool(self.data))

        def border(left: str, middle: str, right: str) -> str:
            return left + middle.join("─" * (value + 2) for value in widths) + right

        def render_row(row: Sequence[str], *, header: bool = False) -> list[str]:
            wrapped = [
                textwrap.wrap(str(value), width=widths[index], break_long_words=True, break_on_hyphens=False) or [""]
                for index, value in enumerate(row)
            ]
            rendered = []
            for line in range(max(map(len, wrapped))):
                cells = []
                for index, values in enumerate(wrapped):
                    value = values[line] if line < len(values) else ""
                    cells.append(value.rjust(widths[index]) if numeric[index] and not header else value.ljust(widths[index]))
                rendered.append("│ " + " │ ".join(cells) + " │")
            return rendered

        lines = [str(self.title), border("┌", "┬", "┐"), *render_row(self.columns, header=True), border("├", "┼", "┤")]
        for index, row in enumerate(self.data):
            lines.extend(render_row(row))
            if index + 1 < len(self.data):
                lines.append(border("├", "┼", "┤"))
        lines.append(border("└", "┴", "┘"))
        return "\n".join(lines) + "\n"

    def to_html(self) -> str:
        """Return a portable HTML table."""
        esc = html.escape
        headings = "".join(f'<th style="padding:6px 10px;text-align:{"left" if i == 0 else "right"};border-bottom:1px solid currentColor">{esc(str(value))}</th>' for i, value in enumerate(self.columns))
        rows = "".join("<tr>" + "".join(f'<td style="padding:5px 10px;text-align:{"left" if i == 0 else "right"}">{esc(str(value))}</td>' for i, value in enumerate(row)) + "</tr>" for row in self.data)
        return f'<div style="display:inline-block;color:currentColor"><strong>{esc(str(self.title))}</strong><table style="border-collapse:collapse;margin-top:6px"><thead><tr>{headings}</tr></thead><tbody>{rows}</tbody></table></div>'

    def _repr_mimebundle_(self, include=None, exclude=None) -> dict[str, str]:
        return {"text/plain": self.to_text(), "text/html": self.to_html()}

    def _update(self) -> None:
        if self._jupyter:
            from IPython.display import HTML, display
            rendered = HTML(self.to_html())
            if self._handle is None:
                self._handle = display(rendered, display_id=True)
            else:
                self._handle.update(rendered)
        elif sys.stdout.isatty():
            if self._rendered_lines:
                sys.stdout.write(f"\033[{self._rendered_lines}F\033[J")
            output = self.to_text()
            sys.stdout.write(output)
            sys.stdout.flush()
            self._rendered_lines = output.count("\n")

    def show(self) -> None:
        """Display the table in the current environment."""
        if self._jupyter:
            from IPython.display import HTML, display
            display(HTML(self.to_html()))
        else:
            print(self.to_text(), end="")

    def finish(self) -> None:
        """Preserve the final state of a live table."""
        if self._finished:
            return
        if self.mode in {"live", "dynamic"} and not self._jupyter and not sys.stdout.isatty():
            print(self.to_text(), end="")
        self._finished = True

    def to_csv(self, path: str | PathLike[str]) -> Path:
        destination = Path(path).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(self.columns)
            writer.writerows(self.data)
        return destination

    def to_latex(self, path: str | PathLike[str] | None = None, *, caption: str | None = None, label: str | None = None) -> str:
        """Return a booktabs LaTeX table and optionally write it to a file."""
        replacements = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}
        def escape(value: object) -> str:
            return "".join(replacements.get(character, character) for character in str(value))
        lines = [r"\begin{table}", r"\centering"]
        if caption is not None:
            lines.append(rf"\caption{{{escape(caption)}}}")
        if label is not None:
            lines.append(rf"\label{{{escape(label)}}}")
        row_end = " " + "\\" * 2
        lines.extend([rf"\begin{{tabular}}{{{'l' + 'r' * (len(self.columns) - 1)}}}", r"\toprule", " & ".join(map(escape, self.columns)) + row_end, r"\midrule"])
        lines.extend(" & ".join(map(escape, row)) + row_end for row in self.data)
        lines.extend([r"\bottomrule", r"\end{tabular}", r"\end{table}"])
        output = "\n".join(lines) + "\n"
        if path is not None:
            destination = Path(path).expanduser()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(output, encoding="utf-8")
        return output
