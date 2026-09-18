#!/usr/bin/env bash
# Installs the Claudication native-messaging host for Chrome and the Claude Code hooks.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
HOST_NAME="com.tpojka.claudication"
EXTENSION_ID="hpoodlefheijkfkpebmooehgnjkibdnc"  # fixed by the "key" in extension/manifest.json
HOST_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"

chmod +x "$ROOT/host/claudication_host.py" "$ROOT/hooks/claudication_hook.py"

mkdir -p "$HOST_DIR"
cat > "$HOST_DIR/$HOST_NAME.json" <<JSON
{
  "name": "$HOST_NAME",
  "description": "Claudication: Claude Code status for Chrome",
  "path": "$ROOT/host/claudication_host.py",
  "type": "stdio",
  "allowed_origins": ["chrome-extension://$EXTENSION_ID/"]
}
JSON
echo "✓ Native host registered: $HOST_DIR/$HOST_NAME.json"

python3 "$ROOT/scripts/configure_hooks.py" install "$ROOT/hooks/claudication_hook.py"
echo "✓ Claude Code hooks added to ~/.claude/settings.json (backup: settings.json.claudication.bak)"

cat <<MSG

Next: open chrome://extensions, enable Developer mode, click "Load unpacked"
and pick: $ROOT/extension
Then pin the knee to the toolbar. Restart running Claude Code sessions to pick up the hooks.
MSG
