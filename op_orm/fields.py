from onepassword import ItemField, ItemFieldType
from op_orm.exceptions import OpOrmException
import time


class ORMItemField:
    """Base field class for 1Password item fields.

    Handles field value management and synchronization with 1Password.
    """

    def __init__(
        self, field_type: ItemFieldType, section_id: str = None, value: str = None
    ) -> None:
        """Initialize a new field.

        Args:
            field_type: Type of the 1Password field
            section_id: Optional section identifier
            value: Optional initial value
        """
        self.field_type = field_type
        self.section_id = section_id
        self._value = value
        self._sync = False
        self._last_sync = None
        self._client = None
        self._vault_id = None
        self._vault_name = None
        self.title = None
        self.field_name = None
        self._default_value = None

    @property
    def vault_name(self) -> str:
        if self._vault_name is None:
            self._vault_name = self._client.vault_name
        return self._vault_name

    @property
    def id(self) -> str:
        if self._client is None:
            raise OpOrmException("Client is not set")
        if self.title is None:
            raise OpOrmException("Title is not set")
        return self._client.get_item_uuid(self.title)

    @property
    def default_value(self) -> str | None:
        return self._default_value

    @default_value.setter
    def default_value(self, value: str):
        self._default_value = value
        self._sync = False

    @property
    def value(self) -> str | None:
        # print("Getter for value is being called")  # Add this debug line
        if self._sync:
            if not self._value or (
                self._last_sync and (time.time() - float(self._last_sync)) > 5
            ):
                self._value = self._resolve()
                self._last_sync = str(time.time())
            return self._value
        elif not self._value:
            if self._default_value:
                return self._default_value
            else:
                raise OpOrmException(
                    "No value or default value set and sync is disabled."
                )
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value
        self._sync = False

    def to_item_field(self) -> ItemField:
        """Convert to a 1Password ItemField.

        Returns:
            Configured ItemField instance
        """
        return ItemField(
            id=self.field_name,
            title=self.field_name,
            field_type=self.field_type,
            value=self._value if self._value is not None else "",
            section_id=self.section_id,
        )

    def _resolve(self) -> str:
        """Resolve the field value from 1Password.

        Returns:
            Resolved field value

        Raises:
            OpOrmException: If client is not set
        """
        if self._client is None:
            raise OpOrmException("Client is not set")

        return self._client.resolve_secret(self._reference)

    @property
    def _reference(self) -> str:
        """Generate the 1Password reference string for this field.

        Returns:
            Reference string in format op://vault/item/[section/]field

        Raises:
            OpOrmException: If required properties are not set
        """
        if self.vault_name and self.field_name and self.title:
            if self.section_id:
                reference = f"op://{self.vault_name}/{self.title}/{self.section_id}/{self.field_name}"
            else:
                reference = f"op://{self.vault_name}/{self.title}/{self.field_name}"

            try:
                self._client.validate_secret_reference(reference)
            except Exception as e:
                raise OpOrmException(f"Invalid secret reference: {reference}") from e
            return reference
        raise OpOrmException(
            "Vault name, Item title, and Field ID must be set to create a reference."
        )

    def __repr__(self):
        return f"<ORMItemField(id={self.id}, title={self.title}, section={self.section_id} ,value={self.value})>"

    def __getitem__(self, key):
        if key == "id":
            return self.id
        elif key == "value":
            return self.value
        elif key == "title":
            return self.title
        elif key == "section_id":
            return self.section_id
        else:
            raise KeyError(f"Key {key} not found")
