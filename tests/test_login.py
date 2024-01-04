from fractal.cli.controllers.auth import AuthController


def test_login_with_password(mock_getpass):
    auth_cntrl = AuthController()
    auth_cntrl.login(matrix_id="@admin:localhost", homeserver_url="http://localhost:8008")
