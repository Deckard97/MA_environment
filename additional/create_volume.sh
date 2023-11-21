#!/bin/bash

# Name of your Docker volume
VOLUME_NAME="ma_environment_logs"

# Create the volume if it doesn't exist
docker volume create "$VOLUME_NAME"

# Run a container to create the directories
docker run --rm -v "$VOLUME_NAME":/mnt alpine sh -c \
  "mkdir -p /mnt/httpd && mkdir -p /mnt/db && mkdir -p /mnt/app1 && mkdir -p /mnt/app2"

echo "Volume $VOLUME_NAME is set up with required directories."
