# tap-freshservice

`tap-freshservice` is a Singer tap for Freshservice.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps.

## Installation

Install from PyPi:

```bash
pipx install tap-freshservice
```

Install from GitHub:

```bash
pipx install git+https://github.com/Datateer/tap-freshservice.git@main
```


## Configuration

### Settings

| Setting | Required | Default | Description |
|:--------|:--------:|:-------:|:------------|
| api_key | True | None | The Freshservice API key |
| url_base | True | `https://<your org>.freshservice.com/api/v2` | The Freshservice API base URL |
| ticket_lookback_days | False | `45` | Days of ticket `updated_at` history to request on each full sync. Sent as Freshservice `updated_since`. Child streams only run for tickets in this window. |
| request_delay_seconds | False | `1.0` | Minimum seconds to wait between API requests. Increase if you see 429 rate-limit errors. |
| stream_maps | False | None | Config object for stream maps. See [Stream Maps](https://sdk.meltano.com/en/latest/stream_maps.html). |
| stream_map_config | False | None | User-defined config values for map expressions. |
| flattening_enabled | False | None | `true` to enable schema flattening and expand nested properties. |
| flattening_max_depth | False | None | Max depth to flatten schemas. |
| batch_config | False | None | Configuration for BATCH message capabilities. |

### Replication behavior

All streams use **full-table** replication. There is no Singer incremental mode.

Each run requests tickets whose `updated_at` falls within the configured
`ticket_lookback_days` window (default 45). That value is sent to Freshservice as
the `updated_since` query parameter. Child streams such as `time_entries` run only
for tickets returned in that window.

Note: `updated_since` filters on ticket `updated_at` only. It does not reflect
activity such as new time entries when the ticket itself was not updated.

### Large Singer messages (Meltano line size limit)

Meltano limits each tap output line to **half of `elt.buffer_size`** (default 50 MiB).
If a run fails with `Output line length limit exceeded`, a single `RECORD` or `SCHEMA`
line is too large.

Common causes in this tap:

- `tickets` with `flattening_enabled: true` (large nested schemas)
- `tickets` fields such as `description` / `description_text` (large HTML bodies)

Fixes, in order of preference:

1. **Keep flattening off** for API extraction (recommended for `time_entries`-only jobs)
2. **Exclude large ticket fields** with stream maps when syncing `tickets`
3. **Raise the Meltano buffer** if large records are expected:

```yaml
elt:
  buffer_size: 209715200  # 200 MiB → 100 MiB max line size
```

Or: `meltano config set meltano elt.buffer_size 209715200`

### Example Meltano config

```yaml
plugins:
  extractors:
    - name: tap-freshservice
      config:
        api_key: $TAP_FRESHSERVICE_API_KEY
        url_base: https://your-org.freshservice.com/api/v2
        ticket_lookback_days: 45
        request_delay_seconds: 1.0
```

### Supported Python versions

Python 3.10–3.13

### Capabilities

`catalog`, `discover`, `stream-maps`, `schema-flattening`, `batch`, and others. Run `tap-freshservice --about` for the full list.

A full list of supported settings and capabilities is available by running:

```bash
tap-freshservice --about
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

## Usage

You can easily run `tap-freshservice` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-freshservice --version
tap-freshservice --help
tap-freshservice --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-freshservice` CLI interface directly using `poetry run`:

```bash
poetry run tap-freshservice --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-freshservice
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-freshservice --version
# OR run a test `elt` pipeline:
meltano elt tap-freshservice target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.
