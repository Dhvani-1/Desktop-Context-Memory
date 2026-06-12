import time

from capture.context_capture import capture_context
from ai.groq_service import classify_context
from services.save_memory import save_memory


def auto_capture():

    while True:

        try:

            print("Capturing...")

            context = capture_context()

            memory = classify_context(
                context
            )

            memory_id = save_memory(
                context,
                memory
            )

            print(
                f"Saved memory {memory_id}"
            )

        except Exception as e:

            print(
                "Error:",
                e
            )

        # Wait 5 seconds
        time.sleep(5)


auto_capture()