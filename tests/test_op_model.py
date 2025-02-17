import pytest


@pytest.mark.parametrize("model_builder", [{"cleanup": True}], indirect=True)
def test_create_item(model_builder):
    for op_model in model_builder:
        op_model.create()
        secret = op_model.token._resolve()
        assert secret is not None


@pytest.mark.parametrize(
    "model_builder", [{"create": True, "cleanup": True}], indirect=True
)
def test_get_item(model_builder):
    for op_model in model_builder:
        op_model.resolve_all()
        assert op_model.token.value is not None
        assert op_model.url.value is not None
        assert op_model.username.value is not None


@pytest.mark.parametrize(
    "model_builder", [{"create": True, "cleanup": True}], indirect=True
)
def test_update_item(model_builder):
    for op_model in model_builder:
        new_value = "new_value"
        op_model.update_existing_fields({"username": new_value})
        op_model.resolve_all()
        assert op_model.username.value == new_value


@pytest.mark.parametrize("model_builder", [{"create": True}], indirect=True)
def test_archive_item(model_builder):
    for op_model in model_builder:
        op_model.archive()
        try:
            op_model.get()
            assert False  # This should not be reached
        except Exception as e:
            assert e.args[0] == "item is not in an active state"


@pytest.mark.parametrize("model_builder", [{"create": True}], indirect=True)
def test_delete_item(model_builder):
    for op_model in model_builder:
        op_model.delete()
