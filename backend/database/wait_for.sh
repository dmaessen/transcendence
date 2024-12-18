#!/usr/bin/env bash

# wait-for-it.sh: waits for a service to be available before executing a command.

TIMEOUT=15
QUIET=0

# Parse options
while getopts "t:q" opt; do
  case "$opt" in
    t) TIMEOUT=$OPTARG ;;
    q) QUIET=1 ;;
    *) echo "Usage: wait_for.sh [-t timeout] [-q] host port command"; exit 1 ;;
  esac
done

# Wait for the service to be available
echo "Waiting for $POSTGRES_HOST:$POSTGRES_PORT to be available..."

for i in $(seq $TIMEOUT); do
  nc -z "$POSTGRES_HOST" "$POSTGRES_PORT" > /dev/null 2>&1
  result=$?
  if [ $result -eq 0 ]; then
    # Host and port are available
    if [ $QUIET -eq 0 ]; then
      echo "$POSTGRES_HOST:$POSTGRES_PORT is available."
    fi
    exec "$@"
    exit 0
  fi
  sleep 1
done

# If timeout is reached and service is still not available
echo "$POSTGRES_HOST:$POSTGRES_PORT is not available after $TIMEOUT seconds"
exit 1
