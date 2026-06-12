import pygetwindow as gw


def get_active_app():
    try:
        window = gw.getActiveWindow()

        if window:

            title = window.title

            if "Visual Studio Code" in title:
                return {"sourceApp": "Visual Studio Code"}

            elif "Chrome" in title:
                return {"sourceApp": "Google Chrome"}

            elif "Edge" in title:
                return {"sourceApp": "Microsoft Edge"}

            else:
                return {"sourceApp": "Unknown"}

        return {"sourceApp": "Unknown"}

    except Exception:
        return {"sourceApp": "Unknown"}