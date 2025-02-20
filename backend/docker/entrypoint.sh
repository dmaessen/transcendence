#!/bin/bash

echo "Waiting for PostgreSQL to start..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 2
done
echo "PostgreSQL is up - executing command"


echo "Checking for pending migrations..."
python manage.py makemigrations data

echo "Applying migrations..."

#python manage.py makemigrations
# python manage.py migrate sites 0001 --fake
python manage.py migrate data

# dont want to make unecessary migrations everytime i make an image
# run migrations only if there are unapplied changes
echo "Checking for pending migrations..."
python manage.py makemigrations

echo "Applying migrations..."
#python manage.py makemigrations
# python manage.py migrate sites 0001 --fake
python manage.py migrate

# Start Daphne with custom timeout settings
# echo "Starting Daphne server..."
# exec python daphne_run.py

# if [ $? -eq 0 ]; then
#   echo "Applying migrations..."
#   #python manage.py makemigrations
#   python manage.py migrate
# else
#   echo "No migrations needed."
# fi

echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
# exec python ./backend/game_server/game_server.py

