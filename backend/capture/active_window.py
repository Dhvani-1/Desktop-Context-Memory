import pygetwindow as gw


def get_active_window():

    try:
        window = gw.getActiveWindow()

        if window:
            return {
                "windowTitle": window.title
            }

        return {
            "windowTitle": "Unknown"
        }

    except Exception as e:
        return {
            "windowTitle": str(e)
        }