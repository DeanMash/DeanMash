import os

# Keep background auto-send off during the test suite.
os.environ.setdefault("OPENPIPE_AUTO_RUN", "0")
