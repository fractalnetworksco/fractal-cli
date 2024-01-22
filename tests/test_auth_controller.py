import os
import pytest
from unittest.mock import MagicMock, patch

import yaml
from asgiref.sync import async_to_sync
from fractal.cli import FRACTAL_DATA_DIR
from fractal.cli.controllers.auth import AuthController
from fractal.cli.utils import read_user_data #! use this to read yaml

# TODO: figure out how to enter command line args automatically 


def test_authcontroller_login_no_access_token(mock_getpass):
    """
    Tests that if you do not pass an access token, the controller will login with a
    password and call _login_with_password()
    """
    auth_cntrl = AuthController()

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # patch the _login_with_with_access_token() function to verify it was not called
    with patch(
        "fractal.cli.controllers.auth.AuthController._login_with_access_token",
        new_callable=MagicMock(),
    ) as mock_login_with_access_token:
        auth_cntrl.login("@admin:localhost", homeserver_url="http://localhost:8008")

    # verify that _login_with_access_token() was not called
    mock_login_with_access_token.assert_not_called()


    # verify that after the login, the fractal data directory exists as well as the
    # associated yaml file
    assert os.path.exists(FRACTAL_DATA_DIR)
    assert os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")

    # ! ============== finish this
    data, _ = read_user_data(auth_cntrl.TOKEN_FILE)



def test_authcontroller_login_with_access_token():
    """
    FIXME: use something to enter command line args when asked for a password
    """
    auth_cntrl = AuthController()

    homeserver_url = "http://localhost:8008"
    _, access_token = async_to_sync(auth_cntrl._login_with_password)(
        "@admin:localhost", homeserver_url=homeserver_url
    )

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    with patch(
        "fractal.cli.controllers.auth.AuthController._login_with_password",
        new_callable=MagicMock(),
    ) as mock_login_with_password:
        auth_cntrl.login(
            "@admin:localhost", homeserver_url=homeserver_url, access_token=access_token
        )

    # verify that _login_with_access_token() was not called
    mock_login_with_password.assert_not_called()

    # verify that after the login, the fractal data directory exists as well as the
    # associated yaml file
    assert os.path.exists(FRACTAL_DATA_DIR)
    assert os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")

def test_authcontroller_login_no_homeserver_url():
    """
    Tests that a SystemExit exception is raised if a homeserver is not passed as a
    parameter and _login_with_password() isn't called to supply one.
    """

    auth_cntrl = AuthController()

    access_token = "test token"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # call login without a homeserver_url to raise SystemExit
    with pytest.raises(SystemExit):
        auth_cntrl.login(
            "@admin:localhost", access_token=access_token
        )

    # verify that the fractal data directory is not created
    assert not os.path.exists(FRACTAL_DATA_DIR)

def test_authcontroller_login_invalid_access_token():
    """
    Tests that a SystemExit exception is raised if there is an invalid access token
    passed.
    """

    auth_cntrl = AuthController()

    access_token = "test token"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # call login without a homeserver_url to raise SystemExit
    with pytest.raises(SystemExit):
        auth_cntrl.login(
            "@admin:localhost", homeserver_url="http://localhost:8008", access_token=access_token
        )

    # verify that the fractal data directory is not created
    assert not os.path.exists(FRACTAL_DATA_DIR)

def test_authcontroller_whoami_key_error():
    """
    """