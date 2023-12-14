import functools
import os
from typing import Any, Callable, Optional, Tuple

from fractal.cli.utils import read_user_data


class AuthenticatedController:
    PLUGIN_NAME = "auth_check"
    TOKEN_FILE = "matrix.creds.yaml"
    homeserver_url: Optional[str] = None
    access_token: Optional[str] = None

    def __init__(self):
        self.check_if_user_is_authenticated()

    @classmethod
    def get_creds(cls) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        Returns the access token of the logged in user.
        """
        try:
            token_file, _ = read_user_data(cls.TOKEN_FILE)
            access_token = token_file.get("access_token")
            homeserver_url = token_file.get("homeserver_url")
        except FileNotFoundError:
            return None

        return access_token, homeserver_url

    def check_if_user_is_authenticated(self) -> bool:
        """
        Checks to see if the user is logged in.
        """
        creds = self.get_creds()
        if not creds:
            return False
        self.access_token, self.homeserver_url = creds
        os.environ["MATRIX_HOMESERVER_URL"] = self.homeserver_url
        os.environ["MATRIX_ACCESS_TOKEN"] = self.access_token
        return True


Controller = AuthenticatedController


def auth_required(func: Callable[..., Any]):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.access_token:
            print("You must be logged in to use this command.")
            print("Login with fractal login.")
            exit(1)
        args = [self] + list(args)
        res = func(*args, **kwargs)
        return res

    return wrapper
