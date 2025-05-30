import os
import sys
from pathlib import Path

# path of project root directory
project_root = Path(__file__).parent.absolute()

# Add the project root to path
sys.path.insert(0, project_root)