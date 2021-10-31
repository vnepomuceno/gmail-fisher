#!/bin/bash
# Treats unset variables as an error
set -u

echo "==> Exporting to path: '$1'"
echo "==> Copying .json file to path: '$2'"
poetry run export_food_expenses --output-filepath=$1
cp $1 $2