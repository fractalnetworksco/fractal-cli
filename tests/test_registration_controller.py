from fractal.cli.controllers.registration import RegistrationController
import secrets

async def test_registration_controller_register_local_():
    """
    """
    matrix_id = f"@test-user-{secrets.token_hex(8)}:localhost"
    password = "test_password"

    test_registration_controller = RegistrationController()

    access_token, homeserver_url = await test_registration_controller._register_local(
        matrix_id=matrix_id, password=password
    )