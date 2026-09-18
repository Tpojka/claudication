#!/usr/bin/env bash
# macOS / Ubuntu entry point; the real uninstaller is install.py.
exec python3 "$(cd "$(dirname "$0")" && pwd)/install.py" uninstall
