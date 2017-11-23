from PIL import ImageStat
from PIL import Image

def get_image_brightness(image_path):
    img = Image.open(image_path).convert('L')
    stat = ImageStat.Stat(img)
    return stat.mean[0]


