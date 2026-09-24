# Hướng dẫn vẽ use case cho Warehouse Atlas

Bản bổ sung 1.1 cho kế hoạch Tkinter–OOP–PostgreSQL. Điểm xuất phát là mục tiêu của người dùng và phạm vi ứng dụng; số lượng bảng không quyết định số use case.

## 1. Ranh giới hệ thống

Khung chữ nhật đặt tên **Warehouse Atlas — Ứng dụng quản lý kho**. Trong khung là các chức năng của GUI, application/domain services, dữ liệu và worker nội bộ. Dịch vụ LLM chạy qua API local được chọn nằm ngoài boundary phần mềm Atlas, vì Atlas gọi nó như một hệ thống hỗ trợ. “Bên ngoài” ở đây không đồng nghĩa với chạy trên internet.

Khách hàng và nhà cung cấp là bên liên quan về nghiệp vụ, nhưng chưa trực tiếp dùng ứng dụng trong phạm vi v1. Nhân viên kho nhập thông tin đơn và hàng thay họ, nên không nối hai bên này vào các use case của ứng dụng. Nếu sau này có portal để họ trực tiếp đặt đơn/xác nhận, lúc đó thêm actor và mở rộng boundary phù hợp.

| Thành phần | Có vẽ actor không? | Vì sao |
|---|---|---|
| Nhân viên kho | Có | Trực tiếp lập phiếu, giữ hàng, đếm và lấy hàng |
| Quản lý kho | Có | Phê duyệt, ghi sổ, chốt kiểm kê, khóa lô, quyết định mua |
| Quản trị hệ thống | Có | Tài khoản và vai trò |
| Người dùng nội bộ | Actor tổng quát, abstract | Gom mục tiêu chung như đăng nhập; không phải role thứ tư trong DB |
| Dịch vụ LLM local | Có, actor hỗ trợ ở sơ đồ AI | Giao tiếp với Atlas qua interface ngoài boundary đã chọn |
| Khách hàng/nhà cung cấp | Chưa trong v1 | Không trực tiếp sử dụng ứng dụng |
| PostgreSQL | Không | Thành phần lưu trữ bên trong hệ thống đã chọn |
| Tkinter, SQLAlchemy, repository | Không | Chi tiết triển khai |
| Worker hết hạn reservation | Không | Hành vi nội bộ theo thời gian, ghi thành quy tắc vận hành |
| Máy quét giả bàn phím | Không cần | Cách nhập dữ liệu; chưa có tích hợp thiết bị độc lập |

Định nghĩa actor và use case dựa trên metamodel chính thức: actor là vai trò tương tác với hệ thống; use case tạo ra kết quả có giá trị quan sát được. [OMG UML — model chuẩn](https://www.omg.org/spec/UML/20161101/UML.xmi).

## 2. Actor và quyền không được đánh đồng

Ba role đã có trong database: OPERATOR, MANAGER, ADMIN. Một tài khoản có thể nhận nhiều role qua user_role. Admin không mặc định kế thừa toàn bộ quyền kho. Manager có các quyền được nêu trong ma trận, không suy luận từ tên chức danh.

Trong trang “00 — Actor”, cả ba actor chuyên biệt trỏ generalization về “Người dùng nội bộ”. Kế thừa ở đây chỉ giúp nhận hành vi chung như UC01. Không vẽ “Admin kế thừa Manager” khi policy của bạn chưa cho quyền đó.

Nếu sau này tách “Nhân viên nhập” và “Nhân viên xuất” trên phân tích nghiệp vụ, có thể coi là hai vai trò nghiệp vụ cùng map vào OPERATOR trong bản đầu. Chỉ tách role DB khi thật sự cần quyền khác nhau; không mở rộng bảng vì sơ đồ có nhiều hình người.

## 3. Cách đặt tên oval

Dùng động từ + đối tượng + mục tiêu đủ rõ, ví dụ “Giữ hàng cho đơn”, “Lập phiếu nhập hàng”, “Ghi sổ phiếu kho”, “Truy vết lô hàng”. Tên như “Kho”, “AI”, “Database”, “Button Save”, “CRUD stock_balance” không diễn tả tốt mục tiêu use case.

Các nhóm quản lý master như UC03/04 được trình bày ở mức nhóm tác vụ; nếu giảng viên yêu cầu use case rất nhỏ, bạn có thể tách “Tạo SKU”, “Sửa thông tin SKU”, “Ngừng sử dụng SKU” trong một trang chi tiết và ghi luồng tương ứng. Bản hiện tại giữ cùng cách phân rã để không nở thành hàng trăm oval.

## 4. Nối dây đúng UML

| Quan hệ | Kiểu đường | Hướng | Ý nghĩa |
|---|---|---|---|
| Association | Nét liền, thường không mũi tên | Actor nối use case | Actor tham gia tương tác |
| Include | Nét đứt, đầu mũi tên mở, nhãn `<<include>>` | Use case sử dụng → hành vi được dùng | Hành vi được bao gồm tại điểm quy định |
| Extend | Nét đứt, đầu mũi tên mở, nhãn `<<extend>>` | Use case mở rộng → use case gốc | Chèn hành vi bổ sung theo điều kiện tại extension point |
| Actor generalization | Nét liền, tam giác rỗng | Actor chuyên biệt → actor tổng quát | Vai trò chuyên biệt nhận hành vi/quan hệ phù hợp của vai trò tổng quát |

Hướng Include và Extend được đối chiếu với model Include/Extend trong [OMG UML](https://www.omg.org/spec/UML/20161101/UML.xmi). Điều kiện và extension point cần viết rõ trong đặc tả; số lượng mũi tên nhiều không chứng minh mô hình tốt.

### Các quan hệ dùng thật trong bộ này

| Từ | Quan hệ | Đến | Lý do |
|---|---|---|---|
| UC09 Ghi sổ phiếu | include | SF01 Kiểm tra điều kiện ghi sổ | Mỗi lần ghi phải kiểm dữ liệu hiện tại |
| UC09 Ghi sổ phiếu | include | SF02 Ghi biến động nguyên tử | Tác động thành công phải được commit đồng nhất |
| UC11 Giữ hàng | include | SF03 Xác định lô đủ điều kiện | Luôn xác định nguồn có thể cấp phát |
| UC21 Đảo chứng từ | include | SF01 và SF02 | Đảo cũng dùng cùng engine kiểm và ghi |
| UC27 Lập kế hoạch lấy hàng | include | SF04 Tính đường hợp lệ | Kết quả plan phải đi qua đường hợp lệ |
| UC31 Tạo đề xuất trong hội thoại | extend | UC29 Hỏi trợ lý kho | Tại EP-AI-1 sau phần giải thích, khi manager yêu cầu đề xuất |
| UC31 Tạo đề xuất trong hội thoại | include | SF05 Kiểm chứng dữ liệu đề xuất | Không chấp nhận payload model chưa kiểm |
| UC32 Duyệt đề xuất thành PO nháp | include | SF05 Kiểm chứng dữ liệu đề xuất | Kiểm lại current state trước khi áp dụng |

SF01–SF05 là hành vi con để phân rã trên sơ đồ chi tiết; không có actor khởi chạy độc lập. Sơ đồ tổng quan chỉ cần các UC cấp mục tiêu. Các mũi tên include mô tả hành vi được dùng trong use case, không phải biểu đồ phụ thuộc module code.

### Những quan hệ không nên nối

- Không nối `Lập phiếu nhập include Phê duyệt phiếu`: phiếu có thể được lưu rồi manager duyệt ở thời điểm khác.
- Không nối `Phê duyệt include Ghi sổ`: APPROVED có thể kết thúc mà tồn chưa đổi.
- Không nối `Lập phiếu xuất include Giữ hàng` chỉ vì cần hold trước: hold hiện hữu là tiền điều kiện của luồng này.
- Không nối `Giữ hàng include Đăng nhập` trên mỗi use case: đăng nhập là tiền điều kiện chung, không cần thực hiện lại mỗi lần giữ.
- Không nối `Truy vết lô include Khóa lô`: người dùng có thể xem truy vết mà không khóa gì.
- Không nối `Hỏi AI include Duyệt đề xuất`: nhiều câu hỏi chỉ tra cứu; phê duyệt diễn ra độc lập sau khi có proposal.
- Không gắn `extend` cho mọi lỗi như hết hàng, sai mã, mất kết nối. Chúng được mô tả trong luồng thay thế/ngoại lệ.
- Không vẽ `UC18 chốt kiểm kê include ghi một adjustment` cho mọi trường hợp: nếu chênh lệch bằng 0 thì không tạo phiếu/movement0.

Nếu bạn cần thể hiện “nhập trước, duyệt sau, cuối cùng ghi sổ”, hãy dùng activity hoặc sequence diagram. Use case diagram trả lời ai sử dụng mục tiêu nào; nó không biểu diễn trình tự thời gian bằng vị trí oval hoặc dây association.

## 5. Tổ chức các trang trong file drawio

| Trang | Nội dung | Use case |
|---|---|---|
| 00 | Actor và hành vi chung | UC01 + generalization |
| 01 | Tài khoản và danh mục | UC01–05 |
| 02 | Nhập hàng và ghi sổ | UC06–09, UC35, SF01–02 |
| 03 | Đơn xuất và giữ hàng | UC10–13, SF03 |
| 04 | Di chuyển, trả và đảo | UC14–15, UC19–21, SF01–02 |
| 05 | Kiểm kê | UC16–18 |
| 06 | Tra cứu và kiểm soát | UC22–25, UC33 |
| 07 | Bản đồ và lấy hàng | UC26–28, SF04 |
| 08 | Trợ lý và đề xuất AI | UC29, UC31–32, SF05, LLM |
| 09 | Bổ sung hàng và what-if | UC30, UC34 |

Mỗi trang là một góc nhìn của cùng hệ thống Atlas, không phải mười hệ thống con triển khai riêng. Biên hệ thống có thể ghi tên nhóm phía sau để dễ đọc nhưng actor vẫn ngoài khung. Mỗi use case giữ ID thống nhất ở sơ đồ, đặc tả, test và task agent.

## 6. Bạn nên vẽ trước phần nào?

Bắt đầu trang 02 và 03. Bạn cần nắm chắc:

1. O lập RECEIPT/SHIPMENT ở DRAFT.
2. M xem và duyệt → APPROVED, chưa đổi tồn.
3. M ghi sổ → POSTED, movement và balance thay đổi cùng transaction.
4. UC11 chỉ giữ hàng; on_hand không giảm.
5. Giao một phần làm consumed tăng và reserved giảm đúng phần đã giao.

Sau khi tự giải thích được năm ý này, vẽ kiểm kê và trace. Phần AI được thêm sau với ba use case tách rõ: hỏi → tạo proposal theo yêu cầu → manager duyệt thành PO nháp. Không nối dây theo chuỗi này trên use case diagram; dùng mô tả tiền/hậu điều kiện để liên hệ.

## 7. Ví dụ đặc tả ngắn để bạn tự viết tiếp

**UC11 — Giữ hàng cho đơn.** Actor: nhân viên/quản lý kho. Tiền điều kiện: SO CONFIRMED còn nhu cầu. Kích hoạt: chọn Giữ hàng. Luồng chính: lấy tồn đủ điều kiện → chọn FEFO/FIFO → kiểm dưới khóa → tạo hold và ALLOCATE event → hiện kết quả. Hậu điều kiện: on_hand giữ nguyên, reserved tăng đúng lượng. Ngoại lệ: không đủ thì all-or-nothing mặc định không giữ; hai phiên cạnh tranh phải kiểm lại; lô block/expiry không được cấp.

Tình huống tính tay: tồn10, hai đơn cùng yêu cầu7. Một đơn giữ7; đơn còn lại thấy3 và báo thiếu4. Nếu bạn tự dự đoán được dữ liệu trước/sau thì use case đã đủ cụ thể để kiểm code.

## 8. Trạng thái và chỗ chưa có trong DB

Bổ sung use case không mặc định yêu cầu thêm bảng. Đặc tả này dùng các bảng đã thiết kế. Các yêu cầu mới về ma trận quyền là policy ở service. Những mở rộng như comment phê duyệt, gửi email, request assignment, quản lý ca/nhân viên hoặc reservation gắn trước vào dòng phiếu cần ADR và migration riêng nếu nhóm quyết định làm.

V1 chưa có FK trực tiếp từ inventory_document_line đến stock_reservation. Ở UC13/09, dòng nháp lưu SO line + SKU/lot/location/condition; lúc ghi sổ service khóa các reservation phù hợp, phân lượng tiêu thụ xác định và lưu liên kết thực tế trong reservation_event.document_line_id. Nếu muốn nhân viên chỉ định bất biến một reservation ngay khi lập nháp, phải thêm bảng liên kết draft allocations có kế hoạch migration; không giả vờ schema hiện tại đã lưu được lựa chọn đó. Plan picking có reservation_id rõ trong pick_stop, nhưng vẫn phải kiểm lại khi shipment được ghi.

## 9. Tự kiểm sơ đồ trước khi nộp

Actor ở ngoài khung; use case ở trong; mỗi oval có tên hành động và ID; quan hệ có đúng ý nghĩa/hướng; không dùng mũi tên để kể thứ tự thao tác; không đặt database/GUI class làm actor; mọi quyền trên dây khớp ma trận; tình huống lỗi nằm ở đặc tả; mỗi use case có tiền/hậu điều kiện và một kết quả quan sát được.

35 use case là phạm vi đặc tả theo mức đã chọn, không phải mục tiêu phải vẽ 35 oval lên một trang. Giữ sơ đồ tổng quan ngắn, sơ đồ nhóm đủ đọc và luồng chi tiết đủ để người khác nghiệm thu.
