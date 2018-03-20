import io
import qrcode

from os import path
from PIL import Image


_static_path = path.join(path.dirname(path.dirname(__file__)), '.uibuild')


def generate(s):
  qr = qrcode.QRCode(version=1,
                     error_correction=qrcode.constants.ERROR_CORRECT_Q,
                     box_size=10,
                     border=2)
  qr.add_data(s)
  qr.make(fit=True)
  img = qr.make_image().convert('RGBA')
  img_w, img_h = img.size
  with Image.open(path.join(_static_path, 'icon.png')) as icon:
    factor = 4
    size_w = img_w // factor
    size_h = img_h // factor
    icon_w, icon_h = icon.size
    if icon_w > size_w:
      icon_w = size_w
    if icon_h > size_h:
      icon_h = size_h
    icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
    w = (img_w - icon_w) // 2
    h = (img_h - icon_h) // 2
    img.paste(icon, (w, h), icon)
    with io.BytesIO() as buffer:
      img.save(buffer, 'PNG')
      img.close()
      return buffer.getvalue()
