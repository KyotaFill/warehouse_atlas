# Bách Khoa Toàn Thư Phân Tích Toàn Bộ Ứng Dụng & Tính Năng ECOUNT ERP

> **Hồ sơ nghiên cứu & Thiết kế hệ thống:** Warehouse Atlas (Đồ Án Tốt Nghiệp)  
> **Nguồn đối chiếu:** ECOUNT ERP (Vietnam Commercial Version)  
> **Cơ cấu thực hiện:** Đội ngũ 8 Agent chuyên trách từng phân hệ

---

## 🗺️ TỔNG QUAN CẤU TRÚC ĐA TẦNG CỦA HỆ THỐNG

Giao diện ECOUNT ERP được tổ chức theo cấu trúc phân cấp **4 tầng sâu** kết hợp với **thanh công cụ ứng dụng tiện ích bên phải**:

```
[ TẦNG 1: Menu phân hệ chính (Top Navbar) ]
  ├─ 1. Trang cá nhân (Dashboard & Custom Widgets)
  ├─ 2. Tùy chỉnh (System Settings & Customization)
  ├─ 3. Groupware (Văn phòng điện tử & Điều hành)
  ├─ 4. Kiểm kê I (Quản lý Mua - Bán - Kho vận hàng ngày)
  ├─ 5. Kiểm kê II (Sản xuất, QC, Serial/Lot, WMS)
  ├─ 6. Kế toán I (Kế toán Tiền mặt, Ngân hàng, Hóa đơn VAT)
  ├─ 7. Kế toán II (Quản lý Công nợ Phải thu/Phải trả, Ngân sách, Hợp đồng)
  ├─ 8. Trung tâm dữ liệu (Data Center & Đồng bộ Excel)
  └─ 9. Nhân sự (Bảng lương, Chấm công, Hợp đồng lao động)

[ TẦNG 2: Tab nghiệp vụ ngang (Sub-tabs) ]
  Ví dụ chọn Kế toán II ➔ [ Quản lý phải thu | Quản lý phải trả | Quản lý ngân sách | Nhập khẩu | Chi phí | Hợp đồng ]

[ TẦNG 3: Cây menu chức năng dọc bên trái (Left Sidebar Menu) ]
  Ví dụ trong Quản lý phải thu ➔ [ Giảm phải thu mới | Danh sách phải thu | Sổ phải thu KH/NCC | Phân tích số dư... ]

[ TẦNG 4: Lưới dữ liệu & Biểu mẫu trung tâm (Data Grid & Input Forms) ]
  Bảng chi tiết cột, các nút thao tác nghiệp vụ, phím tắt F2/F3/F8.

[ THANH TIỆN ÍCH DỌC BÊN PHẢI (15 Popup & Apps) ]
  Dark Mode, AI hỗ trợ, Tìm kiếm tổng hợp, Customer Center, Mở cửa sổ mới, E Note, Thông báo, Tin nhắn, Messenger, Email, Phân quyền, Hỗ trợ từ xa, Timeline, Bookmark, UserPay.
```

---

## 👥 BÁO CÁO BÓC TÁCH CHI TIẾT TỪ TỪNG AGENT CHUYÊN TRÁCH

---

### 🟦 AGENT 1: Bóc Tách Phân Hệ KIỂM KÊ I (Inventory I)
*Trách nhiệm: Quản lý toàn bộ dòng hàng hóa thương mại mua vào, bán ra và dịch chuyển kho hàng ngày.*

#### 1.1 Nhánh "Bán hàng" (Sales)
- **Báo giá (Quotation):** Lập và gửi báo giá cho khách hàng; theo dõi tỷ lệ chuyển đổi từ báo giá thành đơn hàng.
- **Đơn bán hàng (Sales Order):** Tiếp nhận đơn đặt hàng từ khách hàng, kiểm tra lượng hàng khả dụng (`available_qty`), kích hoạt cơ chế giữ hàng (`StockReservation`).
- **Bán hàng (Sales / Goods Shipment):** Lập phiếu thực xuất hàng giao cho khách. Khi ghi sổ:
  - Giảm tồn kho vật lý (`on_hand`).
  - Tiêu thụ lượng hàng đã giữ (`reserved`).
  - Ghi nhận doanh thu bán hàng và công nợ phải thu của khách.
- **Đơn bán hàng chưa xuất kho:** Cảnh báo các đơn hàng đã chốt nhưng chưa nhặt xong hàng hoặc thiếu hàng tồn để giao.

#### 1.2 Nhánh "Mua hàng" (Purchasing)
- **Đề nghị mua hàng:** Bộ phận kho hoặc kinh doanh đề xuất số lượng cần mua khi chạm ngưỡng tồn kho an toàn (`Reorder Point`).
- **Đơn mua hàng (Purchase Order - PO):** Đặt hàng chính thức với Nhà cung cấp; ghi nhận giá mua dự kiến, ngày dự kiến giao hàng (`expected_on`).
- **Mua hàng (Goods Receipt / Inbound):** Lập phiếu thực nhập kho khi xe hàng về cửa nhận hàng (`RECEIVING_DOCK`):
  - Khởi tạo mã Lô nội bộ (`Lot`), ghi nhận hạn sử dụng, ngày sản xuất và giá vốn thực tế.
  - Tăng tồn kho vật lý (`on_hand`).
  - Cập nhật số lượng đã nhận trên PO (hỗ trợ nhập nhiều đợt - Partial Receipts).
- **Đơn mua hàng chưa nhập kho (Backorders):** Theo dõi tiến độ giao hàng của từng nhà cung cấp.

#### 1.3 Nhánh "Biến động hàng" (Stock Movements)
- **Chuyển kho / Chuyển vị trí (Stock Transfer):** Điều chuyển hàng giữa các ô kệ (`A-01-01` ➔ `A-01-02`) hoặc giữa các kho (`WH-MAIN` ➔ `WH-SUB`). Bảo toàn tuyệt đối tổng lượng tồn.
- **Kiểm kê thực tế (Physical Stocktake):** Đóng băng vị trí đếm (`is_frozen = True`), kiểm kê mù (Blind Count), so khớp số thực đếm và số sổ sách.
- **Điều chỉnh tồn kho (Stock Adjustment):** Sinh bút toán điều chỉnh tăng/giảm số dư có lý do giải trình.
- **Đổi trạng thái hàng (Reclassify):** Chuyển hàng giữa các phân loại chất lượng `GOOD` ➔ `QUARANTINE` ➔ `DAMAGED`.

#### 1.4 Nhánh "Báo cáo Kiểm kê I"
- **Số dư hàng tồn kho:** Báo cáo tồn kho tức thời đa chiều: theo Mặt hàng, theo Kho, theo Ô kệ, theo Lô và Hạn dùng.
- **Sổ chi tiết thẻ kho (Thẻ kho):** Lịch sử toàn bộ biến động nhập - xuất - tồn của từng mặt hàng theo trình tự thời gian.
- **Tình hình lợi nhuận theo mặt hàng / theo ngày:** Đối trừ giá bán và giá vốn thực tế để ra lợi nhuận gộp.

---

### 🟨 AGENT 2: Bóc Tách Phân Hệ KIỂM KÊ II (Inventory II)
*Trách nhiệm: Quản lý sản xuất, định mức vật tư, kiểm soát chất lượng, truy vết số Serial/Lô và hệ thống WMS nâng cao.*

#### 2.1 Nhánh "Sản xuất & Tính giá thành"
- **Định mức nguyên vật liệu (BOM - Bill of Materials):** Khai báo công thức: Để sản xuất 1 thùng sữa thành phẩm cần bao nhiêu sữa tươi nguyên liệu, bao nhiêu đường, bao nhiêu vỏ hộp và màng bọc.
- **Đơn hàng sản xuất (Manufacturing Order):** Lập kế hoạch sản xuất theo tuần/tháng.
- **Xuất kho NVL:** Xuất kho nguyên vật liệu đưa vào dây chuyền sản xuất (ghi giảm tồn kho nguyên vật liệu).
- **Nhập kho thành phẩm:** Đóng gói và nhập kho thành phẩm đã hoàn tất (ghi tăng tồn kho thành phẩm).
- **Tính giá thành sản xuất:** Tự động tập hợp chi phí nguyên vật liệu trực tiếp, chi phí nhân công và chi phí chung để tính ra giá thành đơn vị chính xác.

#### 2.2 Nhánh "Số Serial / Lot" (Serial & Lot Tracking)
- Quản lý định danh từng chiếc hàng bằng mã Serial duy nhất hoặc từng đợt hàng bằng mã Lô (Batch/Lot).
- **Truy vết thu hồi (Product Recall):** Khi phát hiện 1 lô bị lỗi từ nhà máy, chỉ cần nhập mã Lô ➔ Hệ thống lập tức truy ra: Lô này đã nhập ngày nào, đang nằm ở ô kệ nào, đã xuất bán cho những khách hàng nào, trên các hóa đơn nào.

#### 2.3 Nhánh "Quản lý chất lượng (QC)" & "WMS"
- Quy trình kiểm định chất lượng trước khi nhập kho chính thức.
- Tối ưu hóa sơ đồ vị trí lưu kho 2D, quản lý sức chứa của từng ô kệ.

---

### 🟩 AGENT 3: Bóc Tách Phân Hệ KẾ TOÁN I (Accounting I)
*Trách nhiệm: Kế toán tài chính, tiền tệ, ngân hàng, hóa đơn điện tử VAT và báo cáo thuế theo luật Việt Nam.*

#### 3.1 Tiền mặt & Tiền gửi ngân hàng
- **Phiếu thu (Cash Receipt):** Thu tiền bán hàng, thu hồi nợ tạm ứng, thu tiền khác.
- **Phiếu chi (Payment Voucher):** Chi thanh toán tiền hàng cho NCC, chi phí điện nước, tiếp khách.
- **Sổ quỹ tiền mặt & Sổ phụ ngân hàng:** Đối soát số dư tiền theo thời gian thực.

#### 3.2 Hóa đơn & Hóa đơn điện tử (VN)
- Tích hợp phát hành hóa đơn điện tử GTGT theo Thông tư 78 / Nghị định 123 tại Việt Nam.
- Tự động lấy dữ liệu từ Phiếu bán hàng sang để xuất hóa đơn nhanh chóng, tránh sai lệch mã hàng, số lượng và thuế suất.

#### 3.3 Tài sản cố định & Báo cáo kế toán
- Khấu hao tài sản cố định hàng tháng (máy móc kho, xe nâng, giá kệ).
- Bảng cân đối phát sinh, Báo cáo kết quả hoạt động kinh doanh (P&L), Bảng lưu chuyển tiền tệ.

---

### 🟧 AGENT 4: Bóc Tách Phân Hệ KẾ TOÁN II (Accounting II - Đúng Màn Hình Ảnh #5)
*Trách nhiệm: Quản lý chuyên sâu về Công nợ đối tác, Hợp đồng kinh tế, Ngân sách và Hàng nhập khẩu.*

#### 4.1 Quản lý phải thu (Accounts Receivable - Đúng màn hình bạn vừa mở!)
- **Giảm phải thu mới:** Màn hình lập chứng từ ghi nhận giảm công nợ khách hàng (khi khách thanh toán tiền mặt, chuyển khoản ngân hàng hoặc được chiết khấu/giảm giá).
  - *Cột dữ liệu:* Số theo dõi phải thu, Ngày, Ngày đến hạn, Tên tài khoản, Mã & Tên khách hàng, Số dư nợ hiện tại, Số tiền chiết khấu, Số tiền giảm trừ thực tế.
  - *Nút hành động:* **`Tạo nhật ký thu tiền`** (tự động hạch toán sang sổ kế toán tiền mặt/ngân hàng).
- **Danh sách phải thu & Chi tiết giao dịch:** Xem tất cả các khoản nợ của từng khách hàng.
- **Phân tích số dư phải thu:** Báo cáo tuổi nợ (Aging Report): nợ trong hạn (0-30 ngày), nợ quá hạn (30-60 ngày, >90 ngày) để có biện pháp nhắc nợ.

#### 4.2 Quản lý phải trả (Accounts Payable)
- Theo dõi chi tiết công nợ phải trả cho từng Nhà cung cấp theo từng lô hàng đã nhập.
- Lập kế hoạch thanh toán đúng hạn để hưởng chiết khấu thanh toán sớm.

#### 4.3 Quản lý ngân sách & Hợp đồng
- Lập dự toán ngân sách chi tiêu cho từng phòng ban (Kho, Bán hàng, Marketing).
- Quản lý hợp đồng mua bán, hợp đồng nguyên tắc, tiến độ thanh toán và ký kết điện tử.

---

### 🟪 AGENT 5: Bóc Tách Phân Hệ GROUPWARE & NHÂN SỰ
*Trách nhiệm: Môi trường làm việc số nội bộ, phê duyệt tờ trình và tính lương nhân viên.*

#### 5.1 Groupware (Văn phòng điện tử)
- **Phê duyệt điện tử (e-Approval):** Luồng duyệt online nhiều cấp: Nhân viên kho tạo phiếu ➔ Trưởng kho duyệt ➔ Kế toán duyệt ➔ Giám đốc phê duyệt trực tuyến (kèm chữ ký số).
- **Bảng tin & Thông báo nội bộ:** Đăng thông báo nghỉ lễ, quy định an toàn kho, chính sách thưởng kinh doanh.
- **Lịch công tác (Schedule):** Lịch hẹn giao nhận hàng, lịch kiểm kê kho, lịch họp công ty.
- **Quản lý công việc (Task Management):** Giao việc cho nhân viên kho, theo dõi tiến độ hoàn thành (To Do, In Progress, Done).

#### 5.2 Nhân sự & Tiền lương (HR & Payroll)
- **Hồ sơ nhân sự:** Quản lý thông tin nhân viên, hợp đồng lao động, bảo hiểm xã hội.
- **Chấm công (Time Management):** Đồng bộ máy quét vân tay/khuôn mặt tại kho, tính giờ làm thêm ca đêm (OT).
- **Bảng lương tự động:** Tính lương theo ngày công, phụ cấp độc hại/nặng nhọc tại kho, thưởng năng suất đóng gói và khấu trừ thuế TNCN.

---

### 🟫 AGENT 6: Bóc Tách Phân Hệ TÙY CHỈNH & TRUNG TÂM DỮ LIỆU
*Trách nhiệm: Quản trị hệ thống, phân quyền người dùng và trao đổi dữ liệu quy mô lớn.*

#### 6.1 Tùy chỉnh (Customization)
- **Phân quyền người dùng (RBAC - Role-Based Access Control):** Cấu hình quyền chi tiết đến từng nút bấm: Nhân viên kho chỉ thấy phân hệ Kho; Kế toán chỉ thấy Tiền và Công nợ; Giám đốc thấy toàn bộ báo cáo doanh thu.
- **Thiết kế mẫu in (Print Form Designer):** Kéo thả tùy chỉnh mẫu Phiếu nhập kho, Phiếu xuất kho, Hóa đơn theo đúng nhận diện thương hiệu của công ty.
- **Thêm trường tùy biến (Custom Fields):** Tự do thêm trường thông tin vào mặt hàng hoặc phiếu (ví dụ: thêm trường *Vị trí kệ*, *Nhiệt độ bảo quản*).

#### 6.2 Trung tâm dữ liệu (Data Center)
- **Tải lên hàng loạt qua Excel:** Nhập danh mục 10,000 SKU, 5,000 khách hàng từ file Excel chỉ bằng 1 thao tác kéo thả.
- **Sao lưu & Phục hồi dữ liệu (Backup & Restore):** Đảm bảo an toàn dữ liệu định kỳ.

---

### ⚙️ AGENT 7: Bóc Tách TOÀN BỘ 15 TIỆN ÍCH TRÊN THANH BÊN PHẢI (Right Toolbar Apps)

Khi click vào từng biểu tượng trên thanh dọc bên phải, hệ thống kích hoạt các popup/ứng dụng độc lập sau:

| Icon / Tên App | Khi Click vào sẽ làm gì? | Ý nghĩa nghiệp vụ trong thực tế |
|---|---|---|
| 🌙 **Dark Mode** | Chuyển đổi giao diện sáng/tối tức thì | Giúp thủ kho làm việc ca đêm không bị mỏi mắt |
| 🤖 **AI hỗ trợ công việc** | Mở hộp thoại chat AI: *"Yêu cầu tóm tắt bằng AI"*, tự động tổng hợp thông báo và phân tích số liệu | Trợ lý ảo AI giúp tóm tắt báo cáo tồn kho và cảnh báo rủi ro |
| 🔍 **Tìm kiếm tổng hợp** | Mở ô tìm kiếm toàn cục: Gõ từ khóa tìm ra ngay Chứng từ, Khách hàng, SKU, Hóa đơn | Tìm nhanh 1 phiếu kho trong hàng triệu chứng từ |
| 🎧 **Hỗ trợ thông minh** | Mở ticket gửi câu hỏi trực tiếp cho đội kỹ thuật hoặc kết nối tổng đài hỗ trợ | Hỗ trợ người dùng khi gặp lỗi thao tác trên phần mềm |
| 🗗 **Mở cửa sổ mới** | Bật một cửa sổ/tab độc lập | Giúp người dùng vừa xem bảng Tồn kho vừa lập Phiếu xuất ở màn hình thứ hai |
| 📝 **E Note** | Mở sổ tay ghi chú nhanh dán lên màn hình | Ghi nhớ các việc cần làm gấp: *"Chiều nay nhập 50 thùng Vinamilk"* |
| 🔔 **Thông báo** | Mở khay thông báo đẩy (Push Notifications) | Báo có đơn hàng mới cần xuất, hoặc có phiếu chờ duyệt |
| 💬 **Tin nhắn** | Mở hộp thư tin nhắn nội bộ | Gửi chỉ đạo công việc giữa các phòng ban |
| 🗨️ **Messenger** | Mở cửa sổ chat tức thời (Real-time Chat) | Nhắn tin, gửi ảnh hàng hỏng tại kho cho người quản lý xem ngay |
| ✉️ **Email** | Mở trình duyệt Webmail doanh nghiệp | Gửi trực tiếp Phiếu đặt hàng cho Nhà cung cấp qua email |
| 🛡️ **Chỉ xem menu có quyền** | Bật/tắt chế độ lọc menu phân quyền | Ẩn các menu không được cấp quyền để giao diện gọn gàng |
| 🖥️ **Hỗ trợ từ xa** | Mở trình kết nối điều khiển máy từ xa | Kỹ thuật viên kết nối vào máy người dùng để hướng dẫn trực tiếp |
| ⏱️ **Dòng thời gian (Timeline)** | Mở nhật ký kiểm toán (Audit Trail) | Xem ai đã sửa phiếu, ai đã duyệt, vào thời điểm nào (truy vết trách nhiệm) |
| ⭐ **Bookmark** | Mở danh sách các chức năng đánh dấu sao | Truy cập 1-click vào các màn hình làm việc thường xuyên nhất |
| 💳 **UserPay** | Mở trang thanh toán cước phí phần mềm | Quản lý gia hạn gói phần mềm ERP định kỳ |

---

## 🎯 AGENT 8 (TÔI - LEAD ORCHESTRATOR): ĐÁNH GIÁ & ĐỊNH HƯỚNG CHO ĐỒ ÁN TỐT NGHIỆP

Qua việc bóc tách toàn diện hệ thống ở trên, chúng ta rút ra một kết luận chiến lược vô cùng quan trọng:

1. **ECOUNT ERP là một hệ sinh thái khổng lồ:** Bao gồm cả Kế toán thuế, Nhân sự chấm công, Groupware, Hợp đồng điện tử... Một công ty phần mềm lớn mất hàng chục năm để phát triển toàn bộ hệ thống này.
2. **Định vị chính xác cho Đồ Án Tốt Nghiệp của bạn:**
   - **Tên đồ án:** *Warehouse Atlas — Hệ Thống Quản Lý Kho Thông Minh*.
   - **Trọng tâm bảo vệ:** Đồ án của bạn tập trung sâu và sắc bén vào **Phân hệ KIỂM KÊ I & II (Toàn bộ chu trình Mua hàng - Bán hàng - Tồn kho - Quản lý Lô & Hạn sử dụng theo FEFO - Sổ cái đối soát toàn vẹn)** kết hợp với **Sơ đồ quy trình 13 mắt xích** và **Trợ lý AI hỗ trợ công việc**.
   - **Giữ nguyên giao diện ECOUNT ERP:** Chúng ta giữ nguyên 100% bố cục màn hình chuyên nghiệp này, và kích hoạt các luồng tương tác thực tế kết nối vào database PostgreSQL của bạn!
