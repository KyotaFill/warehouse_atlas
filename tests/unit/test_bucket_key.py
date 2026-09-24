import uuid

from warehouse_atlas.common.constants import Condition
from warehouse_atlas.common.types import BucketKey


def test_bucket_key_equality():
    p_id = uuid.uuid4()
    loc_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    key1 = BucketKey(product_id=p_id, location_id=loc_id, lot_id=lot_id, condition=Condition.GOOD)
    key2 = BucketKey(product_id=p_id, location_id=loc_id, lot_id=lot_id, condition=Condition.GOOD)
    key3 = BucketKey(
        product_id=p_id, location_id=loc_id, lot_id=lot_id, condition=Condition.DAMAGED
    )

    assert key1 == key2
    assert key1 != key3
    assert hash(key1) == hash(key2)


def test_bucket_key_as_dict_key():
    p_id = uuid.uuid4()
    loc_id = uuid.uuid4()
    lot_id = uuid.uuid4()

    key = BucketKey(product_id=p_id, location_id=loc_id, lot_id=lot_id, condition=Condition.GOOD)
    d = {key: 100}
    assert d[key] == 100
