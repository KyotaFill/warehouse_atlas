# Hướng dẫn đọc, vẽ và đối chiếu class diagram

Warehouse Atlas · 14/09/2026.

## 1. Bắt đầu từ đâu?

Mở `warehouse_atlas_class_diagrams.drawio` trong diagrams.net. Mỗi tab là một góc nhìn của cùng hệ thống, không phải một ứng dụng độc lập. Các lớp trùng tên ở nhiều tab là cùng một lớp. File chứa ô và connector chỉnh sửa được, không phải ảnh dán vào canvas. SVG/PNG để xem hoặc đưa vào báo cáo; PlantUML để chỉnh bằng text.

Thứ tự học/vẽ nên là 00 (tồn kho), 02 (chứng từ), 03 (FEFO/FIFO), 04 (ghi sổ), 05 (kiểm kê), rồi 07 (Tkinter). Khi hiểu phần này hãy thêm 08–10. Chọn 4–6 hình quan trọng cho phần thân báo cáo, đưa phần chi tiết vào phụ lục thay vì in cả hệ thống trong một hình chữ cực nhỏ.

## 2. Quy ước UML dùng trong bộ này

| Ký hiệu | Ý nghĩa | Ví dụ |
|---|---|---|
| Ô ba ngăn | Tên lớp / thuộc tính / phương thức | StockReservation |
| + | Public | + remaining(): Decimal |
| - | Private theo ý định thiết kế | - consumed_qty: Decimal |
| {readOnly} | Giá trị không đổi sau khởi tạo theo contract | PostDocumentCommand |
| T? | Ký hiệu rút gọn của T hoặc None trong dự án | expires_on: date? |
| Nét liền, không mũi tên | Association; chưa chỉ định navigability | Product — Lot |
| Hình thoi đen ở đầu chủ | Composition, bộ phận có một chủ sở hữu | InventoryDocument *— InventoryDocumentLine |
| Nét đứt, mũi tên mở | Dependency, lớp nguồn sử dụng lớp đích | InventoryService → PostingEngine |
| Nét đứt, tam giác rỗng | Realization: thực hiện interface, mũi tên về interface | FefoPolicy → AllocationPolicy |
| Nét liền, tam giác rỗng | Generalization/kế thừa lớp; chỉ thêm khi thực sự cần | Một view cụ thể kế thừa ttk.Frame nếu triển khai theo cách đó |

Realization và generalization khác nhau. Bộ này dùng realization cho chiến lược và adapter; không ép thêm một cây kế thừa nghiệp vụ giả. Chữ «entity», «service», «value object»... là nhãn quy ước của Atlas để người đọc biết vai trò lớp, không tuyên bố là một UML profile đã đăng ký. Nền ký pháp tham khảo [UML 2.5.1 của OMG](https://www.omg.org/spec/UML/2.5.1/About-UML).

### Đọc multiplicity đúng đầu

`Product "1" — "0..*" Lot`: một Product có thể có 0 hoặc nhiều Lot; mỗi Lot thuộc đúng một Product. Chữ cạnh Lot là số Lot ứng với một Product. `SalesOrderLine "1" — "0..*" StockReservation` đọc tương tự. Đây là số lượng instance, không phải số dòng code hoặc thứ tự xử lý.

`InventoryDocument "1" *— "0..*" InventoryDocumentLine`: một dòng thuộc một phiếu. DRAFT có thể rỗng nên không ghi 1..* cho toàn bộ vòng đời; constraint riêng yêu cầu >=1 khi duyệt/post. Composition không chỉ dẫn cascade delete chứng từ lịch sử.

BucketKey là value object nằm trong StockBalance; cùng giá trị key có thể được copy sang DTO/candidate, không bắt buộc chia sẻ cùng object có danh tính. Nét thoi ở đây biểu diễn giá trị thuộc object, không một bảng con có khóa chính.

## 3. Danh sách các trang

| Trang | Chủ đề | Điều cần giải thích |
|---|---|---|
| 00 | Lõi tồn kho: lô, vị trí, số dư và giữ hàng | StockBalance giữ lượng theo bốn chiều. free_qty chưa kiểm eligibility. Product không có quantity. Quan hệ là liên kết đối tượng; các reference có thể được lưu bằng UUID. |
| 01 | Danh mục: sản phẩm, đơn vị và nguồn cung | Một thùng của hai SKU có thể có hệ số khác nhau. Service kiểm dữ liệu đã được dùng; phiếu giữ factor snapshot của riêng nó. |
| 02 | Đơn hàng và chứng từ: cấu trúc và vòng đời | DRAFT có thể chưa có dòng; APPROVED/POSTED phải có ít nhất một dòng. Mỗi dòng POSTED sinh đúng một movement. Dòng phiếu không đồng thời gắn PO line và SO line. |
| 03 | Giữ hàng: đa hình FEFO/FIFO và điều kiện cấp phát | Mũi tên tam giác rỗng nét đứt hướng về interface. Policy thuần tính toán; ReservationService giữ transaction và kiểm lại dữ liệu trước khi cấp phát. |
| 04 | Ghi sổ: service, engine, repository và transaction | InventoryService sở hữu commit. PostingEngine.post_in dùng UoW đã mở, cũng được StocktakeService dùng lại. Adapter triển khai interface; repository không commit. |
| 05 | Kiểm kê: snapshot, đếm và điều chỉnh nguyên tử | Một location có tối đa một phiên COUNTING/REVIEW. Freeze là trạng thái nghiệp vụ, không giữ DB transaction trong lúc người dùng đếm. Chênh lệch 0: không tạo adjustment. |
| 06 | Tài khoản, quyền và cấu trúc kho | Role là dữ liệu qua user_role, không phải cây kế thừa User. Location có parent 0..1 và children 0..* trong cùng warehouse; service kiểm chu trình. |
| 07 | Tkinter: view, presenter, worker và design tokens | View/Presenter ở main thread; tác vụ nặng chạy worker. Queue chỉ mang DTO. Main thread dùng after() để nhận kết quả; mỗi tác vụ DB tạo UoW/session riêng. |
| 08 | Bản đồ và kế hoạch lấy hàng — P1 | FEFO/hold chọn hàng trước, route chọn đường sau. PickStop chỉ ghi nhận checklist. input_hash khác thì báo kế hoạch cũ; không thêm STALE vào PickStatus. |
| 09 | Trợ lý AI: evidence, đề xuất và bước duyệt — P1 | Model yêu cầu tool, ứng dụng kiểm quyền và thực thi. AssistantService chỉ lưu proposal; ProposalService kiểm lại dữ liệu rồi tạo PO DRAFT. Chưa có tác động tồn. |
| 10 | Truy vấn, bổ sung hàng và mô phỏng | P0: QueryService. P1: truy vết và bổ sung hàng. P2: ScenarioService. Phân tích dùng snapshot; không sửa vận hành. Alert có bảng sẵn nhưng chưa thêm UC quản lý cảnh báo riêng. |

## 4. Association quan trọng chưa vẽ hết

Các sơ đồ đã lược bớt dây để đọc được. Đây là quan hệ bắt buộc vẫn phải giữ trong implementation. Thuộc tính reference có thể mang UUID; dùng FK thật khi lưu.

| Đầu A | Đầu B | Quy tắc |
|---|---|---|
| Product 1 | ProductUom 1..* | Mỗi SKU hợp lệ có base=1; mức tối thiểu do service bảo đảm |
| Uom 1 | Product 0..* | base_uom; ngoài quan hệ Uom–ProductUom đã vẽ |
| Product/Lot/Location mỗi đầu 1 | StockBalance 0..* | StockBalance luôn có đúng product, lot và location; lot.product phải khớp |
| Product/Lot/ProductUom mỗi đầu 1 | InventoryDocumentLine 0..* | SKU phải khớp các reference; một dòng một lot |
| Location 0..1 | InventoryDocumentLine 0..* | Hai association riêng from và to; tối thiểu một phía có location |
| Location 0..1 | StockMovement 0..* | Hai association riêng from và to; source/destination NULL là ngoài kho |
| InventoryDocumentLine gốc 0..1 | InventoryDocumentLine trả/đảo 0..* | original_line_id; service kiểm loại và tổng lượng còn được trả |
| InventoryDocument gốc 0..1 | InventoryDocument đảo 0..1 | reversal_of_id unique; một phiếu đảo tối đa một gốc và ngược lại |
| StockMovement gốc 0..1 | StockMovement đảo 0..1 | reverses_movement_id unique |
| InventoryDocumentLine 0..1 | ReservationEvent 0..* | CONSUME bắt buộc một document_line; event khác có thể NULL |
| Warehouse 1 | Location/PO/SO/MapNode/PickRun 0..* | Mỗi đối tượng ở phía phải thuộc một kho; Doc có thể liên kho qua location |
| Partner 1 | PurchaseOrder/SalesOrder 0..* | Supplier cho PO, customer cho SO; không áp một kiểu partner cho cả hai |
| Partner 0..1 | Lot 0..* | Lot có thể không có supplier ở tồn đầu kỳ; nếu có phải là supplier |
| Location cha 0..1 | Location con 0..* | Cùng kho; không chu trình; self-link ở trang06 dùng đúng hai vai trò |
| SalesOrder 1 | PickRun 0..* | Kế hoạch lấy hàng gắn một đơn |
| MapNode 1 | MapEdge 0..* | Hai quan hệ riêng from/to; node hai đầu cùng kho |
| Product/Warehouse 1 | ReorderPolicy 0..* | Unique (product, warehouse) |
| PurchaseOrderLine 0..1 | ReplenishmentSuggestion 0..* | result_po_line_id nullable, schema không UNIQUE đầu kết quả |
| User | created_by/approved_by/actor_id | Theo NOT NULL/nullable của từng bảng; không kéo mọi dây User vào cùng một hình |

Một số liên kết kết quả chưa có UNIQUE trong schema. Cụ thể trang05 vẽ Stocktake "0..*" — "0..1" InventoryDocument: một Stocktake chọn tối đa một adjustment, còn schema chưa cấm nhiều Stocktake cùng tham chiếu một document; trang09 một proposal có tối đa một PO, còn một PO có thể được nhiều proposal tham chiếu ở mức DB. Service của v1 tạo mới riêng và không tái dùng kết quả tùy ý. Nếu muốn DB enforce 1–1 ở chiều ngược, cần migration UNIQUE, không chỉ sửa nhãn trên hình. Không nhầm “một proposal apply một lần” với “schema đã UNIQUE result_purchase_order_id”.

Không vẽ association trực tiếp InventoryDocumentLine nháp→StockReservation như thể schema đã có FK. Khi post shipment, dùng SO line và bucket để tìm/khóa hold; ReservationEvent ghi consumption thực tế. Muốn cố định hold ngay từ draft thì cần bảng allocation link và migration riêng.

## 5. Ánh xạ đầy đủ 35 use case

| Use case | Service/entry point | Lớp cộng tác |
|---|---|---|
| UC01 | IdentityService.login | User, Role, ActorContext |
| UC02 | IdentityService.update_user | User, Role, AuthorizationPolicy |
| UC03 | CatalogService | Product, ProductUom, ProductBarcode, Category, Uom |
| UC04 | WarehouseService | Warehouse, Location |
| UC05 | CatalogService | Partner, SupplierProduct |
| UC06 | OrderService | PurchaseOrder, PurchaseOrderLine |
| UC07 | DocumentService.save_draft | InventoryDocument, InventoryDocumentLine, Lot |
| UC08 | DocumentService.approve | InventoryDocument |
| UC09 | InventoryService.post_document | PostingEngine, UnitOfWork, StockMovement, StockBalance |
| UC10 | OrderService | SalesOrder, SalesOrderLine |
| UC11 | ReservationService.reserve | AllocationPolicy, LotEligibility, StockReservation, StockBalance |
| UC12 | ReservationService.release | StockReservation, ReservationEvent, StockBalance |
| UC13 | DocumentService.save_draft | InventoryDocumentLine, SalesOrderLine |
| UC14 | DocumentService.save_draft | InventoryDocumentLine, Location |
| UC15 | DocumentService.save_draft | InventoryDocumentLine, StockCondition |
| UC16 | StocktakeService.start | Stocktake, StocktakeLine, Location |
| UC17 | StocktakeService.record_count | StocktakeLine |
| UC18 | StocktakeService.finalize | Stocktake, PostingEngine, UnitOfWork |
| UC19 | DocumentService.save_draft | InventoryDocumentLine.original_line_id, Lot |
| UC20 | DocumentService.save_draft | InventoryDocumentLine.original_line_id, Lot |
| UC21 | InventoryService.reverse | InventoryDocument, PostingEngine, StockMovement |
| UC22 | QueryService.stock | StockPage, các read query |
| UC23 | TraceabilityService.trace_lot | Lot, chứng từ và movement |
| UC24 | TraceabilityService.block_lots | Lot, AuditEvent |
| UC25 | QueryService.replay | StockMovement |
| UC26 | MapService.save_graph | MapNode, MapEdge |
| UC27 | PickService.create_plan | RoutePlanner, PickRun, PickStop |
| UC28 | PickService.confirm_stop | PickStop, PickRun |
| UC29 | AssistantService.ask | LLMPort, ToolGateway, AIRun, AIToolCall |
| UC30 | ReplenishmentService.compute | ReorderPolicy, AnalysisRun, ReplenishmentSuggestion |
| UC31 | AssistantService.propose_purchase | AIProposal, ToolGateway |
| UC32 | ProposalService.apply | AIProposal, PurchaseOrder |
| UC33 | QueryService.reconcile | AuditEvent, StockMovement, StockBalance, ReservationEvent |
| UC34 | ScenarioService.simulate | AnalysisRun |
| UC35 | DocumentService.save_draft | InventoryDocument kind OPENING, Lot |

SF01/SF02 ở use case diagram được thực hiện bên trong PostingEngine và các repository/policy. SF03 là LotEligibility + AllocationPolicy. SF04 là RoutePlanner. SF05 dùng ReplenishmentService và kiểm dữ liệu hiện tại trong AssistantService/ProposalService. Chúng không phải năm lớp bắt buộc mang tên use case.

## 6. Ánh xạ 37 bảng

| Bảng hiện có | Lớp hoặc cách biểu diễn |
|---|---|
| app_user | User |
| app_role | Role |
| user_role | User.roles ↔ Role; association, không bắt buộc UserRole class |
| category | Category |
| uom | Uom |
| product | Product |
| product_uom | ProductUom |
| product_barcode | ProductBarcode |
| partner | Partner |
| supplier_product | SupplierProduct |
| warehouse | Warehouse |
| location | Location |
| lot | Lot |
| purchase_order | PurchaseOrder |
| purchase_order_line | PurchaseOrderLine |
| sales_order | SalesOrder |
| sales_order_line | SalesOrderLine |
| inventory_document | InventoryDocument |
| inventory_document_line | InventoryDocumentLine |
| stock_movement | StockMovement |
| stock_balance | StockBalance + BucketKey |
| stock_reservation | StockReservation |
| reservation_event | ReservationEvent |
| stocktake | Stocktake |
| stocktake_line | StocktakeLine |
| audit_event | AuditEvent |
| reorder_policy | ReorderPolicy |
| map_node | MapNode |
| map_edge | MapEdge |
| pick_run | PickRun |
| pick_stop | PickStop |
| analysis_run | AnalysisRun |
| inventory_alert | InventoryAlert |
| replenishment_suggestion | ReplenishmentSuggestion |
| ai_run | AIRun |
| ai_tool_call | AIToolCall |
| ai_proposal | AIProposal |

Mapping trên không tạo bảng mới. Class có thuộc tính tính toán hoặc command/DTO không được tự động biến thành một cột/bảng mới khi agent dùng ORM. Cột version chỉ dùng nơi schema đã có; với PickRun/PickStop/AIProposal dùng lock/hash và trạng thái theo contract, không giả vờ đã có version column.

## 7. Enum phải giữ đúng schema

| Enum trong Python | Giá trị lưu |
|---|---|
| RoleCode | ADMIN, MANAGER, OPERATOR |
| LocationUsage | STRUCTURAL, STORAGE, RECEIVING, DISPATCH, TRANSIT |
| StockCondition | GOOD, QUARANTINE, DAMAGED |
| RecallStatus | ACTIVE, BLOCKED |
| OrderStatus | DRAFT, CONFIRMED, CLOSED, CANCELLED |
| DocumentKind | OPENING, RECEIPT, SHIPMENT, TRANSFER, RECLASSIFY, ADJUSTMENT, CUSTOMER_RETURN, SUPPLIER_RETURN, REVERSAL |
| DocumentStatus | DRAFT, APPROVED, POSTED, CANCELLED |
| ReservationEventKind | ALLOCATE, CONSUME, RELEASE, EXPIRE |
| StocktakeStatus | DRAFT, COUNTING, REVIEW, POSTED, CANCELLED |
| MapNodeKind | AISLE, PICK, ENTRY, EXIT |
| PickStatus | PLANNED, IN_PROGRESS, DONE, CANCELLED |
| AIRunStatus | RUNNING, SUCCEEDED, FAILED, CANCELLED |
| ProposalStatus | PROPOSED, APPLIED, REJECTED, STALE |
| SuggestionStatus | PROPOSED, ACCEPTED, REJECTED, STALE |
| AlertSeverity | INFO, WARNING, CRITICAL |
| AlertStatus | OPEN, ACKNOWLEDGED, RESOLVED |

Postgres hiện dùng text + CHECK, không phải CREATE TYPE enum. Python Enum ánh xạ chuỗi trên; thêm thành viên chỉ ở Python có thể gây lỗi DB. Không thêm PENDING_APPROVAL/REJECTED vào DocumentStatus hoặc STALE vào PickStatus. StockReservation không có status column; remaining là lượng suy ra từ allocated/consumed/released.

## 8. Giao việc theo thứ tự trong hai tháng

| Giai đoạn | Hợp đồng bạn cần duyệt trước khi agent code |
|---|---|
| Tuần 1 | Entity/enum, ownership, bảng→lớp, DTO và UI mẫu; hiểu trang00/02 |
| Tuần 2 | InventoryService, PostingEngine, repository/UoW; chứng minh transaction và idempotency |
| Tuần 3 | OrderService, ReservationService, FEFO/FIFO; ca tranh tồn |
| Tuần 4 | StocktakeService, return/reversal; các state màn và trường hợp lỗi |
| Tuần 5 | Map/Pick + Traceability; input_hash, baseline và giới hạn heuristic |
| Tuần 6 | Replenishment + AI ports/tools/proposal; evidence và approval |
| Tuần 7–8 | Sửa tích hợp, đóng gói, bảo vệ; ScenarioService chỉ nếu P0/P1 đã ổn |

Số lớp trong phụ lục gồm entity/record, interface, service, adapter, DTO và lớp UI mẫu; không phải số module lớn phải làm ngay. Các DTO và port có thể nằm chung module. Ưu tiên hiểu và chạy được một luồng hoàn chỉnh trước khi mở rộng màn.

### Prompt mẫu giao agent

> Triển khai UC09 theo trang04 và contract ghi sổ. Public entry là InventoryService.post_document(PostDocumentCommand, ActorContext). Dùng PostingEngine.post_in trong UoW đang mở; không commit ở repository/engine. Domain không import Tkinter/SQLAlchemy. Giữ schema hiện có, không tự thêm state hoặc reservation FK vào dòng nháp. Test retry cùng key, rollback khi lỗi giữa chừng, hai dòng trùng bucket vượt tổng, lot bị block sau draft. Trả PostResult DTO sau commit và AppError có code khi thất bại. Chưa làm UI trong task này.

## 9. Câu hỏi tự bảo vệ

1. Vì sao Product không có quantity nhưng StockBalance có on_hand/reserved?
2. Dòng phiếu và movement giống/khác nhau gì? Khi nào 0..1 trở thành đúng1?
3. Vì sao composition không đồng nghĩa xóa chứng từ lịch sử theo cascade?
4. Entity.consume thành công trong RAM đã đủ để báo xuất kho chưa?
5. Hai policy FEFO/FIFO thay thế nhau qua hợp đồng nào? Lựa chọn strategy được quyết định ở đâu?
6. Vì sao StocktakeService không gọi một service tự commit adjustment rồi mới đóng phiên?
7. Vì sao Admin/Manager là Role, còn FefoPolicy/FifoPolicy là hai lớp thực hiện interface?
8. Worker nào được cầm Session? UI nhận kiểu dữ liệu nào?
9. Tại sao LLMPort không trực tiếp ghi stock_balance?
10. Quan hệ nào trong class diagram chỉ được service bảo đảm, chưa có constraint DB tương ứng?

Đáp án nằm trong `warehouse_atlas_dac_ta_class.md`. Mục tiêu của bộ sơ đồ là giúp bạn trả lời được các câu này bằng ví dụ nghiệp vụ và luồng code cụ thể.
