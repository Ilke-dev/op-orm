from op_orm.types import (
    OpModelServer,
    OpModelDatabase,
    OpModelAPIKey,
    OpModelSSHKey,
    StringField,
    PasswordField,
    UrlField,
)


class Server(OpModelServer):
    title = "Server"
    sections = ["server"]
    ip_address = StringField(value="192.168.1.1", section_id="server")
    username = StringField(value="root", section_id="server")
    password = PasswordField(section_id="server")


class Database(OpModelDatabase):
    title = "Database"
    sections = ["database"]
    username = StringField(value="root", section_id="database")
    ip_address = StringField(value="192.168.1.1", section_id="database")
    password = PasswordField(section_id="database")


class APIKey(OpModelAPIKey):
    title = "API Key"
    sections = ["api"]
    key = StringField(value="1234567890", section_id="api")
    url = UrlField(value="https://example.com/api", section_id="api")


class SSHKey(OpModelSSHKey):
    title = "SSH Key"
    sections = ["ssh"]
    private_key = StringField(section_id="ssh")
    public_key = StringField(section_id="ssh")
