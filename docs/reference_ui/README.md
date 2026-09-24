# Hồ Sơ Tham Chiếu Giao Diện & Nghiệp Vụ Chuẩn ERP (ECOUNT ERP)

> **Mục tiêu:** Nâng tầm đồ án tốt nghiệp **Warehouse Atlas** lên tiêu chuẩn của một phần mềm ERP quản lý kho thương mại chuyên nghiệp thực tế (Industrial-grade ERP/WMS).

---

## 1. Dữ Liệu Tham Chiếu Đã Tải Về
- **Ảnh chụp màn hình thực tế (1920x1080):** `docs/reference_ui/ecount_erp_dashboard.png`
- **Mã nguồn trang giao diện chính:** `docs/reference_ui/ecount_erp_page_source.html`
- **Bộ CSS & Design System chuẩn (8 bundles):** `docs/reference_ui/css/`
  - `bundle-v5-common-css`: Bố cục form, bảng dữ liệu (Data Grid), input, typography.
  - `bundle-v5-navigation-css`: Cây điều hướng phân hệ (Module Tree Navigation).
  - `bundle-v5-common-responsive-css`: Khả năng co giãn theo độ phân giải màn hình.
  - `bundle-v5-common-dark-css` & `font-icon-css`: Bảng màu và icon chức năng.

---

## 2. Phân Tích Cấu Trúc Giao Diện Chuẩn ERP (Layout Breakdown)

### 2.1 Bố cục 4 khu vực chuẩn (Standard 4-Zone Layout)
1. **Thanh Tiêu Đề Trên Cùng (Top System Header):**
   - Logo thương hiệu + Tên chi nhánh / Kho làm việc hiện tại (cho phép chuyển nhanh giữa Tổng kho & Kho phụ).
   - Thông tin tài khoản đăng nhập + Vai trò (Admin / Quản lý kho / Thủ kho).
   - Phím tắt tìm kiếm nhanh toàn cục (Global Search).

2. **Cây Menu Điều Hướng Trái (Left Navigation Tree):**
   - Phân chia theo nghiệp vụ rõ ràng, có khả năng thu gọn (Collapsible Accordion):
     - **Quản lý Tồn kho (Inventory):** Tồn kho tức thời, Nhập kho, Xuất kho, Điều chuyển ô kệ, Điều chỉnh kiểm kê.
     - **Mua hàng (Purchasing):** Đơn mua hàng (PO), Phiếu nhận hàng NCC, Trả hàng NCC.
     - **Bán hàng (Sales):** Đơn bán hàng (SO), Cấp phát giữ hàng (Reservation), Phiếu xuất giao hàng.
     - **Báo cáo & Sổ sách (Reports):** Sổ chi tiết biến động kho (Ledger), Báo cáo đối soát (Reconciliation), Cảnh báo hạn dùng (Expiry Risk).

3. **Thanh Lọc Đa Điều Kiện (Filter Bar - Phía trên bảng):**
   - Khoảng ngày chứng từ (Từ ngày - Đến ngày).
   - Kho / Khu vực lưu trữ (Dropdown).
   - Trạng thái chứng từ (Tất cả, Bản nháp, Đã duyệt, Đã ghi sổ).
   - Ô tìm kiếm nhanh SKU / Barcode / Tên hàng.

4. **Khu Vực Bảng Dữ Liệu Dày Đặc (Dense Data Grid):**
   - Hàng bảng có độ cao tối ưu (30 - 34px) hiển thị được nhiều dòng thông tin trên một màn hình mà không cần cuộn quá nhiều.
   - Đánh dấu trực quan bằng Status Badges (ĐÃ GHI SỔ, BẢN NHÁP, HƯ HỎNG...).
   - Hỗ trợ sắp xếp cột, căn lề chuẩn (Mã & Tên căn trái, Số lượng & Giá tiền căn phải, Trạng thái căn giữa).

5. **Thanh Hành Động Nghiệp Vụ Ở Đáy (Action Footer Toolbar):**
   - Các nút bấm hành động kèm phím tắt tiêu chuẩn:
     - `[F2]` Thêm mới dòng / phiếu
     - `[F8]` Ghi sổ / Lưu dữ liệu
     - `[Esc]` Đóng / Hủy bỏ
     - `[F3]` Áp dụng bộ lọc
     - Xuất Excel / In phiếu kho

---

## 3. Lộ Trình Tinh Chỉnh Giao Diện Cho Warehouse Atlas

1. **Giai đoạn 1 (Layout & Theme Transformation):**
   - Chuyển đổi giao diện Tkinter hiện tại sang phong cách ERP layout (Top Bar + Collapsible Module Tree + Dense Grid).
   - Áp dụng bảng màu doanh nghiệp: Xanh chủ đạo `#1B4F9B` / `#2457D6`, nền làm việc `#F4F6F9`, đường viền bảng rõ nét `#D0D7DE`.

2. **Giai đoạn 2 (Hoàn thiện Form Chứng Từ Nghiệp Vụ):**
   - Màn hình **Nhập kho (Goods Receipt):** Chọn PO -> Quét SKU/Barcode -> Chọn Lô/Hạn dùng -> Điền số lượng -> Xem tác động trước ghi -> Ghi sổ.
   - Màn hình **Điều chuyển kho (Transfer):** Chọn kho nguồn -> ô nguồn -> ô đích -> số lượng chuyển -> Ghi sổ bảo toàn tồn.
   - Màn hình **Xuất kho theo FEFO (Shipment):** Tự động gợi ý các lô hết hạn trước lên đầu danh sách lấy hàng.

3. **Giai đoạn 3 (Bảng Báo Cáo & Đối Soát Chuẩn Doanh Nghiệp):**
   - Tích hợp bảng đối soát sổ cái tự động (Reconciliation View) chứng minh tính bất biến và toàn vẹn của hệ thống khi bảo vệ đồ án tốt nghiệp.
