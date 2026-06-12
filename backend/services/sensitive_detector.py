import re
import base64
import os
from ai.groq_service import client

# Patterns for sensitive data detection
OPENAI_KEY_PATTERN = re.compile(r'\bsk-[a-zA-Z0-9]{32,}\b')
GROQ_KEY_PATTERN = re.compile(r'\bgsk_[a-zA-Z0-9]{40,}\b')
GOOGLE_KEY_PATTERN = re.compile(r'\bAIzaSy[a-zA-Z0-9_-]{33}\b')
PRIVATE_KEY_PATTERN = re.compile(r'-----BEGIN [A-Z ]+ PRIVATE KEY-----[ \t]*\n[\s\S]+?\n[ \t]*-----END [A-Z ]+ PRIVATE KEY-----')
PASSWORD_ASSIGNMENT_PATTERN = re.compile(r'(?i)\b(password|passwd|secret_key|pwd)\b\s*[:=]\s*(["\']?)([^"\s\']{4,})\2')
CREDIT_CARD_CANDIDATE_PATTERN = re.compile(r'\b(?:\d[ -]*?){13,19}\b')


def is_luhn_valid(digits: str) -> bool:
    """Validate a digit string using the Luhn algorithm."""
    total = 0
    reverse_digits = digits[::-1]
    for i, digit in enumerate(reverse_digits):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def detect_and_mask_sensitive_data(text: str) -> tuple[bool, str]:
    """
    Detect passwords, API keys, tokens, private keys, and credit cards.
    Returns (has_sensitive_data, masked_text).
    """
    if not text:
        return False, text

    has_sensitive = False
    masked = text

    # 1. API Keys & Tokens
    if OPENAI_KEY_PATTERN.search(masked):
        has_sensitive = True
        masked = OPENAI_KEY_PATTERN.sub("[MASKED_API_KEY]", masked)

    if GROQ_KEY_PATTERN.search(masked):
        has_sensitive = True
        masked = GROQ_KEY_PATTERN.sub("[MASKED_API_KEY]", masked)

    if GOOGLE_KEY_PATTERN.search(masked):
        has_sensitive = True
        masked = GOOGLE_KEY_PATTERN.sub("[MASKED_API_KEY]", masked)

    # 2. Private Keys
    if PRIVATE_KEY_PATTERN.search(masked):
        has_sensitive = True
        masked = PRIVATE_KEY_PATTERN.sub("[MASKED_PRIVATE_KEY]", masked)

    # 3. Passwords / Secret fields
    if PASSWORD_ASSIGNMENT_PATTERN.search(masked):
        has_sensitive = True
        def mask_pass(m):
            key = m.group(1)
            quote = m.group(2)
            return f"{key} = {quote}[MASKED_PASSWORD]{quote}"
        masked = PASSWORD_ASSIGNMENT_PATTERN.sub(mask_pass, masked)

    # 4. Credit Cards
    for match in CREDIT_CARD_CANDIDATE_PATTERN.finditer(masked):
        candidate = match.group(0)
        digits = re.sub(r'\D', '', candidate)
        if 13 <= len(digits) <= 19:
            if is_luhn_valid(digits):
                has_sensitive = True
                masked = masked.replace(candidate, "[MASKED_FINANCIAL_INFO]")

    return has_sensitive, masked


def extract_ocr_text_from_screenshot(screenshot_path: str) -> str:
    """
    Send the screenshot to Groq using llama-3.2-11b-vision-preview to perform OCR.
    Returns the extracted text, or an empty string on error.
    """
    if not screenshot_path or not os.path.exists(screenshot_path):
        return ""

    try:
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        response = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Extract all readable text from this screenshot. Return ONLY the raw extracted text, with no preamble, formatting, markdown code blocks, or comments."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0,
            max_tokens=1024
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Groq OCR Vision extraction failed: {e}")
        return ""


def check_sensitivity_rules(window_title: str, clipboard_text: str, ocr_text: str, summary: str) -> tuple[bool, str]:
    """
    Check if the context details contain actual secret patterns (API keys, private keys, passwords, CCs).
    Returns (is_sensitive, sensitivity_reason).
    """
    has_win, _ = detect_and_mask_sensitive_data(window_title)
    has_clip, _ = detect_and_mask_sensitive_data(clipboard_text)
    has_ocr, _ = detect_and_mask_sensitive_data(ocr_text)
    has_sum, _ = detect_and_mask_sensitive_data(summary)

    if has_win or has_clip or has_ocr or has_sum:
        reason = "API key, private key, credit card, or password assignment found"
        print(f"[Sensitive] {reason}")
        print("[Sensitive] Save blocked until user confirmation")
        return True, reason

    return False, ""
