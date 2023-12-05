from typing import Optional, Tuple

from fractal.cli.utils import read_user_data


class AuthenticatedController:
    PLUGIN_NAME = "auth_check"
    TOKEN_FILE = "matrix.creds.yaml"
    homeserver_url: Optional[str] = None
    access_token: Optional[str] = None

    def __init__(self):
        self.check_if_user_is_authenticated()

    def get_creds(self) -> Optional[Tuple[Optional[str], Optional[str]]]:
        """
        Returns the access token of the logged in user.
        """
        try:
            token_file, _ = read_user_data(self.TOKEN_FILE)
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
            print("You must be logged in to use this command.")
            print("Login with fractal login.")
            exit(1)
        self.access_token, self.homeserver_url = creds
        return True


Controller = AuthenticatedController
