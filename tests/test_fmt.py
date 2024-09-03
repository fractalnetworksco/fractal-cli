import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fractal.cli import fmt
from fractal.cli.fmt import Table
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


def test_pretty_link_link_domain_return():
    link_obj = {"default": {"domain": "example.com"}}
    link_domain = fmt._pretty_link(link_obj)
    assert link_domain == "https://example.com"


def test_pretty_link_keyerror():
    dic = {"Dic": "Will Fail"}
    with pytest.raises(Exception) as e:
        fmt._pretty_link(dic)
    assert "Failed to pretty print link domain" in str(e.value)


def test_json_to_table_if_given_dictionary_wrap_it():
    title = "Test Title"
    data_dict = {"key": "value"}
    table = fmt.json_to_table(title=title, data=data_dict)
    # Table class requires list so if our final table is of class Table, then data successfully turned into list
    assert isinstance(data_dict, dict) and isinstance(table, Table)


def test_json_to_table_add_column():
    title = "Test Title"
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    table = fmt.json_to_table(title=title, data=data)
    # Number of columns in final table matches the number of keys
    assert len(table.columns) == len(data)


def test_json_to_table_data_contains_links():
    title = "Test Title"
    data = [{"links": {"default": {"domain": "example.com"}}}]
    table = fmt.json_to_table(title=title, data=data)
    # Key correctly matched with links and _pretty_link returned link as expected
    assert any("https://example.com" in column._cells for column in table.columns)


def test_json_to_table_render_health_data_contains_health():
    title = "Test Title"
    data = [{"health": "green"}]
    table = fmt.json_to_table(title=title, data=data)
    # We don't need to check for bold green since if it wasn't there, it would fail our renderhealth test
    assert str(table.columns[0]._cells[0]) == "green"


def test_json_to_table_data_contains_size():
    title = "Test Title"
    size = 1024
    data = [{"size": size}]
    table = fmt.json_to_table(title=title, data=data)
    # Size correctly converted and returned
    assert any("1.0 KiB" in column._cells for column in table.columns)


def test_json_to_table_exclude_list_continues_past_key():
    title = "Test Title"
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    exclude_list = ["key2"]
    table = fmt.json_to_table(title=title, data=data, exclude=exclude_list)
    # If false, key2 was successfully excluded
    assert any("value2" in column._cells for column in table.columns) == False


def test_print_json_to_table():
    title = "Test Title"
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    with patch("fractal.cli.fmt.Console.print") as mock_print:
        fmt.print_json_to_table(title=title, data=data)
        mock_print.assert_called_once()


def test_print_json_with_indent():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    indent = 4
    with patch("fractal.cli.fmt.json.dumps") as mock_dump:
        fmt.print_json(data=data, indent=indent)
        mock_dump.assert_called_once_with(data, indent=indent, default=str)


def test_print_json_without_indent():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    with patch("fractal.cli.fmt.json.dumps") as mock_dump:
        fmt.print_json(data=data, indent=0)
        mock_dump.assert_called_once_with(data, default=str)


def test_display_data_format_is_json():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    with patch("fractal.cli.fmt.print_json") as mock_print_json:
        fmt.display_data(data=data, format="json")
        mock_print_json.assert_called_once_with(data)


def test_display_data_format_is_table():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    title = "Test title"
    exclude_list = ["key2"]
    with patch("fractal.cli.fmt.print_json_to_table") as mock_print_json_to_table:
        fmt.display_data(data=data, title=title, exclude=exclude_list)
        mock_print_json_to_table.assert_called_once_with(title, data, exclude_list)


def test_display_data_format_is_unsupported_display():
    data = {"key1": "value1", "key2": "value2", "key3": "value3"}
    title = "Test title"
    exclude_list = ["key2"]
    with patch("fractal.cli.fmt.print_json_to_table") as mock_print_json_to_table:
        fmt.display_data(data=data, title=title, format="invalid", exclude=exclude_list)
        mock_print_json_to_table.assert_called_once_with(title, data, exclude_list)
