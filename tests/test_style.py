from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

import onsaemiro as osm


def test_default_style_uses_science_single_column():
    osm.set_style()
    assert tuple(plt.rcParams["figure.figsize"]) == osm.figsize("science", "single")
    osm.reset_style()


def test_subplots_creates_single_axes():
    fig, ax = osm.subplots(figsize=(4, 3))
    ax.plot([0, 1], [0, 1])
    assert fig.axes == [ax]
    plt.close(fig)


def test_subplots_supports_gridspec():
    fig, axes = osm.subplots(
        nrows=2,
        ncols=2,
        gridspec_kw={"width_ratios": [2, 1]},
    )
    assert axes.shape == (2, 2)
    assert len(fig.axes) == 4
    plt.close(fig)


def test_subplots_accepts_width_shortcut():
    fig, axes = osm.subplots(1, 2, widths=[2, 1])
    assert len(axes) == 2
    assert axes[0].get_position().width > axes[1].get_position().width
    plt.close(fig)


def test_subplots_supports_constrained_layout():
    fig, axes = osm.subplots(
        ncols=2,
        layout="constrained",
    )
    assert len(axes) == 2
    assert fig.get_constrained_layout()
    plt.close(fig)


def test_subplots_forwards_shared_axis_configuration():
    fig, axes = osm.subplots(1, 2, sharex=True, sharey="all")

    assert axes[0].get_shared_x_axes().joined(axes[0], axes[1])
    assert axes[0].get_shared_y_axes().joined(axes[0], axes[1])
    plt.close(fig)


@pytest.mark.parametrize("journal", ["nature", "science", "ieee", "aps"])
def test_journal_presets_apply(journal):
    options = osm.set_journal_style(journal)
    assert tuple(plt.rcParams["figure.figsize"]) == options["figure_size"]
    osm.reset_style()


def test_export_figure_supports_multiple_formats(tmp_path):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])
    outputs = osm.export_figure(fig, tmp_path / "figure", formats=("png", "pdf", "svg"))
    assert outputs == tuple(Path(tmp_path / f"figure.{suffix}") for suffix in ("png", "pdf", "svg"))
    assert all(output.stat().st_size > 0 for output in outputs)
    plt.close(fig)


def test_science_size_and_journal_subplots():
    assert osm.figsize("science") == (2.24, 2.20)
    fig, _ = osm.subplots(journal="science", column="double")
    assert tuple(fig.get_size_inches()) == (4.76, 3.40)
    plt.close(fig)
