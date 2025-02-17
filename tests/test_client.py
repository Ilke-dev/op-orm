import pytest
from op_orm.client import OpClient


@pytest.fixture
def op_client():
    return OpClient(integration_name="test-integration")


def test_client_initialization(op_client):
    assert op_client._integration_name == "test-integration"
    assert op_client._client is None
    assert op_client._vault_id is None


@pytest.mark.parametrize(
    "model_builder",
    [{"create": True, "cleanup": True, "once": True}],
    indirect=True,
)
def test_client_items_list(model_builder):
    client = model_builder[0].client
    items = client.items
    assert len(items) > 0


def test_client_vault_properties(op_client):
    vault_id = op_client.vault_id
    vault_name = op_client.vault_name
    assert vault_id is not None
    assert vault_name is not None
    assert op_client._vault_id == vault_id  # Test caching


def test_validate_secret_reference(op_client):
    valid_ref = "op://vault/item/field"
    op_client.validate_secret_reference(valid_ref)

    with pytest.raises(ValueError):
        op_client.validate_secret_reference("invalid_reference")
