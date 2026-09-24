# Danh mục và đặc tả use case — Warehouse Atlas

Phiên bản bổ sung 1.1 · 13/09/2026 · Bám schema 27 bảng lõi + 10 bảng mở rộng ở bộ thiết kế trước.

## Cách dùng

Đọc hướng dẫn actor/quan hệ UML trong `warehouse_atlas_huong_dan_ve.md`, mở file `.drawio` để chỉnh sơ đồ. Danh mục dưới đây có 35 use case cấp mục tiêu/tác vụ người dùng, bao gồm một số nhóm bảo trì dữ liệu. Không phải 35 màn hình,35 bảng hoặc 35 module code. Các luồng con SF01–SF05 chỉ hiện trên sơ đồ chi tiết.

## Giả định và quyết định bổ sung

- A=ADMIN, M=MANAGER, O=OPERATOR. U là actor tổng quát chỉ cho hành vi chung; role thực lưu trong app_role/user_role. Không mặc định ADMIN có quyền ghi kho.
- O lập phiếu và thao tác hold; M phê duyệt/ghi sổ. M cũng có các thao tác vận hành được ghi rõ trong ma trận; không có actor M kế thừa O chỉ vì chức danh.
- Không bắt buộc người lập khác người duyệt trong baseline này. Nếu học phần yêu cầu nguyên tắc hai người, phải bổ sung policy actor!=created_by và phân công phù hợp.
- Trong v1 không có PENDING_APPROVAL hoặc REJECTED cho inventory_document. Phiếu lưu DRAFT để manager xem; APPROVED chưa tác động tồn. Ý kiến cần sửa ghi audit/giao diện; không giả vờ đã có hệ thống comment/task phê duyệt riêng.
- Tài khoản bị khóa/quyền bị thu hồi được kiểm lại tại mỗi service call. Audit quyền và phiên là chi tiết cần agent triển khai, chưa phải tính năng đã có.
- Cột giá vốn và giá mua chỉ cho M trong báo cáo/công cụ AI là policy đề xuất mới của bổ sung này; không cần thêm bảng nếu map quyền bằng code.
- Barcode là một cách nhập của cùng use case; v1 không bắt buộc mọi dòng đều phải quét. Không tạo một oval cho mỗi nút thêm/sửa/xóa/quét.
- Chức năng sao lưu/khôi phục vẫn là runbook vận hành đã có trong kế hoạch; chưa giả định có màn trong ứng dụng nên không thêm nó vào boundary use case GUI.

## Danh mục và ma trận actor

| ID | Use case | Actor | Mức | Quyền/ghi chú |
|---|---|---|---|---|
| UC01 | Đăng nhập | U | P0 |  |
| UC02 | Quản lý tài khoản và vai trò | A | P0 |  |
| UC03 | Quản lý hàng hóa, đơn vị và mã vạch | M | P0 |  |
| UC04 | Quản lý kho và vị trí | M | P0 |  |
| UC05 | Quản lý đối tác và nguồn cung | M | P0 |  |
| UC06 | Quản lý đơn mua | O, M | P0 | O: soạn DRAFT; M: soạn, xác nhận, đóng/hủy. |
| UC07 | Lập phiếu nhập hàng | O, M | P0 |  |
| UC08 | Phê duyệt phiếu kho | M | P0 |  |
| UC09 | Ghi sổ phiếu kho | M | P0 |  |
| UC10 | Quản lý đơn xuất | O, M | P0 | O: soạn DRAFT; M: soạn, xác nhận, đóng/hủy. |
| UC11 | Giữ hàng cho đơn | O, M | P0 |  |
| UC12 | Nhả hàng đã giữ | O, M | P0 |  |
| UC13 | Lập phiếu xuất hàng | O, M | P0 |  |
| UC14 | Lập phiếu chuyển vị trí | O, M | P0 |  |
| UC15 | Lập phiếu đổi tình trạng hàng | O, M | P0 |  |
| UC16 | Mở phiên kiểm kê | M | P0 |  |
| UC17 | Ghi số đếm kiểm kê | O, M | P0 |  |
| UC18 | Duyệt và chốt kiểm kê | M | P0 |  |
| UC19 | Lập phiếu nhận hàng khách trả | O, M | P0 |  |
| UC20 | Lập phiếu trả nhà cung cấp | O, M | P0 |  |
| UC21 | Đảo chứng từ đã ghi sổ | M | P0 |  |
| UC22 | Tra cứu tồn kho và báo cáo | O, M | P0 | O: xem lượng; M: thêm giá vốn/giá mua. |
| UC23 | Truy vết lô hàng | O, M | P1 |  |
| UC24 | Khóa hoặc mở khóa lô | M | P1 |  |
| UC25 | Xem tồn tại mốc ghi sổ | M | P1 |  |
| UC26 | Thiết kế sơ đồ và lối đi kho | M | P1 |  |
| UC27 | Lập kế hoạch lấy hàng | O, M | P1 |  |
| UC28 | Xác nhận lấy hàng theo kế hoạch | O, M | P1 |  |
| UC29 | Hỏi trợ lý kho | O, M | P1 | O: hỏi nghiệp vụ lượng/truy vết; M: thêm giá và đề xuất mua. |
| UC30 | Xem đề xuất bổ sung hàng | M | P1 |  |
| UC31 | Tạo đề xuất mua trong hội thoại | M | P1 |  |
| UC32 | Duyệt đề xuất AI để tạo PO nháp | M | P1 |  |
| UC33 | Xem nhật ký và đối soát kho | M | P0 |  |
| UC34 | Mô phỏng kịch bản nhu cầu và cung ứng | M | P2 |  |
| UC35 | Lập phiếu tồn đầu kỳ | M | P0 |  |

## Bảo đảm chung

G1: Mọi use case cần phiên và quyền, trừ UC01. Thao tác đăng xuất phải hủy phiên; đây là yêu cầu quản lý phiên chung trong bản đặc tả này. Đăng nhập là tiền điều kiện của các use case khác, không phải include cần vẽ ở mọi oval.
G2: W/R trong đặc tả là ánh xạ kỹ thuật hỗ trợ triển khai; không biến database hoặc repository thành actor.
G3: Header DRAFT có thể chưa đủ dòng, nhưng mỗi dòng lưu DB vẫn phải thỏa NOT NULL/CHECK. Nội dung form nhập dở giữ ở UI; không mặc định schema lưu được mọi giá trị thiếu. Luồng chính dùng dữ liệu đầy đủ.
G4: Với thao tác ghi kho, khóa và kiểm lại theo đặc tả database; check UI chỉ là phản hồi sớm. Các màn không được gọi SQL cập nhật balance trực tiếp.
G5: Lượng là Decimal theo base UOM; snapshot quy đổi của chứng từ không đổi khi master đổi.
G6: Lỗi trước commit không để lại tác động kho một phần. Mất phản hồi mạng sau commit phải tra lại kết quả theo khóa yêu cầu, không tự kết luận đã rollback.
G7: Chỉ UC09 và các use case compound được quy định (UC18/21) gọi cùng engine ghi sổ. Lưu draft, duyệt, quét checklist và trò chuyện AI chưa tạo movement.
G8: Error code/Thông báo phải có ngữ cảnh hành động nhưng không lộ credential, stack trace, prompt bí mật. LLM/query chạy ngoài Tk main thread và ngoài transaction kho kéo dài.

G9: Schema chưa có FK trực tiếp từ dòng phiếu nháp tới reservation. UC13 lưu SO line + SKU/lot/location/condition; UC09 khóa các hold phù hợp và lưu liên kết tiêu thụ thực trong reservation_event.document_line_id. Nếu cần cố định lựa chọn hold ngay ở draft, phải bổ sung bảng liên kết và migration.

## Đặc tả chi tiết

### UC01 — Đăng nhập

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Thiết lập phiên làm việc với đúng quyền. |
| Actor chính | Người dùng nội bộ |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Đăng nhập” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Có tài khoản đang hoạt động. |
| Dữ liệu vào | Tên đăng nhập; mật khẩu. |

**Luồng chính**

1. Người dùng mở màn đăng nhập và nhập thông tin.
2. Hệ thống chuẩn hóa tên, kiểm mật khẩu bằng hash và trạng thái tài khoản.
3. Hệ thống nạp các vai trò, mở màn được phép và thiết lập phiên.

**Luồng thay thế/ngoại lệ**

- 2a. Sai thông tin hoặc tài khoản bị khóa: thông báo không đăng nhập được; quay về bước 1.
- 1a. Người dùng hủy đăng nhập trước khi xác thực xong: kết thúc không tạo phiên.

**Hậu điều kiện thành công:** Có phiên gắn user_id và các role hiện tại; chưa thay đổi tồn.

**Bảo đảm khi không thành công:** Không tạo phiên có quyền khi xác thực thất bại.

**Ánh xạ database:** R: app_user, app_role, user_role; W: audit_event (sự kiện đăng nhập phù hợp).

**Tiêu chí nghiệm thu đại diện:**

- Tài khoản bị khóa không đăng nhập được.
- Đăng xuất rồi gọi use case ghi dữ liệu phải bị từ chối.

### UC02 — Quản lý tài khoản và vai trò

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Tạo, khóa tài khoản và gán quyền vận hành. |
| Actor chính | Quản trị hệ thống |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Quản lý tài khoản và vai trò” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Actor ADMIN đã đăng nhập. |
| Dữ liệu vào | Username, tên hiển thị, mật khẩu khởi tạo, role, lý do khóa/thay quyền. |

**Luồng chính**

1. Admin tìm tài khoản hoặc tạo tài khoản mới.
2. Hệ thống kiểm username duy nhất và danh sách role hợp lệ.
3. Admin xác nhận tạo/sửa/khóa và gán role.
4. Hệ thống lưu hash, quan hệ role và audit; cập nhật quyền ở lần gọi nghiệp vụ tiếp theo.

**Luồng thay thế/ngoại lệ**

- 2a. Username trùng: báo lỗi ở field; sửa tại bước 1.
- 3a. Thao tác làm mất admin hoạt động cuối cùng: từ chối; kết thúc không đổi.

**Hậu điều kiện thành công:** Tài khoản/quyền được cập nhật, có audit; người bị khóa không tiếp tục ghi dữ liệu.

**Bảo đảm khi không thành công:** Không lưu mật khẩu thô; không có thay đổi quyền dở dang.

**Ánh xạ database:** R/W: app_user, app_role, user_role; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Operator không gọi được use case này.
- Khóa tài khoản làm phiên đang mở mất quyền ghi ở request kế tiếp.

### UC03 — Quản lý hàng hóa, đơn vị và mã vạch

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Duy trì SKU và quy cách để nhận/xuất đúng đơn vị. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Quản lý hàng hóa, đơn vị và mã vạch” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Actor MANAGER; mã master đang ở phiên bản hiện tại. |
| Dữ liệu vào | SKU, tên, nhóm, base UOM, hệ số quy đổi, barcode, cờ hạn dùng. |

**Luồng chính**

1. Quản lý tạo/tìm SKU và nhập thuộc tính.
2. Hệ thống kiểm mã, đơn vị chuẩn và quy đổi theo SKU; tạo quy đổi base=1.
3. Quản lý lưu; hệ thống lưu master và audit.
4. Hệ thống cho tra cứu theo barcode vừa gắn.

**Luồng thay thế/ngoại lệ**

- 2a. Barcode thuộc SKU khác: từ chối; quay về bước 1.
- 2b. SKU đã có giao dịch mà đổi base UOM: từ chối thay đổi đó; không sửa lịch sử.
- 3a. Ngừng dùng SKU: đổi is_active; giữ dữ liệu đã tham chiếu.

**Hậu điều kiện thành công:** Master hợp lệ; phiếu cũ giữ factor snapshot.

**Bảo đảm khi không thành công:** Không tạo mã barcode trùng hoặc thay ý nghĩa lượng tồn cũ.

**Ánh xạ database:** R/W: category, uom, product, product_uom, product_barcode; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Một thùng SKU A=48 không làm thùng SKU B cũng bằng48.
- Deactive SKU không xóa lịch sử movement.

### UC04 — Quản lý kho và vị trí

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Mô tả đúng kho, kệ, ô và công dụng vị trí. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Quản lý kho và vị trí” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Actor MANAGER. |
| Dữ liệu vào | Kho, mã ô, cha, usage, timezone, trạng thái. |

**Luồng chính**

1. Quản lý chọn kho và thêm/sửa vị trí trong cây.
2. Hệ thống kiểm cha cùng kho, không chu trình, mã không trùng.
3. Quản lý xác nhận; hệ thống lưu cấu trúc và audit.

**Luồng thay thế/ngoại lệ**

- 2a. Chọn con làm cha hoặc cha ở kho khác: từ chối.
- 2b. Đổi warehouse/usage của vị trí đã có giao dịch: từ chối; đề nghị tạo vị trí khác.
- 3a. Vô hiệu hóa vị trí còn hàng/hold: yêu cầu xử lý chúng trước theo policy.

**Hậu điều kiện thành công:** Cây hợp lệ; node STRUCTURAL không dùng chứa hàng.

**Bảo đảm khi không thành công:** Không làm hàng có lịch sử tự chuyển sang kho khác.

**Ánh xạ database:** R/W: warehouse, location; R: stock_balance, stock_movement; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- FK cùng kho và kiểm chu trình cùng hoạt động.
- Ghi hàng vào STRUCTURAL bị từ chối.

### UC05 — Quản lý đối tác và nguồn cung

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Có thông tin khách/NCC và điều kiện đặt hàng theo SKU. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Quản lý đối tác và nguồn cung” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Actor MANAGER; SKU tồn tại. |
| Dữ liệu vào | Mã đối tác, loại khách/NCC, thông tin liên hệ; SKU, lead time, MOQ, bội số đặt. |

**Luồng chính**

1. Quản lý tạo/tìm đối tác, chọn các vai trò kinh doanh.
2. Hệ thống kiểm mã duy nhất và ít nhất một vai trò.
3. Nếu là NCC, quản lý khai báo mặt hàng và điều kiện cung ứng.
4. Hệ thống lưu và ghi audit.

**Luồng thay thế/ngoại lệ**

- 2a. Đối tác vừa mua vừa bán: bật cả hai cờ; tiếp tục.
- 3a. MOQ âm/bội số bằng0: từ chối field sai.
- 4a. Ngừng hợp tác: deactivate, giữ chứng từ cũ.

**Hậu điều kiện thành công:** Nguồn cung có dữ liệu cho PO và gợi ý mua.

**Bảo đảm khi không thành công:** Không tạo supplier_product trỏ đối tác không phải NCC.

**Ánh xạ database:** R/W: partner, supplier_product; R: product; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- NCC không bị gán tự động thành khách hàng.
- Chỉ một NCC ưu tiên cho SKU theo unique index hiện tại.

### UC06 — Quản lý đơn mua

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Ghi nhu cầu mua và xác nhận lượng còn chờ nhận. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Quản lý đơn mua” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Nhà cung cấp và SKU hợp lệ. |
| Dữ liệu vào | NCC, kho nhận, SKU/UOM, lượng đặt, giá, ngày dự kiến. |

**Luồng chính**

1. Nhân viên lập hoặc sửa PO DRAFT.
2. Hệ thống tính lượng chuẩn, giữ hệ số snapshot và kiểm dữ liệu.
3. Quản lý kiểm nội dung và xác nhận PO thành CONFIRMED.
4. Hệ thống hiển thị lượng còn nhận dựa trên phiếu đã ghi sổ.

**Luồng thay thế/ngoại lệ**

- 3a. Chưa xác nhận: giữ DRAFT; kết thúc chưa tạo cam kết nhận.
- 4a. Đóng thiếu: quản lý nhập lượng đóng và lý do; hệ thống kiểm không vượt phần còn lại.
- 4b. Hủy: chỉ phần chưa thực hiện theo điều kiện; không xóa phiếu đã nhận.

**Hậu điều kiện thành công:** PO phản ánh cam kết; không tăng tồn vật lý.

**Bảo đảm khi không thành công:** PO lỗi không được CONFIRMED, không có movement.

**Ánh xạ database:** R/W: purchase_order, purchase_order_line; R: partner, product_uom, inventory_document_line; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Xác nhận PO100 không làm tồn tăng100.
- Đã nhận60 thì chỉ được đóng thiếu tối đa40.

### UC07 — Lập phiếu nhập hàng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Ghi chính xác hàng thực nhận để chờ duyệt. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu nhập hàng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | PO CONFIRMED còn lượng nhận; vị trí lá hợp lệ. |
| Dữ liệu vào | PO line, lượng thực nhận/UOM, mã lô NCC, hạn dùng, giá, vị trí, condition. |

**Luồng chính**

1. Nhân viên chọn PO và các dòng còn nhận.
2. Hệ thống hiển thị lượng còn nhận cùng dữ liệu SKU.
3. Nhân viên quét/chọn SKU, nhập lượng, lô, hạn, vị trí.
4. Hệ thống kiểm quy đổi và dữ liệu lô; hiển thị tác động dự kiến.
5. Nhân viên lưu phiếu RECEIPT ở DRAFT để quản lý xem.

**Luồng thay thế/ngoại lệ**

- 3a. Nhận một phần: nhập lượng thực tế nhỏ hơn phần còn; tiếp tục bước4.
- 3b. Chia cùng SKU vào hai ô: tạo hai dòng với cùng lot nội bộ nếu cùng lần nhận/giá.
- 4a. SKU theo hạn thiếu expires_on: yêu cầu bổ sung; chưa cho lưu phiếu hợp lệ.
- 4b. Có dấu hiệu hỏng: chọn QUARANTINE/DAMAGED, không tự coi là hàng tốt.

**Hậu điều kiện thành công:** Có phiếu nháp đầy đủ; chưa tăng on_hand hoặc tạo movement.

**Bảo đảm khi không thành công:** Không ảnh hưởng tồn nếu hủy thao tác; lot chưa dùng có thể còn ở master nhưng không mang số dư.

**Ánh xạ database:** R: purchase_order, purchase_order_line, product_uom, location; W: lot, inventory_document, inventory_document_line, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Nhập2 thùng×48 hiển thị dự kiến96; tồn chưa đổi.
- Hai người lập nháp cùng PO được, nhưng lúc ghi sổ phải kiểm tổng lại.

### UC08 — Phê duyệt phiếu kho

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Cho phép phiếu hợp lệ đi tới bước ghi sổ. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Phê duyệt phiếu kho” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Phiếu DRAFT, có dòng; manager có quyền với loại phiếu. |
| Dữ liệu vào | Mã phiếu, expected_version, quyết định duyệt hoặc nội dung cần sửa. |

**Luồng chính**

1. Quản lý mở phiếu nháp và đọc nguồn/đích, lô, lượng, căn cứ.
2. Hệ thống kiểm tính đầy đủ và hiển thị tác động dự kiến mới nhất.
3. Quản lý chọn Phê duyệt.
4. Hệ thống kiểm version rồi đặt APPROVED, approved_by, tăng version, ghi thời điểm vào audit.

**Luồng thay thế/ngoại lệ**

- 2a. Dữ liệu sai: giữ DRAFT, phản hồi lý do cần sửa qua giao diện/audit.
- 3a. Muốn sửa phiếu APPROVED: manager trả về DRAFT, bỏ approved_by, tăng version và audit trước khi sửa dòng.
- 4a. Người khác đã sửa: báo xung đột, tải lại để xem rồi duyệt lại.

**Hậu điều kiện thành công:** Phiếu APPROVED, dòng bị khóa sửa; tồn vẫn không đổi.

**Bảo đảm khi không thành công:** Không phê duyệt phiên bản mà manager chưa xem.

**Ánh xạ database:** R/W: inventory_document; R: inventory_document_line, master liên quan; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- APPROVED chưa có movement.
- Không tạo trạng thái PENDING_APPROVAL mới trong DB hiện tại.

### UC09 — Ghi sổ phiếu kho

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Xác nhận tác động tồn của phiếu đúng một lần. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Ghi sổ phiếu kho” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Phiếu APPROVED; dữ liệu, quyền và điều kiện hiện tại còn hợp lệ. |
| Dữ liệu vào | document_id, expected_version, idempotency_key và nội dung đã phê duyệt. |

**Luồng chính**

1. Quản lý chọn Ghi sổ; hệ thống hiện tóm tắt tác động và căn cứ.
2. Quản lý xác nhận. Hệ thống thực hiện SF01: khóa/kiểm dữ liệu hiện tại, version, đơn, lô, vị trí và lượng giữ.
3. Hệ thống thực hiện SF02: trong một transaction, ghi movement, cập nhật balance/reservation theo loại phiếu, audit và trạng thái POSTED.
4. Sau commit, hệ thống trả mã phiếu và số dư mới, cho mở lịch sử liên quan.

**Luồng thay thế/ngoại lệ**

- 2a. Không đủ hàng/lô block/ô đang đếm: từ chối, giữ phiếu APPROVED; nêu nguyên nhân.
- 2b. Đã ghi thành công cùng key và payload: trả phiếu cũ, không ghi lần hai.
- 2c. Cùng key nhưng payload khác: conflict, kết thúc không ghi.
- 3a. Một thao tác ghi lỗi: rollback toàn bộ; không được báo thành công.
- 4a. Mất kết nối sau commit: lần thử lại dùng cùng key để lấy kết quả cũ.

**Hậu điều kiện thành công:** Phiếu POSTED bất biến; mỗi dòng có đúng một movement khớp; sổ và số dư đồng nhất.

**Bảo đảm khi không thành công:** Tồn/hold giữ nguyên khi transaction không commit; nếu kết quả mạng chưa rõ phải tra theo key.

**Ánh xạ database:** R/W: inventory_document, stock_balance, stock_reservation; R: lines, orders, lot, location, stocktake; W: stock_movement, reservation_event, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Nhấp2 lần chỉ một lần tăng/giảm tồn.
- Hai dòng cùng lấy7+6 từ bucket10 phải bị từ chối toàn phiếu.

### UC10 — Quản lý đơn xuất

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Ghi nhu cầu giao cho khách và phần còn phải đáp ứng. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Quản lý đơn xuất” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Khách hàng và SKU hợp lệ. |
| Dữ liệu vào | Khách, kho, các SKU/UOM, lượng, ngày giao dự kiến. |

**Luồng chính**

1. Nhân viên lập SO DRAFT.
2. Hệ thống kiểm SKU/UOM, lượng và lưu hệ số snapshot.
3. Quản lý xác nhận SO thành CONFIRMED.
4. Hệ thống hiển thị đã giao, đang giữ và còn thiếu theo dữ liệu hiện tại.

**Luồng thay thế/ngoại lệ**

- 3a. Chưa xác nhận: giữ DRAFT.
- 4a. Đóng thiếu/hủy phần còn lại: manager giải phóng các hold liên quan và cập nhật lượng đóng trong giao dịch kiểm soát.
- 4b. Khách trả hàng sau giao: tạo UC19; không tự mở lại nhu cầu cũ.

**Hậu điều kiện thành công:** Nhu cầu được xác nhận; chưa tự trừ tồn hoặc tự giữ hàng.

**Bảo đảm khi không thành công:** Không để canceled/closed demand tiếp tục chiếm hold chưa xử lý.

**Ánh xạ database:** R/W: sales_order, sales_order_line; R: partner, product_uom; W theo đóng/hủy: stock_reservation, reservation_event, stock_balance, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- SO50 confirmed không làm tồn giảm50.
- Đóng phần chưa giao chỉ nhả phần giữ chưa consumed.

### UC11 — Giữ hàng cho đơn

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Dành lượng hàng đủ điều kiện cho từng dòng đơn đã xác nhận. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Giữ hàng cho đơn” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | SO CONFIRMED còn nhu cầu; vị trí không bị freeze. |
| Dữ liệu vào | order_id, dòng cần giữ, lượng, chế độ đủ toàn bộ/một phần. |

**Luồng chính**

1. Nhân viên chọn đơn và yêu cầu giữ hàng.
2. Hệ thống lấy và khóa dữ liệu hiện tại, thực hiện SF03 để xác định các lô/bucket đủ điều kiện theo ngày giao.
3. Hệ thống chọn FEFO cho SKU theo hạn, FIFO cho SKU còn lại; phân lượng theo các bucket.
4. Hệ thống kiểm tổng nhu cầu và khả dụng, tạo reservation + ALLOCATE event, tăng reserved nguyên tử.
5. Hệ thống hiển thị lô/vị trí/lượng đã giữ, lý do chọn và phần thiếu nếu có.

**Luồng thay thế/ngoại lệ**

- 3a. Chỉ có3 nhưng cần7: chế độ mặc định all-or-nothing báo thiếu4, không tạo hold.
- 3b. Người dùng đã chọn Giữ một phần: có thể giữ3, hiển thị còn thiếu4; không tự đổi mode.
- 4a. Phiên khác vừa giữ hàng: đọc lại dưới khóa; từ chối hoặc phân lại theo mode.
- 4b. Hold đến hạn: xử lý EXPIRE nguyên tử theo quy tắc freeze, rồi tính lại; không chỉ bỏ qua bằng view.

**Hậu điều kiện thành công:** On_hand không đổi; reserved tăng đúng lượng; hold gắn đúng SO line và bucket.

**Bảo đảm khi không thành công:** Không reserved vượt tồn; lỗi toàn giao dịch không để lại hold lẻ.

**Ánh xạ database:** R: sales_order/line, lot, location, stocktake; R/W: stock_balance, stock_reservation; W: reservation_event, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Tồn10, hai phiên cần7: chỉ một phiên giữ đủ7.
- Đơn cần50 lấy L1=30,L2=20 có hai reservation đúng nguồn.

### UC12 — Nhả hàng đã giữ

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Giải phóng phần chưa tiêu thụ của một hold. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Nhả hàng đã giữ” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Hold còn active quantity; người dùng có quyền với đơn; ô không freeze trừ UC18 ngoại lệ có kiểm soát. |
| Dữ liệu vào | reservation_id, lượng nhả, lý do. |

**Luồng chính**

1. Nhân viên chọn hold và lượng cần nhả.
2. Hệ thống khóa/kiểm active quantity và tình trạng đơn/ô.
3. Hệ thống tăng released_qty, tạo RELEASE event, giảm reserved của bucket và audit cùng transaction.
4. Hệ thống hiển thị lượng còn giữ và khả dụng mới.

**Luồng thay thế/ngoại lệ**

- 2a. Lượng đã consumed hoặc lớn hơn phần còn: từ chối.
- 2b. Ô đang kiểm kê: luồng thông thường bị chặn; manager dùng xử lý hold của UC18 khi cần.
- 4a. Lô đang block: nhả hold thành công nhưng available vẫn bằng0.

**Hậu điều kiện thành công:** On_hand không đổi, reserved giảm tương ứng.

**Bảo đảm khi không thành công:** Không nhả cùng một phần lượng hai lần khi cạnh tranh.

**Ánh xạ database:** R/W: stock_reservation, stock_balance; W: reservation_event, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Hold30 consumed20 chỉ nhả tối đa10.
- Nhả hold trên lô block không làm hàng được xuất.

### UC13 — Lập phiếu xuất hàng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Chuẩn bị đúng lô/lượng sẽ giao từ các hold hiện hữu. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu xuất hàng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | SO CONFIRMED, có hold hợp lệ; hoàn tất checklist nếu dùng P1 picking. |
| Dữ liệu vào | SO, reservation, lượng giao từng phần, lô/vị trí. |

**Luồng chính**

1. Nhân viên mở đơn và các reservation.
2. Hệ thống hiển thị lượng còn giữ, lô/vị trí và cảnh báo.
3. Nhân viên xác nhận lượng thực giao từ từng hold; hệ thống tạo các dòng SHIPMENT theo lot/bucket.
4. Nhân viên lưu DRAFT để UC08 và UC09 xử lý sau.

**Luồng thay thế/ngoại lệ**

- 3a. Giao một phần: lượng nhỏ hơn hold; phần còn giữ tiếp tục tồn tại.
- 2a. Hold hết hạn/lô block: yêu cầu xử lý hold trước, không cho dùng nháp để bỏ qua quy tắc.
- 3b. Quét sai lô: báo đúng lô cần lấy; người dùng kiểm lại.

**Hậu điều kiện thành công:** Có phiếu xuất DRAFT gắn dòng SO và nguồn SKU/lot/ô; hold cụ thể được khóa và phân lượng tiêu thụ lúc ghi sổ; tồn chưa giảm.

**Bảo đảm khi không thành công:** Không có CONSUME event chỉ vì quét/lưu nháp.

**Ánh xạ database:** R: sales_order/line, stock_reservation, lot, stock_balance; W: inventory_document, inventory_document_line, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Giữ30, lập phiếu20 chưa thay đổi tồn/hold.
- Shipment POSTED sau đó phải consumed20, còn10.

### UC14 — Lập phiếu chuyển vị trí

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Chuyển lượng hàng chưa giữ tới vị trí khác, bảo toàn tổng. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu chuyển vị trí” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Có hàng đủ tại nguồn, vị trí nguồn/đích hợp lệ. |
| Dữ liệu vào | SKU, lot, condition, lượng, vị trí nguồn/đích, lý do. |

**Luồng chính**

1. Nhân viên chọn hàng nguồn và nơi nhận.
2. Hệ thống hiển thị lượng chưa giữ và kiểm nguồn/đích.
3. Nhân viên nhập lượng, xem tác động hai vị trí.
4. Hệ thống lưu TRANSFER DRAFT; duyệt/ghi sổ bằng UC08/09.

**Luồng thay thế/ngoại lệ**

- 2a. Cùng một bucket: từ chối.
- 3a. Lượng thuộc hold: v1 từ chối phần đó; phải nhả/cấp lại bằng use case phù hợp.
- 2b. Liên kho có thời gian vận chuyển: lập hai chặng qua TRANSIT; chưa có quản lý chuyến vận tải đầy đủ.

**Hậu điều kiện thành công:** Có phiếu chuyển nháp; khi POSTED, tổng lượng cùng lot trong doanh nghiệp được bảo toàn.

**Bảo đảm khi không thành công:** Không đổi lot hoặc chất lượng ngầm khi chuyển.

**Ánh xạ database:** R: stock_balance, stock_reservation, location, lot; W: inventory_document, inventory_document_line, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Chuyển10 làm nguồn-10/đích+10 khi ghi sổ.
- Vị trí đang kiểm kê chặn posting ở cả hai đầu.

### UC15 — Lập phiếu đổi tình trạng hàng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Ghi việc chuyển GOOD/QUARANTINE/DAMAGED có căn cứ. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu đổi tình trạng hàng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Hàng tồn tại, người dùng có quyền; hold được xử lý trước khi giảm phần GOOD đã giữ. |
| Dữ liệu vào | SKU/lot, nguồn condition, đích condition, lượng, lý do. |

**Luồng chính**

1. Nhân viên chọn lượng hàng cần đổi tình trạng.
2. Hệ thống hiển thị trạng thái nguồn, hold liên quan và tác động available.
3. Nhân viên chọn trạng thái đích, nhập lý do, lưu RECLASSIFY DRAFT.
4. Quản lý xem căn cứ ở UC08 và thực ghi bằng UC09.

**Luồng thay thế/ngoại lệ**

- 2a. Hàng đang giữ: cần xử lý hold trước; không làm reserved lớn hơn on_hand GOOD.
- 3a. Từ QUARANTINE về GOOD: manager phải xác nhận căn cứ; lot bị block vẫn không eligible.

**Hậu điều kiện thành công:** Tồn vật lý không đổi khi ghi sổ; lượng ở các condition thay đổi đúng.

**Bảo đảm khi không thành công:** Không sửa condition trực tiếp trên balance để xóa dấu vết.

**Ánh xạ database:** R: lot, stock_balance, stock_reservation; W: inventory_document, inventory_document_line, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- GOOD10 đổi QUARANTINE3: tổng10, khả dụng giảm3 nếu chưa giữ.
- Reclassify không tự gỡ recall_status.

### UC16 — Mở phiên kiểm kê

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Chụp tồn kỳ vọng và tạm dừng biến động tại một ô để đếm. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Mở phiên kiểm kê” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Vị trí lá đang hoạt động, chưa có phiên COUNTING/REVIEW. |
| Dữ liệu vào | Vị trí kiểm kê và người khởi tạo. |

**Luồng chính**

1. Quản lý chọn vị trí và xem phạm vi sẽ bị tạm dừng.
2. Quản lý xác nhận mở phiên.
3. Hệ thống khóa ngắn warehouse/location, kiểm phiên active, chụp expected_qty từng SKU/lot/condition.
4. Hệ thống chuyển COUNTING, ghi frozen_at rồi commit; nhân viên bắt đầu đếm.

**Luồng thay thế/ngoại lệ**

- 3a. Đã có phiên khác: từ chối; mở phiên đang có để xem.
- 3b. Đang có giao dịch ghi trước đó: chờ khóa rồi chụp trạng thái sau commit của giao dịch đó.
- 4a. Hủy phiên: manager đặt CANCELLED, nhả freeze; không adjustment.

**Hậu điều kiện thành công:** Có snapshot và freeze nghiệp vụ; không giữ transaction DB suốt thời gian đếm.

**Bảo đảm khi không thành công:** Không có hai snapshot active cùng location.

**Ánh xạ database:** R: location, stock_balance; W: stocktake, stocktake_line, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Nhập/xuất/reserve ở ô bị freeze đều bị chặn.
- Hủy count không tạo movement.

### UC17 — Ghi số đếm kiểm kê

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Lưu số quan sát độc lập với số trên hệ thống. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Ghi số đếm kiểm kê” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Phiên COUNTING để đếm lần đầu, hoặc REVIEW khi manager cho phép đếm lại; người ghi có quyền tương ứng. |
| Dữ liệu vào | SKU, lot, condition, lượng đếm, ghi chú. |

**Luồng chính**

1. Nhân viên mở danh sách cần đếm; hệ thống ẩn expected_qty trong màn đếm.
2. Nhân viên quét/chọn hàng và nhập số đếm theo base UOM.
3. Hệ thống kiểm lượng, lưu counted_qty, counted_by và audit.
4. Sau khi đủ dòng, người đếm gửi kết quả để phiên chuyển REVIEW.

**Luồng thay thế/ngoại lệ**

- 2a. Không thấy hàng trong danh sách: nhập0 cho dòng đó, không bỏ qua.
- 2b. Tìm thấy hàng ngoài snapshot: xác minh SKU/lot, thêm dòng expected0 rồi nhập lượng.
- 3a. Cần đếm lại: giữ counted ban đầu, lưu recount vào recounted_qty; audit người và thời điểm.
- 4a. Còn dòng chưa đếm: chưa cho gửi review.

**Hậu điều kiện thành công:** Số quan sát được lưu; tồn hệ thống chưa đổi.

**Bảo đảm khi không thành công:** Không dùng chênh lệch để sửa balance trước UC18.

**Ánh xạ database:** R/W: stocktake, stocktake_line; R: product, lot; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Người đếm không thấy expected trên màn này.
- Count0 khác NULL chưa đếm.

### UC18 — Duyệt và chốt kiểm kê

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Chấp nhận chênh lệch có căn cứ và kết thúc freeze. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Duyệt và chốt kiểm kê” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Phiên REVIEW; tất cả dòng đã đếm; manager có quyền chốt. |
| Dữ liệu vào | Kết quả count/recount, lý do chênh lệch, quyết định duyệt. |

**Luồng chính**

1. Quản lý xem expected, số đếm cuối và chênh lệch từng dòng.
2. Hệ thống tính delta từ COALESCE(recounted_qty,counted_qty), kiểm snapshot và reserved.
3. Quản lý xác nhận chốt.
4. Nếu có chênh lệch, hệ thống tạo ADJUSTMENT được manager phê duyệt trong thao tác này và ghi qua SF02 sau SF01; gắn adjustment_document_id.
5. Trong cùng transaction, hệ thống đặt phiên POSTED, closed_at, approved_by và nhả freeze.

**Luồng thay thế/ngoại lệ**

- 1a. Chưa tin số đếm: yêu cầu đếm lại; giữ REVIEW và freeze, cho UC17 ghi recount có quyền.
- 2a. Số thật nhỏ hơn reserved: giữ REVIEW; manager chọn hold thiếu cần nhả trong giao dịch đặc biệt của phiên, có audit; trở lại bước2.
- 4a. Delta tất cả bằng0: không tạo phiếu/movement0, chỉ chốt phiên.
- 4b. Lỗi ghi sổ: rollback cả điều chỉnh và đóng phiên; phiên vẫn REVIEW.

**Hậu điều kiện thành công:** Balance khớp số đã duyệt, adjustment truy vết được nếu có; phiên kết thúc và ô dùng lại được.

**Bảo đảm khi không thành công:** Không thể đã nhả freeze/POSTED mà adjustment chưa ghi thành công.

**Ánh xạ database:** R/W: stocktake, stocktake_line, stock_balance, stock_reservation; W khi cần: inventory_document/line, stock_movement, reservation_event, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Expected10,count9 tạo adjustment-1.
- Delta0 không tạo movement có qty0.

### UC19 — Lập phiếu nhận hàng khách trả

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Nhận lại hàng vật lý từ khách với nguồn gốc rõ. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu nhận hàng khách trả” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Shipment gốc POSTED, còn lượng được trả; hàng xác định được lot. |
| Dữ liệu vào | Phiếu/dòng xuất gốc, lượng trả, lot, vị trí nhận, lý do. |

**Luồng chính**

1. Nhân viên tìm dòng shipment gốc.
2. Hệ thống hiển thị lượng đã giao, đã trả hiệu lực và còn được trả.
3. Nhân viên nhập lượng thực nhận và nơi nhận; mặc định QUARANTINE, giữ lot gốc.
4. Hệ thống tạo CUSTOMER_RETURN DRAFT với original_line_id; đưa qua UC08/09.

**Luồng thay thế/ngoại lệ**

- 2a. Lượng vượt phần chưa trả: từ chối.
- 3a. Không xác định nguồn/lot: giữ ngoài luồng nhận có căn cứ, yêu cầu manager xử lý; không tự gán một lot bất kỳ.
- 4a. Lô gốc đang block: vẫn có thể nhận về cách ly, không trở thành available.

**Hậu điều kiện thành công:** Phiếu trả nháp có nguồn; khi POSTED tăng vật lý/quarantine, không mở lại SO tự động.

**Bảo đảm khi không thành công:** Không trả vượt nguồn khi hai phiên cùng lập/ghi phiếu.

**Ánh xạ database:** R: inventory_document/line, lot; W: inventory_document/line, audit_event; posting qua UC09.

**Tiêu chí nghiệm thu đại diện:**

- Đã ship20, tổng trả tối đa20 kể cả nhiều phiếu.
- Trả2 quarantine không tăng available.

### UC20 — Lập phiếu trả nhà cung cấp

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Ghi lượng hàng thực trả về nhà cung cấp. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu trả nhà cung cấp” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Receipt gốc POSTED; còn hàng tại nguồn và quyền trả phù hợp. |
| Dữ liệu vào | Dòng nhận gốc, SKU/lot, lượng, ô nguồn, lý do. |

**Luồng chính**

1. Nhân viên tìm lần nhận gốc và lot còn hàng.
2. Hệ thống tính lượng đã trả hiệu lực, lượng đang có và lượng chưa bị giữ.
3. Nhân viên chọn lượng và lý do; hệ thống lưu SUPPLIER_RETURN DRAFT.
4. Quản lý duyệt và ghi qua UC08/09.

**Luồng thay thế/ngoại lệ**

- 2a. Đã bán/chuyển đi nên không đủ tại nguồn: chỉ lập theo lượng hợp lệ hoặc xử lý nguồn trước.
- 2b. Hàng đang giữ: không lấy phần hold.
- 3a. Trả lô block/hỏng: cho luồng trả có kiểm soát, không dùng quy tắc eligibility của shipment bán hàng để cấm mọi trả.

**Hậu điều kiện thành công:** Khi POSTED, vật lý giảm đúng; PO cũ không tự mở lại.

**Bảo đảm khi không thành công:** Không đảo toàn receipt khi chỉ muốn trả một phần hàng.

**Ánh xạ database:** R: inventory_document/line, stock_balance, stock_reservation, lot; W: inventory_document/line, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Nhận100 còn30 có thể trả30, không thể trả100.
- Trả NCC có original_line_id.

### UC21 — Đảo chứng từ đã ghi sổ

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Sửa tác động hồ sơ bằng chứng từ đối ứng có thể thực hiện ở hiện tại. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Đảo chứng từ đã ghi sổ” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Phiếu gốc POSTED, chưa đảo, không có phụ thuộc chưa xử lý; đủ điều kiện nguồn hiện tại. |
| Dữ liệu vào | Phiếu gốc, lý do, xác nhận tác động đối ứng. |

**Luồng chính**

1. Quản lý mở phiếu gốc và yêu cầu đảo.
2. Hệ thống dựng các dòng đảo nguồn/đích, hiển thị phụ thuộc và kiểm tính khả thi.
3. Quản lý xác nhận lý do và tác động.
4. Hệ thống tạo REVERSAL với tham chiếu gốc, phê duyệt theo quyền manager và ghi SF01/SF02 trong giao dịch.
5. Hệ thống hiển thị phiếu đảo; phiếu gốc vẫn POSTED và đọc được.

**Luồng thay thế/ngoại lệ**

- 2a. Nhập100 đã dùng70, chỉ còn30: không đủ để đảo100; từ chối.
- 2b. Đã có reversal hoặc downstream chưa xử lý: từ chối và nêu chứng từ liên quan.
- 4a. Đảo shipment hợp lệ: không khôi phục reservation cũ; nhu cầu tính lại và cần reserve mới.

**Hậu điều kiện thành công:** Có movement đối ứng ở thời điểm mới; lịch sử gốc không bị sửa/xóa.

**Bảo đảm khi không thành công:** Không đảo được một phần phiếu hoặc đảo hai lần trong v1.

**Ánh xạ database:** R: original documents, movements, downstream refs; W: inventory_document/line, stock_movement, stock_balance, audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Reversal_of_id chỉ có một phiếu đảo cho mỗi phiếu gốc.
- Replay trước đảo vẫn thấy tác động cũ.

### UC22 — Tra cứu tồn kho và báo cáo

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Biết hàng còn ở đâu, đang giữ bao nhiêu và lượng có thể cấp phát. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Tra cứu tồn kho và báo cáo” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Đăng nhập có quyền xem; bộ lọc hợp lệ. |
| Dữ liệu vào | SKU/barcode, kho, ô, lot, tình trạng, bộ lọc ngày. |

**Luồng chính**

1. Người dùng nhập bộ lọc và chọn báo cáo/tồn chi tiết.
2. Hệ thống đọc view số dư/khả dụng, phân trang và trả thời điểm dữ liệu.
3. Người dùng mở dòng để xem các bucket và chứng từ giải thích.
4. Nếu cần xuất CSV, hệ thống xuất đúng bộ lọc và các cột được phép.

**Luồng thay thế/ngoại lệ**

- 2a. Không có kết quả: hiển thị trạng thái rỗng và bộ lọc đang dùng.
- 2b. Dữ liệu thay đổi: refresh hiển thị as_of mới; không coi số cũ là cam kết giữ hàng.
- 4a. Operator xem báo cáo: loại cột giá vốn/giá mua theo policy đề xuất.

**Hậu điều kiện thành công:** Người dùng có số liệu và nguồn drill-down; không ghi tồn.

**Bảo đảm khi không thành công:** Không cộng các đơn vị khác nhau thành một tổng vô nghĩa.

**Ánh xạ database:** R: stock_balance, stock_reservation, product, lot, location, warehouse, stock_movement, documents; W: audit_event nếu xuất cần audit.

**Tiêu chí nghiệm thu đại diện:**

- 100 GOOD giữ30 +20 quarantine cho vật lý120, available70.
- CSV khớp filter và không lộ cột giá vốn cho operator.

### UC23 — Truy vết lô hàng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Xác định nguồn, nơi còn hàng và các khách/đơn đã bị ảnh hưởng. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Truy vết lô hàng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Có SKU và mã lô xác định; quyền xem dữ liệu liên quan. |
| Dữ liệu vào | SKU + mã lô nhà sản xuất hoặc lot nội bộ. |

**Luồng chính**

1. Người dùng nhập mã lô và phạm vi.
2. Hệ thống phân giải toàn bộ lot nội bộ liên quan trong đúng SKU.
3. Hệ thống tổng hợp nhận/chuyển/xuất/trả/đảo/kiểm kê, tồn theo ô và hold liên quan.
4. Người dùng mở phiếu hoặc danh sách khách từng nhận/khách còn lượng ròng.

**Luồng thay thế/ngoại lệ**

- 2a. Mã lô trùng giữa SKU: yêu cầu chọn SKU, không gộp bừa.
- 3a. Có phiếu trả/đảo: tính lượng hiệu lực, phân biệt từng nhận và ròng chưa trả.

**Hậu điều kiện thành công:** Có báo cáo truy vết đủ lot con, không đổi block hay tồn.

**Bảo đảm khi không thành công:** Không gửi thông báo cho khách/NCC tự động trong v1.

**Ánh xạ database:** R: lot, stock_movement, inventory_document/line, partner, stock_balance, stock_reservation, orders.

**Tiêu chí nghiệm thu đại diện:**

- Mã NCC giống nhau qua hai lần nhận được tìm đủ.
- Transfer nội bộ không bị đếm thành bán cho khách.

### UC24 — Khóa hoặc mở khóa lô

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Thay đổi quyền cấp phát lô khi có sự cố/chứng cứ xử lý. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Khóa hoặc mở khóa lô” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Lô được xác định rõ; manager có lý do và quyền. |
| Dữ liệu vào | Tập lot nội bộ, hành động BLOCK/UNBLOCK, lý do. |

**Luồng chính**

1. Quản lý chọn lot từ tra cứu/chi tiết và xem hàng, đơn bị ảnh hưởng.
2. Hệ thống hiển thị phạm vi cụ thể, đặc biệt khi cùng mã NCC có nhiều lot con.
3. Quản lý xác nhận; hệ thống khóa row lot, đổi recall_status/block_reason và audit nguyên tử.
4. Hệ thống refresh available và hiển thị các hold cần xử lý tiếp bằng UC12/11.

**Luồng thay thế/ngoại lệ**

- 3a. Shipment commit trước block: hàng nằm trong báo cáo đã xuất; không hồi tố xóa xuất.
- 3b. Block commit trước shipment: shipment kiểm lại và bị chặn.
- 3c. Mở khóa: cần căn cứ mới; expiry/condition vẫn có thể làm available0.

**Hậu điều kiện thành công:** Chỉ thay trạng thái cấp phát; on_hand và các hold chưa được xử lý vẫn giữ nguyên.

**Bảo đảm khi không thành công:** Không âm thầm nhả/xóa hold hoặc sửa lịch sử shipment.

**Ánh xạ database:** R/W: lot; R: stock_balance, stock_reservation; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Block lô còn77 không làm vật lý giảm77.
- Mở khóa lô hết hạn vẫn không cấp phát được.

### UC25 — Xem tồn tại mốc ghi sổ

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Tái dựng lượng đã ghi nhận tại thời điểm T. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Xem tồn tại mốc ghi sổ” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Có lịch sử movement, bao gồm OPENING. |
| Dữ liệu vào | Mốc T có timezone, SKU/kho/vị trí tùy chọn. |

**Luồng chính**

1. Quản lý chọn thời điểm và phạm vi.
2. Hệ thống tổng hợp hai chân movement có recorded_at<=T, gồm bút toán đảo khi đến mốc của nó.
3. Hệ thống hiển thị lượng theo bucket và cho mở các biến động cấu thành.

**Luồng thay thế/ngoại lệ**

- 2a. Mốc trước tồn đầu: trả0/không có biến động, không lấy balance hiện tại thế vào.
- 3a. Người dùng hỏi available lịch sử: giải thích v1 chỉ tái dựng lượng vật lý theo mốc ghi sổ.

**Hậu điều kiện thành công:** Báo cáo lịch sử lượng, không chỉnh lại ngày hoặc lượng hiện tại.

**Bảo đảm khi không thành công:** Không tuyên bố đây là timestamp commit chính xác hoặc lịch sử mọi thuộc tính master.

**Ánh xạ database:** R: stock_movement, product, location, lot.

**Tiêu chí nghiệm thu đại diện:**

- Trước reversal còn tác động gốc; sau reversal có cả hai.
- Tất cả dòng trong một posting dùng cùng mốc ghi sổ.

### UC26 — Thiết kế sơ đồ và lối đi kho

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Mô tả các điểm tiếp cận hàng và đường đi hợp lệ. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Thiết kế sơ đồ và lối đi kho” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Kho/vị trí đã tồn tại. |
| Dữ liệu vào | Node, tọa độ, location liên kết, cạnh có hướng, chiều dài, trạng thái cạnh. |

**Luồng chính**

1. Quản lý mở kho và đặt các node lối đi/điểm lấy.
2. Hệ thống kiểm node-location cùng kho và mã duy nhất.
3. Quản lý nối các cạnh, nhập mét, thiết lập một/hai chiều.
4. Hệ thống lưu graph; các kế hoạch cũ được nhận diện stale bằng input_hash khi sử dụng.

**Luồng thay thế/ngoại lệ**

- 3a. Đóng lối đi: disable cạnh; không xóa lịch sử path_snapshot của pick_run.
- 3b. Cạnh chiều dài<=0 hoặc nối chính nó: từ chối.

**Hậu điều kiện thành công:** Có graph có thể dùng tính đường; đồ án mô phỏng không tự biết layout kho thật.

**Bảo đảm khi không thành công:** Không âm thầm tính lại rồi sửa số đo lịch sử pick_run.

**Ánh xạ database:** R/W: map_node, map_edge; R: warehouse, location, pick_run; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Đường hai chiều có hai cạnh.
- Node của kho A không gắn location kho B.

### UC27 — Lập kế hoạch lấy hàng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Tạo thứ tự ghé ô cho tập hàng đã được giữ. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập kế hoạch lấy hàng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Đơn có reservation hợp lệ; graph và điểm tiếp cận đã có. |
| Dữ liệu vào | SO, các hold, điểm bắt đầu/kết thúc, graph hiện tại. |

**Luồng chính**

1. Nhân viên chọn Lập kế hoạch trên đơn đã giữ hàng.
2. Hệ thống chụp tập hold và graph; thực hiện SF04 tính các đường hợp lệ, baseline cùng tập điểm và phương án đề xuất.
3. Hệ thống giữ baseline nếu heuristic kém hơn, lưu pick_run/pick_stop và input_hash.
4. Nhân viên xem route, lượng từng stop và lý do chọn lô từ allocation.

**Luồng thay thế/ngoại lệ**

- 2a. Chưa giữ đủ: quay về UC11 như một thao tác riêng; không vẽ route cho hàng chưa được giữ.
- 2b. Có điểm không tới được: báo cụ thể, không tạo plan hợp lệ giả.
- 3a. Hold/graph vừa đổi trước khi dùng plan: đánh dấu stale trên giao diện và yêu cầu lập lại; không thêm enum STALE vào pick_run.

**Hậu điều kiện thành công:** Có kế hoạch và snapshot có thể giải thích; không tăng hold hoặc trừ tồn.

**Bảo đảm khi không thành công:** Không đổi lô để giảm đường đi mà phá FEFO/điều kiện giữ.

**Ánh xạ database:** R: stock_reservation, stock_balance, lot, sales_order, map_node, map_edge; W: pick_run, pick_stop.

**Tiêu chí nghiệm thu đại diện:**

- So baseline trên đúng cùng tập hold/điểm.
- Chặn cạnh làm tính lại hoặc báo không có đường.

### UC28 — Xác nhận lấy hàng theo kế hoạch

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Đánh dấu lượng đã lấy đúng SKU/lô tại các điểm. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Xác nhận lấy hàng theo kế hoạch” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Pick_run còn hợp lệ, PLANNED hoặc IN_PROGRESS; hold chưa hết hạn/block. |
| Dữ liệu vào | pick_run, stop, mã hàng/lô, lượng lấy. |

**Luồng chính**

1. Nhân viên mở plan và bắt đầu làm, hệ thống đặt IN_PROGRESS.
2. Tại từng stop, nhân viên quét/chọn đúng SKU/lô và xác nhận lượng.
3. Hệ thống kiểm stop/hold, cập nhật picked_qty và picked_at.
4. Khi đạt các stop, hệ thống đặt DONE và cho lập phiếu xuất ở UC13.

**Luồng thay thế/ngoại lệ**

- 2a. Sai lô/vị trí: báo lỗi, không tăng picked_qty.
- 2b. Lấy thiếu: lưu lượng thực lấy, plan vẫn chưa DONE; nhân viên xử lý thiếu trước khi hoàn tất hoặc hủy/lập lại.
- 3a. Plan stale: dừng tiếp tục, yêu cầu UC27 lập lại từ dữ liệu mới.

**Hậu điều kiện thành công:** Checklist phản ánh xác nhận lấy; stock_movement chưa được tạo.

**Bảo đảm khi không thành công:** Quét hai lần không tự ghi kho hai lần; chỉnh checklist phải có audit.

**Ánh xạ database:** R/W: pick_run, pick_stop; R: stock_reservation, lot, map; W: audit_event.

**Tiêu chí nghiệm thu đại diện:**

- Pick20 chưa giảm on_hand; UC09 mới giảm.
- Không DONE khi stop bắt buộc còn thiếu lượng.

### UC29 — Hỏi trợ lý kho

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Nhận giải thích tiếng Việt dựa trên dữ liệu kho được phép xem. |
| Actor chính | Nhân viên kho, Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Hỏi trợ lý kho” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Đăng nhập; dịch vụ suy luận có thể đáp ứng; tool được whitelist theo quyền. |
| Dữ liệu vào | Câu hỏi, ngữ cảnh SKU/đơn/kho tùy chọn. |

**Luồng chính**

1. Người dùng gửi câu hỏi.
2. Hệ thống xác định ý định, dữ kiện còn thiếu và tập tool được phép.
3. Dịch vụ LLM hỗ trợ diễn giải/gọi tool; ứng dụng kiểm tham số, tự chạy tool nghiệp vụ và lưu evidence.
4. Hệ thống trình bày câu trả lời cùng ID, đơn vị và as_of; kiểm các con số theo tool.
5. Tại điểm mở rộng EP-AI-1 sau câu trả lời, nếu manager yêu cầu đề xuất mua thì UC31 có thể diễn ra; nếu không, kết thúc.

**Luồng thay thế/ngoại lệ**

- 2a. SKU/tên mơ hồ: hỏi chọn, quay về bước2 sau trả lời.
- 3a. Timeout hoặc tool lỗi: hiện trạng thái chưa hoàn tất, cho dùng màn nghiệp vụ thường; không bịa câu trả lời.
- 3b. Nội dung note yêu cầu bỏ quy tắc: xử lý như dữ liệu, không thay quyền/tool.
- 4a. Operator hỏi giá vốn: từ chối phần ngoài quyền, không gọi tool để lấy rồi mới che ở UI.

**Hậu điều kiện thành công:** Có câu trả lời có evidence hoặc lý do không trả lời được; không tự thay tồn.

**Bảo đảm khi không thành công:** Không rò dữ liệu ngoài quyền; không SQL/shell tùy ý; không giao dịch kho mở trong lúc chờ LLM.

**Ánh xạ database:** W: ai_run, ai_tool_call; R: dữ liệu được các tool có quyền cho phép; có thể W: ai_proposal qua UC31.

**Tiêu chí nghiệm thu đại diện:**

- Câu hỏi tồn có số khớp tool và as_of.
- AI timeout không treo Tkinter hoặc ảnh hưởng phiếu kho.

### UC30 — Xem đề xuất bổ sung hàng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Tính lượng cần mua bằng policy minh bạch và điều kiện NCC. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Xem đề xuất bổ sung hàng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Có reorder_policy, nguồn cung; biết phạm vi dữ liệu và đơn đang mở. |
| Dữ liệu vào | Kho/SKU, cutoff, policy và lead time. |

**Luồng chính**

1. Quản lý chọn phạm vi phân tích.
2. Hệ thống đọc một snapshot nhất quán của eligible on_hand, PO còn nhận và nhu cầu SO còn mở.
3. Hệ thống tính inventory_position, min/target, MOQ/bội số; tách hàng inbound quá hạn.
4. Hệ thống lưu analysis_run/replenishment_suggestion và hiển thị bằng chứng, giả định.

**Luồng thay thế/ngoại lệ**

- 2a. Thiếu nguồn cung/lead time: đánh dấu dữ kiện thiếu, không giả định một NCC bất kỳ.
- 3a. Không thiếu hàng: trả không cần mua, không tạo suggestion_qty0 bị CHECK từ chối.
- 4a. Người dùng muốn đặt mua: thực hiện UC06 riêng, tham chiếu đề xuất; chưa tự gửi PO cho NCC.

**Hậu điều kiện thành công:** Có kết quả định lượng có thể kiểm lại, chưa tăng tồn/chưa đặt hàng tự động.

**Bảo đảm khi không thành công:** Không trừ reserved hai lần khi open demand đã bao gồm phần giữ.

**Ánh xạ database:** R: reorder_policy, supplier_product, stock_balance, orders/lines, receipts; W: analysis_run, replenishment_suggestion.

**Tiêu chí nghiệm thu đại diện:**

- Eligible100 + inbound20 - demand50 cho position70, không trừ hold30 thêm.
- Đề xuất tuân MOQ và bội số đặt.

### UC31 — Tạo đề xuất mua trong hội thoại

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Lưu một đề xuất có cấu trúc để quản lý xem trước khi tạo PO. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Tạo đề xuất mua trong hội thoại” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Đang tại EP-AI-1 của UC29; manager yêu cầu mua; SKU và nguồn cung đã xác định. |
| Dữ liệu vào | Phạm vi mua, lượng dự kiến, NCC, lý do và evidence. |

**Luồng chính**

1. Quản lý yêu cầu đề xuất mua sau phần giải thích.
2. Hệ thống thực hiện SF05 bằng tool compute_replenishment/kiểm policy và dữ liệu được phép.
3. Hệ thống dựng payload theo schema, kiểm SKU/NCC/UOM và lưu ai_proposal PROPOSED với input_hash.
4. Hệ thống hiển thị đề xuất, số tiền/đơn vị, căn cứ và hành động sang UC32.

**Luồng thay thế/ngoại lệ**

- 2a. Thiếu dữ kiện: hỏi rõ trong hội thoại; không lưu đề xuất giả hoàn chỉnh.
- 3a. Model trả payload sai schema: sửa qua luồng kiểm có giới hạn hoặc báo thất bại.
- 4a. Không muốn áp dụng: giữ PROPOSED hoặc chuyển REJECTED khi manager từ chối.

**Hậu điều kiện thành công:** Có proposal; chưa có PO hoặc movement.

**Bảo đảm khi không thành công:** Không đưa văn bản tự do vào DB như lệnh thực thi.

**Ánh xạ database:** R: tool data, ai_run, ai_tool_call; W: ai_proposal; SF05 có thể dùng analysis_run, replenishment_suggestion.

**Tiêu chí nghiệm thu đại diện:**

- UC29 vẫn hoàn tất được nếu không có UC31.
- Proposal chứa được các ID và bằng chứng cần kiểm lại.

### UC32 — Duyệt đề xuất AI để tạo PO nháp

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Chuyển proposal đã xem thành đơn mua nháp có thể quản lý. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P1 |
| Kích hoạt | Người dùng yêu cầu thao tác “Duyệt đề xuất AI để tạo PO nháp” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Proposal PROPOSED và nội dung được manager xem; đủ quyền tạo PO. |
| Dữ liệu vào | proposal_id, quyết định duyệt/từ chối, input_hash hiện tại. |

**Luồng chính**

1. Quản lý mở đề xuất và xem SKU, NCC, lượng, giá, căn cứ.
2. Quản lý chọn Tạo PO nháp.
3. Hệ thống khóa proposal, kiểm quyền, hash và tính lại điều kiện bằng SF05 trên dữ liệu hiện tại.
4. Hệ thống tạo PO/lines DRAFT rồi đặt proposal APPLIED và result_purchase_order_id trong cùng transaction.
5. Hệ thống mở PO mới; xác nhận đơn diễn ra riêng trong UC06.

**Luồng thay thế/ngoại lệ**

- 1a. Quản lý từ chối: lưu REJECTED, kết thúc không tạo PO.
- 3a. Dữ liệu thay đổi làm đề xuất cũ không còn đúng: đặt STALE, yêu cầu tạo/xem đề xuất mới; không duyệt mù số mới.
- 3b. Đã APPLIED: trả PO hiện có, không tạo thêm.
- 4a. Lỗi tạo PO: rollback; không để APPLIED mà không có result.

**Hậu điều kiện thành công:** Chính xác một PO DRAFT liên kết proposal; chưa gửi NCC, chưa tăng tồn.

**Bảo đảm khi không thành công:** Không áp dụng proposal cũ hoặc tạo trùng khi nhấp2 lần.

**Ánh xạ database:** R/W: ai_proposal; W: purchase_order, purchase_order_line, audit_event; R: policy/master/snapshot liên quan.

**Tiêu chí nghiệm thu đại diện:**

- Nhấp hai lần trả cùng PO.
- APPLIED chỉ xảy ra cùng commit có result_purchase_order_id.

### UC33 — Xem nhật ký và đối soát kho

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Giải thích biến động và phát hiện số dư/lượng giữ lệch nguồn. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Xem nhật ký và đối soát kho” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Có quyền MANAGER; truy vấn theo phạm vi được chọn. |
| Dữ liệu vào | Thời gian, người thực hiện, loại nghiệp vụ, SKU/kho. |

**Luồng chính**

1. Quản lý chọn lịch sử hoặc chạy đối soát.
2. Hệ thống tổng hợp ledger với balance, reservation snapshot với events và dòng phiếu đã post.
3. Hệ thống hiển thị sai lệch và ID liên quan; cho mở phiếu/audit.
4. Quản lý lập công việc điều tra nếu có lệch; không tự rebuild balance từ nút xem.

**Luồng thay thế/ngoại lệ**

- 2a. Không lệch: báo không phát hiện sai lệch trong phạm vi/as_of.
- 2b. Thiếu movement cho phiếu POSTED: báo lỗi toàn vẹn dù tổng balance tình cờ vẫn khớp.

**Hậu điều kiện thành công:** Có kết quả kiểm soát và bằng chứng để điều tra.

**Bảo đảm khi không thành công:** Không sửa dữ liệu nguồn trong use case chỉ đọc này.

**Ánh xạ database:** R: audit_event, stock_movement, stock_balance, stock_reservation, reservation_event, inventory_document/line.

**Tiêu chí nghiệm thu đại diện:**

- Cố ý lệch balance-1 được báo.
- Không thể suy ra mọi invariant đúng chỉ từ một tổng SUM.

### UC34 — Mô phỏng kịch bản nhu cầu và cung ứng

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | So sánh phương án khi nhu cầu/lead time thay đổi trên dữ liệu snapshot. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P2 |
| Kích hoạt | Người dùng yêu cầu thao tác “Mô phỏng kịch bản nhu cầu và cung ứng” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | P0/P1 ổn; đã có baseline phân tích hợp lệ. |
| Dữ liệu vào | Hệ số nhu cầu, số ngày trễ, SKU/kho, horizon. |

**Luồng chính**

1. Quản lý chọn snapshot và nhập giả định, ví dụ nhu cầu+30%, giao trễ3 ngày.
2. Hệ thống giữ cùng dữ liệu gốc, chạy baseline và scenario bằng thuật toán được ghi phiên bản.
3. Hệ thống hiển thị chênh lệch thiếu hàng/đề xuất và lưu analysis_run có parameters.

**Luồng thay thế/ngoại lệ**

- 2a. Thiếu dữ liệu hoặc mẫu không đủ: giới hạn kết luận, không dựng độ chính xác dự báo giả.
- 3a. Muốn hành động theo kết quả: tạo đề xuất/PO qua use case riêng sau khi kiểm dữ liệu hiện tại.

**Hậu điều kiện thành công:** Có so sánh được gắn rõ giả định; dữ liệu vận hành không bị sửa.

**Bảo đảm khi không thành công:** Không coi kết quả scenario là dữ kiện chắc chắn hoặc tự đặt hàng.

**Ánh xạ database:** R: snapshots và dữ liệu phân tích; W: analysis_run; có thể W: replenishment_suggestion.

**Tiêu chí nghiệm thu đại diện:**

- Hai phương án dùng cùng cutoff gốc.
- Tăng nhu cầu trong what-if không sửa SO thật.

### UC35 — Lập phiếu tồn đầu kỳ

| Thuộc tính | Nội dung |
|---|---|
| Mục tiêu | Đưa lượng tồn ban đầu vào sổ có nguồn gốc và giá/lô. |
| Actor chính | Quản lý kho |
| Mức ưu tiên | P0 |
| Kích hoạt | Người dùng yêu cầu thao tác “Lập phiếu tồn đầu kỳ” trong ngữ cảnh tương ứng. |
| Tiền điều kiện | Đang khởi tạo dataset/kho theo policy; không dùng để lách nhập/điều chỉnh thường kỳ. |
| Dữ liệu vào | SKU, lot, lượng chuẩn, giá, vị trí, condition, căn cứ số đầu. |

**Luồng chính**

1. Quản lý nhập số đầu theo SKU/lot/ô từ nguồn đã đối chiếu.
2. Hệ thống kiểm đơn vị, lô/hạn, vị trí và chống trùng đợt nhập theo policy.
3. Hệ thống lưu OPENING DRAFT; quản lý xem/duyệt và ghi qua UC08/09.

**Luồng thay thế/ngoại lệ**

- 2a. Dữ liệu không xác định lot/hạn của SKU bắt buộc: yêu cầu bổ sung.
- 3a. Đã có vận hành cần sửa số: dùng kiểm kê/điều chỉnh có căn cứ, không lập thêm tồn đầu tùy ý.

**Hậu điều kiện thành công:** Khi ghi sổ có movement nguồn NULL và số dư có thể tái dựng từ đầu.

**Bảo đảm khi không thành công:** Không seed stock_balance trực tiếp rồi thiếu lịch sử.

**Ánh xạ database:** R: product, location; W: lot, inventory_document/line, audit_event; posting qua UC09.

**Tiêu chí nghiệm thu đại diện:**

- OPENING20 có đúng movement và balance20.
- Nháp opening không tăng tồn.

## Luồng con dùng chung trên sơ đồ chi tiết

| ID | Tên | Vai trò trong use case |
|---|---|---|
| SF01 | Kiểm tra điều kiện ghi sổ | Khóa dữ liệu, quyền/version/idempotency, hướng phiếu, hạn/block/freeze, lượng đơn/hold và lượng cuối. Không phải màn hình độc lập. |
| SF02 | Ghi biến động nguyên tử | Ghi movement, balance, reservation theo tác động, POSTED và audit trong cùng transaction. |
| SF03 | Xác định lô đủ điều kiện | Kiểm SKU/condition/vị trí/hạn/ngày giao/block; chọn FEFO/FIFO trước khi phân lượng giữ. |
| SF04 | Tính đường lấy hàng hợp lệ | Cùng tập hold/stop, shortest paths + thứ tự ghé heuristic/baseline; phát hiện điểm không thể tới. |
| SF05 | Kiểm chứng dữ liệu đề xuất | Kiểm SKU/NCC/UOM/policy, snapshot/current state, input_hash; không cho model tự quyết các phép tính tồn. |

SF01/SF02 là luồng con phân rã ở tầng đặc tả hệ thống, chỉ vẽ ở trang chi tiết ghi sổ. Nếu giảng viên muốn use case diagram thuần mục tiêu người dùng, ẩn các SF khỏi hình nộp và giữ chúng trong phần luồng của UC09.

## Bản đồ để giao việc cho agent

| Module OOP | Use case chính | Lưu ý |
|---|---|---|
| IdentityService | UC01–02 | Tài khoản và role |
| CatalogService / WarehouseService | UC03–05 | Quy đổi, master và cây vị trí |
| OrderService | UC06, UC10 | Cam kết và phần còn thực hiện |
| DocumentService + InventoryService | UC07–09, UC13–15, UC19–21, UC35 | Một engine post; nhiều loại phiếu |
| ReservationService | UC11–12 | Cạnh tranh, expiry, tiêu thụ khi ship |
| StocktakeService | UC16–18 | Freeze ngắn, đếm người, chốt atomic |
| QueryService / TraceabilityService | UC22–25, UC33 | View, trace và block |
| MapService / RoutePlanner | UC26–28 | Snapshot kế hoạch, không trừ tồn khi quét |
| AssistantService / ReplenishmentService | UC29–32, UC34 | Evidence, proposal, revalidation |

Các tiêu chí trên là yêu cầu kiểm thử khi triển khai, không phải báo cáo rằng 35 use case đã chạy.
