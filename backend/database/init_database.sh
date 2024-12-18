#!/bin/bash

# Check if the database exists
# echo "Checking if database $POSTGRES_NAME exists..."
# DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_NAME';")

# if [[ $DB_EXISTS == 1 ]]; then
#     echo "Database $POSTGRES_NAME already exists."
# else
#     echo "Database $POSTGRES_NAME does not exist. Creating it..."
#     PGPASSWORD=$POSTGRES_PASSWORD createdb -h $POSTGRES_HOST -U $POSTGRES_USER $POSTGRES_NAME
#     echo "Database $POSTGRES_NAME created successfully."
# fi

# Run Django migrations
echo "Running Django migrations..."
python manage.py migrate

# Start the Django development server
echo "Starting Django server..."
exec python manage.py runserver 0.0.0.0:8000
