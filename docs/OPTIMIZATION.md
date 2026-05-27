# Optimization Notes

## Recommended Architecture

Use one long-running receiver service and one separate uploader timer:

- `rtl433.service` owns the RTL-SDR dongle and writes decoded packets
- `weather-underground.timer` starts an upload job every few minutes
- uploader validates freshness before sending

This avoids running multiple SDR processes and makes failures visible through systemd.

## Prefer JSONL For New Integrations

CSV is convenient for legacy scripts, but JSONL is safer for downstream parsing because fields can vary by device model.

Recommended outputs:

```sh
RTL433_ENABLE_CSV=1
RTL433_ENABLE_JSON=1
```

## Narrow Protocols After Discovery

During setup, keep `RTL433_PROTOCOLS` empty for autodetection. After identifying your weather station protocol, set only the required protocol IDs to reduce noise and CPU use.

Example:

```sh
RTL433_PROTOCOLS="32"
```

Use `rtl_433 -R help` to list protocols.

## Gain And Frequency

Start with automatic gain. If reception is weak or noisy, test fixed gain values in `RTL433_EXTRA_ARGS`.

Examples:

```sh
RTL433_EXTRA_ARGS="-Y classic -g 20"
RTL433_EXTRA_ARGS="-Y classic -g 0"
```

Some sensors are slightly offset from nominal frequency. Use foreground tests with `-M level` to inspect received packet frequency estimates.

## Log Rotation

For continuously appended CSV/JSONL files, configure logrotate:

```text
/var/lib/meteo-rtl-sdr/*.csv /var/lib/meteo-rtl-sdr/*.jsonl {
    daily
    rotate 14
    compress
    missingok
    notifempty
    copytruncate
}
```

Save as `/etc/logrotate.d/meteo-rtl-sdr`.

## Health Monitoring

Useful checks:

- systemd service state
- age of latest decoded packet
- Weather Underground upload result
- USB enumeration of the RTL-SDR dongle

A monitoring script should check packet age, not only whether `rtl433.service` is running.
