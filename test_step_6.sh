#!/bin/bash
echo "--- Starting Step 6 Verification (Resilient) ---"

# 1. Determine the correct docker-compose command
if docker compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version > /dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "FAILURE: Neither 'docker compose' nor 'docker-compose' found."
    exit 1
fi

echo "Using command: $DOCKER_COMPOSE"

# 2. Start the Postgres container
$DOCKER_COMPOSE up -d postgres
echo "Waiting for database to initialize (10s)..."
sleep 10

# 3. Apply the schema
docker exec -i avatrada_postgres psql -U avatrada_admin -d avatrada_ledger < db/migrations/001_initial_schema.sql

# 4. Insert a test record
docker exec -i avatrada_postgres psql -U avatrada_admin -d avatrada_ledger -c \
"INSERT INTO audit_log (event_type, payload) VALUES ('TEST_ENTRY', '{\"status\": \"immutable\"}');"

echo "Verification: Attempting to DELETE the record (This SHOULD fail)..."

# 5. Attempt to delete (The core test)
RESULT=$(docker exec -i avatrada_postgres psql -U avatrada_admin -d avatrada_ledger -c "DELETE FROM audit_log;" 2>&1)

if [[ $RESULT == *"DIAMOND_PROTOCOL_VIOLATION"* ]]; then
    echo "------------------------------------------------"
    echo "SUCCESS: Immutability trigger is ACTIVE."
    echo "------------------------------------------------"
    echo "Error Message Received: $RESULT"
else
    echo "FAILURE: Record was deleted or error not caught."
    echo "Output: $RESULT"
    exit 1
fi
