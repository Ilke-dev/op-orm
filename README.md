# 1Password ORM

A robust Python ORM for managing 1Password secrets with elegance. This library provides a secure, type-safe interface for interacting with 1Password items using familiar ORM patterns.

## 🌟 Key Features

- 🔐 Type-safe field definitions with built-in validation
- 🔄 Automated password generation and management
- 🎯 Clean, Pythonic model-based structure
- 🔑 Comprehensive support for all 1Password item types
- 🚀 Easy CRUD operations with version tracking
- 🔒 Secure integration with 1Password Connect
- 📦 Kubernetes secrets generation

## 📦 Installation

```bash
pip install op-orm
```

## 🔧 Quick Start

1. Set up environment variables:
```bash
export OP_CONNECT_TOKEN="your-1password-connect-token"
export OP_INTEGRATION_NAME="your-app-name"
```

2. Define your models:
```python
from op_orm.types import OpModelDatabase, StringField, PasswordField, UrlField

class PostgresDatabase(OpModelDatabase):
    title = "production-postgres"
    sections = ["connection", "auth"]
    
    host = StringField(section_id="connection", value="db.example.com")
    port = StringField(section_id="connection", value="5432")
    database = StringField(section_id="connection", value="myapp")
    username = StringField(section_id="auth", value="admin")
    password = PasswordField(section_id="auth")
```

3. Use your models:
```python
# Create and save credentials
db = PostgresDatabase()
db.password.generate_password()  # Generates secure random password
db.create()

# Update credentials
db.update_existing_fields({
    "username": "new_admin",
    "host": "new-db.example.com"
})

# Retrieve credentials
db.resolve_all()  # Fetches latest values from 1Password
print(f"Connection string: postgresql://{db.username.value}@{db.host.value}")
```

## 🏗️ Model Types

The library provides specialized models for common credential types:

- `OpModelServer` - Server credentials
- `OpModelDatabase` - Database connections
- `OpModelAPIKey` - API credentials
- `OpModelLogin` - Login credentials
- `OpModelSSHKey` - SSH keys
- `OpModelSecureNote` - Secure notes
- And more...

## 🔐 Field Types

Available field types for model attributes:

- `StringField` - Text values (optionally concealed)
- `PasswordField` - Auto-generating password fields
- `UrlField` - URL fields with validation

## 🚀 Advanced Usage

### Kubernetes Secret Generation

Generate Kubernetes secrets from your models:

```python
from op_orm.deployment_generator import generate_deployment_files

# Generate YAML for k8s secrets
deployment = generate_deployment_files([PostgresDatabase])
with open("k8s-secrets.yaml", "w") as f:
    f.write(deployment)
```

### Custom Field Validation

Add custom validation to your fields:

```python
class APICredentials(OpModelAPIKey):
    api_key = StringField(section_id="api", concealed=True)
    environment = StringField(section_id="api")
    
    def validate(self):
        if self.environment.value not in ["prod", "staging", "dev"]:
            raise ValueError("Invalid environment")
```

## Generate Kubernetes Secrets from OpModel

The `generate_deployments` command-line tool streamlines the integration between your Python OpModel classes and the 1Password Kubernetes Operator (connect). It automates the process of creating Kubernetes secret definitions by scanning your Python files for OpModel subclasses and converting them into the appropriate YAML format required by the 1Password k8s operator.

### Usage
- Use `-p` flag to preview the generated YAML in terminal
- Use `-o` flag followed by a filename to save the deployments
- Simply point to your Python file containing OpModel definitions

This tool helps bridge the gap between your application's secrets management and the 1Password Kubernetes Operator, ensuring smooth deployment of your secrets in a Kubernetes environment.
```shell
usage: generate_deployments [-h] [-p] [-o OUTPUT] file_path

Collect OpModel subclasses from a Python file.

positional arguments:
  file_path             Path to the Python file.

options:
  -h, --help            show this help message and exit
  -p, --print           print to stdout
  -o OUTPUT, --output OUTPUT
                        File to save the k8s secret deployments.
```

Example usage:
```shell 
generate_deployments examples/example_models.py -p -o secrets.yaml 
```
This will output the 1password k8s items in a single deployment file 

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the GPL3 License - see the [LICENSE](LICENSE) file for details.