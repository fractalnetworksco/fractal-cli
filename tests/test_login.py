from fractal.cli.controllers.auth import AuthController


def test_login_with_password(mock_getpass, test_homeserver_url):
    auth_cntrl = AuthController()
    auth_cntrl.login("@admin:localhost", homeserver_url=test_homeserver_url)
