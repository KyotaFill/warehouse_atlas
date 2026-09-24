# Thiết kế lớp — Warehouse Atlas

Phiên bản bổ sung 1.0 · 14/09/2026 · Python/Tkinter · Bám 35 use case và schema 27 bảng lõi + 10 bảng mở rộng.

Đây là mô hình thiết kế đề xuất để triển khai, không phải sơ đồ reverse-engineer từ ứng dụng đã có. Tài liệu chọn lọc thuộc tính/phương thức quan trọng; tên API là hợp đồng đề xuất và cần được giữ đồng bộ khi agent viết code. Các trường/FK không vẽ vẫn phải tuân schema. Không có migration hoặc ứng dụng mới trong bộ bổ sung này.

## 1. Đọc ba loại sơ đồ cùng nhau

| Tài liệu | Câu hỏi trả lời | Ví dụ trong Atlas |
|---|---|---|
| Use case | Ai thực hiện mục tiêu gì, khi nào thành công/thất bại? | Quản lý ghi sổ phiếu xuất |
| Class diagram | Những loại đối tượng nào, ai chịu trách nhiệm, hợp tác thế nào? | InventoryService dùng PostingEngine và UnitOfWork |
| ERD | Dữ liệu lưu ở đâu, ràng buộc và liên kết ra sao? | inventory_document_line có FK và stock_movement có UNIQUE(document_line_id) |

Một use case có thể dùng nhiều lớp. Một lớp có thể hỗ trợ nhiều use case. Một bảng không bắt buộc trở thành một entity có hành vi độc lập; user_role có thể ánh xạ thành collection Role. Presenter, policy, repository, command và view thường không có bảng riêng.

## 2. Ranh giới trách nhiệm

| Phần | Lớp đại diện | Chịu trách nhiệm | Giới hạn |
|---|---|---|---|
| Presentation | InventoryView, InventoryPresenter, ThemeTokens | Form, trạng thái màn, callback, design system | Không SQL, không tự tính nghiệp vụ cuối cùng |
| Application | DocumentService, InventoryService, ReservationService, StocktakeService | Điều phối use case, quyền, khóa, transaction, DTO | Không widget; không giữ transaction qua thời gian con người/LLM chờ |
| Domain | InventoryDocument, StockReservation, StocktakeLine, LotEligibility, AllocationPolicy | Trạng thái đối tượng, invariant, phép tính, chiến lược | Không import Tkinter/SQLAlchemy/SDK model |
| Ports | UnitOfWork, InventoryRepository, LLMPort, InventoryViewPort | Hợp đồng dùng để thay adapter và kiểm thử | Không nhúng SQL hoặc thư viện UI cụ thể |
| Infrastructure | SqlAlchemyUnitOfWork, SqlAlchemyInventoryRepository, OllamaAdapter | Database, mapping, giao tiếp model | Không tự quyết định bỏ qua quyền/điều kiện xuất |

PostingEngine là cộng tác viên application dùng chung; LotEligibility và AllocationPolicy là domain thuần. AuthorizationPolicy là policy application vì cần kiểm phiên/quyền hiện tại qua port, không phải domain entity tự đọc DB. Ports có thể đặt trong package application/ports; diagram không yêu cầu kiến trúc microservice.

Một entity giữ invariant cục bộ; service giữ invariant xuyên nhiều đối tượng. Ví dụ StockReservation.consume(qty) chặn qty vượt remaining trong RAM. Reservation/balance/event phải được nạp dưới khóa và lưu trong cùng transaction do service kiểm soát, nên gọi entity.consume đơn lẻ không được coi là đã xuất hàng thành công.

## 3. Các quyết định OOP quan trọng

### 3.1 Product khác StockBalance

Product là danh mục SKU. StockBalance là số dư theo (product, location, lot, condition). Không thêm Product.quantity hoặc Product.stock để chứa một tổng không biết đang ở đâu. BucketKey là value object biểu diễn bốn chiều, không phải bảng mới. Trong object model, association có thể dùng tham chiếu ID và nạp theo nhu cầu; không cần tải toàn bộ lịch sử khi mở một product.

StockBalance.free_qty() = on_hand − reserved. Số này chỉ trở thành available nếu eligibility đúng. Lô block có thể còn free_qty=70 nhưng available=0. Lượng bảo quản là Decimal; datetime phải có timezone. Không dùng float để tính lượng/giá. Các giá trị geometry hoặc timeout không có cùng yêu cầu với lượng tồn.

### 3.2 Một loại InventoryDocument, chín DocumentKind

Chọn một InventoryDocument và các quy tắc theo kind cho OPENING, RECEIPT, SHIPMENT, TRANSFER, RECLASSIFY, ADJUSTMENT, CUSTOMER_RETURN, SUPPLIER_RETURN, REVERSAL. Chưa tạo chín subclass có cùng bộ trường chỉ để tăng số lớp. Nếu sau này từng loại có hành vi lớn riêng, có thể tách posting policy sau khi giữ cùng engine và contract.

InventoryDocument sở hữu InventoryDocumentLine về mặt vòng đời nghiệp vụ. DRAFT được rỗng nên multiplicity là 0..*; khi APPROVED/POSTED phải có ít nhất một dòng. Composition không có nghĩa phải bật ON DELETE CASCADE: chứng từ đã post phải được lưu lại; schema hiện dùng RESTRICT.

Một dòng phiếu có 0..1 StockMovement trong toàn vòng đời; khi POSTED là đúng 1. Movement ghi từ/đến bằng location+condition và product+lot; không có stock_balance_id. Đối soát/replay dựng BucketKey từ dữ liệu đó. Không vẽ association movement→balance như thể đã có FK.

### 3.3 FEFO/FIFO là đa hình có mục đích

AllocationPolicy là interface chung. FefoPolicy và FifoPolicy cùng thực hiện allocate(candidates, requested). ReservationService được cấp strategy phù hợp theo SKU; nó dùng cùng lời gọi dù thuật toán khác. FefoPolicy ưu tiên expires_on, received_at, định danh; FifoPolicy ưu tiên received_at, định danh. Cả hai chỉ nhận ứng viên đủ điều kiện và trả kế hoạch, không tự cập nhật kho.

Ví dụ đã loại hàng cấm: lô A nhận trước nhưng hết hạn sau, còn 6; lô B nhận sau nhưng hết hạn trước, còn 8; cần 10. FEFO chọn B8+A2; FIFO chọn A6+B4. Cả hai có tổng 10 nhưng thể hiện ưu tiên khác. Sản phẩm theo hạn mặc định dùng FEFO, không để người dùng tùy ý chọn FIFO nhằm né quy tắc.

Trong Python có thể thể hiện hợp đồng bằng Protocol hoặc ABC. Nếu dùng ABC, subclass triển khai phương thức abstract; nếu dùng Protocol, đối tượng có đúng hành vi/hợp đồng có thể thay thế mà không cần kế thừa danh nghĩa. UML realization vẫn diễn tả quan hệ thực hiện interface. Không cần xây cây Product→Food→Drink chỉ để có inheritance.

### 3.4 UoW và engine tránh commit nửa chừng

InventoryService.post_document và InventoryService.reverse mở UoW mới. StocktakeService.finalize mở UoW của nó và gọi cùng PostingEngine.post_in. Engine dùng transaction đã mở, không gọi lại public InventoryService.post_document để tạo transaction độc lập.

Nhờ vậy, khi chốt kiểm kê, adjustment, balance, movement, trạng thái phiên và audit cùng commit hoặc cùng rollback. Repository chỉ stage/flush dữ liệu; chỉ service ở biên use case commit. Từ chữ UnitOfWork trong sơ đồ này là abstraction application bao quanh Session, không phải yêu cầu viết lại cơ chế flush nội bộ của SQLAlchemy.

### 3.5 Role là dữ liệu

User có nhiều Role qua user_role. Không dùng User→Admin→Manager làm cây kế thừa: một người có thể kiêm vai trò, quyền có thể thay đổi khi chương trình đang chạy. ActorContext chỉ chứa định danh phiên/người dùng; service phải kiểm phiên, is_active và quyền hiện tại. ADMIN riêng chỉ quản trị tài khoản, chưa được mặc nhiên ghi kho.

## 4. Hợp đồng đầu vào và kiểu phụ

Tên cmd trong hình là tham số có kiểu command riêng theo tác vụ; actor là ActorContext. Hình rút gọn chữ ký để dễ đọc. Khi code, agent cần type hint đầy đủ. Các kiểu phụ dưới đây có thể là dataclass/TypedDict, không cần dựng tất cả thành ô trong sơ đồ chính.

| Kiểu | Nội dung tối thiểu |
|---|---|
| PostDocumentCommand | document_id: UUID; expected_version: int; idempotency_key: UUID |
| ReserveCommand | sales_order_id: UUID; line requests gồm sales_order_line_id và qty_base; expected_order_version; ngày giao kiểm từ SO; mặc định all-or-nothing |
| ReleaseCommand | reservation_id; qty_base >0; expected_version; reason |
| ApproveDocumentCommand | document_id; expected_version; quyết định được map sang approve/return_to_draft |
| ReverseCommand | original_document_id; expected_version; reason; idempotency_key |
| FinalizeStocktakeCommand | stocktake_id; expected_version; lý do chênh lệch; idempotency_key cho adjustment nếu phát sinh |
| ApplyProposalCommand | proposal_id; input_hash mà manager đã xem; không cho UI tự gửi status APPLIED |
| ConfirmPickStopCommand | pick_stop_id; expected_input_hash; picked_qty_total; gửi tổng, không gửi phép cộng không có chống trùng |
| PostResult | document_id/code; status=POSTED; posted_at; new_version; was_replay; correlation_id |
| BucketDelta | key: BucketKey; delta_on_hand: Decimal; delta_reserved: Decimal |
| AllocationPlan | allocations gồm candidate/bucket ID và qty_base; total; policy code; không phải reservation đã lưu |
| ReservationResult | IDs đã tạo; lượng từng dòng; tổng được giữ; as_of |
| EligibilityContext | business_date/delivery_date; min_shelf_life_days; trạng thái active, freeze, usage, condition, recall; có đủ snapshot để policy không đọc DB |
| EligibilityResult | eligible: bool; reason_codes; evaluated_at/context |
| PostingContext | Các entity/header/line/bucket/hold đã nạp dưới khóa; thông tin phiên kiểm kê nếu có; timestamp DB cho cả lần post |
| PostingScope | NORMAL hoặc verified stocktake scope do StocktakeService tạo sau khi khóa/kiểm phiên; không nhận từ input người dùng |
| PostingMeta | actor_id; timestamp lấy từ DB; idempotency_key; canonical payload hash |
| StocktakeResult | stocktake_id; POSTED; adjustment_document_id nullable; closed_at |
| RoutePlan | thứ tự stop; path_snapshot; baseline/planned distance; algorithm/version; input_hash; unreachable nodes nếu lỗi |
| ToolEvidence | tool_name; normalized arguments; result; IDs; đơn vị; as_of; quyền đã áp dụng |
| ModelResponse | text và/hoặc danh sách tool request có tên và arguments; model không được đưa Python/SQL để thực thi |
| AnswerDTO | câu trả lời; danh sách evidence/tool call ID; as_of; trạng thái; proposal ID nếu đã tạo |
| AnalysisResult | analysis_run_id; cutoff; metrics; suggestions; assumptions |
| StockPage | các dòng DTO; pagination/cursor; filter; as_of; chỉ cột được phép |
| TraceResult | lot IDs; inbound/outbound effective; vị trí còn; đơn/khách liên quan và chứng từ nguồn |
| ReconcileResult | phạm vi; as_of; chênh lệch ledger/balance, hold/events, thiếu movement của POSTED |
| AppError | code; message an toàn; field/context; retryable; correlation_id; không raw SQL/secret |

received_net/shipped_net trong phương thức outstanding là lượng thực hiện hiệu lực sau reversal, không trừ phiếu trả NCC/khách trả; các phiếu trả vật lý không tự mở lại PO/SO. Reconcile và phân tích dùng một snapshot nhất quán (một truy vấn hoặc transaction đọc có isolation phù hợp), tránh so hai số lấy ở hai trạng thái khác nhau.

Các API save_draft/save_product có form DTO riêng chứa các trường hợp lệ của bảng tương ứng. Form chưa hoàn chỉnh ở RAM; không ép DB lưu các NULL trái schema. actor không được nhận tự do từ model, barcode hoặc người nhập.

## 5. Contract transaction cần giao cho agent

### 5.1 Ghi sổ

1. Presenter tạo một idempotency key cho hành động; giữ nguyên key khi thử lại hành động đó. Hộp thoại xác nhận kết thúc trước khi mở transaction.
2. Service kiểm phiên/quyền, tạo UoW trong worker và xác định kho cần khóa từ snapshot. Khóa warehouse theo UUID, sau đó document/order headers theo loại cố định và UUID; tiếp location, lot, balance, reservation theo chuẩn đã có. Nếu mục tiêu đổi trong lúc chờ, abort/restart đúng tập khóa.
3. Đọc lại phiếu dưới khóa. Nếu đã POSTED với cùng key/hash, trả kết quả trước đó; không từ chối máy móc vì version đã tăng sau lần post. Key dùng cho phiếu/payload khác là conflict. Canonical hash lấy nội dung nghiệp vụ bất biến, loại các trường workflow như status, posted_at và version thay đổi do post.
4. Kiểm version khi đây là lần post mới; phiếu APPROVED, đủ dòng, đúng hướng, quyền, PO/SO/return/reversal còn hợp lệ, product-lot-UOM, block/hạn và freeze. Nhận mới/đảo/trả có quy tắc riêng, không áp tất cả điều kiện xuất bán cho mọi kind.
5. Tạo zero balance còn thiếu theo chuẩn insert-on-conflict, khóa nó, gộp delta cho từng BucketKey và kiểm số dư cuối. Hai dòng 7+6 không được cùng xuất từ bucket chỉ có 10.
6. Shipment phải khóa các hold cùng SO line + SKU/lot/location/condition; tiêu thụ đúng lượng, ghi CONSUME có document_line_id. Schema chưa có dòng phiếu nháp→reservation FK; draft không được giả định đã khóa riêng một hold.
7. Ghi movement (mỗi dòng một bản ghi), balance, reservation/event, audit và document POSTED trong cùng transaction. Mọi dòng dùng một recorded_at lấy từ DB.
8. Commit ở service. Lỗi trước commit rollback. Mất kết nối sau commit nhưng trước phản hồi là kết quả chưa biết; tra/retry cùng key, không tự báo chắc chắn rollback hoặc tạo yêu cầu mới.

PostingContext tập hợp dữ liệu cần thiết để engine làm kiểm nghiệp vụ; repository thực hiện cơ chế khóa và nạp, không tự quyết eligibility. Check trong domain không thay FK/CHECK/UNIQUE/trigger; ngược lại, DB constraint không thay các kiểm liên bảng còn nằm ở service.

### 5.2 Giữ hàng

Kiểm SO CONFIRMED và lượng còn cần. Khóa theo chuẩn warehouse→order→location→lot→balance→reservation, kiểm lại ứng viên; gọi LotEligibility rồi strategy. Tạo reservations, tăng balance.reserved và thêm ALLOCATE trong cùng transaction. Reserve mặc định all-or-nothing: tồn10, hai yêu cầu7 thì một yêu cầu thành công, yêu cầu còn lại báo thiếu4 và không giữ3 ngầm.

Hết hạn không tự làm remaining bằng0. Worker expiry dùng danh tính tác vụ nội bộ có audit, giới hạn scope và cùng khóa để tăng released_qty, giảm reserved, ghi EXPIRE. expires_at không thay thế sự kiện đó. Shipment không được tiêu thụ hold đã hết hạn; xử lý expiry theo contract trước khi tiếp tục. Nếu freeze kiểm kê đang chặn thay đổi hold, tác vụ chờ/xử lý lại sau; ngoại lệ nhả hold thiếu chỉ qua StocktakeService.release_shortage được manager yêu cầu.

Reserve v1 chưa có bảng request idempotency tổng quát. UI không retry mù một yêu cầu giữ một phần sau timeout: tải lại hold và lượng còn cần. Kiểm lượng cần dưới khóa tránh over-reserve, nhưng không được tuyên bố mọi request partial đều exactly-once. Nếu cần retry mọi partial command, bổ sung request log/migration trong một phiên bản riêng.

### 5.3 Kiểm kê

start khóa ngắn, chụp snapshot và chuyển COUNTING rồi commit. Màn đếm chỉ nhận DTO đã bỏ expected_qty; không chỉ ẩn cột nhưng vẫn đưa số cho người đếm qua tool/API. NULL là chưa đếm, 0 là đã đếm không thấy.

finalize khóa phiên, kiểm REVIEW và version; tính delta bằng số cuối. Nếu delta=0, đóng phiên mà không tạo movement qty0. Nếu actual<reserved, giữ REVIEW; manager dùng release_shortage chọn hold để nhả trong transaction đặc biệt có audit. Sau đó mới finalize lại. Khi có adjustment, tạo/duyệt và gọi engine trong cùng UoW; exemption freeze chỉ áp dụng đúng phiên/location đã xác minh. Lỗi bất kỳ phải giữ cả số dư và phiên ở trạng thái trước giao dịch.

### 5.4 Bản đồ và AI

PickService chụp dữ liệu, tính route ngoài transaction dài, rồi kiểm hash lại khi lưu và khi confirm_stop. Confirm ghi picked_qty_total dưới khóa; cùng request tổng không cộng lần hai. Route cũ stale là kết quả so hash, không phải một trạng thái mới trong CHECK pick_run.status. Sơ đồ không thêm bảng đồ thị; MapNode/MapEdge dùng bảng mở rộng sẵn có.

AssistantService gọi LLM ngoài transaction. ToolGateway chạy allowlist được kiểm quyền. Sau trả lời có evidence, manager mới yêu cầu đề xuất. ProposalService khóa proposal, xác nhận nội dung đã xem và dữ liệu hiện tại; nếu đổi đánh STALE rồi yêu cầu xem lại. Nếu còn đúng, tạo PO DRAFT + APPLIED + liên kết kết quả + audit cùng transaction. Adapter LLM không được có đường gọi trực tiếp tới InventoryRepository hoặc PostingEngine.

## 6. Repository và mapping Python

| Port bổ trợ (không vẽ hết ở trang 04) | Thao tác đề xuất | Bảng/nguồn |
|---|---|---|
| IdentityRepository | get_active_user, load_roles, save_user, count_active_admins | app_user/app_role/user_role |
| CatalogRepository | get_product, resolve_barcode, save_product, load_conversion, has_history | category/uom/product/product_uom/product_barcode/partner/supplier_product |
| WarehouseRepository | get_warehouse, lock_warehouses, get_ancestors, save_location | warehouse/location |
| OrderRepository | load_order, lock_order, effective_fulfilled, save_order | PO/SO và line, chứng từ hiệu lực |
| DocumentRepository | load_document, save_draft, compare_version, save_status | inventory_document/line |
| StocktakeRepository | load_active_count, save_snapshot, save_counts, save_status | stocktake/line |
| AuditRepository | append(event) | audit_event |
| MapRepository | load_graph, save_graph, load_pick, save_pick | map_node/map_edge/pick_run/pick_stop |
| AnalysisRepository | save_run, save_suggestions, load_snapshot | analysis_run/replenishment_suggestion/inventory_alert |
| AssistantRepository | save_run, append_tool_call, lock_proposal, save_proposal | ai_run/ai_tool_call/ai_proposal |
| QueryRepository | stock_page, replay, trace, reconcile | View/SQL read-only theo quyền service |

UoW expose các repository cần cho use case bằng thuộc tính hoặc constructor injection cùng session. InventoryRepository là facade phục vụ posting; có thể phối hợp những repository nhỏ này nhưng không tạo session mới trong từng repository. Không ép tạo một GenericRepository với CRUD cho mọi bảng, đặc biệt movement/event không có update/delete.

Domain object là Python thuần; mapping ORM nằm trong infrastructure. Agent có thể dùng imperative mapping hoặc các ORM record riêng và mapper rõ ràng. Nếu tách record riêng, tên đề xuất ProductRow/InventoryDocumentRow là chi tiết triển khai, không thêm bảng. Read query có thể trả DTO trực tiếp; không cần hydrate toàn bộ aggregate chỉ để hiển thị danh sách.

Entity/collection không nhất thiết một file mỗi lớp. Có thể nhóm product+conversion+barcode trong catalog.py, document+line trong documents.py. Tên lớp đủ trách nhiệm quan trọng hơn số lượng file.

## 7. Tkinter và phần design system của bạn

Bạn thiết kế ThemeTokens, quy tắc bố cục, component và toàn bộ trạng thái của màn. InventoryView là mẫu; khi code tách StockView, DocumentView, StocktakeView, MapView, AssistantView theo mức cần thiết. Mỗi màn có presenter hoặc controller với trách nhiệm tương đương; không buộc mọi màn kế thừa một BaseView quá lớn.

| Việc bạn chốt | Hợp đồng giao agent |
|---|---|
| Màu, spacing, typography | ThemeTokens bất biến; ttk styles và Canvas cùng dùng |
| Hiển thị phiếu | DRAFT/APPROVED/POSTED/CANCELLED; các thao tác hợp lệ theo state/quyền |
| Lỗi nhập | Field error, lỗi nghiệp vụ có mã, lý do thiếu hàng/lô bị khóa |
| Tác vụ chậm | Loading, timeout, retry; khóa nút tác vụ đang chạy; kết quả cũ không đè màn mới |
| Xác nhận | Tóm tắt tác động trước commit; đang confirm không có transaction mở |
| Drill-down | Mã chứng từ, lot, vị trí, evidence có thể mở chi tiết |
| Báo cáo | Empty, loading, error, stale/as_of, pagination và cột theo quyền |

Quy ước triển khai của Atlas: toàn bộ widget/after() chạy ở main thread. Worker chỉ đưa TaskResult/DTO vào queue; main thread polling bằng after rồi gọi presenter/view. Event handler dài chặn event loop theo [tài liệu Tkinter chính thức](https://docs.python.org/3/library/tkinter.html#threading-model).

Mỗi tác vụ DB tạo UoW/Session riêng trong worker; chỉ factory/engine được chia sẻ theo thiết kế, không chia một Session giữa các tác vụ đồng thời. Đây là mô hình phù hợp với [hướng dẫn concurrency của SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks).

## 8. Tiêu chí review thiết kế và nghiệm thu khi code

| Ca | Điều cần chứng minh |
|---|---|
| Domain import | Entity/policy chạy được mà không import Tkinter, SQLAlchemy hoặc SDK model |
| FEFO vs FIFO | Cùng candidate và requested, hai strategy cho kết quả đúng thứ tự, không vượt lượng |
| Giữ đồng thời | Hai connection khác nhau tranh tồn10 để giữ7; không over-reserve |
| Lô block sau draft | Shipment phải kiểm lại và từ chối; draft/approval không bảo đảm eligibility tương lai |
| Ghi lỗi giữa chừng | Không có movement/balance/hold/document POSTED dở dang |
| Retry post | Cùng key trả kết quả cũ; không tạo movement lần hai |
| Gộp delta | Hai dòng cùng lấy7 và6 từ tồn10 bị chặn |
| Chuyển | Chuyển chưa giữ từ A sang B bảo toàn tổng SKU/lot/condition |
| Kiểm kê0 | Count=0 khác chưa nhập; delta=0 không tạo movement0 |
| Commit kiểm kê | Lỗi adjustment thì phiên vẫn REVIEW/freeze |
| Đảo | Gốc vẫn POSTED, thêm movement đối ứng, không khôi phục hold cũ ngầm |
| AI | Operator không lấy giá vốn qua tool; stale proposal không thành PO; double apply một PO |
| UI | Tác vụ DB/AI chậm vẫn tương tác được; request cũ không ghi đè state mới |
| Map | Chặn cạnh làm route cũ không dùng được; quét checklist không trừ tồn |

Đây là tiêu chí cho ứng dụng tương lai, không phải thông báo các ca đã chạy. Bộ hiện tại kiểm nội dung sơ đồ và tính nhất quán với schema/use case; chưa triển khai các service.

## 9. Danh mục lớp, thuộc tính và phương thức

Các stereotype entity/service/policy/record/view/DTO/value object là quy ước diễn giải của dự án. Interface dùng ý nghĩa UML thông thường. Record có thể có trạng thái cập nhật như AIRun; chỉ record được quy định append-only (movement, reservation event, audit) mới bất biến sau ghi. Visibility '-' chỉ ý định đóng gói; Python thường dùng thuộc tính `_name` và property, không phải cơ chế phân quyền DB.

### Product
- Loại: **entity** · Mức: **P0** · Trang: 00, 01.
- Trách nhiệm: Thông tin một SKU; không sở hữu số lượng tồn.
- Lưu trữ: product.
- Use case: UC03.
- Quy tắc: Đổi base UOM sau giao dịch phải bị CatalogService chặn; không dùng deactivate để xóa lịch sử.

Thuộc tính được chọn:

```text
- id: UUID
- sku: str
- name: str
- track_expiry: bool
- min_shelf_life_days: int
- is_active: bool
- version: int
```

Phương thức:

```text
+ rename(name): None
+ deactivate(): None
```

### Category
- Loại: **entity** · Mức: **P0** · Trang: 01.
- Trách nhiệm: Nhóm hàng một cấp.
- Lưu trữ: category.
- Use case: UC03.
- Quy tắc: SKU luôn tham chiếu một category hợp lệ.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- name: str
```

Phương thức:

```text
+ rename(name): None
```

### Uom
- Loại: **entity** · Mức: **P0** · Trang: 01.
- Trách nhiệm: Đơn vị đo và độ chính xác cho phép.
- Lưu trữ: uom.
- Use case: UC03.
- Quy tắc: Không dùng float cho lượng; kiểm khả năng biểu diễn trước khi quy đổi.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- decimal_places: int
```

Phương thức:

```text
+ validate_precision(qty): None
```

### ProductUom
- Loại: **entity** · Mức: **P0** · Trang: 01.
- Trách nhiệm: Quy cách riêng của một SKU; ví dụ thùng của SKU A bằng 48 chai.
- Lưu trữ: product_uom.
- Use case: UC03.
- Quy tắc: Factor > 0; mỗi SKU có quy đổi base=1; phiếu lưu factor snapshot.

Thuộc tính được chọn:

```text
- id: UUID
- factor_to_base: Decimal
```

Phương thức:

```text
+ to_base(qty): Decimal
```

### ProductBarcode
- Loại: **entity** · Mức: **P0** · Trang: 01.
- Trách nhiệm: Mã vạch nhận diện ProductUom.
- Lưu trữ: product_barcode.
- Use case: UC03.
- Quy tắc: Code duy nhất; một barcode không tự nhận diện lot.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- is_active: bool
```

Phương thức:

```text
+ deactivate(): None
```

### Partner
- Loại: **entity** · Mức: **P0** · Trang: 01.
- Trách nhiệm: Đối tác có thể đồng thời mua và bán.
- Lưu trữ: partner.
- Use case: UC05.
- Quy tắc: Ít nhất một vai trò; service kiểm đúng vai trò khi lập PO/SO.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- name: str
- is_supplier: bool
- is_customer: bool
```

Phương thức:

```text
+ deactivate(): None
```

### SupplierProduct
- Loại: **entity** · Mức: **P0** · Trang: 01, 10.
- Trách nhiệm: Nguồn cung cho một SKU.
- Lưu trữ: supplier_product.
- Use case: UC05, UC30.
- Quy tắc: Lượng đề xuất dương phải đạt MOQ và làm tròn lên bội số; nhu cầu bằng 0 không bị nâng thành MOQ.

Thuộc tính được chọn:

```text
- id: UUID
- lead_time_days: int
- moq_base: Decimal
- order_multiple_base: Decimal
- quoted_unit_cost: Decimal?
```

Phương thức:

```text
+ round_order_qty(qty): Decimal
```

### CatalogService
- Loại: **service** · Mức: **P0** · Trang: 01.
- Trách nhiệm: Điều phối UC03/05, kiểm trùng và bất biến qua nhiều bản ghi.
- Lưu trữ: —.
- Use case: UC03, UC05.
- Quy tắc: Kiểm quyền manager, version khi có, dữ liệu đã sử dụng và audit trong transaction.

Phương thức:

```text
+ save_product(cmd, actor): UUID
+ set_conversion(cmd, actor): UUID
+ save_supplier(cmd, actor): UUID
```

### Warehouse
- Loại: **entity** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Kho, múi giờ nghiệp vụ và phạm vi khóa ghi.
- Lưu trữ: warehouse.
- Use case: UC04.
- Quy tắc: Chuyển liên kho khóa mọi warehouse theo thứ tự UUID.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- timezone: str
- is_active: bool
```

Phương thức:

```text
+ business_date(at): date
```

### Location
- Loại: **entity** · Mức: **P0** · Trang: 00, 05, 06, 08.
- Trách nhiệm: Vị trí thuộc đúng một kho, có thể có cha.
- Lưu trữ: location.
- Use case: UC04.
- Quy tắc: Cây cùng kho không chu trình; STRUCTURAL không chứa tồn; can_store_stock chưa kiểm mọi điều kiện cấp phát.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- usage: LocationUsage
- is_active: bool
```

Phương thức:

```text
+ can_store_stock(): bool
```

### WarehouseService
- Loại: **service** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Quản lý cây vị trí, không gian kho.
- Lưu trữ: —.
- Use case: UC04.
- Quy tắc: Kiểm tổ tiên, kho cha/con, lịch sử trước thay usage/kho và audit.

Phương thức:

```text
+ save_location(cmd, actor): UUID
+ reparent(cmd, actor): None
```

### Lot
- Loại: **entity** · Mức: **P0** · Trang: 00.
- Trách nhiệm: Lô nội bộ theo lần nhận và giá; có thể trùng mã lô nhà sản xuất giữa nhiều lần nhận.
- Lưu trữ: lot.
- Use case: UC07, UC23, UC24.
- Quy tắc: block chỉ đổi trạng thái đối tượng; TraceabilityService khóa/lưu/audit. Không tự giảm tồn hay nhả hold.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- expires_on: date?
- received_at: datetime
- unit_cost: Decimal
- recall_status: RecallStatus
```

Phương thức:

```text
+ block(reason): None
+ unblock(reason): None
```

### BucketKey
- Loại: **value object** · Mức: **P0** · Trang: 00.
- Trách nhiệm: Giá trị bất biến nhận diện một ô số dư.
- Lưu trữ: các cột khóa ghép của stock_balance.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: So sánh theo bốn thành phần; không có bảng bucket_key hoặc ID riêng.

Thuộc tính được chọn:

```text
+ product_id: UUID {readOnly}
+ location_id: UUID {readOnly}
+ lot_id: UUID {readOnly}
+ condition: StockCondition {readOnly}
```

Phương thức:

```text
+ equals(other): bool
```

### StockBalance
- Loại: **entity** · Mức: **P0** · Trang: 00, 03.
- Trách nhiệm: Số dư hiện tại cho một SKU/lô/vị trí/tình trạng.
- Lưu trữ: stock_balance.
- Use case: UC09, UC11, UC12.
- Quy tắc: 0 <= reserved <= on_hand. free_qty=on_hand-reserved, chưa đồng nghĩa available. apply_delta chỉ dùng trong luồng ghi hợp lệ và không tự lưu DB.

Thuộc tính được chọn:

```text
- id: UUID
- on_hand: Decimal
- reserved: Decimal
- version: int
```

Phương thức:

```text
+ free_qty(): Decimal
+ apply_delta(on_hand, reserved): None
```

### StockReservation
- Loại: **entity** · Mức: **P0** · Trang: 00, 03, 08.
- Trách nhiệm: Lượng giữ của một dòng SO trên một bucket.
- Lưu trữ: stock_reservation.
- Use case: UC11, UC12, UC09.
- Quy tắc: remaining=allocated-consumed-released >=0; consume/release sửa trạng thái trong RAM; service lưu event và balance cùng transaction.

Thuộc tính được chọn:

```text
- id: UUID
- allocated_qty: Decimal
- consumed_qty: Decimal
- released_qty: Decimal
- expires_at: datetime?
- version: int
```

Phương thức:

```text
+ remaining(): Decimal
+ consume(qty): None
+ release(qty): None
```

### ReservationEvent
- Loại: **record** · Mức: **P0** · Trang: 00.
- Trách nhiệm: Bằng chứng ALLOCATE/CONSUME/RELEASE/EXPIRE.
- Lưu trữ: reservation_event.
- Use case: UC11, UC12, UC09.
- Quy tắc: Không sửa/xóa; CONSUME bắt buộc trỏ dòng phiếu xuất.

Thuộc tính được chọn:

```text
+ id: UUID {readOnly}
+ kind: ReservationEventKind
- qty_base: Decimal
- created_at: datetime
```

### StockMovement
- Loại: **record** · Mức: **P0** · Trang: 02, 04.
- Trách nhiệm: Biến động bất biến, nguồn hoặc đích có thể ở ngoài kho.
- Lưu trữ: stock_movement.
- Use case: UC09, UC21, UC25.
- Quy tắc: Mỗi dòng đã POSTED có đúng một movement; đảo bằng movement mới. Không FK tới stock_balance, chỉ suy ra BucketKey từ các chiều.

Thuộc tính được chọn:

```text
+ id: UUID {readOnly}
+ qty_base: Decimal {readOnly}
+ recorded_at: datetime {readOnly}
+ actor_id: UUID {readOnly}
```

Phương thức:

```text
+ bucket_deltas(): list[BucketDelta]
```

### PurchaseOrder
- Loại: **entity** · Mức: **P0** · Trang: 02, 09.
- Trách nhiệm: Cam kết mua, khác với hàng đã thực nhận.
- Lưu trữ: purchase_order.
- Use case: UC06.
- Quy tắc: DRAFT có thể chưa có dòng; confirm cần >=1 dòng và kiểm liên bảng từ service; nhận hàng không ghi vào on_hand của PO.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- status: OrderStatus
- expected_on: date?
- version: int
```

Phương thức:

```text
+ add_line(line): None
+ confirm(): None
+ cancel(): None
```

### PurchaseOrderLine
- Loại: **entity** · Mức: **P0** · Trang: 02.
- Trách nhiệm: Dòng mua với quy đổi đã chụp.
- Lưu trữ: purchase_order_line.
- Use case: UC06.
- Quy tắc: Outstanding trừ receipt hiệu lực và phần đóng thiếu. received_net chỉ net reversal, không trừ SUPPLIER_RETURN để mở lại PO; entity không đọc DB.

Thuộc tính được chọn:

```text
- id: UUID
- ordered_qty: Decimal
- factor_to_base_snapshot: Decimal
- closed_qty_base: Decimal
```

Phương thức:

```text
+ ordered_base(): Decimal
+ outstanding(received_net): Decimal
```

### SalesOrder
- Loại: **entity** · Mức: **P0** · Trang: 02.
- Trách nhiệm: Nhu cầu xuất hàng; có thể được đáp ứng từng phần.
- Lưu trữ: sales_order.
- Use case: UC10.
- Quy tắc: Không hủy phần đã thực hiện; OrderService xử lý hold còn mở theo policy.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- status: OrderStatus
- expected_on: date?
- version: int
```

Phương thức:

```text
+ add_line(line): None
+ confirm(): None
+ cancel(): None
```

### SalesOrderLine
- Loại: **entity** · Mức: **P0** · Trang: 00, 02.
- Trách nhiệm: Dòng đơn có thể có nhiều reservation và dòng shipment.
- Lưu trữ: sales_order_line.
- Use case: UC10, UC11.
- Quy tắc: shipped_net do query cung cấp, chỉ net reversal; CUSTOMER_RETURN không mở lại SO. Không giữ cột shipped_qty mới.

Thuộc tính được chọn:

```text
- id: UUID
- ordered_qty: Decimal
- factor_to_base_snapshot: Decimal
- closed_qty_base: Decimal
```

Phương thức:

```text
+ ordered_base(): Decimal
+ outstanding(shipped_net): Decimal
```

### OrderService
- Loại: **service** · Mức: **P0** · Trang: 02.
- Trách nhiệm: Điều phối PO/SO, kiểm quyền, cam kết và lượng đã thực hiện.
- Lưu trữ: —.
- Use case: UC06, UC10.
- Quy tắc: Nhân viên soạn nháp; manager xác nhận/đóng. Không tăng hoặc giảm tồn khi confirm.

Phương thức:

```text
+ save_draft(cmd, actor): UUID
+ confirm(cmd, actor): None
+ close_short(cmd, actor): None
```

### InventoryDocument
- Loại: **entity** · Mức: **P0** · Trang: 02, 04, 05.
- Trách nhiệm: Chứng từ dùng chung cho 9 loại biến động.
- Lưu trữ: inventory_document.
- Use case: UC07–09, UC13–15, UC19–21, UC35.
- Quy tắc: DRAFT có 0..* dòng; APPROVED/POSTED phải >=1. mark_posted chỉ được PostingEngine gọi sau kiểm đủ; bản ghi gốc đã post không sửa.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- kind: DocumentKind
- status: DocumentStatus
- version: int
- idempotency_key: UUID?
```

Phương thức:

```text
+ add_line(line): None
+ approve(actor_id): None
+ return_to_draft(): None
+ mark_posted(meta): None
```

### InventoryDocumentLine
- Loại: **entity** · Mức: **P0** · Trang: 02.
- Trách nhiệm: Một SKU, một lot và một hướng dịch chuyển.
- Lưu trữ: inventory_document_line.
- Use case: UC07, UC13–15, UC19–21, UC35.
- Quy tắc: qty_base=entered_qty*factor; từ/đến có thể NULL nhưng không cùng NULL; quan hệ location/lot/đơn minh họa ở các trang khác.

Thuộc tính được chọn:

```text
- id: UUID
- line_no: int
- entered_qty: Decimal
- factor_to_base_snapshot: Decimal
- qty_base: Decimal
- from_condition: StockCondition?
- to_condition: StockCondition?
```

Phương thức:

```text
+ validate_shape(kind): None
+ bucket_deltas(): list[BucketDelta]
```

### DocumentService
- Loại: **service** · Mức: **P0** · Trang: 02.
- Trách nhiệm: Tạo và duyệt phiếu trước ghi sổ.
- Lưu trữ: —.
- Use case: UC07, UC08, UC13–15, UC19, UC20, UC35.
- Quy tắc: Không append movement hoặc cập nhật balance; kiểm expected_version và quyền duyệt.

Phương thức:

```text
+ save_draft(cmd, actor): UUID
+ approve(cmd, actor): None
+ return_to_draft(cmd, actor): None
```

### LotEligibility
- Loại: **policy** · Mức: **P0** · Trang: 03.
- Trách nhiệm: Quy tắc khả dụng theo active, vị trí, condition, block, freeze và ngày giao.
- Lưu trữ: —.
- Use case: UC11, UC09.
- Quy tắc: Xuất bán: STORAGE, GOOD, lot ACTIVE; hạn > ngày nghiệp vụ + min_shelf_life. Trả NCC/khách trả dùng policy theo loại phiếu, không áp chặn xuất bán cho mọi hướng.

Phương thức:

```text
+ check(candidate, context): EligibilityResult
```

### AllocationCandidate
- Loại: **value object** · Mức: **P0** · Trang: 03.
- Trách nhiệm: Ảnh chụp một bucket ứng viên; chỉ ứng viên vượt LotEligibility mới chuyển cho AllocationPolicy.
- Lưu trữ: snapshot trong RAM.
- Use case: UC11.
- Quy tắc: Ảnh chụp không tự đảm bảo số còn mới; ReservationService khóa và kiểm lại trước giữ.

Thuộc tính được chọn:

```text
+ balance_id: UUID {readOnly}
+ bucket: BucketKey {readOnly}
+ free_qty: Decimal {readOnly}
+ expires_on: date? {readOnly}
+ received_at: datetime {readOnly}
```

### AllocationPolicy
- Loại: **interface** · Mức: **P0** · Trang: 03.
- Trách nhiệm: Hợp đồng chọn lượng từ các ứng viên hợp lệ.
- Lưu trữ: —.
- Use case: UC11.
- Quy tắc: Pure function trên ứng viên cùng SKU/base UOM; requested >0. Không SQL/cập nhật reserved; đủ đúng requested hoặc báo thiếu theo mặc định all-or-nothing.

Phương thức:

```text
+ allocate(candidates, requested): AllocationPlan
```

### FefoPolicy
- Loại: **strategy** · Mức: **P0** · Trang: 03.
- Trách nhiệm: Chọn lô hết hạn sớm trước.
- Lưu trữ: —.
- Use case: UC11.
- Quy tắc: Cùng hạn: received_at rồi định danh ổn định; thiếu expires_on của SKU theo hạn bị loại ở eligibility.

Phương thức:

```text
+ allocate(candidates, requested): AllocationPlan
```

### FifoPolicy
- Loại: **strategy** · Mức: **P0** · Trang: 03.
- Trách nhiệm: Chọn lô nhận sớm trước cho SKU không theo hạn.
- Lưu trữ: —.
- Use case: UC11.
- Quy tắc: Cùng received_at dùng định danh ổn định; đây là chọn hàng vật lý, không phải FIFO kế toán.

Phương thức:

```text
+ allocate(candidates, requested): AllocationPlan
```

### ReservationService
- Loại: **service** · Mức: **P0** · Trang: 03.
- Trách nhiệm: Khóa, cấp phát/nhả, cập nhật reservation, balance và event.
- Lưu trữ: —.
- Use case: UC11, UC12.
- Quy tắc: Policy chọn theo cấu hình SKU. Reserve mặc định toàn bộ hoặc không; expiry phải tạo EXPIRE và giảm reserved trong transaction, không chỉ so giờ.

Thuộc tính được chọn:

```text
- policy: AllocationPolicy
- eligibility: LotEligibility
```

Phương thức:

```text
+ reserve(cmd, actor): ReservationResult
+ release(cmd, actor): None
+ expire_due(scope): int
```

### InventoryService
- Loại: **service** · Mức: **P0** · Trang: 04, 07.
- Trách nhiệm: Biên transaction của ghi sổ và đảo chứng từ.
- Lưu trữ: —.
- Use case: UC09, UC21.
- Quy tắc: Mở UoW mới mỗi lời gọi; engine không tự commit. UI chỉ nhận DTO sau commit.

Thuộc tính được chọn:

```text
- uow_factory: Callable
- engine: PostingEngine
```

Phương thức:

```text
+ post_document(cmd, actor): PostResult
+ reverse(cmd, actor): PostResult
```

### PostingEngine
- Loại: **service** · Mức: **P0** · Trang: 04, 05.
- Trách nhiệm: Một engine dùng lại cho ghi sổ, đảo và chốt kiểm kê.
- Lưu trữ: —.
- Use case: UC09, UC18, UC21.
- Quy tắc: Khóa/kiểm, gộp delta, ghi movement/balance/hold/audit/document. Không mở/commit transaction con; scope kiểm kê phải do service xác minh, không do UI tự gửi.

Phương thức:

```text
+ post_in(uow, cmd, actor, scope): PostResult
```

### UnitOfWork
- Loại: **interface** · Mức: **P0** · Trang: 04, 05.
- Trách nhiệm: Hợp đồng quản lý một transaction và các repository cùng session.
- Lưu trữ: —.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Nếu thoát chưa commit phải rollback và close. Thuộc tính inventory là phần minh họa; các repository khác cùng UoW được đặc tả trong hướng dẫn.

Thuộc tính được chọn:

```text
+ inventory: InventoryRepository
```

Phương thức:

```text
+ begin(): None
+ commit(): None
+ rollback(): None
+ close(): None
```

### InventoryRepository
- Loại: **interface** · Mức: **P0** · Trang: 04.
- Trách nhiệm: Hợp đồng nạp/khóa/lưu cho engine, tách PostgreSQL khỏi domain.
- Lưu trữ: stock_movement, stock_balance, stock_reservation và chứng từ liên quan.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: lock_context tuân thứ tự khóa toàn hệ thống; repository không quyết định hàng được xuất hay không và không commit.

Phương thức:

```text
+ lock_context(cmd, scope): PostingContext
+ append_movement(movement): None
+ save_changes(context): None
+ find_posted(key): PostResult?
```

### SqlAlchemyUnitOfWork
- Loại: **adapter** · Mức: **P0** · Trang: 04.
- Trách nhiệm: Triển khai UnitOfWork bằng SQLAlchemy.
- Lưu trữ: —.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Session tạo bên trong worker đang dùng; một tác vụ một session, đóng sau giao dịch.

Thuộc tính được chọn:

```text
- session: Session
```

Phương thức:

```text
+ begin(): None
+ commit(): None
+ rollback(): None
+ close(): None
```

### SqlAlchemyInventoryRepository
- Loại: **adapter** · Mức: **P0** · Trang: 04.
- Trách nhiệm: Triển khai SQL và mapping cho InventoryRepository.
- Lưu trữ: ánh xạ SQLAlchemy cho schema hiện có.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Dùng cùng session của UoW; FK/unique/check là bảo vệ bổ sung, không thay nghiệp vụ.

Thuộc tính được chọn:

```text
- session: Session
```

Phương thức:

```text
+ lock_context(cmd, scope): PostingContext
+ append_movement(movement): None
+ save_changes(context): None
+ find_posted(key): PostResult?
```

### PostDocumentCommand
- Loại: **DTO** · Mức: **P0** · Trang: 04, 07.
- Trách nhiệm: Yêu cầu bất biến từ UI; không mang ORM entity.
- Lưu trữ: không có bảng.
- Use case: UC09.
- Quy tắc: Server/service tính canonical hash từ nội dung đã duyệt, đối chiếu cùng key khi retry; actor lấy từ phiên xác thực.

Thuộc tính được chọn:

```text
+ document_id: UUID {readOnly}
+ expected_version: int {readOnly}
+ idempotency_key: UUID {readOnly}
```

### Stocktake
- Loại: **entity** · Mức: **P0** · Trang: 05.
- Trách nhiệm: Phiên kiểm kê một vị trí lá.
- Lưu trữ: stocktake.
- Use case: UC16–18.
- Quy tắc: COUNTING/REVIEW là freeze nghiệp vụ; DRAFT/CANCELLED/POSTED không freeze; submit phải đủ số đếm.

Thuộc tính được chọn:

```text
- id: UUID
- status: StocktakeStatus
- frozen_at: datetime?
- closed_at: datetime?
- version: int
```

Phương thức:

```text
+ start(snapshot, at): None
+ submit_for_review(): None
+ mark_posted(meta): None
+ cancel(): None
```

### StocktakeLine
- Loại: **entity** · Mức: **P0** · Trang: 05.
- Trách nhiệm: Snapshot và số quan sát thực tế.
- Lưu trữ: stocktake_line.
- Use case: UC17, UC18.
- Quy tắc: variance dùng recount nếu có, còn không dùng counted. NULL khác 0; chưa đếm thì báo lỗi thay vì tính delta giả.

Thuộc tính được chọn:

```text
- id: UUID
- expected_qty: Decimal
- counted_qty: Decimal?
- recounted_qty: Decimal?
- variance_reason: str?
```

Phương thức:

```text
+ record_count(qty): None
+ record_recount(qty): None
+ variance(): Decimal
```

### StocktakeService
- Loại: **service** · Mức: **P0** · Trang: 05.
- Trách nhiệm: Mở, ghi số, chốt kiểm kê và xử lý thiếu hold có kiểm soát.
- Lưu trữ: —.
- Use case: UC16–18.
- Quy tắc: Finalize chỉ một transaction, adjustment và đóng phiên cùng commit; delta=0 không tạo movement. release_shortage chỉ nhả hold được manager chọn trong đúng phiên REVIEW.

Thuộc tính được chọn:

```text
- engine: PostingEngine
- uow_factory: Callable
```

Phương thức:

```text
+ start(cmd, actor): UUID
+ record_count(cmd, actor): None
+ finalize(cmd, actor): StocktakeResult
+ release_shortage(cmd, actor): None
```

### User
- Loại: **entity** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Tài khoản vận hành, khác phiên người dùng.
- Lưu trữ: app_user.
- Use case: UC01, UC02.
- Quy tắc: Không trả password_hash tới view hoặc LLM; không kế thừa AdminUser/ManagerUser chỉ vì vai trò.

Thuộc tính được chọn:

```text
- id: UUID
- username: str
- password_hash: str
- is_active: bool
```

Phương thức:

```text
+ deactivate(): None
```

### Role
- Loại: **entity** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Vai trò được gán cho nhiều tài khoản.
- Lưu trữ: app_role; liên kết qua user_role.
- Use case: UC01, UC02.
- Quy tắc: ADMIN không mặc nhiên MANAGER; một user có thể có nhiều role.

Thuộc tính được chọn:

```text
- id: UUID
- code: RoleCode
- name: str
```

### ActorContext
- Loại: **value object** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Định danh người thực hiện từ phiên đã xác thực.
- Lưu trữ: phiên trong bộ nhớ, không phải bảng mới.
- Use case: UC01 và các UC có quyền.
- Quy tắc: Không nhận actor tùy ý từ form. Session phải tồn tại; role/is_active được kiểm lại ở service call.

Thuộc tính được chọn:

```text
+ user_id: UUID {readOnly}
+ session_id: UUID {readOnly}
```

### AuthorizationPolicy
- Loại: **policy** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Cửa kiểm quyền trước tác vụ và trước lấy dữ liệu nhạy cảm.
- Lưu trữ: đọc app_user, user_role, app_role qua application.
- Use case: UC01–35.
- Quy tắc: Kiểm phiên còn hiệu lực, tài khoản active và quyền hiện tại. Lớp này là application policy, được dùng port IdentityRepository; domain entity không tự truy DB.

Phương thức:

```text
+ require(actor, permission): None
```

### IdentityService
- Loại: **service** · Mức: **P0** · Trang: 06.
- Trách nhiệm: Xác thực, phiên và quản trị tài khoản.
- Lưu trữ: —.
- Use case: UC01, UC02.
- Quy tắc: Hash mật khẩu; bảo vệ admin hoạt động cuối cùng; thay role/khóa có hiệu lực ở lời gọi tiếp theo.

Phương thức:

```text
+ login(credentials): ActorContext
+ logout(actor): None
+ update_user(cmd, actor): None
```

### InventoryViewPort
- Loại: **interface** · Mức: **P0** · Trang: 07.
- Trách nhiệm: Hợp đồng hiển thị để presenter không phụ thuộc widget cụ thể.
- Lưu trữ: —.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Các phương thức UI chỉ được gọi trên Tk main thread.

Phương thức:

```text
+ render(data): None
+ set_busy(value): None
+ show_error(error): None
```

### InventoryView
- Loại: **view** · Mức: **P0** · Trang: 07.
- Trách nhiệm: Màn Tkinter/ttk mẫu cho phiếu và tồn.
- Lưu trữ: —.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Đọc input, phát callback, hiển thị DTO; không SQL, không giữ ORM entity; tên này là mẫu để tách DocumentView/StockView khi triển khai.

Thuộc tính được chọn:

```text
- tokens: ThemeTokens
```

Phương thức:

```text
+ render(data): None
+ set_busy(value): None
+ show_error(error): None
```

### InventoryPresenter
- Loại: **presenter** · Mức: **P0** · Trang: 07.
- Trách nhiệm: Chuyển thao tác người dùng thành command, quản lý loading/error và dữ liệu hiển thị.
- Lưu trữ: —.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Giữ idempotency key khi retry cùng tác vụ; kết quả cũ theo request_id không được đè màn mới.

Thuộc tính được chọn:

```text
- view: InventoryViewPort
- runner: BackgroundTaskRunner
```

Phương thức:

```text
+ on_post_clicked(): None
+ on_result(result): None
+ refresh(): None
```

### BackgroundTaskRunner
- Loại: **utility** · Mức: **P0** · Trang: 07.
- Trách nhiệm: Chạy DB, AI và tính route ngoài handler giao diện.
- Lưu trữ: —.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Worker đưa DTO/error vào queue; main thread polling bằng after(). Hủy UI không có nghĩa undo DB đã commit.

Thuộc tính được chọn:

```text
- max_workers: int
- results: Queue
```

Phương thức:

```text
+ submit(task): UUID
+ poll_results(): list[TaskResult]
+ shutdown(): None
```

### TaskResult
- Loại: **DTO** · Mức: **P0** · Trang: 07.
- Trách nhiệm: Phong bì kết quả qua queue.
- Lưu trữ: không có bảng.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Không chứa Session/ORM entity/Tk widget; payload cụ thể dùng DTO theo màn.

Thuộc tính được chọn:

```text
+ request_id: UUID {readOnly}
+ payload: object? {readOnly}
+ error: AppError? {readOnly}
```

### ThemeTokens
- Loại: **value object** · Mức: **P0** · Trang: 07.
- Trách nhiệm: Design tokens do bạn sở hữu, dùng cho các component.
- Lưu trữ: cấu hình giao diện.
- Use case: Hạ tầng/hợp đồng dùng chung.
- Quy tắc: Màu trạng thái và kích thước nhất quán; không chứa quyền hay quy tắc tính tồn.

Thuộc tính được chọn:

```text
+ colors: Mapping {readOnly}
+ spacing: Mapping {readOnly}
+ typography: Mapping {readOnly}
```

### MapNode
- Loại: **entity** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Điểm lối đi hoặc điểm tiếp cận một vị trí.
- Lưu trữ: map_node.
- Use case: UC26.
- Quy tắc: Location liên kết tối đa một node; cùng warehouse.

Thuộc tính được chọn:

```text
- id: UUID
- code: str
- x_m: Decimal
- y_m: Decimal
- kind: MapNodeKind
```

Phương thức:

```text
+ move_to(x, y): None
```

### MapEdge
- Loại: **entity** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Cạnh có hướng giữa hai node.
- Lưu trữ: map_edge.
- Use case: UC26.
- Quy tắc: Hai chiều là hai cạnh; from != to và distance >0; không dùng khoảng cách thẳng xuyên kệ.

Thuộc tính được chọn:

```text
- id: UUID
- distance_m: Decimal
- is_enabled: bool
```

Phương thức:

```text
+ disable(): None
```

### PickRun
- Loại: **entity** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Kế hoạch có snapshot route, thuật toán và đầu vào.
- Lưu trữ: pick_run.
- Use case: UC27, UC28.
- Quy tắc: DONE chỉ khi đủ checklist và kế hoạch còn hợp lệ; không thêm trạng thái STALE vào DB, stale là kết quả so hash.

Thuộc tính được chọn:

```text
- id: UUID
- status: PickStatus
- input_hash: str
- baseline_distance_m: Decimal
- planned_distance_m: Decimal
```

Phương thức:

```text
+ start(): None
+ complete(): None
+ cancel(): None
```

### PickStop
- Loại: **entity** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Một dòng checklist gắn reservation và điểm lấy.
- Lưu trữ: pick_stop.
- Use case: UC28.
- Quy tắc: Ghi tổng đã lấy 0..planned_qty dưới row lock; gọi lặp cùng tổng không cộng đôi; quét chưa giảm tồn.

Thuộc tính được chọn:

```text
- id: UUID
- sequence_no: int
- planned_qty: Decimal
- picked_qty: Decimal
```

Phương thức:

```text
+ confirm_total(qty, at): None
```

### RoutePlanner
- Loại: **algorithm** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Tính shortest paths trên graph, so thứ tự baseline và heuristic cho cùng tập stop.
- Lưu trữ: —.
- Use case: UC27.
- Quy tắc: Chỉ sau FEFO/hold; báo unreachable; không tự đổi lot để đường ngắn hơn. Chưa tuyên bố tối ưu toàn cục.

Phương thức:

```text
+ plan(graph, stops, endpoints): RoutePlan
```

### MapService
- Loại: **service** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Kiểm và lưu map.
- Lưu trữ: —.
- Use case: UC26.
- Quy tắc: Kiểm cùng kho, liên kết location; khóa warehouse theo chuẩn. Thay graph làm hash kế hoạch cũ khác.

Phương thức:

```text
+ save_graph(cmd, actor): None
```

### PickService
- Loại: **service** · Mức: **P1** · Trang: 08.
- Trách nhiệm: Chụp hold/map, tính đường, xác minh lại rồi lưu kế hoạch; xác nhận lấy hàng.
- Lưu trữ: —.
- Use case: UC27, UC28.
- Quy tắc: Không giữ transaction trong lúc tính route dài; kiểm input_hash tại lưu và xác nhận; bản cũ không sửa path_snapshot.

Thuộc tính được chọn:

```text
- planner: RoutePlanner
```

Phương thức:

```text
+ create_plan(cmd, actor): UUID
+ confirm_stop(cmd, actor): None
```

### AIRun
- Loại: **record** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Hồ sơ một yêu cầu AI và câu trả lời.
- Lưu trữ: ai_run.
- Use case: UC29.
- Quy tắc: Lưu model/prompt version và trạng thái; không giả định là một hội thoại nhiều lượt đã có bảng session.

Thuộc tính được chọn:

```text
- id: UUID
- question: str
- model_id: str
- prompt_version: str
- status: AIRunStatus
```

### AIToolCall
- Loại: **record** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Evidence thực tế từ công cụ được ứng dụng thực hiện.
- Lưu trữ: ai_tool_call.
- Use case: UC29.
- Quy tắc: Giới hạn payload, loại bí mật; số liệu hiển thị gắn đơn vị, ID và thời điểm.

Thuộc tính được chọn:

```text
- id: UUID
- sequence_no: int
- tool_name: str
- arguments: JSON
- result_snapshot: JSON
```

### AIProposal
- Loại: **entity** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Đề xuất tạo PO nháp, tách khỏi câu trả lời tự do.
- Lưu trữ: ai_proposal.
- Use case: UC31, UC32.
- Quy tắc: APPLIED cùng commit với một PO; kiểm lại snapshot; không có state APPROVED trung gian trong schema.

Thuộc tính được chọn:

```text
- id: UUID
- payload: JSON
- input_hash: str
- status: ProposalStatus
```

Phương thức:

```text
+ reject(): None
+ mark_stale(): None
+ mark_applied(po_id, actor): None
```

### LLMPort
- Loại: **interface** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Hợp đồng model để application không gắn chặt nhà cung cấp.
- Lưu trữ: —.
- Use case: UC29.
- Quy tắc: Trả câu trả lời/tool request có cấu trúc; ứng dụng mới là bên thực thi tool.

Phương thức:

```text
+ generate(messages, tools): ModelResponse
```

### OllamaAdapter
- Loại: **adapter** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Adapter đề xuất cho model chạy local.
- Lưu trữ: —.
- Use case: UC29.
- Quy tắc: Kiểm model thực tế hỗ trợ hợp đồng; có timeout/cancel; không khẳng định mọi model đều tool-call tốt.

Thuộc tính được chọn:

```text
- endpoint: str
- model_id: str
- timeout_s: float
```

Phương thức:

```text
+ generate(messages, tools): ModelResponse
```

### ToolGateway
- Loại: **service** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Allowlist các công cụ đọc/tính nghiệp vụ mà model được yêu cầu.
- Lưu trữ: —.
- Use case: UC29, UC31.
- Quy tắc: Kiểm quyền trước query, kiểm schema tham số; không SQL/shell tùy ý và không cho tool ghi sổ.

Phương thức:

```text
+ execute(request, actor): ToolEvidence
```

### AssistantService
- Loại: **service** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Điều phối model, tool evidence và lưu đề xuất.
- Lưu trữ: —.
- Use case: UC29, UC31.
- Quy tắc: Không mở transaction kho trong lúc chờ LLM. Proposal chỉ từ payload được kiểm chứng; chưa tạo PO.

Thuộc tính được chọn:

```text
- llm: LLMPort
- tools: ToolGateway
```

Phương thức:

```text
+ ask(cmd, actor): AnswerDTO
+ propose_purchase(cmd, actor): UUID
```

### ProposalService
- Loại: **service** · Mức: **P1** · Trang: 09.
- Trách nhiệm: Manager duyệt/từ chối proposal; create PO DRAFT nguyên tử.
- Lưu trữ: —.
- Use case: UC32.
- Quy tắc: Lock proposal rồi kiểm hash/dữ liệu hiện tại; APPLIED trả PO cũ; STALE yêu cầu xem lại, không âm thầm áp dụng con số mới.

Phương thức:

```text
+ apply(cmd, actor): UUID
+ reject(cmd, actor): None
```

### ReorderPolicy
- Loại: **entity** · Mức: **P1** · Trang: 10.
- Trách nhiệm: Chính sách bổ sung theo SKU và warehouse.
- Lưu trữ: reorder_policy.
- Use case: UC30.
- Quy tắc: target >= min >=0; đơn vị base. Công thức min/max cụ thể trong hướng dẫn; tránh trừ reserved hai lần.

Thuộc tính được chọn:

```text
- id: UUID
- min_qty: Decimal
- target_qty: Decimal
- safety_stock_qty: Decimal
- review_period_days: int
```

Phương thức:

```text
+ needs_order(position): bool
```

### AnalysisRun
- Loại: **record** · Mức: **P1** · Trang: 10.
- Trách nhiệm: Snapshot đầu vào và kết quả phân tích.
- Lưu trữ: analysis_run.
- Use case: UC30, UC34.
- Quy tắc: Báo cáo gắn cutoff/giả định; không chứng minh là dự báo ML.

Thuộc tính được chọn:

```text
- id: UUID
- kind: str
- algorithm_version: str
- data_cutoff_at: datetime
- input_snapshot: JSON
- metrics: JSON
```

### ReplenishmentSuggestion
- Loại: **entity** · Mức: **P1** · Trang: 10.
- Trách nhiệm: Một dòng gợi ý mua do rule tính.
- Lưu trữ: replenishment_suggestion.
- Use case: UC30.
- Quy tắc: Qty >0; suggestion không phải ai_proposal. Nếu chuyển thủ công qua OrderService, phải kiểm lại và liên kết result_po_line_id.

Thuộc tính được chọn:

```text
- id: UUID
- suggested_qty_base: Decimal
- reason: str
- status: SuggestionStatus
- evidence: JSON
```

Phương thức:

```text
+ mark_stale(): None
```

### InventoryAlert
- Loại: **record** · Mức: **P1** · Trang: 10.
- Trách nhiệm: Bản ghi cảnh báo và bằng chứng phân tích.
- Lưu trữ: inventory_alert.
- Use case: UC22 (đọc khi có).
- Quy tắc: Đã có bảng nhưng use case quản lý vòng đời cảnh báo chưa tách riêng trong 35 UC; v1 chỉ đọc theo báo cáo, không mở rộng scope ngầm.

Thuộc tính được chọn:

```text
- id: UUID
- kind: str
- severity: AlertSeverity
- status: AlertStatus
- evidence: JSON
```

### ReplenishmentService
- Loại: **service** · Mức: **P1** · Trang: 10.
- Trách nhiệm: Tính min/max với supply/demand snapshot và điều kiện NCC.
- Lưu trữ: —.
- Use case: UC30.
- Quy tắc: position=eligible_on_hand+inbound_hợp_lệ-open_demand. Không trừ reserved nữa khi open_demand đã bao gồm hold.

Phương thức:

```text
+ compute(cmd, actor): AnalysisResult
```

### ScenarioService
- Loại: **service** · Mức: **P2** · Trang: 10.
- Trách nhiệm: Mô phỏng giả định trên cùng một snapshot.
- Lưu trữ: —.
- Use case: UC34.
- Quy tắc: Không sửa đơn/tồn thật; chỉ làm sau P0/P1 ổn.

Phương thức:

```text
+ simulate(cmd, actor): AnalysisResult
```

### QueryService
- Loại: **service** · Mức: **P0** · Trang: 10.
- Trách nhiệm: Tồn, lịch sử ghi nhận và đối soát.
- Lưu trữ: các view và truy vấn đọc.
- Use case: UC22, UC25, UC33.
- Quy tắc: DTO đã lọc quyền; replay là lượng vật lý theo recorded_at, không lịch sử mọi thuộc tính hay available.

Phương thức:

```text
+ stock(filter, actor): StockPage
+ replay(cutoff, actor): StockPage
+ reconcile(scope, actor): ReconcileResult
```

### TraceabilityService
- Loại: **service** · Mức: **P1** · Trang: 10.
- Trách nhiệm: Truy nguồn/đích lô và khóa/mở khóa có lý do.
- Lưu trữ: lot và các chứng từ/biến động liên quan.
- Use case: UC23, UC24.
- Quy tắc: Block chỉ khóa lot, cập nhật flag/audit, không đi ngược thứ tự lấy warehouse trong cùng transaction; hold xử lý riêng.

Phương thức:

```text
+ trace_lot(filter, actor): TraceResult
+ block_lots(cmd, actor): None
```

### AuditEvent
- Loại: **record** · Mức: **P0** · Trang: phụ lục, không đặt ô riêng.
- Trách nhiệm: Dấu vết tác vụ và thay đổi master.
- Lưu trữ: audit_event.
- Use case: UC01–35.
- Quy tắc: Không log mật khẩu; generic entity reference chỉ là audit, không thay FK nghiệp vụ.

Thuộc tính được chọn:

```text
+ id: UUID {readOnly}
+ action: str {readOnly}
+ entity_type: str {readOnly}
+ correlation_id: UUID {readOnly}
+ created_at: datetime {readOnly}
```

