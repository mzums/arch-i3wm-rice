import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
from datetime import datetime
import subprocess
import re


comic_url = "https://xkcd.com/info.0.json"
output_path = "/home/mzums/.config/latest_xkcd.png"


def get_comic():
    response = requests.get(comic_url)
    data = response.json()

    img_url = data['img']
    img_response = requests.get(img_url)

    if img_response.status_code == 200:
        with open("latest_xkcd.png", "wb") as img_file:
            img_file.write(img_response.content)
        print("Saved img as phase_change.png")
    else:
        print(f"Error while saving img: {img_response.status_code}")


def crop_img(width, height):
    crop_width = int(width * 0.01)
    crop_height = int(height * 0.01)
    cropped_img = inverted_img.crop((crop_width, crop_height, width - crop_width, height - crop_height))

    return cropped_img


def get_font(size):
    try:
        font = ImageFont.truetype("/usr/share/fonts/adobe-source-code-pro/SourceCodePro-Regular.otf", size)
    except IOError:
        print("Font error.")
        font = ImageFont.load_default()

    return font


def place_text(textt, font, x, y, r, g, b):
    bbox = draw.textbbox((0, 0), textt, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    text_x = (screen_width - text_width) // x
    text_y = (screen_height - text_height) // y

    draw.text((text_x, text_y), textt, font=font, fill=(r, g, b))


def get_mommy_output():
    mommy_output = subprocess.run(
            ["mommy"],
            text=True,
            capture_output=True,
            check=True
        ).stderr.strip()

    mommy_output = re.sub(r'\x1b\[[0-9;]*m', '', mommy_output)
    mommy_output = re.sub(r'~.*', '', mommy_output)
    return mommy_output


if __name__ == "__main__":
    get_comic()

    img = Image.open("latest_xkcd.png")
    inverted_img = ImageOps.invert(img.convert("RGB"))

    width, height = inverted_img.size

    cropped_img = crop_img(width, height)

    width, height = cropped_img.size
    max_height = 600
    new_height = max_height
    new_width = int((new_height / height) * width)

    img_resized = cropped_img.resize((new_width, new_height))

    screen_width, screen_height = 1920, 1080
    background = Image.new("RGB", (screen_width, screen_height), (0, 0, 0))

    background.paste(img_resized, (int((screen_width - new_width) / 2), screen_height - new_height - 100))

    draw = ImageDraw.Draw(background)
    
    day_of_week = datetime.now().strftime('%A')
    textt = f"It's {day_of_week} outside\nstay safe and don't go out"
    place_text(textt, get_font(30), 10, 10, 255, 255, 255)

    mommy_output = get_mommy_output()
    place_text(f"{mommy_output} \u2764\uFE0F", get_font(20), 20, 4, 255, 20, 147)


    background.save("/home/mzums/.config/latest_xkcd2.png")
    os.system("feh --bg-fill /home/mzums/.config/latest_xkcd2.png")
