import importlib.util
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


SCRIPT = Path(__file__).with_name("yt-qa.py")
SPEC = importlib.util.spec_from_file_location("yt_qa", SCRIPT)
yt_qa = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(yt_qa)


def video(upload_status: str, processing_status: str, **status) -> dict:
    return {
        "status": {"uploadStatus": upload_status, **status},
        "processingDetails": {"processingStatus": processing_status},
    }


class WaitForProcessingTest(unittest.TestCase):
    def test_waits_until_processing_succeeds(self):
        responses = [
            video("uploaded", "processing"),
            video("processed", "succeeded"),
        ]
        with (
            patch.object(yt_qa, "fetch", side_effect=responses),
            patch.object(yt_qa.time, "monotonic", return_value=0),
            patch.object(yt_qa.time, "sleep") as sleep,
        ):
            result, quota = yt_qa.wait_for_processing(Mock(), "video-id")

        self.assertEqual(result, responses[-1])
        self.assertEqual(quota, 2)
        sleep.assert_called_once_with(15)

    def test_stops_on_terminal_processing_failure(self):
        failed = video("failed", "failed", failureReason="invalidFile")
        with (
            patch.object(yt_qa, "fetch", return_value=failed),
            patch.object(yt_qa.time, "monotonic", return_value=0),
            patch.object(yt_qa.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(RuntimeError, "invalidFile"):
                yt_qa.wait_for_processing(Mock(), "video-id")

        sleep.assert_not_called()

    def test_times_out_without_detaching_work(self):
        processing = video("uploaded", "processing")
        with (
            patch.object(yt_qa, "fetch", return_value=processing),
            patch.object(yt_qa.time, "monotonic", side_effect=[0, 31]),
            patch.object(yt_qa.time, "sleep") as sleep,
        ):
            with self.assertRaisesRegex(TimeoutError, "30 seconds"):
                yt_qa.wait_for_processing(
                    Mock(), "video-id", timeout_seconds=30, poll_seconds=5
                )

        sleep.assert_not_called()


if __name__ == "__main__":
    unittest.main()
