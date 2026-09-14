import pytest

import onsaemiro as osm


def test_track_accepts_generators_with_explicit_total(capsys):
    values = list(osm.track((value for value in range(3)), total=3))
    assert values == [0, 1, 2]
    assert "3/3" in capsys.readouterr().out


def test_zero_total_is_complete(capsys):
    progress = osm.Progress(total=0)
    progress.finish()
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
        osm.Progress(**kwargs)


def test_finished_progress_cannot_be_updated(capsys):
    progress = osm.Progress(total=1)
    progress.finish()
    capsys.readouterr()
    with pytest.raises(RuntimeError, match="finished"):
        progress.update()


def test_progress_metrics_and_mimebundle():
    progress = osm.Progress(total=2)
    progress.set(loss="0.12")
    bundle = progress._repr_mimebundle_()
    assert "loss=0.12" in bundle["text/plain"]
    assert "loss" in bundle["text/html"]


def test_progress_metrics_respect_refresh_interval(monkeypatch):
    progress = osm.Progress(total=2, mininterval=999.0)
    refreshes = []
    monkeypatch.setattr(
        progress,
        "_refresh",
        lambda *, force=False: refreshes.append(force),
    )

    progress.set(loss="0.12")

    assert refreshes == [False]


def test_progress_context_finishes(capsys):
    with osm.Progress(total=1) as progress:
        progress.update()
    assert progress._finished
    assert "1/1" in capsys.readouterr().out
