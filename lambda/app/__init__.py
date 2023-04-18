import subprocess
import sys
import logging
from aws_xray_sdk.core import patch_all
patch_all()

# pip install custom package to /tmp/ and add to path
subprocess.call(
    "pip install openai requests -t /tmp/ --no-cache-dir".split(),
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
sys.path.insert(1, "/tmp/")

logging.getLogger().setLevel(logging.INFO)
