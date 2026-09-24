"""add_reconciliation_and_availability_views

Revision ID: 087a448e649d
Revises: 389fd6296895
Create Date: 2026-09-24 15:58:00.000000+00:00

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "087a448e649d"
down_revision: str | None = "389fd6296895"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    # 1. View chân biến động sổ kho (Stock Ledger Leg)
    op.execute("""
    CREATE OR REPLACE VIEW v_stock_ledger_leg AS
    -- Inbound leg
    SELECT
        m.id AS movement_id,
        m.document_line_id,
        m.product_id,
        m.to_location_id AS location_id,
        m.lot_id,
        m.to_condition AS condition,
        m.qty_base AS delta_qty,
        m.recorded_at
    FROM stock_movement m
    WHERE m.to_location_id IS NOT NULL AND m.to_condition IS NOT NULL

    UNION ALL

    -- Outbound leg
    SELECT
        m.id AS movement_id,
        m.document_line_id,
        m.product_id,
        m.from_location_id AS location_id,
        m.lot_id,
        m.from_condition AS condition,
        -m.qty_base AS delta_qty,
        m.recorded_at
    FROM stock_movement m
    WHERE m.from_location_id IS NOT NULL AND m.from_condition IS NOT NULL;
    """)

    # 2. View tồn kho khả dụng tức thời (Stock Availability)
    op.execute("""
    CREATE OR REPLACE VIEW v_stock_availability AS
    SELECT
        b.id AS balance_id,
        b.product_id,
        b.location_id,
        b.lot_id,
        b.condition,
        b.on_hand,
        b.reserved,
        (b.on_hand - b.reserved) AS available_now
    FROM stock_balance b;
    """)

    # 3. View đối soát sổ kho và số dư (Inventory Reconciliation)
    op.execute("""
    CREATE OR REPLACE VIEW v_inventory_reconciliation AS
    WITH ledger_summary AS (
        SELECT
            product_id,
            location_id,
            lot_id,
            condition,
            SUM(delta_qty) AS ledger_on_hand
        FROM v_stock_ledger_leg
        GROUP BY product_id, location_id, lot_id, condition
    ),
    reservation_summary AS (
        SELECT
            product_id,
            location_id,
            lot_id,
            condition,
            SUM(reserved_qty - consumed_qty - released_qty) AS active_reserved
        FROM stock_reservation
        WHERE status IN ('ACTIVE', 'PARTIALLY_CONSUMED')
        GROUP BY product_id, location_id, lot_id, condition
    )
    SELECT
        COALESCE(b.product_id, l.product_id) AS product_id,
        COALESCE(b.location_id, l.location_id) AS location_id,
        COALESCE(b.lot_id, l.lot_id) AS lot_id,
        COALESCE(b.condition, l.condition) AS condition,
        COALESCE(b.on_hand, 0) AS balance_on_hand,
        COALESCE(l.ledger_on_hand, 0) AS ledger_on_hand,
        COALESCE(b.on_hand, 0) - COALESCE(l.ledger_on_hand, 0) AS qty_difference,
        COALESCE(b.reserved, 0) AS balance_reserved,
        COALESCE(r.active_reserved, 0) AS calculated_reserved,
        COALESCE(b.reserved, 0) - COALESCE(r.active_reserved, 0) AS reserved_difference
    FROM stock_balance b
    FULL OUTER JOIN ledger_summary l ON (
        b.product_id = l.product_id AND
        b.location_id = l.location_id AND
        b.lot_id = l.lot_id AND
        b.condition = l.condition
    )
    FULL OUTER JOIN reservation_summary r ON (
        COALESCE(b.product_id, l.product_id) = r.product_id AND
        COALESCE(b.location_id, l.location_id) = r.location_id AND
        COALESCE(b.lot_id, l.lot_id) = r.lot_id AND
        COALESCE(b.condition, l.condition) = r.condition
    );
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS v_inventory_reconciliation;")
    op.execute("DROP VIEW IF EXISTS v_stock_availability;")
    op.execute("DROP VIEW IF EXISTS v_stock_ledger_leg;")
