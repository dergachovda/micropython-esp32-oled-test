#!/usr/bin/env bash
# Заливає device/ на плату й перезавантажує її.
# Приклади: ./deploy.sh | ./deploy.sh -p COM3 | ./deploy.sh --no-reset
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
exec uv run python tools/deploy.py "$@"
