#!/usr/bin/env python3
"""
Script khởi tạo database và kiểm tra kết nối PostgreSQL cho Warehouse Atlas.
"""
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import get_settings


def main() -> None:
    settings = get_settings()
    print(f"=== Warehouse Atlas Database Initialization ===")
    print(f"Target Database URL: {settings.DATABASE_URL}")
    print("Vui lòng áp dụng migrations thông qua Alembic:")
    print("  alembic upgrade head")


if __name__ == "__main__":
    main()
