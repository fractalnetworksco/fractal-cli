from fractal.cli.controllers.registration import RegistrationController
import secrets
import pytest
from unittest.mock import patch

async def test_registration_controller_register_local_error_getting_homeserver_container():
    """
    Tests that an exception is raised when there is an error getting the 
    homeserver container.
    """
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    with patch('fractal.cli.controllers.registration.docker.from_env', side_effect=Exception()) as mock_from_env:
        with patch('fractal.cli.controllers.registration.print') as mock_print:
            with pytest.raises(SystemExit) as e:
                access_token, homeserver_url = await test_registration_controller._register_local(
                    matrix_id=matrix_id, password=password
                )

    mock_print.assert_called_with(f"No synapse server running locally: .")

async def test_registration_controller_user_id_already_taken():
    """
    """

    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    access_token, homeserver_url = await test_registration_controller._register_local(
        matrix_id=matrix_id, password=password
    )

    
    with pytest.raises(SystemExit):
        access_token, homeserver_url = await test_registration_controller._register_local(
            matrix_id=matrix_id, password=password
        )