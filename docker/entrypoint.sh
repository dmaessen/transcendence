#!/bin/bash

# apply database migrations
echo "Running migrations..."
python manage.py migrate

echo "Starting Django server..."
exec "$@"
