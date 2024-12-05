import json

from rich.console import Console
from rich.table import Table
from rich.text import Text

KEYS_TO_EXCLUDE = [
    "deleted",
    "date_created",
    "date_modified",
    "owner",
    "last_seen_timestamp",
    "last_state_change_timestamp",
    "reschedule_to_device",
    "config",
    "current_state",
    "image",
    "icon",
    "app",
    "device",
    "locked",
    "geometry",
    "pinned",
]


def _green(text: str) -> Text:
    return Text.assemble((text, "bold green"))


def _red(text: str) -> Text:
    return Text.assemble((text, "bold blink red"))


def _yellow(text: str) -> Text:
    return Text.assemble((text, "bold yellow"))


def pretty_bytes(num: float, suffix: str = "B") -> str:
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}{suffix}"


def render_health(status: str) -> Text:
    match status:
        case "green":
            return _green(status)
        case "yellow":
            return _yellow(status)
        case "red":
            return _red(status)
        case _:
            raise Exception(f"Got unsupported health color when rendering health: {status}")


def _pretty_link(link_obj: dict) -> str:
    """
    Extracts link domain from link object

    Returns:
        link domain
    """
    try:
        link_domain = f"https://{link_obj['default']['domain']}"
        return link_domain
    except KeyError as e:
        raise Exception(f"Failed to pretty print link domain: {e}")


def json_to_table(title: str, data: list[dict] | dict, exclude: list[str] = []) -> Table:
    """
    Pretty prints given data using a table.
    """
    table = Table(title=title)
    exclude_list = KEYS_TO_EXCLUDE + exclude

    # if given dictionary wrap it in list
    if isinstance(data, dict):
        data = [data]

    [
        table.add_column(key, justify="left", overflow="fold")
        for key in data[0].keys()
        if key not in exclude_list
    ]
    for row in data:
        col = []
        for key in row.keys():
            if key in exclude_list:
                continue

            match key:
                case "links":
                    link_domain = _pretty_link(row[key])
                    col.append(link_domain)
                case "health":
                    col.append(render_health(row[key]))
                case "size":
                    col.append(pretty_bytes(float(row[key])))
                case _:
                    col.append(str(row[key]))

        table.add_row(*col, end_section=True)
    return table


def print_json_to_table(title: str, data: list[dict] | dict, exclude: list[str] = []) -> None:
    """
    Pretty prints given data using a table.
    """
    table = json_to_table(title, data, exclude)
    c = Console()
    c.print(table)


def print_json(data: list[dict] | dict, indent: int = 4) -> None:
    """
    Prints data as JSON (human readable).
    """
    if indent:
        print(json.dumps(data, indent=indent, default=str))
    else:
        print(json.dumps(data, default=str))


def display_data(
    data: list[dict] | dict,
    title: str = "",
    format: str = "table",
    exclude: list[str] = [],
):
    """
    Displays provided data with the specified format
    """
    if format == "json":
        print_json(data)
    elif format == "table":
        print_json_to_table(title, data, exclude)
    else:
        print(f"Got unsupport display format: {format}. Defaulting to pretty print.")
        print_json_to_table(title, data, exclude)
