import secrets
import asyncio
from hashlib import sha256
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from fractal.cli.controllers.registration import (
    RegistrationController,
    get_homeserver_for_matrix_id,
)
from fractal.cli.controllers.auth import AuthController


async def test_registration_controller_register_local_error_getting_homeserver_container():
    """
    Tests that an exception is raised when there is an error getting the
    homeserver container.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # patch docker.from_env() to raise an exception
    with patch(
        "fractal.cli.controllers.registration.docker.from_env", side_effect=Exception()
    ) as mock_from_env:
        # patch print to verify what was called
        with patch("fractal.cli.controllers.registration.print") as mock_print:
            with pytest.raises(SystemExit) as e:
                access_token, homeserver_url = await test_registration_controller._register_local(
                    matrix_id=matrix_id, password=password
                )

    # verify that the expected print statement was called
    mock_print.assert_called_with(f"No synapse server running locally: .")


async def test_registration_controller_register_local_successful_registration(
    test_homeserver_url,
):
    """
    Tests that values are returned from the function if a user is successfully
    registered.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # call _register_local() to register a user, raising no exceptions
    access_token, homeserver_url = await test_registration_controller._register_local(
        matrix_id=matrix_id, password=password, homeserver_url=test_homeserver_url  # type:ignore
    )

    # verify that values were returned
    assert access_token is not None
    assert homeserver_url is not None


async def test_registration_controller_register_local_user_id_already_taken(test_homeserver_url):
    """
    Tests that an exception is raised if an attempt is made to register a user with the
    same user id as an existing user.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # create return variables
    access_token = None
    homeserver_url = None

    # call _register_local() to successfully register a user
    access_token, homeserver_url = await test_registration_controller._register_local(
        matrix_id=matrix_id, password=password, homeserver_url=test_homeserver_url  # type:ignore
    )

    # verify that values were returned
    assert access_token is not None
    assert homeserver_url is not None

    # reset the return variables
    access_token = None
    homeserver_url = None

    # patch the print function to verify what was passed
    with patch("fractal.cli.controllers.registration.print") as mock_print:
        with pytest.raises(SystemExit):
            # call the function using the same id and password to raise an exception
            access_token, homeserver_url = await test_registration_controller._register_local(
                matrix_id=matrix_id,
                password=password,
                homeserver_url=test_homeserver_url,  # type:ignore
            )

    # verify that no values were returned
    assert access_token is None
    assert homeserver_url is None

    # verify that the expected print statement was called
    mock_print.assert_called_with(
        "Sending registration request...\nERROR! Received 400 Bad Request\nUser ID already taken.\n"
    )


async def test_registration_controller_register_local_no_homeserver(test_homeserver_url):
    """
    Tests that get_homeserver_for_matrix_id is called if no homeserver_url is passed to
    the function.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # patch get_homeserver_for_matrix_id() to return a verifiable homeserver_url
    with patch(
        "fractal.cli.controllers.registration.get_homeserver_for_matrix_id"
    ) as mock_get_homeserver:
        mock_get_homeserver.return_value = [test_homeserver_url, False]
        access_token, homeserver_url = await test_registration_controller._register_local(
            matrix_id=matrix_id, password=password
        )

    # verify that the homeserver_url returned matches the homeserver_url fixture provided
    assert homeserver_url == test_homeserver_url


async def test_registration_controller_register_True_local(
    test_registration_token, test_homeserver_url
):
    """
    Tests that _register_local is called when True is passed as the local parameter.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # patch the _register_local() function to verify it was called
    with patch(
        "fractal.cli.controllers.registration.RegistrationController._register_local"
    ) as mock_register_local:
        # patch get_homeserver_for_matrix_id to make sure it was not called
        with patch(
            "fractal.cli.controllers.registration.get_homeserver_for_matrix_id"
        ) as mock_get_homeserver:
            await test_registration_controller._register(
                matrix_id=matrix_id,
                password=password,
                registration_token=test_registration_token,
                local=True,
                homeserver_url=test_homeserver_url,
            )

    # verify function calls
    mock_get_homeserver.assert_not_called()
    mock_register_local.assert_called_once()


async def test_registration_controller_register_existing_homeserver(
    test_registration_token, test_homeserver_url
):
    """
    Tests that get_homeserver_for_matrix_id is not called if there is already an existing
    homeserver_url passed to the function.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # patch get_homeserver_for_matrix_id to make sure it was not called
    with patch(
        "fractal.cli.controllers.registration.get_homeserver_for_matrix_id"
    ) as mock_get_homeserver:
        _, homeserver_url = await test_registration_controller._register(
            matrix_id=matrix_id,
            password=password,
            registration_token=test_registration_token,
            homeserver_url=test_homeserver_url,
        )

    mock_get_homeserver.assert_not_called()
    assert homeserver_url == test_homeserver_url


async def test_registration_controller_register_no_homeserver(
    test_registration_token, test_homeserver_url
):
    """
    Tests that get_homeserver_for_matrix_id is called if there is no existing homeserver_url
    passed to the function and local is set to False.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # create a homserver variable
    homeserver_url = None

    # patch get_homeserver_for_matrix_id to have it return a verifiable homeserver_url
    with patch(
        "fractal.cli.controllers.registration.get_homeserver_for_matrix_id"
    ) as mock_get_homeserver:
        mock_get_homeserver.return_value = [test_homeserver_url, False]
        _, homeserver_url = await test_registration_controller._register(
            matrix_id=matrix_id,
            password=password,
            registration_token=test_registration_token,
        )

    # verify that the homeserver returned matches the test homeserver fixture
    assert homeserver_url == test_homeserver_url


def test_registration_controller_register_cli_method(test_registration_token):
    """
    Tests that _register is called when the register cli method is called.
    """

    # create matrix registration info
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # patch _register() to return two test values and to verify it was called
    with patch(
        "fractal.cli.controllers.registration.RegistrationController._register"
    ) as mock_register:
        mock_register.return_value = ["test", "value"]
        test_registration_controller.register(
            matrix_id=matrix_id,
            password=password,
            registration_token=test_registration_token,
        )

    # verify that the function was called
    mock_register.assert_called()


async def test_registration_controller_create_token():
    """
    Tests that generate_registration_token is called when _create_token is called.
    """

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    # create a token variable
    token = None

    # call _create_token()
    token = await test_registration_controller._create_token()

    # verify that a token is returned
    assert token is not None


def test_registration_controller_token_cases():
    """
    Tests the cases for the token method.

    NOTE: not all cases have been implemented yet
    """

    # creating a token
    test_registration_controller = RegistrationController()
    token = None
    token = test_registration_controller.token("create")
    assert token is not None

    # list case
    with patch("fractal.cli.controllers.registration.print") as mock_print:
        # TODO: update this test when the list case gets implemented
        test_registration_controller.token("list")
    mock_print.assert_called_once_with("FIXME: List not implemented yet.")

    # invalid action case
    with patch("fractal.cli.controllers.registration.print") as mock_print:
        test_registration_controller.token("invalid_action")
    # TODO: might need to update the string if it gets changed in the token function
    mock_print.assert_called_once_with("Invalid action. Must be either 'create'")


# @pytest.skip(reason='Error on registration due to user id already being taken.')
def test_registration_controller_register_remote_functional_test(
    test_homeserver_url, test_registration_token, test_alternate_homeserver_url,
):
    """
    Tests that the homeserver url passed to register_remote is returned after registration.
    TODO: Add functionality to test using synapse2 in the ci.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    # create a RegistrationController object
    test_registration_controller = RegistrationController()

    access_token, homeserver_url = asyncio.run(test_registration_controller._register_local(
        matrix_id=matrix_id, password=password, homeserver_url=test_homeserver_url  # type:ignore
    ))

    # create an AuthController object
    auth_cntrl = AuthController()

    # log the user in patching prompt_matrix_password to use preset password
    with patch(
        "fractal.cli.controllers.auth.prompt_matrix_password", new_callable=MagicMock()
    ) as mock_password_prompt:
        mock_password_prompt.return_value = password
        auth_cntrl.login(matrix_id=matrix_id, homeserver_url=homeserver_url)

    # recreate the RegistrationController object with the user being logged in
    test_registration_controller = RegistrationController()
    test_registration_controller._register = AsyncMock()
    test_registration_controller._register.return_value = ["test_token", test_alternate_homeserver_url]

    # call register_remote and store the values returned
    with patch('fractal.cli.controllers.registration.getpass', new_callable=MagicMock()) as mock_getpass:
        mock_getpass.return_value = password
        returned_access_token, returned_homeserver = test_registration_controller.register_remote(
            test_alternate_homeserver_url, test_registration_token
        )

    # verify that the homeserver returned matches the homeserver fixture passed to the function
    assert returned_homeserver == test_alternate_homeserver_url
    assert returned_homeserver != test_homeserver_url

    # hash the login creds to verify they were passed as parameters in the function
    unique = sha256(f"{matrix_id}{test_alternate_homeserver_url}".encode("utf-8")).hexdigest()[:4]
    remote_matrix_id = f"{matrix_id}-{unique}"
    remote_password = sha256(f"{password}{test_alternate_homeserver_url}".encode("utf-8")).hexdigest()

    # verify arguments
    test_registration_controller._register.assert_called_with(
        matrix_id=remote_matrix_id,
        password=remote_password,
        registration_token=test_registration_token,
        homeserver_url=test_alternate_homeserver_url
    )
