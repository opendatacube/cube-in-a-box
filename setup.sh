#!/usr/bin/env bash
base="$(dirname "$0")"
bash "$base/scripts/install-system-requirements.sh"
bash "$base/scripts/install-docker.sh"
