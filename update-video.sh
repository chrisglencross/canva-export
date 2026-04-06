#!/bin/bash

cd $(dirname $0)
source ./venv/bin/activate

python -m captive_portal

python -m canva_export -d DAHB9p6lzXA
status=$?

# Try to copy to persistent cache directory so we can display after a reboot
if [[ $status -eq 0 ]]; then
   cache=$HOME/data
   if [[ -d $cache ]]; then
     echo "Copying to persistent cache"
     cp DAHB9p6lzXA.mp4 $cache/DAHB9p6lzXA.mp4 || true
     cp DAHB9p6lzXA.mp4.ts $cache/DAHB9p6lzXA.mp4.ts || true
   fi
fi
