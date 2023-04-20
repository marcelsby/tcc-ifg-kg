#!/bin/sh

# Interrompe a execução do script se algum comando falhar
set -e

SRC_DIRS="./app/ ./test/"

echo "Running autopep8..."
autopep8 -r --in-place --max-line-length 120 $SRC_DIRS

echo "Running isort..."
isort $SRC_DIRS