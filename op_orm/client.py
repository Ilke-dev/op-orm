from onepassword import ItemCreateParams, Secrets, ItemOverview
from onepassword.client import Client
from op_orm.exceptions import OpOrmException
import asyncio
import os


class OpClient:
    """Client for interacting with 1Password Connect API.

    Handles authentication and provides methods for managing items.
    """

    def __init__(self, integration_name: str = "op-orm") -> None:
        """Initialize the client.

        Args:
            integration_name: Name to identify this integration to 1Password
        """
        self._client = None
        self._vault_id = None
        self._vault_name = None
        self._integration_name = integration_name

    @property
    def client(self) -> Client:
        if not self._client:
            self._client = asyncio.run(
                Client.authenticate(
                    auth=os.getenv("OP_CONNECT_TOKEN"),
                    integration_name=self._integration_name,
                    integration_version="0.1.0",
                )
            )
        return self._client

    @property
    def vault_id(self) -> str:
        if not self._vault_id:
            vaults = asyncio.run(self.client.vaults.list_all())
            vault = vaults.obj[0]  # Get first vault only
            self._vault_id = vault.id
            self._vault_name = vault.title
        return self._vault_id

    @property
    def vault_name(self) -> str:
        if not self._vault_name:
            vaults = asyncio.run(self.client.vaults.list_all())
            self._vault_id = vaults.obj[0].id
            self._vault_name = vaults.obj[0].name
        return self._vault_name

    @property
    def items(self) -> list[ItemOverview]:
        item_iterator = asyncio.run(self.client.items.list_all(self._vault_id))
        return item_iterator.obj

    def create_all(self, model_classes: list) -> None:
        """Create all items from a list of model classes.

        Args:
            model_classes: List of OpModel classes to create
        """
        [model_class.create() for model_class in model_classes]

    def delete_all(self, model_classes: list):
        [model_class.delete() for model_class in model_classes]

    def archive_all(self, model_classes: list):
        [model_class.archive() for model_class in model_classes]

    def get_item_uuid(self, title: str, exception: bool = True) -> str | None:
        """Get UUID of an item by its title.

        Args:
            title: Title of the item to find
            exception: Whether to raise exceptions on errors

        Returns:
            Item UUID if found, None otherwise

        Raises:
            OpOrmException: If exception=True and item lookup fails
        """
        try:
            items = [item.id for item in self.items if item.title == title]
            return items[0] if items else None
        except Exception as e:
            if exception:
                raise OpOrmException(f"Failed to get item UUID: {e}")
            return None

    def get_item(self, title: str):
        item_uuid = self.get_item_uuid(title)
        if item_uuid:
            return asyncio.run(self.client.items.get(self._vault_id, item_uuid))

    def archive_item(self, title: str):
        item_uuid = self.get_item_uuid(title)
        if item_uuid:
            return asyncio.run(self.client.items.archive(self._vault_id, item_uuid))

    def delete_item(self, title: str):
        item_uuid = self.get_item_uuid(title)
        if item_uuid:
            return asyncio.run(self.client.items.delete(self._vault_id, item_uuid))

    def create_item(self, item_params: ItemCreateParams):
        return asyncio.run(self.client.items.create(item_params))

    def update_item(self, item_params: ItemCreateParams):
        return asyncio.run(self.client.items.put(item_params))

    def validate_secret_reference(self, reference: str) -> bool:
        """Validate a 1Password secret reference string format.

        Args:
            reference: Reference string to validate

        Returns:
            True if valid

        Raises:
            ValueError: If reference format is invalid
        """
        parts = reference.split("/")
        if len(parts) < 4 or not reference.startswith("op://"):
            raise ValueError(f"Invalid secret reference format: {reference}")
        return True

    def resolve_secret(self, secret_reference: str) -> str:
        try:
            return asyncio.run(self.client.secrets.resolve(secret_reference))
        except Exception as e:
            raise OpOrmException(f"Failed to resolve secret: {e}")
