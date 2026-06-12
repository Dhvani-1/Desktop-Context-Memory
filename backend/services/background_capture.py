import time
import threading
from datetime import datetime

from capture.context_capture import capture_context
from ai.groq_service import classify_context
from services.save_memory import save_memory
from services.sensitive_detector import detect_and_mask_sensitive_data, extract_ocr_text_from_screenshot, check_sensitivity_rules


class BackgroundCaptureManager:
    def __init__(self):
        self.is_active = True
        self.last_capture_time = None
        self.thread = None
        self._stop_event = threading.Event()
        self.lock = threading.Lock()

    def start(self):
        with self.lock:
            if self.thread is not None and self.thread.is_alive():
                print("Background Capture is already running.")
                return
            self._stop_event.clear()
            self.thread = threading.Thread(target=self._loop, daemon=True)
            self.thread.start()
            print("Background Capture Thread started.")

    def pause(self):
        with self.lock:
            self.is_active = False
            print("Background Capture paused.")

    def resume(self):
        with self.lock:
            self.is_active = True
            print("Background Capture resumed.")

    def get_status(self):
        with self.lock:
            return {
                "is_active": self.is_active,
                "last_capture_time": self.last_capture_time
            }

    def _loop(self):
        while not self._stop_event.is_set():
            # Sleep in 1-second intervals to allow fast pause/resume responsiveness
            for _ in range(20):
                if self._stop_event.is_set():
                    break
                time.sleep(1)

            # Check if active
            with self.lock:
                active = self.is_active
            if not active:
                continue

            try:
                print("Running background context capture...")

                # 1. Capture context instantly (delay_seconds = 0)
                context = capture_context(delay_seconds=0)

                title = context.get("windowTitle", "")
                if any(keyword in title for keyword in ["Totem", "Question Answering", "localhost:5173", "127.0.0.1:5173"]):
                    print(f"Skipping background capture: active window is Totem dashboard/QA ({title})")
                    continue

                # 2. Extract OCR from screenshot using Groq Vision model
                ocr_text = extract_ocr_text_from_screenshot(context.get("screenshot"))

                # 3. Detect and mask sensitive credentials
                has_sens_win, masked_win = detect_and_mask_sensitive_data(context.get("windowTitle", ""))
                has_sens_clip, masked_clip = detect_and_mask_sensitive_data(context.get("rawContext", ""))
                has_sens_ocr, masked_ocr = detect_and_mask_sensitive_data(ocr_text)

                # Pre-mask context inputs
                context["windowTitle"] = masked_win
                context["rawContext"] = masked_clip

                # 4. Classify context using Groq Llama 3.3
                memory = classify_context(context)

                # Mask sensitive data in summary if generated
                has_sens_sum, masked_sum = detect_and_mask_sensitive_data(memory.get("summary", ""))
                memory["summary"] = masked_sum

                # Run custom sensitivity rules
                is_sensitive, sensitivity_reason = check_sensitivity_rules(masked_win, masked_clip, masked_ocr, masked_sum)

                # Combine with regex match indicators
                regex_sensitive = has_sens_win or has_sens_clip or has_sens_ocr or has_sens_sum
                if regex_sensitive and not is_sensitive:
                    is_sensitive = True
                    sensitivity_reason = "Possible credentials or keys detected"
                    print(f"[Sensitive] {sensitivity_reason}")
                    print("[Sensitive] Save blocked until user confirmation")

                pending_confirmation = 0
                if is_sensitive:
                    memory["sensitivity"] = "High"
                    pending_confirmation = 1

                # 6. Save memory context to database
                memory_id = save_memory(
                    context, 
                    memory, 
                    pending_confirmation=pending_confirmation,
                    sensitivity_reason=sensitivity_reason if is_sensitive else None
                )
                print(f"Background capture saved memory ID #{memory_id} (pending={pending_confirmation})")

                # Update timestamp
                with self.lock:
                    self.last_capture_time = datetime.now().isoformat()

            except Exception as e:
                print(f"Error in background capture execution loop: {e}")


# Singleton instance
background_capture_manager = BackgroundCaptureManager()
