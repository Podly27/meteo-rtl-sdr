# Operations

## Receiver Service

```sh
sudo systemctl status rtl433.service
sudo journalctl -u rtl433.service -n 100 --no-pager
sudo journalctl -u rtl433.service -f
```

Restart the receiver:

```sh
sudo systemctl restart rtl433.service
```

Watch decoded output:

```sh
sudo tail -f /var/lib/meteo-rtl-sdr/rtl_433.csv
sudo tail -f /var/lib/meteo-rtl-sdr/rtl_433.jsonl
```

## Weather Underground Uploads

Check timer and recent upload logs:

```sh
sudo systemctl status weather-underground.timer
sudo journalctl -u weather-underground.service -n 100 --no-pager
```

Run one upload manually:

```sh
sudo systemctl start weather-underground.service
```

Dry run without sending data:

```sh
sudo -u meteo-rtl WU_DRY_RUN=1 /opt/meteo-rtl-sdr/bin/weather-underground-upload.py
```

## Stale Data Guard

`weather-underground-upload.py` refuses to upload stale packets. The default limit is controlled by `MAX_DATA_AGE_SECONDS` in `/etc/meteo-rtl-sdr/weather-underground.env`.

Recommended starting point:

```sh
MAX_DATA_AGE_SECONDS=600
```

If the receiver stops, uploads stop instead of repeatedly sending the last valid reading.

## Runtime Files

Default paths:

- CSV: `/var/lib/meteo-rtl-sdr/rtl_433.csv`
- JSONL: `/var/lib/meteo-rtl-sdr/rtl_433.jsonl`
- uploader state: `/var/lib/meteo-rtl-sdr/state`

Use log rotation for long-running CSV/JSONL outputs. A basic logrotate example is in [docs/OPTIMIZATION.md](OPTIMIZATION.md).
