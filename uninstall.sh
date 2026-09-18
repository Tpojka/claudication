#!/usr/bin/env bash
# Removes the Claudication native host registration and Claude Code hooks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
rm -f "$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.tpojka.claudication.json"
python3 "$ROOT/scripts/configure_hooks.py" uninstall
rm -rf "$HOME/.claude/claudication"
echo "✓ Claudication removed. Remove the extension itself from chrome://extensions."
