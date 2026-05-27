# Project Review And Optimization Plan

## Current Shape

The project is now structured as a public, reusable service bundle:

- receiver runner in `bin/meteo-rtl433-runner.sh`
- Weather Underground uploader in `bin/weather-underground-upload.py`
- systemd units in `systemd/`
- configuration examples in `config/`
- public-safe install and operation docs in `docs/`

Server-specific recovery notes, private SSH details, captured diagnostics, and one-off legacy scripts should stay out of this repository.

## Strengths

- `rtl_433` is isolated as a single long-running service, so only one process owns the dongle.
- Weather Underground upload runs separately as a timer, so upload failures do not restart the receiver.
- The uploader has stale-data protection and will not resend old readings after receiver failure.
- Secrets are loaded from `/etc/meteo-rtl-sdr/weather-underground.env`, not from code.
- CSV and JSONL outputs can run in parallel, which supports both legacy and newer integrations.

## Risks To Watch

- CSV field names vary by `rtl_433` version and decoded device type.
- systemd unit user/group names must match the install guide.
- `RTL433_BIN=rtl_433` depends on systemd PATH; production installs should prefer an absolute path if distribution defaults differ.
- Weather Underground rain calculations are based on cumulative rain fields when present; stations with different rain semantics may need model-specific mapping.
- The project does not yet include automated tests for CSV parsing and stale-data behavior.

## Recommended Optimizations

1. Add parser tests with representative `rtl_433` CSV samples.
2. Add an installer script that renders systemd units with configurable user and install prefix.
3. Prefer JSONL ingestion for new upload/integration code, then keep CSV only for compatibility.
4. Add logrotate packaging for `/var/lib/meteo-rtl-sdr/*.csv` and `*.jsonl`.
5. Add a health-check command that reports dongle visibility, service state, latest packet age, and last upload result.
6. Add optional MQTT output examples for Home Assistant or other consumers.

## Public Repository Rules

Do not commit:

- real station IDs if they identify a private installation
- WU passwords or API keys
- SSH hosts, usernames, private IPs, or recovery transcripts
- captured production logs
- local diagnostics output

Keep those details in private deployment notes or in `/etc/meteo-rtl-sdr/*.env` on the target host.
