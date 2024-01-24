import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import yaml
from asgiref.sync import async_to_sync
from fractal.cli import FRACTAL_DATA_DIR
from fractal.cli.controllers.auth import (
    AuthController,
    LoginError,
    MatrixLoginError,
    WhoamiError,
)
from fractal.cli.utils import read_user_data

# TODO: figure out how to enter command line args automatically


def test_authcontroller_login_no_access_token(mock_getpass):
    """
    Tests that if you do not pass an access token, the controller will login with a
    password and call _login_with_password()
    """
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # patch the _login_with_with_access_token() function to verify it was not called
    with patch(
        "fractal.cli.controllers.auth.AuthController._login_with_access_token",
        new_callable=MagicMock(),
    ) as mock_login_with_access_token:
        auth_cntrl.login(matrix_id, homeserver_url="http://localhost:8008")

    # verify that _login_with_access_token() was not called
    mock_login_with_access_token.assert_not_called()

    # verify that after the login, the fractal data directory exists as well as the
    # associated yaml file
    assert os.path.exists(FRACTAL_DATA_DIR)
    assert os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")

    # read in the data from the file created by the login function
    data, _ = read_user_data(auth_cntrl.TOKEN_FILE)

    # verify that data in the file matches what was created locally
    assert "access_token" in data
    assert data["homeserver_url"] == homeserver_url
    assert data["matrix_id"] == matrix_id


def test_authcontroller_login_with_access_token():
    """
    Tests that if an access token is passed to the function, _login_with_access_token()
    is called instead of _login_with_password().
    """
    auth_cntrl = AuthController()

    homeserver_url = "http://localhost:8008"
    matrix_id = "@admin:localhost"

    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        _, access_token = async_to_sync(auth_cntrl._login_with_password)(
            matrix_id, homeserver_url=homeserver_url
        )

    print(access_token)

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

    # read in the data from the file created by the login function
    data, _ = read_user_data(auth_cntrl.TOKEN_FILE)

    # verify that data in the file matches what was created locally
    assert data["access_token"] == access_token
    assert data["homeserver_url"] == homeserver_url
    assert data["matrix_id"] == matrix_id


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
        auth_cntrl.login("@admin:localhost", access_token=access_token)

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


def test_authcontroller_whoami_filenotfound_not_logged_in():
    """
    Tests that an exception is raised if you are not logged in and make an attempt to
    get information about a logged in user.
    """

    auth_cntrl = AuthController()

    with pytest.raises(SystemExit):
        auth_cntrl.whoami()


def test_authcontroller_whoami_first_keyerror_not_logged_in():
    """
    Tests that an exception is raised if you are not logged in and make an attempt to
    get information about a logged in user.
    """

    auth_cntrl = AuthController()

    with patch(
        "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
    ) as mock_reader:
        mock_reader.side_effect = KeyError()
        with pytest.raises(SystemExit):
            auth_cntrl.whoami()


def test_authcontroller_whoami_keyerror_not_logged_in():
    """
    Tests that an exception is raised if you are not logged in and make an attempt to
    get information about a logged in user.
    """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

    with pytest.raises(SystemExit):
        with patch(
            "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
        ) as mock_reader:
            mock_reader.return_value = [{"homeserver_url": "test"}, {}]
            auth_cntrl.whoami()


def test_authcontroller_whoami_no_errors():
    """
    FIXME: figure out how to mock print
    """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

    #! with patch('builtins.print', new_callable=MagicMock()) as mock_print:
    #! mock_print.assert_called_with(f'You are logged in as {matrix_id} on {homeserver_url}')
    auth_cntrl.whoami()


def test_authcontroller_logout_filenotfound():
    """ """
    auth_cntrl = AuthController()

    auth_cntrl.logout()


def test_authcontroller_logout_keyerror():
    """ """
    auth_cntrl = AuthController()

    with patch(
        "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
    ) as mock_reader:
        with pytest.raises(KeyError):
            mock_reader.return_value = [{"access_token": "test"}, {}]
            auth_cntrl.logout()


def test_authcontroller_logout_confirm_file_deletion():
    """
    Tests that the file containing the user information is deleted upon logging out.
    """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

    assert os.path.exists(FRACTAL_DATA_DIR)
    assert os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")

    auth_cntrl.logout()

    assert not os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")


async def test_authcontroller_login_with_access_token_whoami_error():
    """
    Tests that an exception is raised if a WhoamiError is returned from
    the whoami function
    """

    auth_cntrl = AuthController()

    homeserver_url = "http://localhost:8008"

    with patch(
        "fractal.matrix.async_client.FractalAsyncClient.whoami", new_awaitable=MagicMock()
    ) as mock_whoami:
        mock_whoami.return_value = WhoamiError(message="test_message")
        with pytest.raises(MatrixLoginError) as e:
            await auth_cntrl._login_with_access_token(
                access_token="test_token", homeserver_url=homeserver_url
            )

        assert str(e.value) == "test_message"


async def test_authcontroller_login_with_access_token_no_error():
    """ """

    auth_cntrl = AuthController()

    homeserver_url = "http://localhost:8008"
    matrix_id = "@admin:localhost"
    access_token = "syt_YWRtaW4_QIynvqjNtGjFwtAqnCEW_17qHVu"

    (
        returned_matrix_id,
        returned_homeserver_url,
        returned_access_token,
    ) = await auth_cntrl._login_with_access_token(
        access_token=access_token, homeserver_url=homeserver_url
    )

    assert returned_access_token == access_token
    assert returned_homeserver_url == homeserver_url
    assert returned_matrix_id == matrix_id


async def test_authcontroller_login_with_password_no_password_no_homeserver():
    """ """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    with patch(
        "fractal.cli.controllers.auth.get_homeserver_for_matrix_id", new_awaitable=AsyncMock()
    ) as mock_get_homeserver:
        mock_get_homeserver.return_value = homeserver_url
        with patch(
            "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
        ) as mock_password_prompt:
            mock_password_prompt.return_value = "admin"
            (
                returned_homeserver_url,
                returned_access_token,
            ) = await auth_cntrl._login_with_password(matrix_id=matrix_id)

    mock_get_homeserver.assert_awaited_once()
    mock_password_prompt.assert_called_once()

    assert returned_homeserver_url == homeserver_url


async def test_authcontroller_login_with_password_loginerror():
    """ """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    with patch('fractal.cli.controllers.auth.get_homeserver_for_matrix_id', new_awaitable=AsyncMock()) as mock_get_homeserver:
        with patch('fractal.cli.controllers.auth.prompt_matrix_password', new_callable=MagicMock()) as mock_password_prompt:
            with patch(
                "fractal.matrix.async_client.FractalAsyncClient.login", new_awaitable=MagicMock()
            ) as mock_login:
                mock_login.return_value = LoginError(message="test error message")

                with pytest.raises(MatrixLoginError) as e:
                    returned_homeserer_url, returned_access_token = await auth_cntrl._login_with_password(
                        matrix_id=matrix_id, password="admin", homeserver_url=homeserver_url
                    )

    assert str(e.value) == "test error message"
    mock_get_homeserver.assert_not_called()
    mock_password_prompt.assert_not_called()

async def test_authcontroller_login_invalid_password():
    """
    """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    with pytest.raises(MatrixLoginError) as e:
        returned_homeserer_url, returned_access_token = await auth_cntrl._login_with_password(
            matrix_id=matrix_id, password="wrong_password", homeserver_url=homeserver_url
        )

    assert str(e.value) == "Invalid username or password"



async def test_authcontroller_login_with_password_no_error():
    """
    """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    returned_access_token = "test_access_token"

    returned_homeserer_url, returned_access_token = await auth_cntrl._login_with_password(
        matrix_id=matrix_id, password="admin", homeserver_url=homeserver_url
    )

    assert returned_access_token != "test_access_token"
    assert returned_homeserer_url == homeserver_url
    
def test_authcontroller_show_keyerror():
    """
    """

    auth_cntrl = AuthController()
    key = "access_token"

    assert not os.path.exists(FRACTAL_DATA_DIR)

    with pytest.raises(SystemExit):
        auth_cntrl.show(key)


def test_authcontroller_show_filenotfound():
    """
    """ 

    auth_cntrl = AuthController()
    key = "access_token"

    with patch(
        "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
    ) as mock_reader:
        mock_reader.side_effect = KeyError()
        with pytest.raises(SystemExit):
            auth_cntrl.show(key)

def test_authcontroller_show_key_cases():
    """
    """
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id=matrix_id)

    assert os.path.exists(FRACTAL_DATA_DIR)

    key = "access_token"
    with patch('fractal.cli.controllers.auth.print', new=MagicMock()) as mock_print:
        auth_cntrl.show(key)

    mock_print.assert_called_once()


    key = "homeserver_url"
    with patch('fractal.cli.controllers.auth.print', new=MagicMock()) as mock_print:
        auth_cntrl.show(key)

    mock_print.assert_called_once_with(homeserver_url)

    key = "matrix_id"
    with patch('fractal.cli.controllers.auth.print', new=MagicMock()) as mock_print:
        auth_cntrl.show(key)

    mock_print.assert_called_once_with(matrix_id)


    key = "invalid_key"
    with patch('fractal.cli.controllers.auth.print', new=MagicMock()) as mock_print:
        auth_cntrl.show(key)

    mock_print.assert_not_called()
