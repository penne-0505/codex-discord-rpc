#!/usr/bin/env bash
set -euo pipefail

project_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
config_home="${XDG_CONFIG_HOME:-$HOME/.config}"
unit_dir="$config_home/systemd/user"
config_dir="$config_home/codex-discord-rpc"
unit_file="$unit_dir/codex-discord-rpc.service"
config_file="$config_dir/config.toml"
cli_bin="$project_root/.venv/bin/codex-discord-rpc"
systemctl_bin="${SYSTEMCTL_BIN:-systemctl}"
mode="install"

usage() {
  printf '%s\n' \
    'Usage: scripts/install-user-service.sh [--enable-now|--dry-run|--disable-now]' \
    '' \
    '  --enable-now   install, validate, enable, and start the user service' \
    '  --dry-run      print resolved paths without changing files or systemd state' \
    '  --disable-now  stop and disable the installed service without deleting files'
}

case "${1:-}" in
  "") ;;
  --enable-now) mode="enable-now" ;;
  --dry-run) mode="dry-run" ;;
  --disable-now) mode="disable-now" ;;
  -h|--help) usage; exit 0 ;;
  *) usage >&2; exit 2 ;;
esac

if [[ "$mode" == "dry-run" ]]; then
  printf 'project root: %s\nunit: %s\nconfig: %s\ncli: %s\nsystemctl: %s\n' \
    "$project_root" "$unit_file" "$config_file" "$cli_bin" "$systemctl_bin"
  exit 0
fi

if [[ "$mode" == "disable-now" ]]; then
  "$systemctl_bin" --user disable --now codex-discord-rpc.service
  printf 'Disabled codex-discord-rpc.service; config and unit were retained.\n'
  exit 0
fi

if [[ ! -x "$cli_bin" ]]; then
  printf 'Checkout runtime is missing: %s\nRun: uv sync --extra dev\n' "$cli_bin" >&2
  exit 2
fi

mkdir -p "$unit_dir" "$config_dir"
if [[ ! -e "$config_file" ]]; then
  install -m 0600 "$project_root/config.example.toml" "$config_file"
  printf 'Created config: %s\n' "$config_file"
else
  chmod 0600 "$config_file"
fi

sed \
  -e "s|@PROJECT_ROOT@|$project_root|g" \
  -e "s|@CLI_BIN@|$cli_bin|g" \
  -e "s|@CONFIG_FILE@|$config_file|g" \
  "$project_root/packaging/systemd/codex-discord-rpc.service.in" > "$unit_file"
chmod 0644 "$unit_file"

if [[ "$mode" == "enable-now" ]]; then
  printf 'Checking config and checkout runtime before enabling the service...\n'
  "$cli_bin" --config "$config_file" doctor
fi

"$systemctl_bin" --user daemon-reload

printf 'Installed user unit: %s\n' "$unit_file"
if [[ "$mode" == "enable-now" ]]; then
  "$systemctl_bin" --user enable codex-discord-rpc.service
  "$systemctl_bin" --user restart codex-discord-rpc.service
  printf 'Enabled and started codex-discord-rpc.service\n'
else
  printf 'Edit %s, then run: %s --user enable --now codex-discord-rpc.service\n' \
    "$config_file" "$systemctl_bin"
fi
