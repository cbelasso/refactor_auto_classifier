"""
Generic Prompt Management System

Works for all stages with a unified YAML structure.
Generate Python prompt functions from YAML configuration files.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from ruamel.yaml import YAML

# ============================================================
# Generic YAML → Prompt Builder
# ============================================================


def build_prompt_from_yaml(yaml_path: str | Path) -> str:
    """
    Build prompt from generic YAML structure.
    Works for any stage (1, 2, 3, 4).

    Returns:
        Complete prompt template string
    """
    yaml = YAML()

    with open(yaml_path, "r") as f:
        data = yaml.load(f)

    metadata = data.get("prompt_metadata", {})
    stage = metadata.get("stage", 1)
    focus = metadata.get("focus", "")
    task = metadata.get("task", "Classification")

    # Build header
    header_parts = [f"You are an expert conference feedback analyzer. {task}."]
    if focus:
        header_parts.append(f"\nFOCUS: {focus}")

    header = "\n".join(header_parts)

    # Build labels section (categories, sub-categories, elements, or attributes)
    labels_section = []
    labels_title = data.get("labels_title", "LABELS TO IDENTIFY")

    for label in data["labels"]:
        labels_section.append(f"**{label['name']}**")
        if label.get("description"):
            labels_section.append(label["description"])

        # Add context items if present (e.g., elements under sub-category)
        if label.get("context_items"):
            labels_section.append("Elements include:")
            for item in label["context_items"]:
                labels_section.append(f"- {item}")

        labels_section.append("")  # Blank line

    labels_text = "\n".join(labels_section).strip()

    # Build rules section
    rules_section = []
    for i, rule in enumerate(data["rules"], 1):
        rules_section.append(f"{i}. {rule}")

    rules_text = "\n".join(rules_section)

    # Build examples section
    examples_section = []
    label_field = data.get(
        "label_field", "category"
    )  # category, sub_category, element, or attribute

    for example in data["examples"]:
        comment = example["comment"]
        classifications = example["classifications"]

        if not classifications:
            # Empty classification
            example_text = f'Comment: "{comment}"\n{{"classifications": []}}'
        else:
            # Build classifications JSON
            classification_jsons = []
            for cls in classifications:
                cls_json = (
                    f'{{"excerpt": "{cls["excerpt"]}", '
                    f'"reasoning": "{cls["reasoning"]}", '
                    f'"{label_field}": "{cls[label_field]}", '
                    f'"sentiment": "{cls["sentiment"]}"}}'
                )
                classification_jsons.append(cls_json)

            classifications_str = ", ".join(classification_jsons)
            example_text = (
                f'Comment: "{comment}"\n{{"classifications": [{classifications_str}]}}'
            )

        examples_section.append(example_text)

    examples_text = "\n\n".join(examples_section)

    # Build complete prompt template
    prompt_template = f"""{header}

COMMENT TO ANALYZE:
__COMMENT_PLACEHOLDER__

---

{labels_title}:

{labels_text}

---

CLASSIFICATION RULES:

{rules_text}

---

EXAMPLES:

{examples_text}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""

    return prompt_template


def generate_python_function(
    yaml_path: str | Path,
    output_path: str | Path,
    function_name: str,
) -> Path:
    """
    Generate a Python file with the prompt function.

    Args:
        yaml_path: Path to YAML config
        output_path: Where to save the .py file
        function_name: Name of the generated function

    Returns:
        Path to generated Python file
    """
    yaml_path = Path(yaml_path)
    output_path = Path(output_path)

    # Load YAML to get metadata
    yaml = YAML()
    with open(yaml_path, "r") as f:
        data = yaml.load(f)

    metadata = data.get("prompt_metadata", {})
    stage = metadata.get("stage", 1)
    focus = metadata.get("focus", "")

    # Build prompt template
    prompt_template = build_prompt_from_yaml(yaml_path)

    # Create Python file
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        f.write(f'"""Generated Prompt - Stage {stage}')
        if focus:
            f.write(f": {focus}")
        f.write('"""\n\n')

        # Determine function signature based on stage
        if stage == 1:
            f.write(f"def {function_name}(comment: str) -> str:\n")
        elif stage == 2:
            f.write(f"def {function_name}(comment: str, category: str) -> str:\n")
        elif stage == 3:
            f.write(
                f"def {function_name}(comment: str, category: str, sub_category: str) -> str:\n"
            )
        elif stage == 4:
            f.write(
                f"def {function_name}(comment: str, category: str, sub_category: str, element: str) -> str:\n"
            )
        else:
            f.write(f"def {function_name}(comment: str) -> str:\n")

        f.write(
            '    return f"""'
            + prompt_template.replace("__COMMENT_PLACEHOLDER__", "{comment}")
            + '"""\n'
        )

    print(f"✓ Generated: {output_path}")
    return output_path


def batch_generate_stage(stage_dir: str | Path, output_dir: str | Path) -> List[Path]:
    """
    Generate all prompts for a given stage directory.

    Args:
        stage_dir: Directory containing YAML files (e.g., prompt_templates/stage_2/)
        output_dir: Where to save generated Python files

    Returns:
        List of generated file paths
    """
    stage_dir = Path(stage_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    yaml_files = list(stage_dir.glob("*.yaml"))
    generated_files = []

    print(f"\n{'=' * 60}")
    print(f"GENERATING PROMPTS FROM: {stage_dir}")
    print(f"{'=' * 60}\n")

    for yaml_file in yaml_files:
        # Create function name from filename
        base_name = yaml_file.stem
        function_name = f"{base_name}_prompt"

        # Generate output filename
        output_file = output_dir / f"{base_name}_prompt.py"

        generate_python_function(yaml_file, output_file, function_name)
        generated_files.append(output_file)

    print(f"\n✓ Generated {len(generated_files)} prompt files")
    return generated_files


def batch_generate_all_stages(
    templates_dir: str | Path,
    output_dir: str | Path,
) -> Dict[str, List[Path]]:
    """
    Generate all prompts for all stages.

    Args:
        templates_dir: Root directory with stage_1/, stage_2/, etc.
        output_dir: Where to save all generated files

    Returns:
        Dict mapping stage name to list of generated files
    """
    templates_dir = Path(templates_dir)
    output_dir = Path(output_dir)

    results = {}

    # Find all stage directories
    stage_dirs = sorted(
        [d for d in templates_dir.iterdir() if d.is_dir() and d.name.startswith("stage_")]
    )

    for stage_dir in stage_dirs:
        stage_name = stage_dir.name
        stage_output_dir = output_dir / stage_name

        generated = batch_generate_stage(stage_dir, stage_output_dir)
        results[stage_name] = generated

    return results


# ============================================================
# Validation
# ============================================================


def validate_prompt_yaml(yaml_path: str | Path) -> List[str]:
    """
    Validate prompt YAML file.

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    try:
        yaml = YAML()
        with open(yaml_path, "r") as f:
            data = yaml.load(f)
    except Exception as e:
        errors.append(f"Failed to parse YAML: {e}")
        return errors

    # Check required keys
    required_keys = ["labels", "rules", "examples"]
    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        errors.append(f"Missing required keys: {missing_keys}")
        return errors

    # Validate labels
    if not isinstance(data["labels"], list) or len(data["labels"]) == 0:
        errors.append("'labels' must be a non-empty list")
    else:
        for i, label in enumerate(data["labels"]):
            if "name" not in label:
                errors.append(f"Label {i} missing 'name' field")

    # Validate rules
    if not isinstance(data["rules"], list) or len(data["rules"]) == 0:
        errors.append("'rules' must be a non-empty list")

    # Validate examples
    if not isinstance(data["examples"], list) or len(data["examples"]) == 0:
        errors.append("'examples' must be a non-empty list")
    else:
        valid_sentiments = {"positive", "negative", "neutral", "mixed"}
        label_field = data.get("label_field", "category")

        for i, example in enumerate(data["examples"]):
            if "comment" not in example:
                errors.append(f"Example {i} missing 'comment' field")
            if "classifications" not in example:
                errors.append(f"Example {i} missing 'classifications' field")
            else:
                for j, cls in enumerate(example["classifications"]):
                    required_fields = ["excerpt", "reasoning", label_field, "sentiment"]
                    for field in required_fields:
                        if field not in cls:
                            errors.append(f"Example {i}, classification {j} missing '{field}'")

                    if "sentiment" in cls and cls["sentiment"] not in valid_sentiments:
                        errors.append(
                            f"Example {i}, classification {j} has invalid sentiment: '{cls['sentiment']}'"
                        )

    return errors
