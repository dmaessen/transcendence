#!/bin/bash

# Environment variables are passed by Docker Compose
DB_ENGINE=${DB_ENGINE}
DB_HOST=${POSTGRES_HOST}
DB_PORT=${POSTGRES_PORT}
DB_USER=${POSTGRES_USER}
DB_PASSWORD=${POSTGRES_PASSWORD}
DB_NAME="psql"

until psql -h "localhost" -U "your_username" -c '\q'; do
  echo "Postgres is unavailable - retrying in 5 seconds"
  sleep 5
done

# Check if the database exists
echo "Checking if database $DB_NAME exists..."
DB_EXISTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';")

if [[ $DB_EXISTS == 1 ]]; then
    echo "Database $DB_NAME already exists."
else
    echo "Database $DB_NAME does not exist. Creating it..."
    PGPASSWORD=$DB_PASSWORD createdb -h $DB_HOST -U $DB_USER $DB_NAME
    echo "Database $DB_NAME created successfully."
fi
