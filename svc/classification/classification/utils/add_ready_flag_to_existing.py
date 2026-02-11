# add_ready_flag_to_existing.py
from pathlib import Path

from ruamel.yaml import YAML

yaml = YAML()
yaml.default_flow_style = False
yaml.width = 4096

for yaml_file in Path("./prompt_templates").rglob("*.yaml"):
    with open(yaml_file, "r") as f:
        data = yaml.load(f)

    if "ready" not in data:
        data = {"ready": True, **data}  # Add to beginning

        with open(yaml_file, "w") as f:
            yaml.dump(data, f)

        print(f"✓ Added ready: true to {yaml_file.name}")
