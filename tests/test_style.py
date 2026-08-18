from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pytest

import onsaemiro as osm


def test_fixed_frame_preserves_single_axes_api():
    with osm.fixed_frame(figure_size=(4, 3)) as (fig, ax):
        ax.plot([0, 1], [0, 1])
        assert fig.axes == [ax]
    plt.close(fig)


def test_fixed_frame_supports_gridspec_subplots():
    with osm.fixed_frame(
        nrows=2,
        ncols=2,
        gridspec_kw={"width_ratios": [2, 1]},
    ) as (fig, axes):
        assert axes.shape == (2, 2)
        assert len(fig.axes) == 4
    plt.close(fig)


def test_fixed_frame_supports_constrained_layout():
    with osm.fixed_frame(
        ncols=2,
        layout="constrained",
    ) as (fig, axes):
        assert len(axes) == 2
        assert fig.get_constrained_layout()
    plt.close(fig)


@pytest.mark.parametrize("journal", ["nature", "science", "ieee", "aps"])
def test_journal_presets_apply(journal):
    options = osm.set_journal_style(journal)
    assert tuple(plt.rcParams["figure.figsize"]) == options["figure_size"]
    osm.reset_style()


@pytest.mark.parametrize("suffix", [".png", ".pdf", ".svg"])
def test_export_figure_supports_common_backends(tmp_path, suffix):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [1, 0])
    output = osm.export_figure(fig, tmp_path / f"figure{suffix}")
    assert output == Path(tmp_path / f"figure{suffix}")
    assert output.stat().st_size > 0
    plt.close(fig)

