# conftest.py — project root
# Adds project root to Python path so 'pages' module is found

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))