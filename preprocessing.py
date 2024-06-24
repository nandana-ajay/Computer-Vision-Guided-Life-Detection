from PIL import Image
from werkzeug.utils import secure_filename
import os

def preprocess_image(imagepath):
  image = Image.open(imagepath)
  image=image.resize((640, 640))
  exif = image.getexif()
  orientation = exif.get(0x0112)
  if orientation == 1:
    pass
  elif orientation == 3:
    image = image.rotate(180, expand=True)
  elif orientation == 6:
    image = image.rotate(-90, expand=True)
  elif orientation == 8:
    image = image.rotate(90, expand=True)
  image = image.convert('RGB')

  # Save the processed image to the specified path
  image.save(imagepath)

  # Return the processed image object and the path where it's saved
  return image



