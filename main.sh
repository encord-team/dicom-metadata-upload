#!/bin/bash

set -e

# https://stackoverflow.com/questions/59895
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$SCRIPT_DIR"

export ENCORD_SSH_KEY_FILE=$SCRIPT_DIR/encord-dicom-metadata-upload-private-key.ed25519
export CLOUD_INTEGRATION_TITLE='dicom-metadata-upload-integration'
export DICOM_DIR=$SCRIPT_DIR/dicom-data

poetry run python3 main.py
