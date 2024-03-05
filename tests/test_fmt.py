import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fractal.cli import fmt
from rich.text import Text


def test_green_return():
    text = "text"
    with patch("fractal.cli.fmt.Text.assemble", new=MagicMock()) as mock_assemble:
        fmt._green(text=text)
    mock_assemble.assert_called_once_with((text, "bold green"))


def test_red_return():
    text = "text"
    with patch("fractal.cli.fmt.Text.assemble", new=MagicMock()) as mock_assemble:
        fmt._red(text=text)
    mock_assemble.assert_called_once_with((text, "bold blink red"))


def test_yellow_return():
    text = "text"
    with patch("fractal.cli.fmt.Text.assemble", new=MagicMock()) as mock_assemble:
        fmt._yellow(text=text)
    mock_assemble.assert_called_once_with((text, "bold yellow"))


def test_pretty_bytes_sample_byte_values():
    assert fmt.pretty_bytes(0) == "0.0 B"
    assert fmt.pretty_bytes(100) == "100.0 B"
    assert fmt.pretty_bytes(1024) == "1.0 KiB"
    assert fmt.pretty_bytes(1048576) == "1.0 MiB"


def test_pretty_bytes_sample_large_byte_value():
    assert fmt.pretty_bytes(1024**8) == "1.0B"


def test_render_health_green_health_status():
    status = "green"
    text = ""
    with patch(
        "fractal.cli.fmt.Text.assemble",
        new=MagicMock(return_value=Text(text, style="bold green")),
    ):
        return_val = fmt.render_health(status)
    assert return_val.style == "bold green"


def test_render_health_yellow_health_status():
    status = "yellow"
    text = ""
    with patch(
        "fractal.cli.fmt.Text.assemble",
        new=MagicMock(return_value=Text(text, style="bold yellow")),
    ):
        return_val = fmt.render_health(status)
    assert return_val.style == "bold yellow"


def test_render_health_red_health_status():
    status = "red"
    text = ""
    with patch(
        "fractal.cli.fmt.Text.assemble",
        new=MagicMock(return_value=Text(text, style="bold blink red")),
    ):
        return_val = fmt.render_health(status)
    assert return_val.style == "bold blink red"


def test_render_health_invalid_health_status():
    status = "blue"
    with pytest.raises(Exception) as e:
        return_val = fmt.render_health(status)
    assert f"Got unsupported health color when rendering health: {status}" in str(e.value)


@pytest.mark.skip("Not finished")
def test_pretty_link_link_domain_return():
    fmt._pretty_link = MagicMock()


def test_pretty_link_keyerror():
    dic = {"Dic": "Will Fail"}
    with pytest.raises(Exception) as e:
        fmt._pretty_link(dic)
    assert "Failed to pretty print link domain" in str(e.value)
