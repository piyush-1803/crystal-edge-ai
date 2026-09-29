import sys
import os

# Ensure current working directory / project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.node import main

if __name__ == "__main__":
    main()
