import os

from unittest.mock import patch, MagicMock
from fractal.cli import FRACTAL_DATA_DIR
from fractal.cli.controllers.auth import AuthenticatedController, AuthController




def test_authenticatedcontroller_get_creds_logged_in(logged_in_auth_controller):
    """
    """

    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    returned_access_token = "this should change"

    returned_access_token, returned_homeserver_url, returned_matrix_id = AuthenticatedController.get_creds() # type:ignore

    assert returned_access_token != "this should change"
    assert returned_homeserver_url == homeserver_url
    assert returned_matrix_id == matrix_id

def test_authenticatedcontroller_get_creds_filenotfound():
    """ """
    assert not os.path.exists(FRACTAL_DATA_DIR)
    returned = AuthenticatedController.get_creds()

    assert returned is None

def test_authenticatedcontroller_check_if_user_is_authenticated_not_authenticated():
    """
    """

    test_authenicated_controller = AuthenticatedController()

    result = test_authenicated_controller.check_if_user_is_authenticated()

    assert not result 

def test_authenticatedcontroller_check_if_user_is_authenticated_is_authenticated(logged_in_auth_controller):
    """
    """

    test_authenicated_controller = AuthenticatedController()

    result = test_authenicated_controller.check_if_user_is_authenticated()

    assert result

