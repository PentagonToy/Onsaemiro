import json

import pytest

import onsaemiro as osm


def test_build_color_map_preserves_first_unique_label_order():
    mapping = osm.build_color_map(["alpha", "alpha", "beta"])
    palette = osm.get_palette()
    assert mapping == {"alpha": palette[0], "beta": palette[1]}


@pytest.mark.parametrize("value", [0, -1, 1.5, True])
def test_palette_size_must_be_a_positive_integer(value):
    with pytest.raises(ValueError, match="positive integer"):
        osm.get_palette(n=value)


def test_custom_palette_round_trip(tmp_path):
    osm.register_palette(
        "laboratory",
        {"cold": "#123456", "hot": "#abcdef"},
        overwrite=True,
    )
    path = osm.save_palette("laboratory", tmp_path / "palette.json")
    assert json.loads(path.read_text())["name"] == "laboratory"

    restored = osm.load_palette(
        path,
        name="laboratory-copy",
        overwrite=True,
    )
    assert restored["cold"] == "#123456"
    assert restored["hot"] == "#abcdef"

