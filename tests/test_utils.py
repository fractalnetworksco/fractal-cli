import os
from unittest.mock import patch
from uuid import uuid4

import pytest
import yaml
from fractal.cli import FRACTAL_DATA_DIR
from fractal.cli.utils import InvalidMatrixIdException, read_user_data, write_user_data


def test_utils_write_yamlerror(test_yaml_dict):
    """
    Tests that an exception is raised if yaml.dumps throws a yaml.YAMLError
    """

    file_name = str(uuid4())

    with patch("fractal.cli.utils.yaml.dump") as mock_dump:
        with pytest.raises(yaml.YAMLError) as e:
            mock_dump.side_effect = yaml.YAMLError

            write_user_data(test_yaml_dict, file_name)


def test_utils_write_verify_write(test_yaml_dict):
    """ """

    file_name = str(uuid4())

    assert not os.path.exists(FRACTAL_DATA_DIR)
    write_user_data(test_yaml_dict, file_name)
    assert os.path.exists(f"{FRACTAL_DATA_DIR}/{file_name}")

    file_path = os.path.join(FRACTAL_DATA_DIR, file_name)

    #! verify that the data was written
    #? ============

    try:
        with open(file_path, "r") as file:
            user_data = file.read()
    except FileNotFoundError as error:
        raise error

    try:
        user_data = yaml.safe_load(user_data)
    except yaml.YAMLError as error:
        raise error

    #? ============