"""Stream type classes for tap-freshservice."""
from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_freshservice.client import FreshserviceStream
from tap_freshservice.streams.assets import AssetsStream

class LocationsStream(FreshserviceStream):
    name = "locations"
    path = "/locations"
    records_jsonpath="$.locations[*]"

    def get_url(self, context: dict):
        url = super().get_url(context)
        return url
    
    def build_prepared_request(self, *args, **kwargs):
        req = super().build_prepared_request(*args, **kwargs)
        return req

    schema = th.PropertiesList(
        th.Property("address", th.StringType),
        th.Property("contact_name", th.StringType),
        th.Property("created_at", th.DateTimeType),
        th.Property("email", th.StringType),
        th.Property("id", th.IntegerType),
        th.Property("name", th.StringType),
        th.Property("parent_location_id", th.IntegerType),
        th.Property("phone", th.StringType),
        th.Property("primary_contact_id", th.IntegerType),
        th.Property("updated_at", th.DateTimeType)
     ).to_dict()