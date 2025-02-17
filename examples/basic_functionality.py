from op_orm.types import (
    OpModelServer,
    StringField,
    PasswordField,
)


class Server(OpModelServer):
    title = "Server"
    sections = ["server"]
    ip_address = StringField(value="192.168.1.1", section_id="server")
    username = StringField(value="root", section_id="server")
    password = PasswordField(section_id="server")


server = Server()
server.password.generate_password()
server.create()
server.update_existing_fields({"password": "new_password", "username": "blaa"})
server.delete()
