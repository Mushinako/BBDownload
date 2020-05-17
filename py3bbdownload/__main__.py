#!/usr/bin/env python3
import sys

# Self-defined scripts
from main import main

# Check for Python 3
if sys.version_info.major < 3:
    print('Python 3 or later is required! 3.6+ recommended')
    sys.exit(23)

if __name__ == "__main__":
    main()
