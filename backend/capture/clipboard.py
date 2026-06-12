import pyperclip


def get_clipboard_text():

    try:
        text = pyperclip.paste()

        return {
            "clipboardText": text
        }

    except Exception:

        return {
            "clipboardText": ""
        }