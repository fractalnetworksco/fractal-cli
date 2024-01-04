import random
from sys import exit

from clicz import CLICZ, Color

color = Color()


def main():
    descriptions = [
        "Fractal Networks: Your data, your future.",
        "Fractal Networks: The Future of the Web.",
        "Fractal Networks: Above the Cloud and Beyond the Blockchain.",
        "Fractal Networks: Edge Computing for the People.",
    ]
    description = random.choice(descriptions)
    fn, hero = description.split(":", 1)
    cli = CLICZ(
        cli_module="fractal.plugins",
        description=f"{color.red(fn)}: {color.green(hero.strip())}",
    )
    # cli.default_controller = "fractal"

    cli.dispatch()
    # except Exception as err:
    #     print(f"Error: {err}")
    #     exit(1)
