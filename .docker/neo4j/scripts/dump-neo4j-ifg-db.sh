#!/bin/bash

set -e

neo4j_dump_dir="/dump-volume/dumps"

echo "Starting the dump..."

neo4j-admin dump --database=ifg --to=$neo4j_dump_dir/ifg-kg-neo4j-$(date +"%d%m%Y%H%M%S%z").dump

echo "Dump completed successfully!"