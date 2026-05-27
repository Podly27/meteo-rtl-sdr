# Troubleshooting

## RTL-SDR Is Not Visible

Check USB enumeration:

```sh
lsusb
dmesg -T | grep -Ei 'usb|rtl|2832|2838|sdr|dvb' | tail -n 100
```

If the dongle is not listed, this is usually a physical USB issue: port, hub, cable, power, or VM USB passthrough.

## `No supported devices found`

`rtl_433` cannot open an RTL-SDR device.

Check:

```sh
lsusb
rtl_test -t
sudo fuser -v /dev/bus/usb/*/* 2>/dev/null | grep rtl
```

Typical causes:

- dongle is missing from USB
- another process already owns the dongle
- DVB kernel driver owns the dongle
- service user lacks permissions

## `usb_claim_interface error -6`

The device is already in use. If `rtl433.service` is running, this is expected when testing with `rtl_test`.

```sh
sudo systemctl stop rtl433.service
rtl_test -t
sudo systemctl start rtl433.service
```

## No Weather Packets Are Decoded

The receiver can open the dongle, but no packets match enabled decoders.

Check:

- frequency (`RTL433_FREQUENCY`)
- antenna placement
- gain settings in `RTL433_EXTRA_ARGS`
- whether `RTL433_PROTOCOLS` is too restrictive
- whether the station transmits on a long interval

Run a foreground test:

```sh
sudo systemctl stop rtl433.service
sudo -u meteo-rtl /opt/meteo-rtl-sdr/bin/meteo-rtl433-runner.sh
sudo systemctl start rtl433.service
```

## Weather Underground Sends Nothing

Check the freshness guard and credentials:

```sh
sudo journalctl -u weather-underground.service -n 100 --no-pager
sudo -u meteo-rtl WU_DRY_RUN=1 /opt/meteo-rtl-sdr/bin/weather-underground-upload.py
```

If the latest packet is older than `MAX_DATA_AGE_SECONDS`, the uploader exits without sending.
