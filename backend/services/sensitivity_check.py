SENSITIVE_KEYWORDS = [

    "password",
    "api_key",
    "secret",
    "token",
    "private key",
    "access key",
    "credit card"

]


def is_sensitive(text):

    text = text.lower()

    for keyword in SENSITIVE_KEYWORDS:

        if keyword in text:

            return True

    return False