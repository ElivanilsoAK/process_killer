from PIL import Image
import os

img = Image.open("app_icon.png")
img.save("icon.ico", format='ICO', sizes=[(256, 256)])
print("Icon converted successfully.")
