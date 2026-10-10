#!/bin/sh
set -eu

repo=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bin_dir=${HOME}/.local/bin
unit_dir=${XDG_CONFIG_HOME:-${HOME}/.config}/systemd/user

if [ -L "$unit_dir/seedzero-produce.timer" ] &&
   [ "$(readlink "$unit_dir/seedzero-produce.timer")" = "$repo/systemd/seedzero-produce.timer" ]; then
    systemctl --user disable --now seedzero-produce.timer
    rm "$unit_dir/seedzero-produce.timer"
fi

if [ -L "$unit_dir/seedzero-produce.service" ] &&
   [ "$(readlink "$unit_dir/seedzero-produce.service")" = "$repo/systemd/seedzero-produce.service" ]; then
    systemctl --user stop seedzero-produce.service
    rm "$unit_dir/seedzero-produce.service"
fi

if [ -L "$bin_dir/seedzero-produce" ] &&
   [ "$(readlink "$bin_dir/seedzero-produce")" = "$repo/scripts/seedzero-produce" ]; then
    rm "$bin_dir/seedzero-produce"
fi

systemctl --user daemon-reload
printf 'Uninstalled seedzero-produce user timer and links (repo files retained)\n'
