# scripts/provision_db.sh

#!/bin/bash

# This script provisions and starts the local PostgreSQL database using Docker Compose.
# It is designed to be multi-platform compatible (Linux, macOS, WSL, Git Bash).
# Usage: bash scripts/provision_db.sh

set -euo pipefail  # Strict mode for robustness: exit on error, undefined vars, or pipe failures

# Function to check if Docker is installed and running
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Error: Docker is not installed. Please install Docker and try again."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        echo "Error: Docker is not running. Please start Docker and try again."
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        echo "Error: Docker Compose is not available. Please ensure Docker Compose is installed (v2+ preferred)."
        exit 1
    fi

    echo "Docker is installed and running."
}

# Function to start/restart the PostgreSQL container using Docker Compose
start_container() {
    echo "Starting PostgreSQL container..."
    # Use 'docker compose' for v2, fallback to 'docker-compose' for v1
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    echo "Container started or restarted."
}

# Function to wait for the database to be healthy and ready
wait_for_db() {
    local max_attempts=30
    local attempt=1
    local db_host="localhost"
    local db_port="5432"

    echo "Waiting for PostgreSQL to be ready on ${db_host}:${db_port}..."

    until [ "$attempt" -gt "$max_attempts" ]; do
        if command -v nc &> /dev/null; then
            if nc -z "$db_host" "$db_port"; then
                echo "PostgreSQL is ready!"
                return 0
            fi
        elif command -v timeout &> /dev/null && command -v bash &> /dev/null; then
            if timeout 1 bash -c "</dev/tcp/${db_host}/${db_port}" &> /dev/null; then
                echo "PostgreSQL is ready!"
                return 0
            fi
        else
            echo "Warning: 'nc' or 'timeout' not found. Falling back to sleep-based wait."
            sleep 2
            ((attempt++))
            continue
        fi

        echo "Attempt ${attempt}/${max_attempts}: PostgreSQL not ready yet. Retrying in 2 seconds..."
        sleep 2
        ((attempt++))
    done

    echo "Error: PostgreSQL did not become ready in time. Check Docker logs with 'docker compose logs'."
    exit 1
}

# Function to run Alembic migrations
run_migrations() {
    echo "Running Alembic migrations..."
    # Assume virtualenv or global install; adjust if needed
    alembic upgrade head
    echo "Migrations completed."
}

# Main execution
check_docker
start_container
wait_for_db
run_migrations

echo "Success: Database is ready."
echo "Next steps: Run 'uvicorn api.main:app --reload' to start the API."
echo "DATABASE_URL is set to connect to the local PostgreSQL instance."
