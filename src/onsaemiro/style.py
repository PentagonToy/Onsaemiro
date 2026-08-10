"""Publication-quality Matplotlib style configuration."""

from contextlib import contextmanager

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


def _compute_scale(fig_width, exponent=_SCALE_EXPONENT):
    raw = (fig_width / _REF_WIDTH) ** exponent
    return float(np.clip(raw, 0.55, 2.2))


def set_style(
    base_fontsize=12.5,
    linewidth=1.2,
    figure_size=(3.5, 2.5),
    subplot=None,
    use_tex=False,
    auto_scale=True,
    scale_exponent=_SCALE_EXPONENT,
    palette="okabe-ito",
):
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


def reset_style():
    """Restore matplotlib defaults."""
    plt.rcdefaults()


def fixed_frame(figure_size=None, subplot=None, **ax_kw):
    """
    Context manager for per-figure size/layout override.
    Falls back to current rcParams when arguments are None.
    """
    fs = figure_size or plt.rcParams["figure.figsize"]
    sp = {**_DEFAULT_SUBPLOT, **(subplot or {})}
    rect = [sp["left"], sp["bottom"],
            sp["right"] - sp["left"], sp["top"] - sp["bottom"]]

    prev = plt.rcParams.get("figure.autolayout", False)
    plt.rcParams["figure.autolayout"] = False

    fig = plt.figure(figsize=fs)
    ax = fig.add_axes(rect, **ax_kw)

    try:
        yield fig, ax
    finally:
        plt.rcParams["figure.autolayout"] = prev
