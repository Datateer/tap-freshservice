"""Freshservice tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_freshservice.streams import (agents, assets, asset_types, asset_requests, departments, groups, locations, requesters, tickets, time_entries, ticket_activities)


class TapFreshservice(Tap):
    """Freshservice tap class."""

    name = "tap-freshservice"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="The Freshservice API key",
        ),
        th.Property(
            "ticket_lookback_days",
            th.IntegerType,
            description=(
                "Number of days of ticket updated_at history to request on each run. "
                "Sent to Freshservice as the updated_since query parameter. Child "
                "streams such as time_entries only run for tickets returned in this "
                "window."
            ),
            default=45,
        ),
        th.Property(
            "url_base",
            th.StringType,
            required=True,
            default="https://<replace with your org>.freshservice.com/api/v2",
            description="The url for the Freshservice API",
        ),
        th.Property(
            "request_delay_seconds",
            th.NumberType,
            description=(
                "Minimum seconds to wait between API requests. Increase this if you "
                "see 429 rate-limit errors, especially on child streams like "
                "time_entries."
            ),
            default=1.0,
        ),
    ).to_dict()

    def discover_streams(self) -> list[tickets.FreshserviceStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            agents.AgentsStream(self),
            assets.AssetsStream(self),
            asset_types.AssetTypesStream(self),
            asset_requests.AssetRequestsStream(self),
            departments.DepartmentsStream(self),
            groups.GroupsStream(self),
            locations.LocationsStream(self),
            requesters.RequestersStream(self),
            tickets.TicketsStream(self),
            time_entries.TimeEntriesStream(self),
            ticket_activities.TicketActivitiesStream(self),
        ]


if __name__ == "__main__":
    TapFreshservice.cli()
