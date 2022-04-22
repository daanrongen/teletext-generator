import math
import os
import urllib.request
import uuid
import random
import dateutil.parser
import numpy as np
from PIL import Image, ImageFont, ImageDraw


class Page:
    def __init__(self, data, size):
        super(Page, self).__init__()
        self.title = data["title"]
        self.description = data["description"]
        self.image_url = data["image_url"]
        self.source = data["source"]
        self.date = data["date"]
        self.size = size
        self.rows = 40
        self.cols = 24
        self.ppr = math.ceil(self.size / self.rows)
        self.ppc = math.ceil(self.size / self.cols)
        self.font_path = "./assets/Modeseven-L3n5.ttf"
        self.colours = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "cyan": (0, 255, 255),
            "magenta": (255, 0, 255),
            "yellow": (255, 255, 0),
        }

        self.image_name = uuid.uuid4()
        self.buffer_dir = "./buffer"

        os.makedirs(self.buffer_dir, exist_ok=True)
        self.image_path = f"{self.buffer_dir}/{self.image_name}.png"
        urllib.request.urlretrieve(self.image_url, self.image_path)

        self.image = Image.open(self.image_path)
        self.image = self.image.transpose(Image.ROTATE_90)
        self.image = self.image.convert("RGB")
        self.image = self.center_crop()

        self.output = Image.new(
            mode="RGB", size=(self.size, self.size), color=self.colours["black"]
        )

    def mode7(self):
        ppr, ppc = self.ppr, self.ppc
        image_data = np.array(self.image)
        draw = ImageDraw.Draw(self.output)

        for x in range(self.rows):
            for y in range(0, self.cols - 1):
                (x1, y1), (x2, y2) = (x * ppr, y * ppc), (x * ppr + ppr, y * ppc + ppc)
                pixels = image_data[x1:x2, y1:y2]

                top_left = (x1, y1), (x1 + 0.5 * ppr, y1 + 0.33 * ppc)
                top_right = (x1 + 0.5 * ppr, y1), (x2, y1 + 0.33 * ppc)
                middle_left = (x1, y1 + 0.33 * ppr), (x1 + 0.5 * ppr, y1 + 0.66 * ppc)
                middle_right = (x1 + 0.5 * ppr, y1 + 0.33 * ppc), (x2, y1 + 0.66 * ppc)
                bottom_left = (x1, y1 + 0.66 * ppc), (x1 + 0.5 * ppr, y2)
                bottom_right = (x1 + 0.5 * ppr, y1 + 0.66 * ppc), (x2, y2)

                sliced_pixels = self.split_pixels(pixels)

                avg_colour_1 = self.average_rgb(sliced_pixels[0])
                avg_colour_2 = self.average_rgb(sliced_pixels[1])
                avg_colour_3 = self.average_rgb(sliced_pixels[2])
                avg_colour_4 = self.average_rgb(sliced_pixels[3])
                avg_colour_5 = self.average_rgb(sliced_pixels[4])
                avg_colour_6 = self.average_rgb(sliced_pixels[5])

                draw.rectangle(xy=top_left, fill=self.nearest_colour(avg_colour_1))
                draw.rectangle(xy=top_right, fill=self.nearest_colour(avg_colour_2))
                draw.rectangle(xy=middle_left, fill=self.nearest_colour(avg_colour_3))
                draw.rectangle(xy=middle_right, fill=self.nearest_colour(avg_colour_4))
                draw.rectangle(xy=bottom_left, fill=self.nearest_colour(avg_colour_5))
                draw.rectangle(xy=bottom_right, fill=self.nearest_colour(avg_colour_6))

    def build_top_bar(self, bg_colour, txt_colour):
        ppr, ppc = self.ppr, self.ppc
        font = ImageFont.truetype(self.font_path, ppc)
        draw = ImageDraw.Draw(self.output)
        parsed_date = dateutil.parser.isoparse(self.date).strftime("%d %B, %Y")

        if txt_colour == "random":
            txt_colour = random.choice(
                [ele for ele in list(self.colours.keys()) if ele != bg_colour]
            )

        caption = [
            f"P{np.random.randint(0, 400)} {self.source['name'].upper()}",
            parsed_date,
        ]

        draw.rectangle(
            xy=((0, 0), (self.rows * ppr, 1 * ppc)), fill=self.colours[bg_colour]
        )
        draw.text((2 * ppr, 0), caption[0], font=font, fill=self.colours[txt_colour])
        draw.text(
            ((self.rows - len(caption[1]) - 1) * ppr, 0),
            caption[1],
            font=font,
            fill=self.colours[txt_colour],
        )

    def build_bottom_bar(self, bg_colour, txt_colour):
        ppr, ppc = self.ppr, self.ppc
        font = ImageFont.truetype(self.font_path, ppc)
        draw = ImageDraw.Draw(self.output)

        if txt_colour == "random":
            txt_colour = random.choice(
                [ele for ele in list(self.colours.keys()) if ele != bg_colour]
            )

        draw.rectangle(
            xy=((0, (self.cols - 2) * ppc), (self.rows * ppr, self.cols * ppc)),
            fill=self.colours[bg_colour],
        )
        draw.text(
            (0, 22 * ppc), self.title.upper(), font=font, fill=self.colours[txt_colour]
        )

    def clean_buffer(self):
        os.remove(self.image_path)

    def center_crop(self):
        w, h = self.size, self.size

        left = (w - self.size) / 2
        top = (h - self.size) / 2
        right = (w + self.size) / 2
        bottom = (h + self.size) / 2

        resized = self.image.resize((w, h))
        center_crop = resized.crop((left, top, right, bottom))

        return center_crop

    def nearest_colour(self, rgb):
        return min(
            list(self.colours.values()),
            key=lambda colour: sum((s - q) ** 2 for s, q in zip(colour, rgb)),
        )

    def avg(self, arr):
        return sum(arr) / len(arr)

    def average_rgb(self, rgbs):
        reds = []
        greens = []
        blues = []

        w, h, _ = rgbs.shape

        for x in range(w):
            for y in range(h):
                r, g, b = rgbs[x, y]
                reds.append(r)
                greens.append(g)
                blues.append(b)
        return int(self.avg(reds)), int(self.avg(greens)), int(self.avg(blues))

    def split_pixels(self, list):
        p = 2  # block row size
        q = 3  # block column size
        block_array = []

        for row_block in range(p):
            previous_row = row_block * p
            for column_block in range(q):
                previous_column = column_block * q
                block = list[
                        previous_row: previous_row + p,
                        previous_column: previous_column + q,
                        ]
                block_array.append(block)

        return np.array(block_array)
