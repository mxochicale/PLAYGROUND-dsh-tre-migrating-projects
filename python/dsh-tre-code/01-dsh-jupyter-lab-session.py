#!/usr/bin/env python
# coding: utf-8

# # DHS jupyter lab session

#####################################
# ## 1 Python & System Information
# Record the Python version and platform so results are reproducible and easier to debug.

import sys
import platform
from datetime import datetime

print(f"Date/Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Python    : {sys.version}")
print(f"Platform  : {platform.platform()}")
print(f"Machine   : {platform.machine()}")

#####################################
# ## 2 Default python packages
# List of available python packages

import subprocess
import json

# Get pip list in JSON format
result = subprocess.run(
    ['pip', 'list', '--format=json'],
    capture_output=True,
    text=True,
    check=True
)

packages = json.loads(result.stdout)
for pkg in packages:
    print(f"{pkg['name']}=={pkg['version']}")

