import asyncio
import os
from getpass import getpass
from hashlib import sha256
from sys import exit
from typing import Optional, Tuple

import docker
from clicz import cli_method
from docker.models.containers import Container
from fractal.cli.controllers.auth import AuthenticatedController, auth_required
from fractal.matrix import MatrixClient, get_homeserver_for_matrix_id
from fractal.matrix.utils import parse_matrix_id
from nio import LoginError


class RegistrationController(AuthenticatedController):
    PLUGIN_NAME = "registration"

    async def _register_local(
        self, matrix_id: str, password: str, homeserver_url: Optional[str] = None
    ) -> Tuple[str, str]:
        try:
            # get homeserver container
            docker_client = docker.from_env()
            synapse_label = os.environ.get("SYNAPSE_DOCKER_LABEL", "org.homeserver=true")
            synapse_container: Container = docker_client.containers.list(
                filters={"label": synapse_label}
            )[
                0
            ]  # type: ignore
        except Exception as e:
            print(f"No synapse server running locally: {e}.")
            exit(1)

        username = parse_matrix_id(matrix_id)[0]
        if not homeserver_url:
            homeserver_url, _ = await get_homeserver_for_matrix_id(matrix_id)

        # create admin user on synapse if it doesn't exist
        result = synapse_container.exec_run(
            f"register_new_matrix_user -c /data/homeserver.yaml -a -u {username} -p {password} http://localhost:8008"
        )
        if result.exit_code != 0:
            print(result.output.decode("utf-8"))
            exit(1)

        async with MatrixClient(homeserver_url) as client:
            client.user = username
            await client.login(password=password)
            access_token = client.access_token
            await client.disable_ratelimiting(client.user_id)

        return access_token, homeserver_url

    async def _register(
        self,
        matrix_id: str,
        password: str,
        registration_token: str,
        local: bool = False,
        homeserver_url: Optional[str] = None,
    ) -> Tuple[str, str]:
        if not homeserver_url:
            homeserver_url, _ = await get_homeserver_for_matrix_id(matrix_id)
        if local:
            return await self._register_local(matrix_id, password, homeserver_url=homeserver_url)
        async with MatrixClient(homeserver_url, access_token=self.access_token) as client:  # type: ignore
            access_token = await client.register_with_token(
                matrix_id, password, registration_token
            )
        return access_token, homeserver_url

    @auth_required
    @cli_method
    def register_remote(
        self,
        homeserver_url: str,
        registration_token: str,
    ):
        """
        Registers the currently logged in user on a given HomeServer.
        ---
        Args:
            homeserver_url: Homeserver to register with.
            registration_token: Registration token to use.

        """

        # Get the user's login creds
        matrix_id = self.matrix_id
        password = getpass(f"Enter {matrix_id}'s password: ")

        # Generate a deterministic unique ID to append to the current user's matrix id
        unique = sha256(f"{matrix_id}{homeserver_url}".encode("utf-8")).hexdigest()[:4]
        matrix_id = f"{matrix_id}-{unique}"

        # Generate a deterministic password using the user's password and homeserver
        password = sha256(f"{password}{homeserver_url}".encode("utf-8")).hexdigest()

        # Register the user using the newly generated creds
        access_token, homeserver_url = asyncio.run(
            self._register(
                matrix_id=matrix_id,
                password=password,
                registration_token=registration_token,
                homeserver_url=homeserver_url,
            )
        )

        print(access_token)
        return access_token, homeserver_url

    @cli_method
    def register(
        self,
        matrix_id: str,
        password: str,
        registration_token: str,
        homeserver_url: Optional[str] = None,
        local: bool = False,
    ):
        """
        Registers a given user with a homeserver. Prints out the registered
        user's access token.
        ---
        Args:
            matrix_id: Matrix ID of user to register.
            password: Password to register with.
            registration_token: Registration token to use.
            homeserver_url: Homeserver to register with.
            local: Whether to register locally or not.

        """
        access_token, homeserver_url = asyncio.run(
            self._register(
                matrix_id,
                password,
                registration_token,
                homeserver_url=homeserver_url,
                local=local,
            )
        )
        print(access_token)

    register.clicz_aliases = ["register"]

    async def _create_token(self):
        async with MatrixClient(self.homeserver_url, access_token=self.access_token) as client:  # type: ignore
            return await client.generate_registration_token()

    @cli_method
    def token(
        self,
        action: str,
    ):
        """
        Registers a given user with a homeserver. Prints out the registered
        user's access token.
        ---
        Args:
            action: Action to perform. Such as 'create' or 'list'.
        """
        match action:
            case "create":
                token = asyncio.run(self._create_token())
                print(token)
                return token
            case "list":
                print(f"FIXME: List not implemented yet.")
            case _:
                print("Invalid action. Must be either 'create'")

    token.clicz_aliases = ["token"]


Controller = RegistrationController
