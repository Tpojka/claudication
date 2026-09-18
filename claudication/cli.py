"""Entry point of the installed claudication.pyz: `hook` (called by Claude Code) or `host` (started by Chrome)."""
import sys


def main():
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "hook":
        from . import hook

        hook.main()
    elif command == "host":
        from . import host

        host.main()
    else:
        sys.exit("usage: claudication.pyz hook|host")
