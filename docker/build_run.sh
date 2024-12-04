#!/bin/bash

docker build --no-cache -t matchmaking-image .

docker run -d \
  --name matchmaking \
  -p 8000:8000 \
  -v $(pwd)/../:/app \
  --restart on-failure \
  matchmaking-image \
