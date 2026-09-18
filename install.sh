#!/usr/bin/env bash
# macOS / Ubuntu: install Claudication (see claudication/install).
cd "$(dirname "$0")" && exec python3 -m claudication.install "$@"
