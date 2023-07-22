#!/bin/bash

# Start MongoDB server in the foreground with port 27018
echo "Starting MongoDB server..."
mongod --dbpath ~/mongo-data --port 27018 > logs/mongod.log &

# Wait for MongoDB to start
sleep 5

# MongoDB connection URI for test database
MONGODB_URI="mongodb://localhost:27018/test_db"

# Insert test user in the 'users' collection
echo "Inserting test user..."
mongoimport --uri "$MONGODB_URI" --collection users --file ../tests/integrations/api/resources/standard_user.json
mongoimport --uri "$MONGODB_URI" --collection users --file ../tests/integrations/api/resources/admin_user.json

# Set MONGO_DB_URL environment variable after pytest
export MONGO_DB_URL="mongodb://localhost:27018"
export MONGO_DB_ENV="test_db"

# ---------------------------------- MINIO ---------------------------------- #

# Spin up MinIO server in the foreground with port 9000
echo "Starting MinIO server..."
export MINIO_LOG_CONSOLE=off
export MINIO_ROOT_USER=miniorootuser
export MINIO_ROOT_PASSWORD=miniorootuserpassword
minio server ~/minio-data --address localhost:9000 > logs/minio.log &

# Wait for MinIO server to start
sleep 5
mc alias set myminio http://localhost:9000 $MINIO_ROOT_USER $MINIO_ROOT_PASSWORD > logs/minio.log

sleep 2
# Create bucket
echo "Creating bucket..."
mc mb myminio/test-bucket

# Wait for bucket to be created (optional)
sleep 2

# Copy document to the bucket
echo "Inserting test document..."
mc cp ../tests/integrations/api/resources/10-K_mcdonalds.pdf myminio/test-bucket/K-10_docs/10-K_mcdonalds.pdf
mc cp ../tests/integrations/api/resources/amzn-20221231.pdf myminio/test-bucket/K-10_docs/amzn-20221231.pdf

# set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables
export AWS_ACCESS_KEY_ID=$MINIO_ROOT_USER
export AWS_SECRET_ACCESS_KEY=$MINIO_ROOT_PASSWORD
export S3_REGION_NAME=us
export S3_ENDPOINT_URL=http://localhost:9000
export S3_BUCKET_NAME=test-bucket

# ---------------------------------- PYTEST ---------------------------------- #

## Run pytest
echo "Running pytest..."
pytest ../tests

## ---------------------------------- CLEANUP ---------------------------------- #
#
### Stop MongoDB server
echo "Stopping MongoDB server..."
mongosh --port 27018 --eval "use admin; db.shutdownServer()" > logs/mongod.log
##
### Wait for MongoDB to stop
sleep 5
#
## Clean up MongoDB data files
echo "Cleaning up..."
rm -rf ~/mongo-data/* > logs/mongod.log

# Kill MinIO server
echo "Stopping MinIO server..."
mc rm --recursive myminio/test-bucket --force > logs/minio.log
mc rb myminio/test-bucket --force > logs/minio.log
kill $(lsof -t -i:9000) > logs/minio.log








