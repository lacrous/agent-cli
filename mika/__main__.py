"""Allow running mika as a module: python -m mika."""

import sys

from mika.cli import main

if __name__ == "__main__":
    sys.exit(main())
