"""REST client handling, including FreshserviceStream base class."""

from __future__ import annotations

import time
from functools import cached_property
from typing import Any
from urllib.parse import parse_qsl

import backoff
import requests
from requests.auth import HTTPBasicAuth
from singer_sdk.exceptions import RetriableAPIError
from singer_sdk.pagination import BaseAPIPaginator  # noqa: TCH002
from singer_sdk.streams import RESTStream

from tap_freshservice.paginator import FreshservicePaginator


class FreshserviceStream(RESTStream):
    """Freshservice stream class."""

    _last_request_at: float = 0.0

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("url_base")

    @cached_property
    def authenticator(self) -> HTTPBasicAuth:
        """Return HTTP basic auth for the Freshservice API key."""
        return HTTPBasicAuth(
            username=str(self.config["api_key"]),
            password="X",
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = super().http_headers
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        return headers

    def _throttle(self) -> None:
        """Pace requests to reduce Freshservice 429 rate-limit errors."""
        delay = float(self.config.get("request_delay_seconds", 1.0))
        if delay <= 0:
            return

        elapsed = time.monotonic() - FreshserviceStream._last_request_at
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def _request(
        self,
        prepared_request: requests.PreparedRequest,
        context: dict | None,
    ) -> requests.Response:
        self._throttle()
        try:
            return super()._request(prepared_request, context)
        finally:
            FreshserviceStream._last_request_at = time.monotonic()

    def backoff_wait_generator(self):
        """Retry using Retry-After when present, otherwise wait 10 seconds."""
        return backoff.constant(interval=10)

    def backoff_handler(self, details: dict) -> None:
        """Log backoff details and honor Retry-After on 429 responses."""
        exception = details.get("exception")
        if isinstance(exception, RetriableAPIError) and exception.response is not None:
            retry_after = exception.response.headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                time.sleep(int(retry_after))

        super().backoff_handler(details)

    def backoff_max_tries(self) -> int:
        """Retry for up to one minute when rate limited."""
        return 6

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Create a new pagination helper instance.

        Returns:
            A pagination helper instance.
        """
        return FreshservicePaginator()

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,  # noqa: ANN401
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        # 100 is the max page size https://api.freshservice.com/#pagination
        params: dict = {"per_page": "100"}
        if next_page_token:
            params["page"] = dict(parse_qsl(next_page_token.query)).get("page")

        return params

    def post_process(
        self,
        row: dict,
        context: dict | None = None,
    ) -> dict | None:
        """Truncate oversized string fields so Singer messages stay within limits."""
        row = super().post_process(row, context)
        if row is None:
            return None

        max_field_bytes = int(self.config.get("max_field_bytes", 1_048_576))
        if max_field_bytes <= 0:
            return row

        return self._truncate_values(row, max_field_bytes)

    @staticmethod
    def _truncate_values(value: Any, max_field_bytes: int) -> Any:
        if isinstance(value, str):
            encoded = value.encode("utf-8")
            if len(encoded) <= max_field_bytes:
                return value
            truncated = encoded[:max_field_bytes].decode("utf-8", errors="ignore")
            return f"{truncated}...[truncated]"

        if isinstance(value, dict):
            return {
                key: FreshserviceStream._truncate_values(item, max_field_bytes)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                FreshserviceStream._truncate_values(item, max_field_bytes)
                for item in value
            ]

        return value
