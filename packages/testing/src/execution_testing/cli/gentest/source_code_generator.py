"""
Pytest source code generator.

This module maps a test provider instance to pytest source code.
"""

import subprocess
import sys
from pathlib import Path

import jinja2

from execution_testing.config import AppConfig

from .test_context_providers import Provider

template_loader = jinja2.PackageLoader("execution_testing.cli.gentest")
template_env = jinja2.Environment(
    loader=template_loader, keep_trailing_newline=True
)

# This filter maps python objects to string
template_env.filters["stringify"] = lambda value: repr(value)


# generates a formatted pytest source code by writing provided data on a given
# template.
def get_test_source(provider: Provider, template_path: str) -> str:
    """
    Generate formatted pytest source code by rendering a template with provided
    data.

    This function uses the given template path to create a pytest-compatible
    source code string. It retrieves context data from the specified provider
    and applies it to the template.

    Args:
      provider: An object that provides the necessary context for rendering
                the template.
      template_path (str): The path to the Jinja2 template file
                           used to generate tests.

    Returns:
        str: The formatted pytest source code.

    """
    template = template_env.get_template(template_path)
    rendered_template = template.render(provider.get_context())
    # return rendered_template
    return format_code(rendered_template)


def format_code(code: str) -> str:
    """
    Format the provided Python code using the ruff formatter.

    The code is passed to ruff on stdin and read back from stdout. A temporary
    file would not work on Windows, where a file that is still open cannot be
    reopened by name.

    Args:
      code (str): The Python code to be formatted.

    Returns:
        str: The formatted Python code.

    """
    # Get the path to the formatter executable in the virtual environment
    if sys.platform.startswith("win"):
        formatter_path = Path(sys.prefix) / "Scripts" / "ruff.exe"
    else:
        formatter_path = Path(sys.prefix) / "bin" / "ruff"

    # Call ruff to format the code
    config_path = AppConfig().ROOT_DIR.parent / "pyproject.toml"

    try:
        result = subprocess.run(
            [
                str(formatter_path),
                "format",
                "--config",
                str(config_path),
                "--stdin-filename",
                "generated_test.py",
                "-",
            ],
            input=code,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"Could not run the 'ruff' formatter at '{formatter_path}'. "
            f"gentest requires 'ruff' to format generated tests; ensure "
            f"the development environment is installed, e.g. with "
            f"'uv sync'."
        ) from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Error formatting code using formatter '{formatter_path}': "
            f"returncode={e.returncode}, stdout={e.stdout!r}, "
            f"stderr={e.stderr!r}"
        ) from e

    # Return the formatted source code
    return result.stdout
