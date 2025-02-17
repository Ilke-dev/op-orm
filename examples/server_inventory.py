from op_orm.types import OpModelServer, StringField, PasswordField
from dataclasses import dataclass
from typing import List


class ServerCredentials(OpModelServer):
    sections = ["network", "access", "metadata"]

    hostname = StringField(section_id="network")
    ip_address = StringField(section_id="network")
    ssh_port = StringField(section_id="network", value="22")

    username = StringField(section_id="access")
    password = PasswordField(section_id="access")
    ssh_key = StringField(section_id="access", concealed=True)

    environment = StringField(section_id="metadata")
    role = StringField(section_id="metadata")


@dataclass
class ServerInfo:
    hostname: str
    ip: str
    environment: str
    role: str


def provision_servers(servers: List[ServerInfo]):
    credentials = []
    for server in servers:
        creds = ServerCredentials()
        creds.title = f"server-{server.hostname}"
        creds.hostname.value = server.hostname
        creds.ip_address.value = server.ip
        creds.environment.value = server.environment
        creds.role.value = server.role

        # Set up access credentials
        creds.username.value = "admin"
        creds.password.generate_password()

        creds.create()
        credentials.append(creds)
    return credentials


def main():
    # Example server inventory
    servers = [
        ServerInfo("web-01", "10.0.1.10", "prod", "web"),
        ServerInfo("web-02", "10.0.1.11", "prod", "web"),
        ServerInfo("db-01", "10.0.2.10", "prod", "database"),
    ]

    # Provision credentials for all servers
    credentials = provision_servers(servers)

    # Print inventory
    for creds in credentials:
        print(f"\nServer: {creds.hostname.value}")
        print(f"IP: {creds.ip_address.value}")
        print(f"Role: {creds.role.value}")
        print(f"Username: {creds.username.value}")
        print(f"Password: {creds.password.value}")


if __name__ == "__main__":
    main()
