#!/usr/bin/env bash
# macOS / Ubuntu: remove Claudication.
cd "$(dirname "$0")" && exec python3 -m claudication.install uninstall
