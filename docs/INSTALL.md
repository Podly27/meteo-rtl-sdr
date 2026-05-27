# Installation

This guide assumes a Linux host with systemd and a USB RTL-SDR dongle.

## 1. Packages

Debian/Ubuntu:

```sh
sudo apt update
sudo apt install rtl-sdr rtl-433 python3
```

Fedora/RHEL-like systems:

```sh
sudo dnf install rtl-sdr rtl_433 python3
```

Package names vary by distribution. If `rtl_433` is built from source, set `RTL433_BIN` and `RTL433_LIBRARY_PATH` in `/etc/meteo-rtl-sdr/rtl_433.env`.

## 2. System User And Directories

Create a dedicated service user and directories:

```sh
sudo useradd --system --home-dir /var/lib/meteo-rtl-sdr --create-home --shell /usr/sbin/nologin meteo-rtl
sudo mkdir -p /opt/meteo-rtl-sdr /etc/meteo-rtl-sdr /var/lib/meteo-rtl-sdr /var/log/meteo-rtl-sdr
sudo chown -R meteo-rtl:meteo-rtl /var/lib/meteo-rtl-sdr /var/log/meteo-rtl-sdr
```

If your distribution uses USB access groups, add the service user as needed:

```sh
sudo usermod -aG plugdev,dialout meteo-rtl
```

Some distributions may not have both groups; ignore missing groups and use udev rules if needed.

## 3. RTL-SDR Device Check

Verify that the dongle enumerates:

```sh
lsusb
rtl_test -t
```

Common RTL-SDR IDs include `0bda:2832` and `0bda:2838`.

If `rtl_test` fails because the DVB driver owns the dongle, blacklist the DVB modules:

```sh
printf 'blacklist dvb_usb_rtl28xxu\nblacklist rtl2832\nblacklist rtl2830\n' | sudo tee /etc/modprobe.d/blacklist-rtl-sdr.conf
sudo reboot
```

## 4. Install Project Files

From the repository root:

```sh
sudo rsync -a --delete ./ /opt/meteo-rtl-sdr/
sudo chown -R root:root /opt/meteo-rtl-sdr
sudo chmod +x /opt/meteo-rtl-sdr/bin/*.sh /opt/meteo-rtl-sdr/bin/*.py
```

## 5. Configure Receiver

```sh
sudo cp /opt/meteo-rtl-sdr/config/rtl_433.env /etc/meteo-rtl-sdr/rtl_433.env
sudo editor /etc/meteo-rtl-sdr/rtl_433.env
```

Important settings:

- `RTL433_FREQUENCY` - common values are `433.92M` and `868.176M`
- `RTL433_DEVICE` - leave empty for default or set device index/serial
- `RTL433_PROTOCOLS` - leave empty for autodetection or list `rtl_433` protocol IDs
- `RTL433_CSV` and `RTL433_JSONL` - output paths

## 6. Configure Weather Underground

Weather Underground upload is optional.

```sh
sudo cp /opt/meteo-rtl-sdr/config/weather-underground.env.example /etc/meteo-rtl-sdr/weather-underground.env
sudo chmod 600 /etc/meteo-rtl-sdr/weather-underground.env
sudo editor /etc/meteo-rtl-sdr/weather-underground.env
```

Set:

- `WU_STATION_ID`
- `WU_PASSWORD`
- `METEO_MODEL` if your sensor model differs from the default
- `MAX_DATA_AGE_SECONDS` to control stale-data protection

## 7. Install systemd Units

```sh
sudo cp /opt/meteo-rtl-sdr/systemd/rtl433.service /etc/systemd/system/
sudo cp /opt/meteo-rtl-sdr/systemd/weather-underground.service /etc/systemd/system/
sudo cp /opt/meteo-rtl-sdr/systemd/weather-underground.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now rtl433.service
```

Enable Weather Underground uploads only after configuration is complete:

```sh
sudo systemctl enable --now weather-underground.timer
```

## 8. Verify

```sh
sudo systemctl status rtl433.service
sudo journalctl -u rtl433.service -n 100 --no-pager
sudo tail -f /var/lib/meteo-rtl-sdr/rtl_433.csv
```

For WU:

```sh
sudo systemctl start weather-underground.service
sudo journalctl -u weather-underground.service -n 50 --no-pager
```
