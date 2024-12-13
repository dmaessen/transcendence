#!/bin/bash

# Environment variables are passed by Docker Compose
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DB_USER=${POSTGRES_USER:-postgres}
DB_PASSWORD=${POSTGRES_PASSWORD}
DB_NAME=${POSTGRES_DB}

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
