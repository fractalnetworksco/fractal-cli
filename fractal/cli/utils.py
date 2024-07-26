import json
import os
import re
from getpass import getpass
from os import makedirs
from typing import Any, Dict, Tuple

import appdirs
import yaml

data_dir = appdirs.user_data_dir("fractal")


class InvalidMatrixIdException(Exception):
    pass


def write_user_data(data: Dict[str, Any], filename: str, format: str = "yaml") -> str:
    """
    Write data to yaml file <filename> in user's appdir (ie ~/.local/share/fractal)
    """
    makedirs(data_dir, exist_ok=True)

    match format:
        case "yaml":
            data_to_write = yaml.dump(data)
        case "json":
            data_to_write = json.dumps(data)
        case _:
            raise ValueError(f"Invalid format: {format}")

    data_file = os.path.join(data_dir, filename)
    with open(data_file, "w") as file:
        file.write(data_to_write)

    return data_file


def read_user_data(filename: str) -> Tuple[Dict[str, Any], str]:
    """
    Reads data from <filename> in user's appdir (ie ~/.local/share/fractal)

    TODO: Support multiple file types. Right now this only supports yaml files.

    Returns:
        (user_data, data_file_path): Data in file (as dict), path to file (str).
    """
    data_file_path = os.path.join(data_dir, filename)

    try:
        with open(data_file_path, "r") as file:
            user_data = file.read()
    except FileNotFoundError as error:
        raise error

    try:
        user_data = yaml.safe_load(user_data)
    except yaml.YAMLError as error:
        raise error

    return user_data, data_file_path
