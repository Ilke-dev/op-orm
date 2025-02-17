from op_orm.types import OpModelAPIKey, StringField, PasswordField
from typing import List


class ServiceAccount(OpModelAPIKey):
    sections = ["metadata", "credentials"]

    service_name = StringField(section_id="metadata")
    environment = StringField(section_id="metadata")
    api_key = PasswordField(section_id="credentials")
    api_secret = PasswordField(section_id="credentials")


def create_service_accounts(environments: List[str], service_name: str):
    accounts = []
    for env in environments:
        account = ServiceAccount()
        account.title = f"{service_name}-{env}"
        account.service_name.value = service_name
        account.environment.value = env

        # Generate unique credentials for each environment
        account.api_key.generate_password()
        account.api_secret.generate_password()

        account.create()
        accounts.append(account)
    return accounts


def main():
    # Create service accounts for different environments
    environments = ["dev", "staging", "prod"]
    accounts = create_service_accounts(environments, "payment-service")

    # Demonstrate retrieving credentials
    for account in accounts:
        print(f"\nCredentials for {account.environment.value}:")
        print(f"API Key: {account.api_key.value}")
        print(f"API Secret: {account.api_secret.value}")


if __name__ == "__main__":
    main()
