from sys import exit

from fractal.cli import CLICZ


def main():
    cli = CLICZ(cli_module="fractal.cli")
    # cli.default_controller = "fractal"

    cli.dispatch()
    # except Exception as err:
    #     print(f"Error: {err}")
    #     exit(1)
