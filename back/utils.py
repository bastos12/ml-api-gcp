import numpy as np

def image_to_array(image):
    image_array = np.fromstring(image.read(), np.uint8)
    return image_array