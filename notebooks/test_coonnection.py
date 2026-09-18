import os
import sys
from pathlib import Path

ROOT = str(Path(__file__).resolve().parent.parent)
sys.path.append(ROOT)

from database.connection import test_connection

print(test_connection())
