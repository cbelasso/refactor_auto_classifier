"""
Runtime Prompt Loader

Loads prompts directly from YAML files at runtime.
Automatically determines file structure from hierarchy schema.
"""

from pathlib import Path
from typing import Dict, Optional

from ruamel.yaml import YAML

from classifier.utils import HierarchyNavigator


class PromptLoader:
    """Load and build prompts from YAML at runtime with dynamic file resolution."""

    def __init__(self, templates_dir: str | Path, hierarchy_path: str | Path):
        """
        Initialize prompt loader.

        Args:
            templates_dir: Root directory containing stage_1/, stage_2/, etc.
            hierarchy_path: Path to hierarchy JSON schema
        """
        self.templates_dir = Path(templates_dir)
        self.yaml = YAML()
        self.navigator = HierarchyNavigator(hierarchy_path)
        self._cache: Dict[str, str] = {}

    @staticmethod
    def _label_to_filename(label: str) -> str:
        """
        Convert label to standardized filename.

        Examples:
            "Products & Services" -> "products_and_services.yaml"
            "Food/Beverages" -> "food_beverages.yaml"
            "Location (City)" -> "location_city.yaml"
            "Wi-Fi" -> "wi_fi.yaml"
        """
        filename = (
            label.lower()
            .replace("/", "_")  # Food/Beverages → food_beverages
            .replace(" & ", "_and_")  # Content & Learning → content_and_learning
            .replace("&", "_and_")  # R&D → r_and_d
            .replace("-", "_")  # Wi-Fi → wi_fi
            .replace(" ", "_")  # ADD THIS! All spaces to underscores
            .replace("(", "")  # Remove opening parens
            .replace(")", "")  # Remove closing parens
        )
        return f"{filename}.yaml"

    def _build_prompt_from_data(
        self, data: dict, comment_placeholder: str = "__COMMENT_PLACEHOLDER__"
    ) -> str:
        """Build prompt string from YAML data."""
        metadata = data.get("prompt_metadata", {})

        # Build header
        system_prompt = data.get(
            "system_prompt", "You are an expert conference feedback analyzer."
        )
        task_description = data.get("task_description", "Classification")
        custom_instructions = data.get("custom_instructions", "")

        header_parts = [system_prompt, task_description]
        if custom_instructions:
            header_parts.append(custom_instructions)

        header = " ".join(header_parts)

        # Build labels section
        labels_section = []
        labels_title = data.get("labels_title", "LABELS TO IDENTIFY")

        for label in data["labels"]:
            labels_section.append(f"**{label['name']}**")
            if label.get("description"):
                labels_section.append(label["description"])

            if label.get("context_items"):
                labels_section.append("Elements include:")
                for item in label["context_items"]:
                    labels_section.append(f"- {item}")

            labels_section.append("")

        labels_text = "\n".join(labels_section).strip()

        # Build rules section
        rules_section = []
        for i, rule in enumerate(data["rules"], 1):
            rules_section.append(f"{i}. {rule}")

        rules_text = "\n".join(rules_section)

        # Build examples section
        examples_section = []
        label_field = data.get("label_field", "category")

        for example in data["examples"]:
            comment = example["comment"]
            classifications = example["classifications"]

            if not classifications:
                example_text = f'Comment: "{comment}"\n{{"classifications": []}}'
            else:
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

        # Build complete prompt
        prompt_template = f"""{header}

COMMENT TO ANALYZE:
{comment_placeholder}

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

    def _is_yaml_ready(self, yaml_path: Path) -> bool:
        """Check if YAML is marked as ready."""
        if not yaml_path.exists():
            return False

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        # Default to True if 'ready' field is missing (backward compatible)
        return data.get("ready", True)

    def load_stage1_prompt(self, comment: str) -> str:
        """Load Stage 1 category prompt."""
        yaml_path = self.templates_dir / "stage_1" / "category_prompt.yaml"

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        template = self._build_prompt_from_data(data)
        return template.replace("__COMMENT_PLACEHOLDER__", comment)

    def load_stage2_prompt(self, comment: str, category: str) -> Optional[str]:
        """Load Stage 2 sub-category prompt for a specific category."""
        filename = self._label_to_filename(category)
        yaml_path = self.templates_dir / "stage_2" / filename

        if not self._is_yaml_ready(yaml_path):
            return None  # Skip - not ready yet

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        template = self._build_prompt_from_data(data)
        return template.replace("__COMMENT_PLACEHOLDER__", comment)

    def load_stage3_prompt(
        self, comment: str, category: str, sub_category: str
    ) -> Optional[str]:
        """Load Stage 3 element prompt for a specific sub-category."""
        filename = self._label_to_filename(sub_category)
        yaml_path = self.templates_dir / "stage_3" / filename

        if not self._is_yaml_ready(yaml_path):
            return None  # Skip - not ready yet

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        template = self._build_prompt_from_data(data)
        return template.replace("__COMMENT_PLACEHOLDER__", comment)

    def load_stage4_prompt(
        self, comment: str, category: str, sub_category: str, element: str
    ) -> Optional[str]:
        """Load Stage 4 attribute prompt for a specific element."""
        filename = self._label_to_filename(element)
        yaml_path = self.templates_dir / "stage_4" / filename

        if not self._is_yaml_ready(yaml_path):
            return None  # Skip - not ready yet

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        template = self._build_prompt_from_data(data)
        return template.replace("__COMMENT_PLACEHOLDER__", comment)

    def get_available_stages(self) -> list[int]:
        """Get list of available stages."""
        stages = []
        for i in range(1, 5):
            stage_dir = self.templates_dir / f"stage_{i}"
            if stage_dir.exists() and any(stage_dir.glob("*.yaml")):
                stages.append(i)
        return stages

    def list_required_yamls(self) -> dict:
        """
        List all YAML files that should exist based on hierarchy schema.
        Useful for checking what needs to be created.
        """
        required = {
            "stage_1": ["category_prompt.yaml"],
            "stage_2": [],
            "stage_3": [],
            "stage_4": [],
        }

        # Stage 2: One file per category
        for category in self.navigator.get_categories():
            filename = self._label_to_filename(category)
            required["stage_2"].append(filename)

        # Stage 3: One file per sub-category
        for category in self.navigator.get_categories():
            for subcategory in self.navigator.get_subcategories(category):
                filename = self._label_to_filename(subcategory)
                if filename not in required["stage_3"]:
                    required["stage_3"].append(filename)

        # Stage 4: One file per element
        for category in self.navigator.get_categories():
            for subcategory in self.navigator.get_subcategories(category):
                for element in self.navigator.get_elements(category, subcategory):
                    filename = self._label_to_filename(element)
                    if filename not in required["stage_4"]:
                        required["stage_4"].append(filename)

        return required
