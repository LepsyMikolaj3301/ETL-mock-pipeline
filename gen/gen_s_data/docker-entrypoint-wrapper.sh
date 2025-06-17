#!/bin/bash

# Start Postgres in background
docker-entrypoint.sh postgres &

# Wait for Postgres to become available
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" -h localhost; do
  echo "Waiting for Postgres to be ready..."
  sleep 2
done

# Set environment for your script
export SHOE_DB_HOST='localhost'
export SHOE_DB_PORT='5432'
export SHOE_DB_NAME=$POSTGRES_DB
export SHOE_DB_USER='store'
export SHOE_DB_PASS='store'

# Run your script to populate the database
exec uvicorn gen_api:app --host 0.0.0.0 --port 8000 &
sleep 2

python3 structured_data_gen.py

# Keep container alive by waiting for Postgres
# Finally, start uvicorn


wait