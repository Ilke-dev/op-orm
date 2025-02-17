import pytest
from op_orm.types import StringField
from op_orm.exceptions import OpOrmException


@pytest.fixture
def op_client():
    def test_field_reference_validation_no_section():
        field = StringField()  # No section_id
        field._client = op_client
        field._vault_id = op_client.vault_id
        field.title = "test_title"
        field.field_name = "test_field"
        expected = f"op://{op_client.vault_name}/test_title/test_field"
        assert field._reference == expected

    def test_field_value_setter():
        field = StringField(section_id="test")
        field.value = "new_value"
        assert field._value == "new_value"
        assert field._sync is False

    def test_empty_field_value():
        field = StringField(section_id="test")
        field._value = ""  # Empty string
        field.default_value = None
        with pytest.raises(OpOrmException):
            _ = field.value

    def test_field_value_without_default_fixed():
        field = StringField(section_id="test")
        field._value = None
        field._sync = False  # Ensure sync is disabled
        with pytest.raises(
            OpOrmException, match="No value or default value set and sync is disabled."
        ):
            _ = field.value

    def test_field_sync_property():
        field = StringField(section_id="test")
        field._sync = True
        field._client = op_client
        field._vault_id = op_client.vault_id
        field.title = "test_title"
        field.field_name = "test_field"
        with pytest.raises(
            OpOrmException
        ):  # Should raise when trying to resolve without proper setup
            _ = field.value
