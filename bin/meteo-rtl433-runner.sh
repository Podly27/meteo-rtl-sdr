#!/usr/bin/env bash
set -euo pipefail

CONFIG_FILE="${METEO_RTL433_CONFIG:-/etc/meteo-rtl-sdr/rtl_433.env}"

if [[ -f "$CONFIG_FILE" ]]; then
  # shellcheck disable=SC1090
  source "$CONFIG_FILE"
fi

RTL433_FREQUENCY="${RTL433_FREQUENCY:-433.92M}"
RTL433_BIN="${RTL433_BIN:-rtl_433}"
RTL433_LIBRARY_PATH="${RTL433_LIBRARY_PATH:-}"
RTL433_DEVICE="${RTL433_DEVICE:-}"
RTL433_PROTOCOLS="${RTL433_PROTOCOLS:-}"
RTL433_EXTRA_ARGS="${RTL433_EXTRA_ARGS:--M time:iso:usec -M protocol -M level}"
RTL433_SAMPLE_RATE="${RTL433_SAMPLE_RATE:-}"
RTL433_LOG_DIR="${RTL433_LOG_DIR:-/var/lib/meteo-rtl-sdr}"
RTL433_CSV="${RTL433_CSV:-$RTL433_LOG_DIR/rtl_433.csv}"
RTL433_JSONL="${RTL433_JSONL:-$RTL433_LOG_DIR/rtl_433.jsonl}"
RTL433_ENABLE_JSON="${RTL433_ENABLE_JSON:-1}"
RTL433_ENABLE_CSV="${RTL433_ENABLE_CSV:-1}"
RTL433_MQTT_URL="${RTL433_MQTT_URL:-}"
RTL433_MQTT_TOPIC="${RTL433_MQTT_TOPIC:-meteo/rtl_433[/model][/id]}"

mkdir -p "$RTL433_LOG_DIR"

if [[ -n "$RTL433_LIBRARY_PATH" ]]; then
  export LD_LIBRARY_PATH="$RTL433_LIBRARY_PATH${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi

cmd=("$RTL433_BIN" -f "$RTL433_FREQUENCY")

if [[ "$RTL433_ENABLE_CSV" == "1" ]]; then
  cmd+=(-F "csv:$RTL433_CSV")
fi

if [[ "$RTL433_ENABLE_JSON" == "1" ]]; then
  cmd+=(-F "json:$RTL433_JSONL")
fi

if [[ -n "$RTL433_DEVICE" ]]; then
  cmd+=(-d "$RTL433_DEVICE")
fi

if [[ -n "$RTL433_SAMPLE_RATE" ]]; then
  cmd+=(-s "$RTL433_SAMPLE_RATE")
fi

if [[ -n "$RTL433_PROTOCOLS" ]]; then
  for protocol in $RTL433_PROTOCOLS; do
    cmd+=(-R "$protocol")
  done
fi

if [[ -n "$RTL433_EXTRA_ARGS" ]]; then
  # Intentional word splitting: this field is admin-controlled extra CLI args.
  # shellcheck disable=SC2206
  extra_args=($RTL433_EXTRA_ARGS)
  cmd+=("${extra_args[@]}")
fi

if [[ -n "$RTL433_MQTT_URL" ]]; then
  cmd+=(-F "mqtt://$RTL433_MQTT_URL,events=$RTL433_MQTT_TOPIC")
fi

printf 'Starting:'
printf ' %q' "${cmd[@]}"
printf '\n'

exec "${cmd[@]}"
