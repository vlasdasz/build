#!/usr/bin/env python3

import sys
import time
import subprocess

if len(sys.argv) < 2:
    print("Usage: python run_with_timer.py \"<command>\"")
    sys.exit(1)

command = sys.argv[1]

# Start timer
start_time = time.time()

# Run the command
try:
    subprocess.run(command, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print(f"Command failed with exit code {e.returncode}")

# End timer
end_time = time.time()

# Duration in seconds
duration = int(end_time - start_time)

# Format the output
if duration >= 60:
    minutes = duration // 60
    seconds = duration % 60
    print(f"Time taken: {minutes}:{seconds:02d}")
else:
    print(f"Time taken: {duration} seconds")
