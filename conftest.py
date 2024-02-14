import os
from uuid import uuid4
import secrets
import shutil
from unittest.mock import patch, MagicMock
from fractal.cli.controllers.auth import AuthController
from fractal.cli.controllers.registration import RegistrationController

import pytest
from fractal.cli import FRACTAL_DATA_DIR


@pytest.fixture
def mock_getpass():
    with patch("fractal.matrix.utils.getpass", return_value="admin"):
        yield

@pytest.fixture
def test_user_access_token():
    return os.environ['MATRIX_ACCESS_TOKEN']

@pytest.fixture
def test_homeserver_url() -> str:
    return os.environ.get("TEST_HOMESERVER_URL", "http://localhost:8008")

@pytest.fixture
def test_alternate_homeserver_url() -> str:
    return os.environ.get("TEST_HOMESERVER_URL", "http://localhost:8010")

@pytest.fixture(scope="function")
def logged_in_auth_controller(test_homeserver_url):
    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"

    # log the user in patching prompt_matrix_password to use preset password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id=matrix_id, homeserver_url=test_homeserver_url)

    return auth_cntrl

@pytest.fixture(scope="function")
def test_registration_token():
    test_registration_controller = RegistrationController()
    registration_token = test_registration_controller.token("create")

    return registration_token

@pytest.fixture(scope='function')
def test_yaml_dict():
    yaml_info = {
        str(uuid4()) : str(uuid4()),
        str(uuid4()) : str(uuid4()),
        str(uuid4()) : str(uuid4()),
        str(uuid4()) : str(uuid4())
    }

    return yaml_info

@pytest.fixture(autouse=True)
def cleanup():
    yield

    try:
        shutil.rmtree(FRACTAL_DATA_DIR)
    except FileNotFoundError:
        pass
