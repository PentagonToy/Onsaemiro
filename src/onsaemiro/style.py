"""Publication-quality Matplotlib style configuration."""

from contextlib import contextmanager
from collections.abc import Iterator, Mapping
from os import PathLike
from pathlib import Path
from typing import Any, cast

import numpy as np
import matplotlib.pyplot as plt

from .palette import get_palette


_REF_WIDTH = 6.0


_SCALE_EXPONENT = 0.5


_DEFAULT_SUBPLOT = {
    "left":   0.18,
    "bottom": 0.20,
    "right":  0.95,
    "top":    0.93,
}


_JOURNAL_PRESETS = {
    "nature": {
        "single": (3.50, 2.65),
        "double": (7.20, 4.80),
        "base_fontsize": 10.0,
        "linewidth": 1.0,
    },
    "science": {
        "single": (3.40, 2.55),
        "double": (7.00, 4.70),
        "base_fontsize": 9.5,
        "linewidth": 1.0,
    },
    "ieee": {
        "single": (3.50, 2.55),
        "double": (7.16, 4.80),
        "base_fontsize": 9.0,
        "linewidth": 0.9,
    },
    "aps": {
        "single": (3.40, 2.60),
        "double": (7.00, 4.80),
        "base_fontsize": 10.0,
        "linewidth": 1.0,
    },
}


def _compute_scale(fig_width: float, exponent: float = _SCALE_EXPONENT) -> float:
    raw = (fig_width / _REF_WIDTH) ** exponent
    return float(np.clip(raw, 0.55, 2.2))


def set_style(
    base_fontsize: float = 12.5,
    linewidth: float = 1.2,
    figure_size: tuple[float, float] = (3.5, 2.5),
    subplot: Mapping[str, float] | None = None,
    use_tex: bool = False,
    auto_scale: bool = True,
    scale_exponent: float = _SCALE_EXPONENT,
    palette: str = "okabe-ito",
) -> None:
    """
    One-call global setup.

    figure_size is the primary parameter.  Subplot fractions are
    fixed so the inner axes box occupies the same region regardless
    of tick-label content.  autolayout is OFF; savefig bbox="tight"
    acts as a safety net on export.
    """
    sp = {**_DEFAULT_SUBPLOT, **(subplot or {})}
    s = _compute_scale(figure_size[0], scale_exponent) if auto_scale else 1.0

    fs    = base_fontsize * s
    lw    = linewidth * s
    elw   = lw * 0.6
    ms    = 9.0 * s
    major = 5.0 * s
    minor = 3.0 * s

    plt.rcParams.update({
        # ── Font ──
        "font.family":           "serif",
        "font.serif":            ["Times New Roman", "Times", "DejaVu Serif"],
        "text.latex.preamble":   r"\usepackage{newtxtext,newtxmath}",
        "font.size":             fs - 2 * s,
        "axes.titlesize":        fs,
        "axes.labelsize":        fs - 1 * s,
        "xtick.labelsize":       fs - 2 * s,
        "ytick.labelsize":       fs - 2 * s,

        # ── Figure ──
        "figure.figsize":        figure_size,
        "figure.dpi":            150,
        "figure.autolayout":     False,
        "savefig.dpi":           300,
        "savefig.bbox":          "tight",
        "pdf.fonttype":          42,
        "ps.fonttype":           42,

        # ── Subplot position (fixed fractions) ──
        "figure.subplot.left":   sp["left"],
        "figure.subplot.bottom": sp["bottom"],
        "figure.subplot.right":  sp["right"],
        "figure.subplot.top":    sp["top"],

        # ── Axes ──
        "axes.linewidth":        lw,
        "axes.spines.top":       True,
        "axes.spines.right":     True,
        "axes.labelpad":         6.0 * s,
        "axes.xmargin":          0.03,
        "axes.ymargin":          0.03,
        "axes.titlepad":         13.0 * s,
        "axes.formatter.useoffset":    False,
        "axes.formatter.use_mathtext": True,
        "axes.formatter.limits":       [-4, 5],

        # ── Ticks ──
        "xtick.direction":       "out",
        "ytick.direction":       "out",
        "xtick.major.size":      major,
        "ytick.major.size":      major,
        "xtick.minor.size":      minor,
        "ytick.minor.size":      minor,
        "xtick.major.width":     lw * 0.8,
        "ytick.major.width":     lw * 0.8,
        "xtick.minor.visible":   False,
        "ytick.minor.visible":   False,
        "xtick.major.pad":       4.0 * s,
        "ytick.major.pad":       4.0 * s,

        # ── Lines & Markers ──
        "lines.linewidth":       lw,
        "lines.markersize":      ms,
        "lines.markeredgewidth": elw,
        "lines.markeredgecolor": "black",

        # ── Patches & Scatter ──
        "scatter.edgecolors":    "black",
        "patch.edgecolor":       "black",
        "patch.linewidth":       elw,
        "patch.force_edgecolor": True,

        # ── Legend ──
        "legend.fontsize":       fs - 4 * s,
        "legend.frameon":        True,
        "legend.framealpha":     1.0,
        "legend.facecolor":      "white",
        "legend.edgecolor":      "black",
        "legend.fancybox":       False,
        "legend.handlelength":   1.5,

        # ── Text & Math ──
        "text.usetex":           use_tex,
        "mathtext.fontset":      "stix",

        # ── Grid ──
        "axes.grid":             False,
        "grid.linestyle":        "--",
        "grid.color":            "black",
        "grid.alpha":            0.8,
        "grid.linewidth":        lw * 0.67,
        "axes.axisbelow":        True,
    })

    plt.rcParams["axes.prop_cycle"] = plt.cycler(
        color=list(get_palette(palette))
    )


def reset_style() -> None:
    """Restore matplotlib defaults."""
    plt.rcdefaults()


def journal_preset(name: str, column: str = "single") -> dict[str, Any]:
    """Return a copy of a journal-oriented style preset.

    Presets are practical starting points rather than publisher guarantees;
    authors should still check the current journal instructions.
    """
    key = str(name).lower()
    column_key = str(column).lower()

    if key not in _JOURNAL_PRESETS:
        raise ValueError(
            f"Unknown journal {name!r}; expected one of "
            f"{tuple(_JOURNAL_PRESETS)}."
        )
    if column_key not in {"single", "double"}:
        raise ValueError("column must be 'single' or 'double'.")

    source = _JOURNAL_PRESETS[key]
    figure_size = cast(tuple[float, float], source[column_key])
    return {
        "figure_size": figure_size,
        "base_fontsize": source["base_fontsize"],
        "linewidth": source["linewidth"],
    }


def set_journal_style(
    name: str,
    column: str = "single",
    **overrides: Any,
) -> dict[str, Any]:
    """Apply a journal preset, with optional :func:`set_style` overrides."""
    options = journal_preset(name, column=column)
    options.update(overrides)
    set_style(**options)
    return options


@contextmanager
def fixed_frame(
    figure_size: tuple[float, float] | None = None,
    subplot: Mapping[str, float] | None = None,
    *,
    nrows: int = 1,
    ncols: int = 1,
    gridspec_kw: Mapping[str, Any] | None = None,
    squeeze: bool = True,
    layout: str | None = None,
    **ax_kw: Any,
) -> Iterator[tuple[Any, Any]]:
    """
    Context manager for fixed-frame single or multi-axes figures.

    The original ``with fixed_frame() as (fig, ax)`` form remains unchanged.
    Set ``nrows`` or ``ncols`` for a subplot array, and use ``gridspec_kw`` for
    relative panel sizes.  ``layout="constrained"`` delegates spacing to
    Matplotlib instead of applying fixed subplot fractions.
    """
    fs = figure_size or plt.rcParams["figure.figsize"]
    sp = {**_DEFAULT_SUBPLOT, **(subplot or {})}
    prev = plt.rcParams.get("figure.autolayout", False)
    plt.rcParams["figure.autolayout"] = False

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=fs,
        gridspec_kw=(None if gridspec_kw is None else dict(gridspec_kw)),
        squeeze=squeeze,
        layout=layout,
        subplot_kw=ax_kw or None,
    )

    if layout not in {"constrained", "compressed"}:
        fig.subplots_adjust(**sp)

    try:
        yield fig, axes
    finally:
        plt.rcParams["figure.autolayout"] = prev


def export_figure(
    fig: Any,
    path: str | PathLike[str],
    *,
    dpi: float = 300,
    transparent: bool = False,
    bbox_inches: str | None = "tight",
    metadata: Mapping[str, Any] | None = None,
    close: bool = False,
    **savefig_kw: Any,
) -> Path:
    """Export a figure with publication-safe vector font settings."""
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)

    options = {
        "dpi": dpi,
        "transparent": transparent,
        "bbox_inches": bbox_inches,
        "metadata": metadata,
        **savefig_kw,
    }

    with plt.rc_context({"pdf.fonttype": 42, "ps.fonttype": 42}):
        fig.savefig(destination, **options)

    if close:
        plt.close(fig)

    return destination
