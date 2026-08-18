"""Onsaemiro — publication-quality scientific visualisation and reporting utilities."""

from ._version import __version__, __date__
from .constants import EPS
from .palette import (
    Palette,
    get_palette,
    build_color_map,
    register_palette,
    save_palette,
    load_palette,
)
from .style import (
    set_style,
    reset_style,
    journal_preset,
    set_journal_style,
    fixed_frame,
    export_figure,
)
from .helpers import (
    finalize,
    style_colorbar,
    annotate_panels,
    enable_minor_ticks,
    apply_grid,
)
from .table import TableMaker
from .progress import ProgressBar, track, sleep
from .info import info

__all__ = [
    "EPS",
    "Palette",
    "get_palette",
    "build_color_map",
    "register_palette",
    "save_palette",
    "load_palette",
    "set_style",
    "reset_style",
    "journal_preset",
    "set_journal_style",
    "fixed_frame",
    "export_figure",
    "finalize",
    "style_colorbar",
    "annotate_panels",
    "enable_minor_ticks",
    "apply_grid",
    "TableMaker",
    "ProgressBar",
    "track",
    "sleep",
    "info",
]
