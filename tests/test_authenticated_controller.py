import os
import pytest
from unittest.mock import MagicMock, patch
from clicz import cli_method

from fractal.cli import FRACTAL_DATA_DIR
from fractal.cli.controllers.auth import (
    AuthController,
    AuthenticatedController,
    auth_required,
)


def test_authenticatedcontroller_get_creds_logged_in(logged_in_auth_controller):
    """ 
    Tests that if the user is logged in, there is a file with their credentials and
    that data is returned.
    """

    # create matrix login variables
    matrix_id = "@admin:localhost"
    homeserver_url = "http://localhost:8008"

    # set the access token variable that should change when get_creds() is called
    returned_access_token = "this should change"

    # call get_creds() and store the variables that are returned
    (
        returned_access_token,
        returned_homeserver_url,
        returned_matrix_id,
    ) = AuthenticatedController.get_creds()  # type:ignore

    # verify that the correct variables were returned
    assert returned_access_token != "this should change"
    assert returned_homeserver_url == homeserver_url
    assert returned_matrix_id == matrix_id


def test_authenticatedcontroller_get_creds_filenotfound():
    """ 
    Tests that none is returned if the user is not logged in. 
    """

    # verify that the fractal data file does not exist
    assert not os.path.exists(FRACTAL_DATA_DIR)

    # call get_creds
    returned = AuthenticatedController.get_creds()

    # verify that None is returned
    assert returned is None


def test_authenticatedcontroller_check_if_user_is_authenticated_not_authenticated():
    """ 
    Tests that the function returns False if the user is not logged in.
    """

    # create an AuthenticatedController object
    test_authenicated_controller = AuthenticatedController()

    # call the function and store the result
    result = test_authenicated_controller.check_if_user_is_authenticated()

    # assert that the result is False
    assert not result


def test_authenticatedcontroller_check_if_user_is_authenticated_is_authenticated(
    logged_in_auth_controller,
):
    """ 
    Tests that the function returns True if the user is logged in.
    """

    # create an AuthenticatedController object
    test_authenicated_controller = AuthenticatedController()

    # call the function and store the result
    result = test_authenicated_controller.check_if_user_is_authenticated()

    # assert that the result is True
    assert result


def test_authenticatedcontroller_auth_required():
    """ 
    Tests the cases for being logged in and not being logged in when using an 
    auth_required decorator.
    """
    class TestAuthRequired(AuthenticatedController):
        """
        Needed for custom-defined functions for testing the auth_required decorator
        """

        @auth_required
        def test_decorator(self):
            """"""


    # create a instance of the test class and give it an access token
    logged_in_controller = TestAuthRequired()
    logged_in_controller.access_token = "test_access_token"

    # create another instance of the test class without an access token
    not_logged_in_controller = TestAuthRequired()

    # call the test function to raise an exception
    with pytest.raises(SystemExit):
        not_logged_in_controller.test_decorator() # type:ignore

    # mock the print function to verify it was not called
    with patch('fractal.cli.controllers.auth.print', new=MagicMock()) as mock_print:
        logged_in_controller.test_decorator() # type:ignore

    # verify that the print function was not called
    mock_print.assert_not_called()



