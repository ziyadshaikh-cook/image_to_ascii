#!/usr/bin/env python3
"""
image_to_ascii.py

Converts an image into ASCII text art by mapping pixel brightness to
characters of matching visual density. Works on any photo, not just
faces there's no face detection here, just a brightness-to-character
mapping, which is exactly what produces the look in the reference image.

Usage:
    python3 image_to_ascii.py photo.jpg
    python3 image_to_ascii.py photo.jpg -w 150 -o result.txt
    python3 image_to_ascii.py photo.jpg --invert
"""

from PIL import Image, ImageOps
import numpy as np
import argparse
import sys

# Characters ordered from most "ink" (dark) to least (light).
# index 0 maps to the darkest pixels, the last character to the brightest.
ASCII_CHARS = "@%#*+=-:. "


def load_image(path: str) -> Image.Image:
    try:
        return Image.open(path)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {path}")
    except Exception as e:
        sys.exit(f"Error: could not open image ({e})")


def resize_image(image: Image.Image, new_width: int) -> Image.Image:
    """
    Resize keeping aspect ratio, with a correction factor for the fact that
    terminal/monospace characters are roughly twice as tall as they are
    wide. Without this, output looks vertically stretched.
    """
    width, height = image.size
    aspect_ratio = height / width
    new_height = max(1, round(new_width * aspect_ratio * 0.55))
    return image.resize((new_width, new_height))


def pixels_to_ascii(image: Image.Image, chars: str) -> str:
    grayscale = image.convert("L")
    # Stretch the histogram to use the full 0-255 range. Without this, a photo
    # that's naturally dark or low-contrast (dark hair, dim background) ends up
    # using only the dense end of the character ramp and looks flat/muddy.
    grayscale = ImageOps.autocontrast(grayscale, cutoff=1)
    pixel_array = np.array(grayscale, dtype=np.int32)

    scale = len(chars) - 1
    char_indices = (pixel_array * scale) // 255
    char_lookup = np.array(list(chars))
    char_grid = char_lookup[char_indices]

    return "\n".join("".join(row) for row in char_grid)


def convert_to_ascii_art(path: str, width: int, chars: str) -> str:
    image = load_image(path)
    image = resize_image(image, width)
    return pixels_to_ascii(image, chars)


def main():
    parser = argparse.ArgumentParser(description="Convert an image to ASCII text art.")
    parser.add_argument("image_path", help="Path to the input image")
    parser.add_argument("-w", "--width", type=int, default=120,
                         help="Output width in characters (default: 120)")
    parser.add_argument("-o", "--output", help="Save output to a text file")
    parser.add_argument("--invert", action="store_true",
                         help="Flip the character ramp (try this if the result looks like a photo negative)")
    args = parser.parse_args()

    chars = ASCII_CHARS[::-1] if args.invert else ASCII_CHARS
    art = convert_to_ascii_art(args.image_path, args.width, chars)

    print(art)

    if args.output:
        with open(args.output, "w") as f:
            f.write(art)
        print(f"\nSaved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()