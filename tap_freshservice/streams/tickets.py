"""Stream type classes for tap-freshservice."""

from __future__ import annotations

import typing as t
from datetime import datetime, timedelta, timezone
from typing import Optional

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_freshservice.client import FreshserviceStream


class TicketsStream(FreshserviceStream):
    """Tickets are synced as full-table with an optional API list window.

    Freshservice exposes ``updated_since`` only as a tickets list query parameter.
    It filters on ticket ``updated_at`` and does not reflect child-stream activity
    such as new time entries, so this stream does not use Singer incremental mode.
    """

    name = "tickets"
    path = "/tickets"
    records_jsonpath = "$.tickets[*]"

    def get_url_params(
        self,
        context: dict | None,
        next_page_token,
    ) -> dict[str, t.Any] | str:
        params = {"include": "stats,tags"}
        params.update(super().get_url_params(context, next_page_token))

        updated_since = self._resolve_updated_since_filter()
        params["updated_since"] = updated_since.isoformat()

        return params

    def _resolve_updated_since_filter(self) -> datetime:
        """Return the tickets list ``updated_since`` filter."""
        lookback_days = int(self.config.get("ticket_lookback_days", 45))
        return datetime.now(timezone.utc) - timedelta(days=lookback_days)

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for the child streams."""
        return {"ticket_id": record["id"]}

    schema = th.PropertiesList(
        th.Property("subject", th.StringType),
        th.Property("group_id", th.IntegerType),
        th.Property("department_id", th.IntegerType),
        th.Property("workspace_id", th.IntegerType),
        th.Property("category", th.StringType),
        th.Property("sub_category", th.StringType),
        th.Property("item_category", th.StringType),
        th.Property("requester_id", th.IntegerType),
        th.Property("responder_id", th.IntegerType),
        th.Property("due_by", th.StringType),
        th.Property("fr_escalated", th.BooleanType),
        th.Property("deleted", th.BooleanType),
        th.Property("spam", th.BooleanType),
        th.Property("email_config_id", th.IntegerType),
        th.Property("fwd_emails", th.StringType),
        th.Property("reply_cc_emails", th.StringType),
        th.Property("cc_emails", th.StringType),
        th.Property("is_escalated", th.BooleanType),
        th.Property("fr_due_by", th.StringType),
        th.Property("id", th.IntegerType),
        th.Property("priority", th.IntegerType),
        th.Property("status", th.IntegerType),
        th.Property("source", th.IntegerType),
        th.Property("created_at", th.DateTimeType),
        th.Property("updated_at", th.DateTimeType),
        th.Property("requested_for_id", th.IntegerType),
        th.Property("to_emails", th.StringType),
        th.Property("type", th.StringType),
        th.Property("description", th.StringType),
        th.Property("description_text", th.StringType),
        th.Property("custom_fields", th.ObjectType(
            th.Property("credit_hrs", th.StringType),
            th.Property("estimate", th.StringType),
            th.Property("pending_reason", th.StringType),
            th.Property("quote_hrs", th.StringType),
            th.Property("definition_of_done", th.StringType),
            th.Property("company_division", th.StringType)
        )),
        th.Property("stats", th.ObjectType(
            th.Property("created_at", th.DateTimeType),
            th.Property("updated_at", th.DateTimeType),
            th.Property("ticket_id", th.IntegerType),
            th.Property("opened_at", th.DateTimeType),
            th.Property("group_escalated", th.BooleanType),
            th.Property("inbound_count", th.IntegerType),
            th.Property("status_updated_at", th.DateTimeType),
            th.Property("outbound_count", th.IntegerType),
            th.Property("pending_since", th.StringType),
            th.Property("resolved_at", th.DateTimeType),
            th.Property("closed_at", th.DateTimeType),
            th.Property("first_assigned_at", th.DateTimeType),
            th.Property("assigned_at", th.DateTimeType),
            th.Property("agent_responded_at", th.DateTimeType),
            th.Property("requester_responded_at", th.DateTimeType),
            th.Property("first_responded_at", th.DateTimeType),
            th.Property("first_resp_time_in_secs", th.IntegerType),
            th.Property("resolution_time_in_secs", th.IntegerType),
        )),
        th.Property("tags", th.StringType)
    ).to_dict()
