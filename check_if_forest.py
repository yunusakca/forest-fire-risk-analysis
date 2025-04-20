import requests
from io import BytesIO
from PIL import Image
import cv2
import numpy as np
from calculate_coordinates import parse_dms_string
from dotenv import load_dotenv
import os

def check_if_forest(dms_string):

    load_dotenv()
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    coords = parse_dms_string(dms_string)
    latitude, longitude = coords[0], coords[1]

    url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=15&size=640x640&maptype=satellite&key={API_KEY}"
    response = requests.get(url)

    Image.open(BytesIO(response.content)).save("downloaded_satellite_image.png")

    image = cv2.imread("downloaded_satellite_image.png")

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = np.array([25, 20, 20])
    upper_green = np.array([100, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    green_ratio = np.count_nonzero(mask) / mask.size * 100
    print(f"Yeşil alan oranı: {green_ratio:.2f}%")

    is_forest = green_ratio > 30
    
    return {"green_ratio": green_ratio, "is_forest": is_forest}
