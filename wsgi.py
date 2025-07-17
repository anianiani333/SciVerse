import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from SciVerse import app
print("Using Python version:", sys.version)

if __name__ == "__main__":
    app.run()

