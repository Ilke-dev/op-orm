from op_orm.types import OpModelDatabase, StringField, PasswordField, UrlField


class PostgresCredentials(OpModelDatabase):
    title = "my-postgres-db"
    sections = ["connection", "auth"]

    # Connection details
    host = StringField(section_id="connection", value="db.example.com")
    port = StringField(section_id="connection", value="5432")
    database = StringField(section_id="connection", value="myapp")
    connection_url = UrlField(section_id="connection")

    # Auth details
    username = StringField(section_id="auth", value="admin")
    password = PasswordField(section_id="auth")


def main():
    # Create database credentials with auto-generated password
    db = PostgresCredentials()
    db.password.generate_password()  # Generate secure random password

    # Build connection URL from components
    db.connection_url.value = f"postgresql://{db.username.value}:{db.password.value}@{db.host.value}:{db.port.value}/{db.database.value}"

    # Save to 1Password
    db.create()
    print(f"Created database credentials with ID: {db.id}")


if __name__ == "__main__":
    main()
