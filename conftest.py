from unittest.mock import patch

import pytest


@pytest.fixture
def mock_getpass():
    with patch("fractal.matrix.utils.getpass", return_value="admin"):
        yield
