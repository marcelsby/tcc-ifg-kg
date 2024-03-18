#!/bin/bash

set -e

docker compose -f docker-compose.yml -f docker-compose.dump.yml up neo4j

echo "Dump saved at: './.docker/neo4j/dumps/'"