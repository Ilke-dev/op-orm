import sys
import importlib.util
import inspect
from pathlib import Path

from op_orm.models import OpModel
import argparse
from os import path
from jinja2 import Environment, PackageLoader, select_autoescape
import base64

templates_dir = path.dirname(path.abspath(__file__)) + "/templates"

env = Environment(
    loader=PackageLoader(
        package_name="op_orm", package_path=templates_dir, encoding="utf-8"
    ),
    autoescape=select_autoescape(),
)


def quote_filter(value):
    return f'"{value}"'


env.filters["quote"] = quote_filter


def import_module_from_path(file_path: str) -> object:
    """Dynamically import a Python module from a file path.

    Args:
        file_path: Path to the Python file to import

    Returns:
        Imported module object

    Raises:
        ImportError: If module cannot be loaded
    """
    path = Path(file_path).resolve()
    module_name = path.stem

    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {file_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def collect_model_classes(module) -> list[type[OpModel]]:
    """Find all OpModel subclasses in the given module.

    Args:
        module: Python module to inspect

    Returns:
        List of OpModel subclass types
    """
    models = []
    for name, obj in inspect.getmembers(module):
        if (
            inspect.isclass(obj)
            and issubclass(obj, OpModel)
            and obj != OpModel
            and not obj.__module__.startswith("op_orm")
        ):
            models.append(obj)
    return models


def get_user_model_classes(file_path: str) -> list[type[OpModel]]:
    """Load and collect OpModel classes from a Python file.

    Args:
        file_path: Path to the Python file containing model definitions

    Returns:
        List of OpModel subclass types
    """
    module = import_module_from_path(file_path)
    models = collect_model_classes(module)
    return models


def generate_deployment_files(models: list[type[OpModel]]) -> str:
    """Generate Kubernetes secret YAML from OpModel classes.

    Args:
        models: List of OpModel classes to generate secrets for

    Returns:
        String containing the generated YAML content
    """
    template = env.get_template("secret.yaml.j2")
    rendered_templates = []
    for orm_model in models:
        model = orm_model()
        rendered = template.render(fields=model.fields)
        rendered_templates.append(rendered)
    return "\n---\n".join(rendered_templates)


def run_cli_k8s_deployment_generator():
    parser = argparse.ArgumentParser(
        description="Collect OpModel subclasses from a Python file."
    )
    parser.add_argument(
        "file_path",
        help="Path to the Python file.",
        default="examples/example_models.py",
    )
    parser.add_argument(
        "-p", "--print", help="print to stdout", action="store_true", default=True
    )
    parser.add_argument(
        "-o",
        "--output",
        help="File to save the k8s secret deployments.",
        default="secrets.yaml",
    )

    args = parser.parse_args()

    models = get_user_model_classes(args.file_path)
    deployment_files = generate_deployment_files(models)

    if args.output:
        with open(args.output, "w") as f:
            f.write(deployment_files)

    if args.print:
        print(deployment_files)
