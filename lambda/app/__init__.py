import subprocess
import sys

# pip install custom package to /tmp/ and add to path
subprocess.call(
    "pip install openai requests -t /tmp/ --no-cache-dir".split(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
sys.path.insert(1, "/tmp/")
