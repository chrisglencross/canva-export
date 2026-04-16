#!/bin/bash

cd "$(dirname $0)"
mkdir -p log
cp --update "$HOME/data/"*.mp4 .
cp --update "$HOME/data/"*.mp4.ts .


