import pytest
from op_orm.types import PasswordField, StringField, UrlField
from op_orm.types import (
    OpModelServer,
    OpModelDatabase,
    OpModelAPIKey,
    OpModelSSHKey,
    OpModelLogin,
    OpModelSecureNote,
    OpModelSoftwareLicense,
    OpModelIdentity,
    OpModelEmail,
    OpModelSSHKey,
    OpModelPassword,
)
from op_orm.models import OpModel

MODELS = [
    OpModelServer,
    OpModelDatabase,
    OpModelAPIKey,
    OpModelSSHKey,
    OpModelLogin,
    OpModelSecureNote,
    OpModelSoftwareLicense,
    OpModelIdentity,
    OpModelEmail,
    OpModelSSHKey,
    OpModelPassword,
]

import uuid
import time


def create_model(model_cls: type[OpModel], secret_name: str) -> OpModel:

    class TestSecrets(model_cls):
        title = secret_name
        sections = ["test1", "test2"]
        ip_address = StringField(value="10.13.3.7", section_id="test1")
        url = UrlField(value="https://example.com", section_id="test1")
        token = PasswordField(value="0000-0000-0000-0000", section_id="test2")
        username = StringField(value="Test", section_id="test2")
        password = PasswordField(value="secret", section_id="test2")

    return TestSecrets()


@pytest.fixture(scope="function")
@pytest.hookimpl(optionalhook=True)
def model_builder(request):
    params = request.param if hasattr(request, "param") else {}
    create = params.get("create", False)
    cleanup = params.get("cleanup", False)
    once = params.get("once", True)

    models: list[OpModel] = []
    for model_cls in MODELS:
        op_model = create_model(model_cls, uuid.uuid4().hex)
        models.append(op_model)
        if once:
            break

    if create:
        [op_model.create() for op_model in models]

    yield models

    if cleanup:
        [op_model.delete() for op_model in models]


class EmptyModel(OpModelLogin):
    title = "empty_model"
    sections = ["test"]


class TestModel(OpModelLogin):
    title = "nonexistent_model"
    sections = ["test"]
    username = StringField(section_id="test", value="test")
