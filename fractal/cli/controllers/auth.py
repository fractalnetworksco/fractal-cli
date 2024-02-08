import functools
import os
from hashlib import sha256
from sys import exit
from typing import Any, Callable, Optional, Tuple

from asgiref.sync import async_to_sync
from clicz import cli_method
from fractal.cli.utils import read_user_data, write_user_data
from fractal.matrix import MatrixClient, get_homeserver_for_matrix_id
from fractal.matrix.utils import parse_matrix_id, prompt_matrix_password
from nio import LoginError, WhoamiError


class MatrixLoginError(Exception):
    pass


class AuthController:
    PLUGIN_NAME = "auth"
    TOKEN_FILE = "matrix.creds.yaml"

    @cli_method
    def login(
        self,
        matrix_id: str,
        homeserver_url: Optional[str] = None,
        access_token: Optional[str] = None,
    ):
        """
        Login to a Matrix homeserver.
        ---
        Args:
            matrix_id: Matrix ID of user to login as
            homeserver_url: Homeserver to login to
            access_token: Access token to use for login.

        """
        if not access_token:
            homeserver_url, access_token = async_to_sync(self._login_with_password)(
                matrix_id, homeserver_url=homeserver_url
            )
        else:
            if not homeserver_url:
                print("Please provide a --homeserver-url if logging in with an access token.")
                exit(1)
            try:
                matrix_id, homeserver_url, access_token = async_to_sync(
                    self._login_with_access_token
                )(access_token, homeserver_url=homeserver_url)
            except MatrixLoginError as e:
                print("Error logging in:", e)
                exit(1)

        # save access token to token file
        write_user_data(
            {
                "access_token": access_token,
                "homeserver_url": homeserver_url,
                "matrix_id": matrix_id,
            },
            self.TOKEN_FILE,
        )

        print(f"Successfully logged in as {matrix_id}")

    login.clicz_aliases = ["login"]

    @cli_method
    def whoami(self):
        """
        Get information about the current logged in user.
        ---
        Args:
        """
        try:
            data, _ = read_user_data(self.TOKEN_FILE)
        except (KeyError, FileNotFoundError):
            print("You are not logged in.")
            exit(1)

        try:
            homeserver_url = data["homeserver_url"]
            matrix_id = data["matrix_id"]
        except KeyError:
            print("You are not logged in.")
            exit(1)

        print(f"You are logged in as {matrix_id} on {homeserver_url}")

    @cli_method
    def logout(self):
        """
        Logout of Matrix
        ---
        Args:
        """
        try:
            data, path = read_user_data(self.TOKEN_FILE)
            access_token = data["access_token"]
            homeserver_url = data["homeserver_url"]
        except KeyError:
            raise
        except FileNotFoundError:
            print("You are not logged in.")
            return

        async def _logout():
            async with MatrixClient(homeserver_url, access_token) as client:
                await client.logout()

        if os.path.exists(path):
            os.remove(path)
            async_to_sync(_logout)()
            print("Successfully logged out. Have a nice day.")

    logout.clicz_aliases = ["logout"]

    async def _login_with_access_token(
        self, access_token: str, homeserver_url: str
    ) -> Tuple[str, str, str]:
        async with MatrixClient(
            homeserver_url=homeserver_url, access_token=access_token
        ) as client:
            res = await client.whoami()
            if isinstance(res, WhoamiError):
                raise MatrixLoginError(res.message)
            matrix_id = res.user_id
        return matrix_id, homeserver_url, access_token

    async def _login_with_password(
        self, matrix_id: str, password: Optional[str] = None, homeserver_url: Optional[str] = None
    ) -> Tuple[str, str]:
        apex_changed = False
        if not homeserver_url:
            homeserver_url, apex_changed = await get_homeserver_for_matrix_id(matrix_id)

            if apex_changed:
                response = input(
                    "Your homeserver apex has changed. Do you want to continue? (y/n) "
                ).lower()
                if response != "y":
                    exit(1)
        if not password:
            password = prompt_matrix_password(matrix_id, homeserver_url=homeserver_url)
        async with MatrixClient(homeserver_url) as client:
            if apex_changed:
                local, _ = parse_matrix_id(matrix_id=matrix_id)
                unique_id = sha256(f"{local}{homeserver_url}".encode("utf-8")).hexdigest()[:4]
                client.user = f"{local}-{unique_id}"
                password = sha256(f"{password}{homeserver_url}".encode("utf-8")).hexdigest()
                res = await client.login(password)
            else:
                client.user = matrix_id
                res = await client.login(password)
            if isinstance(res, LoginError):
                raise MatrixLoginError(res.message)
        return homeserver_url, res.access_token

    @cli_method
    def show(self, key: str):
        """

        ---
        Args:
            key: Key to show. Such as 'access_token' or 'homeserver_url'.
        """
        try:
            data, _ = read_user_data(self.TOKEN_FILE)
        except (KeyError, FileNotFoundError):
            print(f"You are not logged in")
            exit(1)

        match key:
            case "access_token":
                print(data["access_token"])
                return data["access_token"]
            case "homeserver_url":
                print(data["homeserver_url"])
                return data["homeserver_url"]
            case "matrix_id":
                print(data["matrix_id"])
                return data["matrix_id"]


class AuthenticatedController:
    PLUGIN_NAME = "auth_check"
    TOKEN_FILE = "matrix.creds.yaml"
    homeserver_url: Optional[str] = None
    access_token: Optional[str] = None
    matrix_id: Optional[str] = None

    def __init__(self):
        self.check_if_user_is_authenticated()

    @classmethod
    def get_creds(cls) -> Optional[Tuple[Optional[str], Optional[str], Optional[str]]]:
        """
        Returns the access token of the logged in user.
        """
        try:
            token_file, _ = read_user_data(cls.TOKEN_FILE)
            access_token = token_file.get("access_token")
            homeserver_url = token_file.get("homeserver_url")
            matrix_id = token_file.get("matrix_id")
        except FileNotFoundError:
            return None

        return access_token, homeserver_url, matrix_id

    def check_if_user_is_authenticated(self) -> bool:
        """
        Checks to see if the user is logged in.
        """
        creds = self.get_creds()
        if not creds:
            return False
        self.access_token, self.homeserver_url, self.matrix_id = creds
        os.environ["MATRIX_HOMESERVER_URL"] = self.homeserver_url or ""
        os.environ["MATRIX_ACCESS_TOKEN"] = self.access_token or ""
        os.environ["MATRIX_USER_TOKEN"] = self.matrix_id or ""
        return True


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


Controller = AuthController
