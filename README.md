# Warehouse Atlas — Hệ Thống Quản Lý Kho Thông Minh (Desktop WMS)

> **Ứng dụng desktop điều hành kho phân phối hàng đóng gói theo lô**  
> Xây dựng bằng **Python 3.12 + Tkinter/ttk + PostgreSQL 16+ + SQLAlchemy 2.0** theo kiến trúc **Modular Monolith / Hexagonal (Ports & Adapters)**.

---

## 1. Thông Điệp & Giá Trị Cốt Lõi

> *“Hệ thống quản lý kho có khả năng truy vết, ngăn cấp phát trùng, lập kế hoạch lấy hàng và giải thích đề xuất bằng dữ liệu thực tế.”*

- **Nhận đúng & Biết hàng ở đâu:** Độ hạt tồn kho 4 chiều hạt nhân `(product_id, location_id, lot_id, condition)`. Phân biệt rõ giữa Danh mục hàng (Product) và Số dư thực tế (StockBalance).
- **Giữ đúng hàng cho đơn:** Cơ chế Soft Reservation ngăn race condition và over-allocation khi nhiều đơn cùng tranh chấp một lô hàng.
- **Xuất đúng lô:** Đa hình chính sách cấp phát **FEFO** (First-Expired, First-Out) cho hàng có date và **FIFO** cho hàng không date.
- **Giải thích biến động:** Sổ cái biến động (StockMovement - Append-only Ledger) là nguồn sự thật (Source of Truth). Không bao giờ sửa/xóa lịch sử sổ; đảo bằng bút toán ngược (Reversal).
- **Lập lộ trình lấy hàng thông minh (P1):** Heuristic Nearest-Neighbor + 2-opt so sánh trực tiếp với Baseline để đo quãng đường di chuyển thực tế.
- **Trợ lý AI an toàn (P1):** Tích hợp Ollama LLM qua ToolGateway allowlist nghiêm ngặt, trả câu trả lời kèm Evidence dữ liệu và thời điểm `as_of`.

---

## 2. Cấu Trúc Dự Án (Project Structure)

```text
warehouse_atlas/
├── README.md                      # Tài liệu tổng quan dự án
├── pyproject.toml                 # Cấu hình đóng gói & linting (Ruff, Pytest)
├── requirements.txt               # Dependencies môi trường chạy
├── requirements-dev.txt           # Dependencies môi trường kiểm thử & dev
├── alembic.ini                    # Cấu hình migrations database
├── .env.example                   # Biến môi trường mẫu
├── docs/                          # Hồ sơ đặc tả nghiệp vụ, DB, Use cases
│   ├── 01_ke_hoach.md             # Kế hoạch tổng thể 8 tuần & phạm vi P0/P1/P2
│   ├── 02_database.md             # Thiết kế 27 bảng lõi + 10 bảng mở rộng
│   ├── 05_erd.dbml                # Mô hình quan hệ thực thể DBML
│   ├── warehouse_atlas_dac_ta_class.md   # Thiết kế chi tiết các lớp OOP
│   ├── warehouse_atlas_dac_ta_usecase.md # Đặc tả 35 Use cases
│   └── diagrams/                  # File Draw.io và BPMN
├── config/                        # Cấu hình ứng dụng & Logging
│   ├── settings.py                # Pydantic Settings
│   └── logging_config.py          # Logging chuẩn hóa
├── scripts/                       # Các script bảo trì, seed dữ liệu, chạy demo
│   ├── init_db.py
│   └── seed_p0_data.py
├── migrations/                    # Thư mục Alembic migrations
├── src/warehouse_atlas/           # Mã nguồn ứng dụng
│   ├── common/                    # Constants, Enums, Exceptions, Types (BucketKey)
│   ├── domain/                    # TẦNG DOMAIN THUẦN TÚY (Entities, VO, Policies)
│   │   ├── model/                 # Catalog, Warehouse, Lot, Balance, Document, Order...
│   │   └── policies/              # FEFO/FIFO AllocationPolicy, LotEligibility...
│   ├── application/               # TẦNG APPLICATION (Use Cases, DTOs, Ports, Services)
│   │   ├── dtos/                  # Data Transfer Objects
│   │   ├── ports/                 # Interfaces: UnitOfWork, Repositories, Clock, LLMPort
│   │   └── services/              # PostingEngine, InventoryService, ReservationService...
│   ├── infrastructure/            # TẦNG INFRASTRUCTURE (DB, ORM, Adapters)
│   │   ├── db/                    # PostgreSQL engine & session factory
│   │   ├── orm/                   # SQLAlchemy 2.0 mapped models
│   │   ├── repositories/          # SqlAlchemy Repositories implementation
│   │   ├── unit_of_work.py        # SqlAlchemyUnitOfWork implementation
│   │   └── adapters/              # Ollama LLM Adapter, System Clock
│   ├── intelligence/              # TẦNG TRÍ TUỆ NHÂN TẠO & THUẬT TOÁN (P1)
│   │   ├── routing/               # RoutePlanner (Nearest Neighbor + 2-opt)
│   │   ├── assistant/             # ToolGateway, AssistantService
│   │   └── analysis/              # ReplenishmentService
│   └── presentation/              # TẦNG GIAO DIỆN TKINTER & DESIGN SYSTEM
│       ├── theme/                 # ThemeTokens (màu sắc, typography, spacing)
│       ├── components/            # Reusable Tkinter components (DataTable, Badges...)
│       ├── views/                 # StockView, DocumentView, StocktakeView, MapView...
│       ├── presenters/            # Presenters điều phối sự kiện màn hình
│       └── workers/               # BackgroundTaskRunner + Queue (chống treo UI)
└── tests/                         # KIỂM THỬ ĐỘC LẬP
    ├── conftest.py
    ├── unit/                      # Kiểm thử nghiệp vụ Domain (FEFO, Eligibility, Balances)
    ├── integration/               # Kiểm thử DB, Concurrency, UnitOfWork
    └── fixtures/                  # Dữ liệu mẫu phục vụ test
```

---

## 3. Ranh Giới Kiến Trúc & Quy Tắc Bất Biến

1. **Domain là trung tâm và thuần túy:** Domain models & policies KHÔNG import Tkinter, SQLAlchemy hay Ollama.
2. **Một Use Case = Một UnitOfWork = Một DB Transaction:** `PostingEngine` hạch toán biến động theo thứ tự khóa chặt chẽ `warehouse -> order -> location -> lot -> balance -> reservation`.
3. **Sổ kho chỉ thêm (Append-Only):** Không UPDATE / DELETE các bản ghi `StockMovement` và `ReservationEvent`.
4. **GUI không bao giờ treo:** Các tác vụ I/O, Database, AI và Thuật toán đồ thị bắt buộc chạy qua `BackgroundTaskRunner` (worker thread). Main thread nhận kết quả DTO qua `queue` và `after()`.
5. **AI không có quyền SQL tùy tiện:** Model ngôn ngữ chỉ có quyền đọc qua các tool định danh nghiêm ngặt, kết quả phải có `ToolEvidence` kèm timestamp `as_of`.

---

## 4. Hướng Dẫn Cài Đặt & Chạy Kiểm Thử

### Yêu cầu môi trường
- Python 3.12+
- PostgreSQL 16+
- Tkinter 8.6+

### Cài đặt dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

### Chạy Unit Tests
```bash
PYTHONPATH=src pytest tests/unit
```
