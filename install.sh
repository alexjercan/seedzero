#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bin_dir=${HOME}/.local/bin
unit_dir=${XDG_CONFIG_HOME:-${HOME}/.config}/systemd/user

mkdir -p "$bin_dir" "$unit_dir"
ln -sfn "$repo/scripts/seedzero-produce" "$bin_dir/seedzero-produce"
ln -sfn "$repo/systemd/seedzero-produce.service" "$unit_dir/seedzero-produce.service"
ln -sfn "$repo/systemd/seedzero-produce.timer" "$unit_dir/seedzero-produce.timer"

systemctl --user daemon-reload
systemctl --user enable --now seedzero-produce.timer

printf 'Installed seedzero-produce in %s\n' "$bin_dir"
printf 'Enabled seedzero-produce.timer for 10:00 local time\n'
