import os
from hashlib import sha256
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from asgiref.sync import async_to_sync
from fractal.cli import FRACTAL_DATA_DIR
from fractal.cli.controllers.auth import (
    AuthController,
    LoginError,
    MatrixLoginError,
    WhoamiError,
)
from fractal.cli.utils import read_user_data
from fractal.matrix.utils import parse_matrix_id


def test_authcontroller_login_no_access_token(mock_getpass, test_homeserver_url):
    """
    Tests that if you do not pass an access token, the controller will login with a
    password and call _login_with_password()
    """
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # patch the _login_with_with_access_token() function to verify it was not called
    with patch(
        "fractal.cli.controllers.auth.AuthController._login_with_access_token",
        new_callable=MagicMock(),
    ) as mock_login_with_access_token:
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

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


def test_authcontroller_login_with_access_token(test_homeserver_url):
    """
    Tests that if an access token is passed to the function, _login_with_access_token()
    is called instead of _login_with_password().
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    homeserver_url = test_homeserver_url
    matrix_id = "@admin:localhost"

    # patch prompt_matrix_password to automatically enter password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        _, access_token = async_to_sync(auth_cntrl._login_with_password)(
            matrix_id, homeserver_url=homeserver_url
        )

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # patch logn_with_password to assert it wasn't called
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

    # create an AuthController object and access token
    auth_cntrl = AuthController()
    access_token = "test token"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # call login without a homeserver_url to raise SystemExit
    with pytest.raises(SystemExit):
        auth_cntrl.login("@admin:localhost", access_token=access_token)

    # verify that the fractal data directory is not created
    assert not os.path.exists(FRACTAL_DATA_DIR)


def test_authcontroller_login_invalid_access_token(test_homeserver_url):
    """
    Tests that a SystemExit exception is raised if there is an invalid access token
    passed.
    """

    # create an AuthController object and test token variable
    auth_cntrl = AuthController()
    access_token = "test token"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # call login without a homeserver_url to raise SystemExit
    with pytest.raises(SystemExit):
        auth_cntrl.login(
            "@admin:localhost", homeserver_url=test_homeserver_url, access_token=access_token
        )

    # verify that the fractal data directory is not created
    assert not os.path.exists(FRACTAL_DATA_DIR)


def test_authcontroller_whoami_filenotfound_not_logged_in():
    """
    Tests that an exception is raised if you are not logged in and make an attempt to
    get information about a logged in user.
    """

    # create an AuthController object
    auth_cntrl = AuthController()

    # call whoami without logging in to raise an exception
    with pytest.raises(SystemExit):
        auth_cntrl.whoami()


def test_authcontroller_whoami_first_keyerror_not_logged_in():
    """
    Tests that an exception is raised if you are not logged in and make an attempt to
    get information about a logged in user.
    """

    # create an AuthController object
    auth_cntrl = AuthController()

    # patch read_user_data to raise an exception
    with patch(
        "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
    ) as mock_reader:
        mock_reader.side_effect = KeyError()
        with pytest.raises(SystemExit):
            auth_cntrl.whoami()


def test_authcontroller_whoami_keyerror_not_logged_in(test_homeserver_url):
    """
    Tests that an exception is raised if you are not logged in and make an attempt to
    get information about a logged in user.
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # login, patching prompt_matrix_password to automatically enter the password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

    # patch read_user_data to raise an exception
    with pytest.raises(SystemExit):
        with patch(
            "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
        ) as mock_reader:
            mock_reader.return_value = [{"homeserver_url": "test"}, {}]
            auth_cntrl.whoami()


def test_authcontroller_whoami_no_errors(test_homeserver_url):
    """
    Tests that no errors are raised if the user is logged in and read_user_data returns
    the expected dictionary.
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # patch prompt_matrix_password to return a preset password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

    # mock the print function to verify it was only called once
    with patch("fractal.cli.controllers.auth.print", new=MagicMock()) as mock_print:
        auth_cntrl.whoami()

    # verify that print was called once with the expected string
    mock_print.assert_called_with(f"You are logged in as {matrix_id} on {homeserver_url}")


def test_authcontroller_logout_filenotfound():
    """
    Tests that you are returned without an exception if you are not logged in and the
    cred file is not found.
    """

    # create an AuthController object
    auth_cntrl = AuthController()

    with patch("fractal.cli.controllers.auth.print", new=MagicMock()) as mock_print:
        auth_cntrl.logout()

    # verify that print was called once with the expected string
    mock_print.assert_called_with(f"You are not logged in.")


def test_authcontroller_logout_keyerror():
    """
    Tests that an exception is raised if there is an error accessing
    """

    # create an AuthController object
    auth_cntrl = AuthController()

    # patch read_user_data to raise an exception
    with patch(
        "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
    ) as mock_reader:
        with pytest.raises(KeyError):
            mock_reader.return_value = [{"access_token": "test"}, {}]
            auth_cntrl.logout()


def test_authcontroller_logout_confirm_file_deletion(test_homeserver_url):
    """
    Tests that the file containing the user information is deleted upon logging out.
    """

    # create an AuthControlle object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # patch prompt_matrix_password to return a preset password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id, homeserver_url=homeserver_url)

    # verify that the fractal data directory exists after login
    assert os.path.exists(FRACTAL_DATA_DIR)
    assert os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")

    # logout
    auth_cntrl.logout()

    # verify that the data file is deleted
    assert not os.path.exists(f"{FRACTAL_DATA_DIR}/{auth_cntrl.TOKEN_FILE}")


async def test_authcontroller_login_with_access_token_whoami_error(test_homeserver_url):
    """
    Tests that an exception is raised if a WhoamiError is returned from
    the whoami function
    """

    # create an AuthController and login variables
    auth_cntrl = AuthController()
    homeserver_url = test_homeserver_url

    # patch client.whoami to return a WhoamiError
    with patch(
        "fractal.matrix.async_client.FractalAsyncClient.whoami", new_awaitable=MagicMock()
    ) as mock_whoami:
        mock_whoami.return_value = WhoamiError(message="test_message")
        with pytest.raises(MatrixLoginError) as e:
            await auth_cntrl._login_with_access_token(
                access_token="test_token", homeserver_url=homeserver_url
            )

        # verify that the error message matches what was set
        assert str(e.value) == "test_message"


async def test_authcontroller_login_with_access_token_no_error(
    test_homeserver_url, test_user_access_token
):
    """
    Tests that login variables are returned if there are no errors in the
    _login_with_access_token() function.
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    homeserver_url = test_homeserver_url
    matrix_id = "@admin:localhost"
    access_token = test_user_access_token

    # call the function and save the return values
    (
        returned_matrix_id,
        returned_homeserver_url,
        returned_access_token,
    ) = await auth_cntrl._login_with_access_token(
        access_token=access_token, homeserver_url=homeserver_url
    )

    # verify that the returned variables match what was expected
    assert returned_access_token == access_token
    assert returned_homeserver_url == homeserver_url
    assert returned_matrix_id == matrix_id


async def test_authcontroller_login_with_password_no_password_no_homeserver(test_homeserver_url):
    """
    Tests that get_homeserver_for_matrix_id and prompt_matrix_password are called if neither
    a password or homeserver_url are passed to _login_with_password
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # patch get_homeserver_for_matrix_id and prompt_matrix_password to verify function calls
    with patch(
        "fractal.cli.controllers.auth.get_homeserver_for_matrix_id", new_awaitable=AsyncMock()
    ) as mock_get_homeserver:
        mock_get_homeserver.return_value = [homeserver_url, False]
        with patch(
            "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
        ) as mock_password_prompt:
            mock_password_prompt.return_value = "admin"
            with patch('fractal.cli.controllers.auth.input') as mock_input:
                (
                    returned_homeserver_url,
                    returned_access_token,
                ) = await auth_cntrl._login_with_password(matrix_id=matrix_id)

    # verify the patched functions are called once
    mock_get_homeserver.assert_awaited_once()
    mock_password_prompt.assert_called_once()

    # verify that the homeserver_url returned by _login_with_password matches what was expected
    assert returned_homeserver_url == homeserver_url

    # verify that input was never called asking the user if they wished to continue
    mock_input.assert_not_called()


async def test_authcontroller_login_with_password_no_homeserver_apex_changed(test_homeserver_url):
    """ 
    Tests that if the apex homeserver changed, a new password and username is hashed for
    a remote login.
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url
    cli_password = "admin"

    # patch get_homeserver_for_matrix_id and prompt_matrix_password to verify function calls
    with patch(
        "fractal.cli.controllers.auth.get_homeserver_for_matrix_id", new_awaitable=AsyncMock()
    ) as mock_get_homeserver:
        mock_get_homeserver.return_value = [homeserver_url, True]
        with patch(
            "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
        ) as mock_password_prompt:
            mock_password_prompt.return_value = cli_password
            # patch input to return 'y', signifying that the user wants to proceed with the
                # remote login
            with patch(
                "fractal.cli.controllers.auth.input", new_callable=MagicMock()
            ) as mock_input:
                mock_input.return_value = "y"
                # patch login to verify the new password
                with patch("fractal.matrix.async_client.FractalAsyncClient.login") as mock_login:
                    (
                        returned_homeserver_url,
                        returned_access_token,
                    ) = await auth_cntrl._login_with_password(matrix_id=matrix_id)

    # verify that input was called with the expected string
    mock_input.assert_called_with(
        "Your homeserver apex has changed. Do you want to continue? (y/n) "
    )

    # hash the user's matrix id and homeserver to set the expected password used to log in
    expected_password = sha256(f"{cli_password}{homeserver_url}".encode("utf-8")).hexdigest()
    mock_login.assert_called_with(expected_password)

    assert returned_homeserver_url == test_homeserver_url

async def test_authcontroller_login_with_password_no_homeserver_apex_changed_no_continue(test_homeserver_url):
    """
    Tests that the sign in process is terminated if the user does not wish to log in through
    another server.
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url
    cli_password = "admin"

    # patch get_homeserver_for_matrix_id and prompt_matrix_password to verify function calls
    with patch(
        "fractal.cli.controllers.auth.get_homeserver_for_matrix_id", new_awaitable=AsyncMock()
    ) as mock_get_homeserver:
        mock_get_homeserver.return_value = [homeserver_url, True]
        with patch(
            "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
        ) as mock_password_prompt:
            mock_password_prompt.return_value = cli_password
            # patch input to return 'n', signifying that the user does NOT want 
                # to proceed with the remote login
            with patch(
                "fractal.cli.controllers.auth.input", new_callable=MagicMock()
            ) as mock_input:
                mock_input.return_value = "n"
                # patch login to verify it was not called
                with patch("fractal.matrix.async_client.FractalAsyncClient.login") as mock_login:
                    with pytest.raises(SystemExit):
                        (
                            returned_homeserver_url,
                            returned_access_token,
                        ) = await auth_cntrl._login_with_password(matrix_id=matrix_id)

    # verify that input was called with the expected string
    mock_input.assert_called_with(
        "Your homeserver apex has changed. Do you want to continue? (y/n) "
    )

    # verify that login was not called
    mock_login.assert_not_called()

async def test_authcontroller_login_with_password_loginerror(test_homeserver_url):
    """
    Tests that an exception is raised if a LoginError is returned by client.login
    """

    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # patch get_homeserver_for_matrix_id and prompt_matrix_password to verify they are not
    # called. Patch the client.login function to raise an exception
    with patch(
        "fractal.cli.controllers.auth.get_homeserver_for_matrix_id", new_awaitable=AsyncMock()
    ) as mock_get_homeserver:
        with patch(
            "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
        ) as mock_password_prompt:
            with patch(
                "fractal.matrix.async_client.FractalAsyncClient.login", new_awaitable=MagicMock()
            ) as mock_login:
                mock_login.return_value = LoginError(message="test error message")

                with pytest.raises(MatrixLoginError) as e:
                    (
                        returned_homeserer_url,
                        returned_access_token,
                    ) = await auth_cntrl._login_with_password(
                        matrix_id=matrix_id, password="admin", homeserver_url=homeserver_url
                    )

    # verify that the error message that was raised matches what was set locally
    assert str(e.value) == "test error message"

    # verify that the patched functions were not called
    mock_get_homeserver.assert_not_called()
    mock_password_prompt.assert_not_called()


async def test_authcontroller_login_invalid_password(test_homeserver_url):
    """
    Tests that an exception is raised if an invalid password is entered
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # call _login_with_pasword passing an invalid password
    with pytest.raises(MatrixLoginError) as e:
        returned_homeserer_url, returned_access_token = await auth_cntrl._login_with_password(
            matrix_id=matrix_id, password="wrong_password", homeserver_url=homeserver_url
        )

    # verify that the error message raised matches what was expected
    assert str(e.value) == "Invalid username or password"


async def test_authcontroller_login_with_password_no_error(test_homeserver_url):
    """
    Tests that no errors are raised and that values are returned if when a valid password
    is given to the function
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # set the returned_access_token and expect it to be changed
    returned_access_token = "test_access_token"

    # call _login_with_password and store the values
    returned_homeserer_url, returned_access_token = await auth_cntrl._login_with_password(
        matrix_id=matrix_id, password="admin", homeserver_url=homeserver_url
    )

    # verify that the access token set was changed when the function was called
    assert returned_access_token != "test_access_token"

    # verify that the homeserver_url that was returned matches what was expected
    assert returned_homeserer_url == homeserver_url


def test_authcontroller_show_filenotfound():
    """
    Tests that an exception is raised if show() is called when the user is not logged in
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    key = "access_token"

    # verify that the fractal data directory does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # call show to raise an exception
    with pytest.raises(SystemExit):
        auth_cntrl.show(key)


def test_authcontroller_show_keyerror():
    """
    Tests that an exception is raised if a KeyError is raised when read_user_data is
    called
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    key = "access_token"

    # patch read_user_data to raise a KeyError and raise an exception
    with patch(
        "fractal.cli.controllers.auth.read_user_data", new_callable=MagicMock()
    ) as mock_reader:
        mock_reader.side_effect = KeyError()
        with pytest.raises(SystemExit):
            auth_cntrl.show(key)


def test_authcontroller_show_key_cases(test_homeserver_url):
    """
    Tests the non-error cases of show() and verifies the print statements associated with
    their key value.
    """

    # create an AuthController object and login variables
    auth_cntrl = AuthController()
    matrix_id = "@admin:localhost"
    homeserver_url = test_homeserver_url

    # log the user in patching prompt_matrix_password to use preset password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = "admin"
        auth_cntrl.login(matrix_id=matrix_id, homeserver_url=homeserver_url)

    # verify that the fractal data directory exists
    assert os.path.exists(FRACTAL_DATA_DIR)

    data, _ = read_user_data("matrix.creds.yaml")

    access_token = data["access_token"]

    # access token case
    key = "access_token"
    assert auth_cntrl.show(key) == access_token

    # homeserver url case
    key = "homeserver_url"
    assert auth_cntrl.show(key) == homeserver_url

    # matrix id case
    key = "matrix_id"
    assert auth_cntrl.show(key) == matrix_id

    # non-matching case
    key = "invalid_key"
    assert auth_cntrl.show(key) == None
