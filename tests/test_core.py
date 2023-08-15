"""Tests standard tap features using the built-in SDK tests library."""

import datetime

from singer_sdk.testing import get_tap_test_class

from tap_freshservice.tap import TapFreshservice


SAMPLE_CONFIG = {
    "api_key": "testing",
    "url_base": "https://testing.com"
}


# Run standard built-in tap tests from the SDK:
TestTapFreshservice = get_tap_test_class(
    tap_class=TapFreshservice,
    config=SAMPLE_CONFIG,
)

