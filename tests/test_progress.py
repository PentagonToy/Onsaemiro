import pytest

import onsaemiro as osm


def test_track_accepts_generators_with_explicit_total(capsys):
    values = list(osm.track((value for value in range(3)), total=3))
    assert values == [0, 1, 2]
    assert "3/3" in capsys.readouterr().out


def test_zero_total_is_complete(capsys):
    with osm.ProgressBar(total=0):
        pass
    assert "100.0%" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"total": -1}, "total"),
        ({"width": 0}, "width"),
        ({"mininterval": -0.1}, "mininterval"),
        ({"smoothing": 2}, "smoothing"),
    ],
)
def test_progress_configuration_validation(kwargs, message):
    with pytest.raises(ValueError, match=message):
        osm.ProgressBar(**kwargs)


def test_closed_progress_cannot_be_updated(capsys):
    progress = osm.ProgressBar(total=1)
    progress.close()
    capsys.readouterr()
    with pytest.raises(RuntimeError, match="closed"):
        progress.update()

