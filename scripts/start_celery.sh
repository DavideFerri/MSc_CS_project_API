#!/bin/bash

# Function to check if Redis server is running
function is_redis_running() {
    pgrep -x redis-server > /dev/null
}

# Start Redis server if it's not already running
if ! is_redis_running; then
    redis-server &
    sleep 2  # Adjust the sleep time as needed
fi

celery -A src.api.tasks worker --loglevel=INFO &

# start uvicorn server
uvicorn main:app --reload &

















