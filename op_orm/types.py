from onepassword import ItemCategory, ItemFieldType
from op_orm.models import OpModel
from onepassword import (
    Secrets,
    PasswordRecipeRandom,
    PasswordRecipeRandomInner,
)
from op_orm.fields import ORMItemField


class OpModelAPIKey(OpModel):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.APICREDENTIALS


class OpModelDatabase(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.DATABASE


class OpModelPassword(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.PASSWORD


class OpModelServer(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.SERVER


class OpModelLogin(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.LOGIN


class OpModelSecureNote(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.SECURENOTE


class OpModelSoftwareLicense(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.SOFTWARELICENSE


class OpModelIdentity(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.IDENTITY


class OpModelEmail(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.EMAIL


class OpModelSSHKey(OpModel):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.category = ItemCategory.SSHKEY


class PasswordField(ORMItemField):
    def __init__(self, section_id: str = None, value: str = None):
        super().__init__(
            field_type=ItemFieldType.CONCEALED, section_id=section_id, value=value
        )

    def generate_password(self):
        password = Secrets.generate_password(
            PasswordRecipeRandom(
                parameters=PasswordRecipeRandomInner(
                    length=100,
                    includeDigits=True,
                    includeSymbols=True,
                )
            ),
        )
        self.value = password.password


class StringField(ORMItemField):
    def __init__(
        self, section_id: str = None, concealed: bool = False, value: str = None
    ):
        field_type = ItemFieldType.CONCEALED if concealed else ItemFieldType.TEXT
        super().__init__(field_type=field_type, section_id=section_id, value=value)


class UrlField(ORMItemField):
    def __init__(self, section_id: str = None, value: str = None):
        super().__init__(
            field_type=ItemFieldType.URL, section_id=section_id, value=value
        )
