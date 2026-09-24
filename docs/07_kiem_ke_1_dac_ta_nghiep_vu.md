# Đặc Tả Chi Tiết Nghiệp Vụ Phân Hệ KIỂM KÊ I (Inventory & Commercial Core)
> **Dự án:** Warehouse Atlas — Hệ Thống Quản Lý Kho Thông Minh (Desktop WMS)  
> **Nguồn tham chiếu:** Phân hệ *Kiểm kê I* trên nền tảng ECOUNT ERP (Vietnam Commercial Standard)  
> **Ánh xạ kiến trúc:** Clean Architecture + PostgreSQL 16+ (27 bảng lõi + 10 bảng mở rộng)

---

## 1. TỔNG QUAN PHÂN HỆ KIỂM KÊ I (INVENTORY I OVERVIEW)

Trong hệ thống ECOUNT ERP, **Kiểm kê I** là trái tim vận hành thương mại và kho vận hàng ngày của doanh nghiệp. Toàn bộ chu trình mua hàng, bán hàng, kiểm soát tồn kho và theo dõi hàng hóa theo dòng chảy vật lý đều được quản lý tại đây:

```
[ NHÀ CUNG CẤP ]                                                            [ KHÁCH HÀNG ]
       │                                                                           ▲
       ▼                                                                           │
  (1) MUA HÀNG                                                                (2) BÁN HÀNG
  Đề nghị mua                                                                  Báo giá
       │                                                                           │
  Đơn mua (PO) ──────┐                                                        Đơn bán (SO) ─────┐
       │             │                                                             │            │
  Phiếu mua hàng     │                                                        Cấp phát giữ      │
  (Goods Receipt)    │                                                        (Reservation)     │
       │             ▼                                                             │            ▼
       │      Đơn mua chưa nhận                                               Phiếu bán hàng   Đơn bán chưa giao
       │      (Backorders)                                                    (Goods Shipment) (Shortages)
       │                                                                           │
       └─────────────────────────────┬─────────────────────────────────────────────┘
                                     │
                                     ▼
                           (3) QUẢN LÝ TỒN KHO
                           • Sổ cái thẻ kho (Movement Ledger)
                           • Số dư tồn kho tức thời (Stock Balance)
                           • Điều chuyển ô kệ / Kho (Stock Transfer)
                           • Quản lý Lô & Hạn sử dụng (FEFO Allocation)
                           • Kiểm kê mù & Điều chỉnh (Physical Stocktake)
```

---

## 2. BÓC TÁCH NGHIỆP VỤ 1: QUY TRÌNH MUA HÀNG & NHẬP KHO (PROCUREMENT & INBOUND)

### 2.1 Đơn mua hàng (Purchase Order - PO)
- **Mục đích:** Ghi nhận cam kết đặt hàng từ Nhà cung cấp, dự trù số lượng và thời gian hàng về kho.
- **Dữ liệu bắt buộc:**
  - Nhà cung cấp (`supplier_id`), Kho dự kiến nhập (`warehouse_id`).
  - Ngày đặt hàng (`order_date`), Ngày giao dự kiến (`expected_on`).
  - Danh sách mặt hàng: Mã SKU, Đơn vị nhập (Thùng/Hộp), Hệ số quy đổi snapshot (`factor_to_base_snapshot`), Đơn giá mua (`unit_price`).
- **Trạng thái vòng đời PO:** `DRAFT` ➔ `CONFIRMED` ➔ `CLOSED` / `CANCELLED`.
- **Bất biến nghiệp vụ:** Xác nhận PO **không làm tăng tồn kho vật lý**. Nó chỉ tạo ra lượng kỳ vọng nhập (`incoming_quantity`) phục vụ tính toán dự trù bổ sung hàng.

### 2.2 Phiếu mua hàng / Thực nhận kho (Goods Receipt / Inbound Shipment)
- **Mục đích:** Ghi nhận hàng hóa thực tế đã cập cảng/cửa nhận hàng (`RECEIVING_DOCK`) và đưa vào lưu trữ (`STORAGE`).
- **Cơ chế kế thừa từ PO:**
  - Người dùng có thể chọn 1 PO đã `CONFIRMED` để tải toàn bộ danh sách mặt hàng và số lượng còn lại cần nhập (`remaining_qty`).
  - Hỗ trợ **nhập kho một phần (Partial Receipt)**: Đặt 100 thùng, nhận trước 40 thùng; hệ thống ghi nhận đã nhận 40, đơn PO vẫn mở với số lượng còn nợ 60 thùng.
- **Ghi nhận thông tin Lô hàng (Internal Lot):**
  - Mỗi lần nhận hàng bắt buộc khởi tạo 1 bản ghi `lot` nội bộ.
  - Ghi nhận: Mã lô nhà sản xuất (`manufacturer_lot_code`), Hạn sử dụng (`expires_on`), Ngày sản xuất (`manufactured_on`), Đơn giá vốn thực tế (`unit_cost`).
- **Hạch toán kho nguyên tử (Atomic Posting via PostingEngine):**
  - Chuyển trạng thái phiếu `APPROVED` ➔ `POSTED`.
  - Sinh 1 bản ghi `stock_movement` ghi nhận biến động tăng tồn kho.
  - Cập nhật số dư `stock_balance` tại vị trí lưu trữ: tăng `on_hand`.
  - Đóng hoặc cập nhật lũy kế `received_qty` trên dòng đơn PO tương ứng.

### 2.3 Báo cáo Đơn mua hàng chưa nhập kho (Outstanding PO / Backorders)
- Hiển thị danh sách các đơn hàng đã đặt nhưng NCC chưa giao hoặc giao thiếu.
- Tính toán: `remaining_qty = ordered_qty - received_qty - closed_qty_base`.
- Cho phép Quản lý kho thực hiện đóng thiếu có lý do (`closed_qty_base`) khi NCC hủy giao phần còn lại.

---

## 3. BÓC TÁCH NGHIỆP VỤ 2: QUY TRÌNH BÁN HÀNG & XUẤT KHO (COMMERCIAL & OUTBOUND)

### 3.1 Đơn bán hàng (Sales Order - SO)
- **Mục đích:** Ghi nhận nhu cầu mua hàng của Khách hàng (Siêu thị, Đại lý).
- **Dữ liệu bắt buộc:** Khách hàng (`customer_id`), Kho xuất (`warehouse_id`), Ngày giao dự kiến (`expected_on`), Chi tiết SKU, Đơn vị bán, Số lượng đặt.
- **Trạng thái:** `DRAFT` ➔ `CONFIRMED` ➔ `CLOSED` / `CANCELLED`.

### 3.2 Cơ chế Cấp phát Giữ hàng (Soft Reservation Engine)
- **Vấn đề thực tế trong kho:** Khi hai nhân viên kinh doanh cùng thấy tồn kho còn 10 thùng và cùng xác nhận đơn bán 7 thùng. Nếu không có cơ chế giữ hàng, kho sẽ bị âm và không đủ hàng giao.
- **Quy tắc giữ hàng của Warehouse Atlas:**
  - Khi SO chuyển sang `CONFIRMED`, hệ thống chạy thuật toán cấp phát giữ hàng `ReservationService.reserve()`.
  - Chiến lược cấp phát đa hình:
    - **FEFO (First-Expired, First-Out):** Đối với sản phẩm có hạn dùng (sữa, bánh, nước ngọt), tự động chọn các lô sắp hết hạn trước (có kiểm tra điều kiện hạn còn tối thiểu `min_shelf_life_days` và tình trạng `GOOD`).
    - **FIFO (First-In, First-Out):** Đối với sản phẩm không theo dõi hạn, ưu tiên lô nhập kho trước.
  - Sinh bản ghi `stock_reservation` gắn chặt với dòng đơn bán `sales_order_line_id`.
  - Tăng `reserved` trong `stock_balance`. Lượng khả dụng bán được tính bằng: `free_qty = on_hand - reserved`.
  - Ghi nhật ký sự kiện `reservation_event` loại `ALLOCATE`.

### 3.3 Phiếu bán hàng / Thực xuất kho (Goods Shipment / Outbound Document)
- **Mục đích:** Nhân viên kho nhặt hàng theo danh sách lấy hàng (Pick list) và xuất giao cho khách.
- **Quy tắc xuất:**
  - Tiêu thụ đúng lượng hàng đã được giữ (`StockReservation.consume()`).
  - Ghi giảm đồng thời `on_hand` và `reserved` trong `stock_balance`.
  - Sinh bản ghi `stock_movement` ghi nhận xuất hàng ra ngoài kho (`to_location_id = NULL`).
  - Ghi nhật ký sự kiện `reservation_event` loại `CONSUME`.
  - Tăng lũy kế `shipped_qty` trên dòng đơn bán SO.

### 3.4 Báo cáo Đơn bán hàng chưa xuất kho (Outstanding SO / Shortages)
- Tra cứu danh sách đơn bán chưa được giao hàng hoặc bị thiếu hàng tồn kho.
- Cung cấp thông tin cảnh báo để bộ phận thu mua lập đề xuất mua hàng kịp thời.

---

## 4. BÓC TÁCH NGHIỆP VỤ 3: QUẢN LÝ VẬN HÀNH KHO NỘI BỘ (WAREHOUSE OPERATIONS)

### 4.1 Thẻ kho & Sổ cái biến động kho (Stock Movement Ledger)
- **Nguồn sự thật tối thượng (Single Source of Truth):** Toàn bộ biến động tăng/giảm vật lý đều được ghi thành các bản ghi `stock_movement` bất biến (Append-only).
- **Tuyệt đối cấm:** Không có lệnh `UPDATE` hay `DELETE` trên bảng `stock_movement`.
- **Bút toán đảo (Reversal Workflow):** Khi phát hiện xuất/nhập nhầm, hệ thống không sửa phiếu cũ mà tạo 1 chứng từ loại `REVERSAL` liên kết với `reversal_of_id`, sinh các dòng movement đối ứng đảo chiều hoàn toàn trong transaction.

### 4.2 Điều chuyển vị trí ô kệ & Điều chuyển kho (Stock Transfer)
- Chuyển hàng giữa các vị trí lưu trữ trong kho (ví dụ: chuyển từ kệ tầng 1 `A-01-01` sang kệ tầng 2 `A-01-02`, hoặc chuyển sang khu vực đóng gói `STAGING`).
- Chuyển hàng giữa Tổng kho `WH-MAIN` và Kho vệ tinh `WH-SUB`.
- **Bảo toàn tổng lượng tồn:** Lượng trừ ở vị trí nguồn phải bằng đúng lượng cộng ở vị trí đích.

### 4.3 Kiểm soát chất lượng & Đổi trạng thái hàng (Reclassify Quality Status)
- Hàng hóa trong kho có 3 tình trạng:
  - `GOOD`: Hàng đạt chuẩn chất lượng, sẵn sàng bán.
  - `QUARANTINE`: Hàng chờ kiểm định hoặc hàng khách trả về cần kiểm tra lại.
  - `DAMAGED`: Hàng móp méo, rách bao bì, hỏng hóc, không được phép cấp phát bán.
- Lập phiếu `RECLASSIFY` để điều chuyển hàng hóa giữa các trạng thái (ví dụ: phát hiện 2 thùng sữa móp méo, lập phiếu chuyển từ `GOOD` sang `DAMAGED`).

### 4.4 Kiểm kê kho thực tế & Điều chỉnh chênh lệch (Stocktake & Adjustment)
- **Quy trình kiểm kê mù (Blind Count):**
  - Trưởng kho tạo đợt kiểm kê `stocktake` tại một vị trí/ô kệ cụ thể.
  - Đóng băng vị trí (`is_frozen = True`): ngăn chặn các giao dịch xuất/nhập/chuyển phát sinh trong thời gian đếm.
  - Nhân viên đếm hàng chỉ nhập số lượng thực tế đếm được (`counted_qty`), hệ thống không hiển thị trước số tồn trên sổ sách (`snapshot_qty`) để tránh gian lận.
- **Xử lý chênh lệch:**
  - Nếu `counted_qty == snapshot_qty`: Đóng phiên kiểm kê, không phát sinh bút toán điều chỉnh.
  - Nếu `counted_qty > snapshot_qty` (Thừa hàng): Tự động tạo phiếu điều chỉnh tăng (`ADJUSTMENT`).
  - Nếu `counted_qty < snapshot_qty` (Thiếu hàng): Kiểm tra lượng tồn chưa giữ; nếu thiếu hụt ảnh hưởng đến hàng đã giữ (reserved), cảnh báo người quản lý giải phóng giữ hàng trước khi ghi sổ điều chỉnh giảm.

---

## 5. BẢNG MA TRẬN ÁNH XẠ CHỨC NĂNG ECOUNT ➔ DATABASE ATLAS

| Chức năng Kiểm kê I (ECOUNT ERP) | Loại chứng từ (`DocumentKind`) | Bảng lưu trữ chính | Cơ chế giao dịch & Khóa |
|---|---|---|---|
| Đơn mua hàng | - | `purchase_order`, `purchase_order_line` | Khóa theo `order_id`, kiểm tra trạng thái |
| Phiếu mua hàng (Nhập kho) | `RECEIPT` | `inventory_document`, `stock_movement`, `stock_balance` | Khóa `warehouse -> order -> lot -> balance` |
| Đơn bán hàng | - | `sales_order`, `sales_order_line` | Khóa theo `order_id` |
| Giữ hàng tự động (FEFO/FIFO) | - | `stock_reservation`, `reservation_event` | All-or-nothing, khóa `stock_balance` tăng `reserved` |
| Phiếu bán hàng (Xuất kho) | `SHIPMENT` | `inventory_document`, `stock_movement`, `stock_balance` | Tiêu thụ reservation, giảm `on_hand` và `reserved` |
| Điều chuyển kho / ô kệ | `TRANSFER` | `inventory_document`, `stock_movement`, `stock_balance` | Khóa nguồn và đích, bảo toàn tổng lượng |
| Chuyển trạng thái (GOOD/DAMAGED)| `RECLASSIFY` | `inventory_document`, `stock_movement`, `stock_balance` | Cùng location/lot, đổi `condition` |
| Phiếu kiểm kê thực tế | - | `stocktake`, `stocktake_line` | Đóng băng `location`, đếm mù |
| Phiếu điều chỉnh kiểm kê | `ADJUSTMENT` | `inventory_document`, `stock_movement`, `stock_balance` | Sinh movement điều chỉnh, mở đóng băng |
| Bút toán đảo chứng từ | `REVERSAL` | `inventory_document`, `stock_movement`, `stock_balance` | Đảo ngược cặp from/to, kiểm tra 1 lần đảo duy nhất |
| Sổ chi tiết thẻ kho | - | `stock_movement` | Append-only ledger, view `v_stock_ledger_leg` |
| Báo cáo đối soát sổ kho | - | `stock_balance`, `stock_movement` | View `v_inventory_reconciliation` |
