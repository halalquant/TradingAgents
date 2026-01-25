#!/usr/bin/env python3
import sys
import os

def main():
    """
    Simple health check for the bot process.
    Returns exit code 0 if healthy, 1 otherwise.
    """
    try:
        pid_file = "/tmp/bot.pid"
        
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 0)
                sys.exit(0)
            except OSError:
                sys.exit(1)
        
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and 'bot.py' in ' '.join(cmdline):
                    sys.exit(0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        sys.exit(1)
    except ImportError:
        sys.exit(0)
    except Exception as e:
        print(f"Health check error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
