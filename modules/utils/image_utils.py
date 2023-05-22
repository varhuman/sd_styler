import os, sys
import PIL.Image as Image
import io
import base64
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

def setup_test_env():
    ext_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    if ext_root not in sys.path:
        sys.path.append(ext_root)

#读取文件地址为图片并转换为base64返回
def image_path_to_base64(image_path):
    if not image_path:
        return image_path
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def image_to_base64(image:Image):
    with io.BytesIO() as output:
        image.save(output, format="JPEG")
        contents = output.getvalue()
        return base64.b64encode(contents).decode("utf-8")

def save_base64_images_to_grids(base64_data_list, output_path, labels, images_per_row = 4):
    images = [Image.open(BytesIO(base64.b64decode(base64_data))) for base64_data in base64_data_list]
    save_images_to_grids(images, output_path, labels, images_per_row)

#grid形式多张拼接，间隙可控，可加label
def save_images_to_grids(images, output_path, labels, images_per_row=4, label_height=100, padding=20, label_font_size=80):
    # 计算拼接后的图片尺寸
    max_width = max([img.size[0] for img in images])
    max_height = max([img.size[1] for img in images])
    total_rows = (len(images) + images_per_row - 1) // images_per_row
    images_in_last_row = len(images) % images_per_row or images_per_row
    total_width = max_width * min(images_per_row, len(images)) + (min(images_per_row, len(images)) - 1) * padding
    total_height = (max_height + label_height) * total_rows + (total_rows - 1) * padding

    # 创建一个空白画布，用于绘制拼接后的图片
    canvas = Image.new("RGB", (total_width, total_height), color=(255, 255, 255))

    # 设置字体和字体大小
    font = ImageFont.truetype("arial.ttf", size=label_font_size)
    draw = ImageDraw.Draw(canvas)

    # 将每张图片及其对应的标签放置到合适的位置
    for i, (image, label) in enumerate(zip(images, labels)):
        x = (i % images_per_row) * (max_width + padding)
        y = (i // images_per_row) * (max_height + label_height + padding)
        canvas.paste(image, (x, y + label_height))

        # 计算文本的宽度，以将其居中放置在图片上方
        text_width, _ = draw.textsize(label, font=font)
        text_x = x + (max_width - text_width) // 2
        draw.text((text_x, y), label, font=font, fill=(0, 0, 0))

    output_path = output_path + ".jpg"
    canvas.save(output_path)

#横向多张图片拼接，无间隙
def merge_images_horizontally(base64_data_list, images_per_row, output_path):
    images = [Image.open(BytesIO(base64.b64decode(base64_data))) for base64_data in base64_data_list]
    # 获取每张图片的宽度和高度
    img_width, img_height = images[0].size

    # 计算合并后图片的总宽度
    total_width = img_width * images_per_row

    # 计算合并后图片的总高度
    total_height = img_height * ((len(images) - 1) // images_per_row + 1)

    # 创建一个新的空白图片，用于存放合并后的图片
    merged_image = Image.new("RGB", (total_width, total_height))

    # 遍历图片列表，将每张图片粘贴到新创建的空白图片中
    for index, image in enumerate(images):
        x = img_width * (index % images_per_row)
        y = img_height * (index // images_per_row)
        merged_image.paste(image, (x, y))

    output_path = output_path + ".jpg"
    # 保存合并后的图片
    merged_image.save(output_path)
    return merged_image
