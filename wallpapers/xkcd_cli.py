import requests
from PIL import Image, ImageOps, ImageDraw, ImageFont
import os
from datetime import datetime
import subprocess
import re
from datetime import datetime


comic_url = "https://xkcd.com/info.0.json"
output_path = "/home/mzums/.config/latest_xkcd.png"
screen_width, screen_height = 1080, 1920


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
    draw = ImageDraw.Draw(background)
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


def get_time():
    sunrise, sunset = subprocess.run(
        ["sunwait", "list", "52.237049N", "21.017532E"],
        text=True,
        capture_output=True,
        check=True
    ).stdout.strip().split(", ")

    place_text(f"sunrise: {sunrise}     sunset: {sunset}", get_font(20), 1.05, 25, 150, 150, 150)

    return sunrise, sunset


def is_day():
    sunrise, sunset = get_time()
    sunrise_time = datetime.strptime(sunrise, "%H:%M").time()
    sunset_time = datetime.strptime(sunset, "%H:%M").time()
    now = datetime.now().time()

    if sunrise_time <= now <= sunset_time:
        place_img("sun.jpg")
    else:
        place_img("moon.jpg")


def place_img(img):
    img = Image.open(img)
    aspect_ratio = img.height / img.width
    img = img.resize((int(screen_width / 5), int(screen_width / 5 * aspect_ratio)))
    width, height = img.size
    background.paste(img, (int((screen_width - width) / 1.15),  int((screen_height - height) / 15)))


def resize_img(img, max_width, max_height):
    max_width = int(max_width * screen_width)
    max_height = int(max_height * screen_height)
    width, height = img.size
    if width > height:
        scale = int(max_width / width)
        width = max_width
        height *= scale
    else:
        scale = int(max_height / height)
        height = max_height
        width *= scale

    resized_img = img.resize((width, height))

    return resized_img


if __name__ == "__main__":
    get_comic()

    img = Image.open("latest_xkcd.png")
    inverted_img = ImageOps.invert(img.convert("RGB"))

    width, height = inverted_img.size

    cropped_img = crop_img(width, height)

    img_resized = resize_img(cropped_img, 0.8, 0.6)

    background = Image.new("RGB", (screen_width, screen_height), (0, 0, 0))

    background.paste(img_resized, (int((screen_width - img_resized.width) / 2), int((screen_height - img_resized.height) / 1.8)))

    is_day()


    draw = ImageDraw.Draw(background)
    
    day_of_week = datetime.now().strftime('%A')
    textt = f"It's {day_of_week} outside\nstay safe and don't go out"
    place_text(textt, get_font(30), 7, 8, 255, 255, 255)

    mommy_output = get_mommy_output()
    place_text(f"{mommy_output} \u2764\uFE0F", get_font(20), 20, 5, 255, 20, 147)


    background.save("/home/mzums/.config/latest_xkcd2.png")
    os.system("feh --bg-center /home/mzums/.config/latest_xkcd2.png")
