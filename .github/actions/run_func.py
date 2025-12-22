import sys
import json
import importlib.util
from pathlib import Path


def main():
    """
    script_path             brands/lememe/start_end_discounts.py
    func_name               start_end_discounts_2025_new_year
    args in json string     {"testrun": false, "start_or_end": "start"}
    """

    script_path = sys.argv[1]
    func_name = sys.argv[2]
    raw_params = sys.argv[3]
    params = json.loads(raw_params)

    module_name = Path(script_path).stem
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None:
        raise ValueError(f"Error: Could not find script at {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = (
        module  # Add to sys.modules so imports within the script work correctly
    )

    spec.loader.exec_module(module)
    resolved_func = getattr(module, func_name)

    resolved_func(**params)


if __name__ == "__main__":
    main()
