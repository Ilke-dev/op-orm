from onepassword import ItemCategory, ItemSection, ItemCreateParams, Item
from op_orm.exceptions import OpOrmException
from op_orm.fields import ORMItemField
from typing import Any
from op_orm.client import OpClient
import os


class OpModel:
    """Base class for 1Password item models.

    Provides core functionality for creating, updating, and managing 1Password items.
    """

    __client__: OpClient | None = None
    title: str
    category: ItemCategory
    sections: list[str]
    id: str | None = None
    vault_id: str | None = None
    fields: list[ORMItemField] = []

    def __init__(self, **data: dict[str, Any]) -> None:
        """Initialize a new 1Password item model.

        Args:
            **data: Dictionary of model attributes
        """
        self.data = data
        self.vault_id = None
        self.fields = {}

        if not hasattr(self, "title"):
            self.title = self.__class__.__name__

        self.vault_id = self.client.vault_id
        self._retrieve_orm_fields()

        if len(self.fields) == 0:
            raise OpOrmException("No fields found in the model")

    def _retrieve_orm_fields(self) -> None:
        """Retrieve and initialize ORM fields from class definition.

        Creates instance-level copies of class-level field definitions.
        """
        # Get all the fields defined in the class
        self._orm_fields = {
            key: val
            for key, val in self.__class__.__dict__.items()
            if isinstance(val, ORMItemField)
        }

        # Create instance-level field copies
        for field_name, field_value in self._orm_fields.items():
            new_field = field_value.__class__(
                # field_type=field_value.field_type,
                # section_id=field_value.section_id,
                value=field_value._value,
            )
            new_field._vault_id = self.vault_id
            new_field._client = self.client
            new_field.title = self.title
            new_field.field_name = field_name
            new_field.field_type = field_value.field_type
            new_field.section_id = field_value.section_id
            self.fields[field_name] = new_field
            setattr(self, field_name, new_field)

    @property
    def client(self) -> OpClient:
        """
        This property ensures that the client is created only once and is reused over all instances of the class.

        Returns:
            OpClient: one password wrapper over the official sdk
        """
        if self.__client__ is None:
            client = OpClient(integration_name=os.environ["OP_INTEGRATION_NAME"])
            OpModel.__client__ = client
            self.__client__ = client
        return self.__client__

    def get_item_create_params(self) -> ItemCreateParams:
        """Generate parameters for creating a new 1Password item.

        Returns:
            ItemCreateParams object with configured item properties
        """
        return ItemCreateParams(
            title=self.title,
            category=self.category,
            vault_id=self.vault_id,
            fields=[field.to_item_field() for field in self.fields.values()],
            sections=[
                ItemSection(id=section, title=section) for section in self.sections
            ],
            tags=["op-orm-managed"],
            websites=[],
        )

    def create(self) -> Item:
        """Create a new item in 1Password.

        Returns:
            The created Item object

        Raises:
            OpOrmException: If item already exists or required fields are missing
        """
        try:
            existing_item = self.client.get_item_uuid(self.title)
            if existing_item:
                raise OpOrmException(f"Item with title {self.title} already exists")

            if any([field.value is None for field in self.fields.values()]):
                raise OpOrmException(
                    "All fields must have a value before creating the item"
                )

            item_params = self.get_item_create_params()
            return self.client.create_item(item_params)
        except Exception as e:
            raise OpOrmException(f"Failed to create item: {e}")

    def resolve_all(self) -> None:
        """Resolve and update all field values from 1Password."""
        values = self.get()
        for field_name, field in self.fields.items():
            field_value = [
                field.value for field in values.fields if field.id == field_name
            ][0]
            field.value = field_value

    def update_existing_fields(self, field_updates: dict[str, str]) -> None:
        """Update values of existing fields in 1Password.

        Args:
            field_updates: Dictionary mapping field names to new values

        Raises:
            OpOrmException: If the item doesn't exist
        """
        item = self.get()
        if not item:
            raise OpOrmException(f"Can't update item: {self.title} does not exist")

        existing_field_ids = [field.id for field in item.fields]

        # Update existing fields and collect new ones
        for name, value in field_updates.items():
            if name in existing_field_ids:
                # Update existing field
                [field for field in item.fields if field.id == name][0].value = value

        self.client.update_item(item)

    def get(self) -> Item:
        """Retrieve the item from 1Password.

        Returns:
            Item object from 1Password
        """
        return self.client.get_item(self.title)

    def archive(self) -> None:
        """Archive the item in 1Password."""
        self.client.archive_item(self.title)

    def delete(self) -> None:
        """Delete the item from 1Password."""
        self.client.delete_item(self.title)

    def restore(self, name: str):
        """
        As per the official sdk, the restore method is not implemented yet.
        """
        raise NotImplementedError(
            "There is no support from onepassword-sdk to restore an item after it's been archived"
        )

    def save(self) -> Item:
        """Create the item in 1Password.

        Returns:
            The created Item object
        """
        self.create()
