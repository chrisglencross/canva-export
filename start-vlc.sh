#!/bin/bash

cd "$(dirname $0)"
VIDEO="./clubroom-video.mp4"

if [[ ! -f "$VIDEO" ]]; then
  ./update-video.sh
fi

# restart on crash
while [[ true ]]; do
  /usr/bin/vlc --loop "$VIDEO" --fullscreen --no-interact --no-video-title-show
  sleep 10
done
