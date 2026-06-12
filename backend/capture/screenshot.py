import os
import time
import pyautogui
from datetime import datetime


def take_screenshot(delay_seconds: int = 0):

    os.makedirs("screenshots", exist_ok=True)

    time.sleep(delay_seconds)

    filename = (
        "screenshots/"
        + datetime.now().strftime("%Y%m%d_%H%M%S")
        + ".png"
    )

    image = pyautogui.screenshot()

    image.save(filename)

    return filename
