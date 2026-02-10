"""
Runtime Prompt Loader

Loads prompts directly from YAML files at runtime.
No Python code generation needed for production use.
"""

from pathlib import Path
from typing import Dict, Optional

from ruamel.yaml import YAML


class PromptLoader:
    """Load and build prompts from YAML at runtime."""

    def __init__(self, templates_dir: str | Path):
        """
        Initialize prompt loader.

        Args:
            templates_dir: Root directory containing stage_1/, stage_2/, etc.
        """
        self.templates_dir = Path(templates_dir)
        self.yaml = YAML()
        self._cache: Dict[str, str] = {}

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

    def load_stage1_prompt(self, comment: str) -> str:
        """Load Stage 1 category prompt."""
        yaml_path = self.templates_dir / "stage_1" / "category_prompt.yaml"

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        template = self._build_prompt_from_data(data)
        return template.replace("__COMMENT_PLACEHOLDER__", comment)

    def load_stage2_prompt(self, comment: str, category: str) -> str:
        """Load Stage 2 sub-category prompt for a specific category."""
        # Map category to filename
        category_to_file = {
            "Client Perceptions": "client_perceptions.yaml",
            "Content & Learning Delivery": "content_learning.yaml",
            "Event Experience & Technology": "event_tech.yaml",
            "People & Community Interactions": "people_community.yaml",
            "Venue & Hospitality": "venue_hospitality.yaml",
        }

        filename = category_to_file.get(category)
        if not filename:
            raise ValueError(f"Unknown category: {category}")

        yaml_path = self.templates_dir / "stage_2" / filename

        with open(yaml_path, "r") as f:
            data = self.yaml.load(f)

        template = self._build_prompt_from_data(data)
        return template.replace("__COMMENT_PLACEHOLDER__", comment)

    def load_stage3_prompt(self, comment: str, category: str, sub_category: str) -> str:
        """Load Stage 3 element prompt."""
        # TODO: Implement when stage 3 YAMLs are ready
        raise NotImplementedError("Stage 3 prompts not yet implemented")

    def load_stage4_prompt(
        self, comment: str, category: str, sub_category: str, element: str
    ) -> str:
        """Load Stage 4 attribute prompt."""
        # TODO: Implement when stage 4 YAMLs are ready
        raise NotImplementedError("Stage 4 prompts not yet implemented")

    def get_available_stages(self) -> list[int]:
        """Get list of available stages."""
        stages = []
        for i in range(1, 5):
            stage_dir = self.templates_dir / f"stage_{i}"
            if stage_dir.exists() and any(stage_dir.glob("*.yaml")):
                stages.append(i)
        return stages
