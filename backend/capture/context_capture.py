from datetime import datetime
import time

from .active_window import get_active_window
from .clipboard import get_clipboard_text
from .app_name import get_active_app
from .screenshot import take_screenshot


def capture_context(delay_seconds: int = 5):

    if delay_seconds > 0:
        time.sleep(delay_seconds)

    window_data = get_active_window()
    clipboard_data = get_clipboard_text()
    app_data = get_active_app()

    return {

        "sourceApp":
        app_data["sourceApp"],

        "windowTitle":
        window_data["windowTitle"],

        "timestamp":
        datetime.now().isoformat(),

        "contextSource":
        "clipboard",

        "rawContext":
        clipboard_data["clipboardText"],

        "url":
        "",

        "sessionId":
        "sess_001",

        "screenshot":
        take_screenshot(delay_seconds=0)
    }