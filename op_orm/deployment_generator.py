import sys
import importlib.util
import inspect
from pathlib import Path

from annotated_types import T
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


def b64encode_filter(value):
    if isinstance(value, str):
        return base64.b64encode(value.encode("utf-8")).decode("utf-8")
    return base64.b64encode(value).decode("utf-8")


def quote_filter(value):
    return f'"{value}"'


env.filters["b64encode"] = b64encode_filter
env.filters["quote"] = quote_filter


def import_module_from_path(file_path: str):
    """Dynamically import a Python module from a file path."""
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
    """Find all OpModel subclasses in the given module."""
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
    module = import_module_from_path(file_path)
    models = collect_model_classes(module)
    return models


def generate_deployment_files(models: list[type[OpModel]]):
    template = env.get_template("secret.yaml.j2")
    rendered_templates = []
    for orm_model in models:
        model = orm_model()
        rendered = template.render(fields=model.fields)
        rendered_templates.append(rendered)
    return "\n---\n".join(rendered_templates)


if __name__ == "__main__":

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
