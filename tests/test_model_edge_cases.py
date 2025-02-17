import pytest
from op_orm.exceptions import OpOrmException
from conftest import EmptyModel


def test_model_without_fields():
    try:
        EmptyModel()
    except OpOrmException as e:
        assert e.args[0] == "No fields found in the model"


@pytest.mark.parametrize(
    "model_builder", [{"create": True, "cleanup": True, "once": True}], indirect=True
)
def test_create_duplicate_item(model_builder):
    model = model_builder[0]
    try:
        model.create()
    except OpOrmException as e:
        assert (
            e.args[0]
            == f"Failed to create item: Item with title {model.title} already exists"
        )


@pytest.mark.parametrize("model_builder", [{"once": True}], indirect=True)
def test_update_nonexistent_item(model_builder):
    model = model_builder[0]
    try:
        model.update_existing_fields({"username": "new_value"})
    except OpOrmException as e:
        assert e.args[0] == f"Can't update item: {model.title} does not exist"


@pytest.mark.parametrize("model_builder", [{"cleanup": True}], indirect=True)
def test_create_with_null_fields(model_builder):
    model = model_builder[0]
    model.username.value = None

    try:
        model.create()
    except OpOrmException as e:
        assert (
            e.args[0]
            == "Failed to create item: No value or default value set and sync is disabled."
        )
