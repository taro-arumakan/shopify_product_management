"""
run this before Python Debugger: Local Attach.
or set an environment variable to run this file at start of a Python process.
export PYTHONSTARTUP=debugpy_listen.py
"""

import debugpy

debugpy.listen(5678)
print("Waiting for debugger attach")
debugpy.wait_for_client()
