import os
import shutil
from unittest.mock import patch

import pytest
from fractal.cli import FRACTAL_DATA_DIR


@pytest.fixture
def mock_getpass():
    with patch("fractal.matrix.utils.getpass", return_value="admin"):
        yield


@pytest.fixture
def test_homeserver_url() -> str:
    return os.environ.get("TEST_HOMESERVER_URL", "http://localhost:8008")


@pytest.fixture(autouse=True)
def cleanup():
    yield

    try:
        shutil.rmtree(FRACTAL_DATA_DIR)
    except FileNotFoundError:
        pass
