from fractal.cli import cli_method


class TestController:
    enable_cli = True
    enable_grpc = True

    PLUGIN_NAME = "deploy"

    @cli_method
    def say_hello(self, name: str, age: int, color: str = None) -> None:
        """
        ---
        Args:
               name: Your name.
               age: Your age.
               color: Your favorite color.
        Returns:
            None
        """
        print(f"Hello {name}, you are {age} years old.")
        if color:
            print(f"{name}s favorite color is {color}")

    @cli_method(parse_docstring=False)
    def start(self, bottle, man):
        pass

    @cli_method
    def ls(
        self,
    ):
        pass
