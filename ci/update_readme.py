import argparse
import re

parser = argparse.ArgumentParser(prog="Coverage badge in README")
parser.add_argument(
    "--coverage", type=str, required=True, help="Coverage value to set in the badge"
)
args = parser.parse_args()


def value_to_colour(value, min_value, max_value):
    # Ensure value is within the specified range
    value = max(min(value, max_value), min_value)

    # Calculate the ratio of the value between min_value and max_value
    ratio = (value - min_value) / (max_value - min_value)

    # Calculate the RGB values for the color
    red = int(255 * (1 - ratio))
    green = int(255 * ratio)
    blue = 0  # Since we're creating a gradient from red to green

    # Convert RGB values to a hex color code
    hex_color = "23{:02X}{:02X}{:02X}".format(red, green, blue)

    return hex_color


def make_sheild(coverage_number: float, minimum, maximum):
    colour = value_to_colour(coverage_number, minimum, maximum)
    return (
        f"![Static Badge](https://img.shields.io/badge/"
        f"Coverage-{coverage_number:.1f}%25-%{colour})"
    )


if __name__ == "__main__":
    coverage_value = float(args.coverage)
    with open("README.md", "r+") as f:
        file = f.read()
        file_update = re.sub(
            r".*https://img.shields.io/badge/coverage-.*",
            make_sheild(coverage_value, 50, 100),
            file,
        )
        f.seek(0)
        f.write(file_update)
