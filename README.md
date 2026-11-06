# Meteo RTL-SDR

Generic Linux project for receiving weather-station data with `rtl_433` and an RTL-SDR USB dongle, storing decoded packets, and optionally uploading current readings to Weather Underground.

The repository is intentionally public-safe:

- no hostnames, private IP addresses, SSH instructions, or recovery notes
- no station passwords or API keys
- no captured diagnostics or production logs
- configuration is provided through `.env` files

## What It Provides

- `rtl_433` runner with configurable binary path, frequency, outputs, and extra arguments
- systemd service for continuous reception
- optional systemd timer for Weather Underground uploads
- freshness guard so stale sensor data is not uploaded after receiver failures
- install and operations documentation

## Quick Start

1. Install `rtl_433` and RTL-SDR userspace tools.
2. Copy this project to `/opt/meteo-rtl-sdr`.
3. Copy and edit configuration:

   ```sh
   sudo mkdir -p /etc/meteo-rtl-sdr
   sudo cp config/rtl_433.env /etc/meteo-rtl-sdr/rtl_433.env
   sudo cp config/weather-underground.env.example /etc/meteo-rtl-sdr/weather-underground.env
   sudo editor /etc/meteo-rtl-sdr/rtl_433.env
   sudo editor /etc/meteo-rtl-sdr/weather-underground.env
   ```

4. Install and start systemd units:

   ```sh
   sudo cp systemd/rtl433.service /etc/systemd/system/
   sudo cp systemd/weather-underground.service /etc/systemd/system/
   sudo cp systemd/weather-underground.timer /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now rtl433.service
   sudo systemctl enable --now weather-underground.timer
   ```

See [docs/INSTALL.md](docs/INSTALL.md) for a full installation guide and [docs/OPERATIONS.md](docs/OPERATIONS.md) for day-to-day commands.

For design review and recommended hardening work, see [docs/REVIEW.md](docs/REVIEW.md).

## Repository Layout

- `bin/meteo-rtl433-runner.sh` - starts `rtl_433` from env configuration
- `bin/weather-underground-upload.py` - uploads the latest fresh CSV reading to WU
- `config/*.env*` - configuration examples
- `systemd/*.service`, `systemd/*.timer` - systemd units
- `docs/` - install, operations, troubleshooting, and optimization notes

## Security Notes

Never commit your real Weather Underground password/API key. Put secrets only in `/etc/meteo-rtl-sdr/weather-underground.env` and keep that file mode `0600`.

## License

MIT, see [LICENSE](LICENSE).

## Integrace se serverem

[Integrace se serverem a dohled aplikací](docs/server-integration.md) · aktualizováno 6. 11. 2026.
