#!/usr/bin/env python3
"""
Điểm khởi chạy ứng dụng Warehouse Atlas.
"""

import sys
from pathlib import Path

# Add project root and src to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "src"))

from config.logging_config import setup_logging  # noqa: E402
from warehouse_atlas.presentation.components.app_shell import AppShell  # noqa: E402


def main() -> None:
    setup_logging()
    app = AppShell()
    app.mainloop()


if __name__ == "__main__":
    main()
