import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

import onsaemiro as osm


def test_public_api():
    expected = [
        "EPS",
        "Palette",
        "get_palette",
        "build_color_map",
        "build_style_map",
        "register_palette",
        "save_palette",
        "load_palette",
        "set_style",
        "reset_style",
        "journal_preset",
        "set_journal_style",
        "figsize",
        "subplots",
        "export_figure",
        "finalize",
        "style_colorbar",
        "annotate_panels",
        "enable_minor_ticks",
        "apply_grid",
        "Table",
        "Progress",
        "track",
        "sleep",
        "echo",
        "rule",
        "info",
    ]

    missing = [name for name in expected if not hasattr(osm, name)]

    assert not missing
    assert not hasattr(osm, "fixed_frame")
    assert not hasattr(osm, "TableMaker")
    assert not hasattr(osm, "ProgressBar")


def test_plotting_api():
    osm.set_style()

    palette = osm.get_palette()

    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], color=palette[0])

    osm.finalize(ax)
    osm.enable_minor_ticks(ax)
    osm.apply_grid(ax)
    osm.annotate_panels([ax])

    plt.close(fig)


def test_table_api():
    table = osm.Table(
        title="Test",
        columns=["Name", "Value"],
        mode="static",
    )

    table.add_row("alpha", 1)

    assert table.data == [["alpha", "1"]]


def test_progress_api():
    progress = osm.Progress(total=2, desc="Test")

    progress.update()
    progress.update()
    progress.finish()

    assert progress.n == 2
