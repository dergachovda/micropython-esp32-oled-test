#!/usr/bin/env bash
# Запускає device/main.py на платі без збереження; вивід іде в термінал (Ctrl+C — зупинка).
# Бібліотеки з device/lib мають уже бути на платі: спершу ./deploy.sh.
# Приклади: ./run.sh | ./run.sh COM3
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"
port="${1:-auto}"
exec uv run mpremote connect "$port" run device/main.py
