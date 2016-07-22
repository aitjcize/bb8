#!/bin/bash

while true; do
  date
  gsutil rsync -d -r /var/lib/bb8/apps gs://bb8-app-states
  sleep 30m
done

