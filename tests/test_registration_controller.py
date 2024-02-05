import secrets
from unittest.mock import patch

import pytest
from fractal.cli.controllers.registration import (
    RegistrationController,
    get_homeserver_for_matrix_id,
)


async def test_registration_controller_register_local_error_getting_homeserver_container():
    """
    Tests that an exception is raised when there is an error getting the
    homeserver container.
    """
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    with patch(
        "fractal.cli.controllers.registration.docker.from_env", side_effect=Exception()
    ) as mock_from_env:
        with patch("fractal.cli.controllers.registration.print") as mock_print:
            with pytest.raises(SystemExit) as e:
                access_token, homeserver_url = await test_registration_controller._register_local(
                    matrix_id=matrix_id, password=password
                )

    mock_print.assert_called_with(f"No synapse server running locally: .")


async def test_registration_controller_register_local_successful_registration(test_homeserver_url):
    """
    Tests that values are returned from the function if a user is successfully
    registered.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    access_token, homeserver_url = await test_registration_controller._register_local(
        matrix_id=matrix_id, password=password, homeserver_url=test_homeserver_url
    )

    assert access_token is not None
    assert homeserver_url is not None


async def test_registration_controller_register_local_user_id_already_taken():
    """
    Tests that an exception is raised if an attempt is made to register a user with the
    same user id as an existing user.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    access_token, homeserver_url = await test_registration_controller._register_local(
        matrix_id=matrix_id, password=password
    )

    access_token = None
    homeserver_url = None

    with patch("fractal.cli.controllers.registration.print") as mock_print:
        with pytest.raises(SystemExit):
            access_token, homeserver_url = await test_registration_controller._register_local(
                matrix_id=matrix_id, password=password
            )

    assert access_token is None
    assert homeserver_url is None

    mock_print.assert_called_with(
        "Sending registration request...\nERROR! Received 400 Bad Request\nUser ID already taken.\n"
    )

async def test_registration_controller_register_True_local(test_registration_token):
    """
    Tests that _register_local is called when True is passed as the local parameter.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    with patch('fractal.cli.controllers.registration.RegistrationController._register_local') as mock_register_local:
        with patch('fractal.cli.controllers.registration.get_homeserver_for_matrix_id') as mock_get_homeserver:
            await test_registration_controller._register(
                matrix_id=matrix_id,
                password=password,
                registration_token=test_registration_token,
                local=True
            )

    mock_get_homeserver.assert_not_called()
    mock_register_local.assert_called_once()


async def test_registration_controller_register_existing_homeserver(test_registration_token, test_homeserver_url):
    """
    Tests that get_homeserver_for_matrix_id is not called if there is already an existing
    homeserver_url passed to the function.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    with patch('fractal.cli.controllers.registration.get_homeserver_for_matrix_id') as mock_get_homeserver:
        _, homeserver_url = await test_registration_controller._register(
            matrix_id=matrix_id,
            password=password,
            registration_token=test_registration_token,
            homeserver_url=test_homeserver_url
        )

    mock_get_homeserver.assert_not_called()
    assert homeserver_url == test_homeserver_url


async def test_registration_controller_register_no_homeserver(test_registration_token):
    """
    Tests that get_homeserver_for_matrix_id is called if there is no existing homeserver_url
    passed to the function and local is set to False.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    homeserver_url = None

    _, homeserver_url = await test_registration_controller._register(
        matrix_id=matrix_id,
        password=password,
        registration_token=test_registration_token,
    )

    assert homeserver_url is not None

def test_registration_controller_register_cli_method(test_registration_token):
    """
    Tests that _register is called when the register cli method is called.
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    with patch('fractal.cli.controllers.registration.RegistrationController._register') as mock_register:
        mock_register.return_value = ["test", "value"]
        test_registration_controller.register(
            matrix_id=matrix_id,
            password=password,
            registration_token=test_registration_token,
        )

    mock_register.assert_called()

async def test_registration_controller_create_token():
    """
    Tests that generate_registration_token is called when _create_token is called.
    """

    test_registration_controller = RegistrationController()

    token = None

    token = await test_registration_controller._create_token()

    assert token is not None

def test_registration_controller_token_cases():
    """
    Tests the cases for the token method.

    NOTE: not all cases have been implemented yet
    """

    # creating a token
    test_registration_controller = RegistrationController()
    token = None
    token = test_registration_controller.token('create')
    assert token is not None

    # list case
    with patch('fractal.cli.controllers.registration.print') as mock_print:
        # TODO: update this test when the list case gets implemented
        test_registration_controller.token('list')
    mock_print.assert_called_once_with('FIXME: List not implemented yet.')

    # invalid action case
    with patch('fractal.cli.controllers.registration.print') as mock_print:
        test_registration_controller.token('invalid_action')
    # TODO: might need to update the string if it gets changed in the token function
    mock_print.assert_called_once_with("Invalid action. Must be either 'create'")
