#!/usr/bin/env bash
# macOS / Ubuntu entry point; the real installer is install.py.
exec python3 "$(cd "$(dirname "$0")" && pwd)/install.py" "$@"
