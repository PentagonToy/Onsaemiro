from io import StringIO

import pytest

import onsaemiro as osm


def test_echo_is_plain_when_redirected():
    output = StringIO()
    osm.echo("complete", tone="success", file=output)
    assert output.getvalue() == "complete\n"


def test_echo_rejects_unknown_tone():
    with pytest.raises(ValueError, match="Unknown tone"):
        osm.echo("message", tone="unknown")


def test_rule_uses_requested_width():
    output = StringIO()
    osm.rule("Results", width=24, file=output)
    assert len(output.getvalue().rstrip("\n")) == 24
