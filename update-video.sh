#!/bin/bash -e

cd $(dirname $0)

# source ./venv/bin/activate
# python -m captive_portal

url="https://www.epsomandewellharriers.org/clubroom-video/"
local_file=clubroom-video.mp4
tmp_file="${local_file}.tmp"

if [[ -f "$tmp_file" ]]; then
  rm "$tmp_file"
fi
if [[ -f "$local_file" ]]; then
  curl -s --fail -L -R -z "$local_file" -o "$tmp_file" "$url"
else
  curl -s --fail -L -R -o "$tmp_file" "$url"
fi
if [[ -f "$tmp_file" ]]; then
  mv "$tmp_file" "$local_file"
  echo "Updated $local_file"
  ls -l "$local_file"
fi

