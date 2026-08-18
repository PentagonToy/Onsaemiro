"""Tests for TableMaker rendering and row insertion functionality."""

import pytest
import onsaemiro as osm


def test_table_maker_add_row_variants():
    """Verify add_row supports positional arguments, lists, and tuples."""
    table = osm.TableMaker(
        title="Thermodynamics & Kinetics Summary",
        columns=["Parameter", "Value", "Unit"],
    )

    # 1. Positional arguments
    table.add_row("Temperature", 400.0, "K")
    table.add_row("Equivalence Ratio", 1.000, "-")

    # 2. Single list
    table.add_row(["Pressure", 101.3, "kPa"])
    table.add_row(["Laminar Flame Speed", 0.3850, "m/s"])

    # 3. Single tuple
    table.add_row(("Density", 1.184, "kg/m^3"))

    # Assertions on internal string representations
    assert len(table.data) == 5
    assert table.data[0] == ["Temperature", "400.0", "K"]
    assert table.data[2] == ["Pressure", "101.3", "kPa"]
    assert table.data[4] == ["Density", "1.184", "kg/m^3"]


def test_table_maker_update_row_variants():
    """Verify update_row replaces rows using supported input forms."""
    table = osm.TableMaker(
        title="Build Status",
        columns=["Component", "Status"],
    )
    table.add_row("SmartRedis", "Pending")
    table.add_row("OpenFOAM", "Pending")

    table.update_row(0, "SmartRedis", "Building")
    table.update_row(1, ["OpenFOAM", "Done"])

    assert table.data == [
        ["SmartRedis", "Building"],
        ["OpenFOAM", "Done"],
    ]


def test_table_maker_update_row_refreshes_live_table(monkeypatch):
    """Verify live tables refresh after an existing row changes."""
    table = osm.TableMaker(
        title="Build Status",
        columns=["Component", "Status"],
        mode="live",
    )
    updates = []

    monkeypatch.setattr(
        table,
        "_update",
        lambda: updates.append(
            tuple(tuple(row) for row in table.data)
        ),
    )

    table.add_row("SmartRedis", "Pending")
    table.update_row(0, "SmartRedis", "Done")

    assert updates == [
        (("SmartRedis", "Pending"),),
        (("SmartRedis", "Done"),),
    ]


def test_table_maker_update_row_rejects_invalid_index():
    """Verify update_row validates row indices."""
    table = osm.TableMaker()
    table.add_row("Temperature", "400", "K")

    with pytest.raises(
        TypeError,
        match="Row index must be an integer",
    ):
        table.update_row(
            "0",
            "Temperature",
            "500",
            "K",
        )

    with pytest.raises(
        IndexError,
        match="Row index out of range: 2",
    ):
        table.update_row(
            2,
            "Temperature",
            "500",
            "K",
        )


def test_table_maker_render_output(capsys):
    """Verify standard text rendering output in console mode."""
    table = osm.TableMaker(
        title="Species Concentration",
        columns=["Species", "Mole Fraction"],
    )
    table.add_row("CH4", 0.0950)
    table.add_row(["O2", 0.1900])

    table.display()
    captured = capsys.readouterr()

    assert "Species Concentration" in captured.out
    assert "CH4" in captured.out
    assert "0.19" in captured.out


def test_invalid_mode():
    """Verify ValueError when passing an unsupported table mode."""
    with pytest.raises(ValueError, match="Unknown mode 'invalid'"):
        osm.TableMaker(mode="invalid")

def test_live_table_suppresses_intermediate_non_tty_output(
    capsys,
):
    """Verify redirected live output emits only the final table."""
    table = osm.TableMaker(
        title="Build Status",
        columns=["Component", "Status"],
        mode="live",
    )

    table.add_row(
        "SmartRedis",
        "Pending",
    )
    table.update_row(
        0,
        "SmartRedis",
        "Building",
    )
    table.update_row(
        0,
        "SmartRedis",
        "Done",
    )

    intermediate = capsys.readouterr()

    assert intermediate.out == ""

    table.close()

    final = capsys.readouterr()

    assert "Build Status" in final.out
    assert "SmartRedis" in final.out
    assert "Done" in final.out
    assert "Pending" not in final.out
    assert "Building" not in final.out
    assert "\033[" not in final.out


def test_live_table_close_is_idempotent(
    capsys,
):
    """Verify closing a live table more than once emits no duplicate."""
    table = osm.TableMaker(
        title="Build Status",
        columns=["Component", "Status"],
        mode="live",
    )
    table.add_row(
        "OpenFOAM",
        "Done",
    )

    table.close()
    first = capsys.readouterr()

    table.close()
    second = capsys.readouterr()

    assert "OpenFOAM" in first.out
    assert second.out == ""


def test_table_rejects_wrong_row_width():
    table = osm.TableMaker(columns=["Name", "Value"])
    with pytest.raises(ValueError, match="Expected 2 values"):
        table.add_row("only-one")


def test_table_format_sort_and_exports(tmp_path):
    table = osm.TableMaker(
        title="Results",
        columns=["Case", "Error"],
        formatters={"Error": ".2f"},
    )
    table.add_row("B", 2.345)
    table.add_row("A", 1.234)
    table.sort("Case")

    assert table.data == [["A", "1.23"], ["B", "2.35"]]

    csv_path = table.to_csv(tmp_path / "results.csv")
    assert csv_path.read_text().splitlines() == [
        "Case,Error",
        "A,1.23",
        "B,2.35",
    ]

    latex = table.to_latex(caption="A & B", label="tab:results")
    assert r"\caption{A \& B}" in latex
    assert r"\toprule" in latex
