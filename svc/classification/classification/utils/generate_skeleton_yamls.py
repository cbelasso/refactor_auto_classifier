"""
Generate skeleton YAML files for all stages based on hierarchy.

Usage:
    python generate_skeleton_yamls.py
"""

from pathlib import Path

from classifier.utils import HierarchyNavigator
from ruamel.yaml import YAML

HIERARCHY_PATH = "/data-fast/data3/clyde/projects/world/documents/schemas/schema_v2.json"
PROMPT_TEMPLATES_DIR = "./prompt_templates"


def label_to_filename(label: str) -> str:
    """Convert label to filename."""
    return (
        label.lower()
        .replace("/", "_")  # Food/Beverages → food_beverages
        .replace(" & ", "_and_")  # Content & Learning → content_and_learning
        .replace("&", "_and_")  # R&D → r_and_d
        .replace("-", "_")  # Wi-Fi → wi_fi
        .replace(" ", "_")  # ADD THIS! All spaces to underscores
        .replace("(", "")  # Remove opening parens
        .replace(")", "")  # Remove closing parens
    ) + ".yaml"


def create_stage2_skeleton(category: str, nav: HierarchyNavigator) -> dict:
    """Create Stage 2 skeleton for a category."""
    subcategories = nav.get_subcategories(category)

    labels = []
    for subcat in subcategories:
        elements = nav.get_elements(category, subcat)
        context_items = [f"{elem}: [Description needed]" for elem in elements]

        labels.append(
            {
                "name": subcat,
                "description": f"[Add description for {subcat}]",
                "context_items": context_items,
            }
        )

    return {
        "ready": False,  # Mark as not ready!
        "prompt_metadata": {
            "stage": 2,
            "focus": category,
            "task": f"Extract sub-category feedback related to {category.upper()}",
            "version": "1.0",
        },
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": f"Extract sub-category feedback related to {category.upper()}",
        "custom_instructions": "",
        "labels_title": "SUB-CATEGORIES TO IDENTIFY",
        "label_field": "sub_category",
        "labels": labels,
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each sub-category.",
            "A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE sub-category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
        ],
        "examples": [
            {
                "comment": "[Add example comment here]",
                "classifications": [
                    {
                        "excerpt": "[Add excerpt here]",
                        "reasoning": "[Add reasoning here]",
                        "sub_category": subcategories[0] if subcategories else "",
                        "sentiment": "positive",
                    }
                ],
            },
        ],
    }


def create_stage3_skeleton(category: str, subcategory: str, nav: HierarchyNavigator) -> dict:
    """Create Stage 3 skeleton for a sub-category."""
    elements = nav.get_elements(category, subcategory)

    labels = []
    for elem in elements:
        labels.append(
            {
                "name": elem,
                "description": f"[Add description for {elem}]",
            }
        )

    return {
        "ready": False,
        "prompt_metadata": {
            "stage": 3,
            "focus": f"{category} > {subcategory}",
            "task": f"Extract element feedback related to {subcategory.upper()}",
            "version": "1.0",
        },
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": f"Extract element feedback related to {subcategory.upper()}",
        "custom_instructions": "",
        "labels_title": "ELEMENTS TO IDENTIFY",
        "label_field": "element",
        "labels": labels,
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each element.",
            "A comment can have MULTIPLE element spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE element only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
        ],
        "examples": [
            {
                "comment": "[Add example comment here]",
                "classifications": [
                    {
                        "excerpt": "[Add excerpt here]",
                        "reasoning": "[Add reasoning here]",
                        "element": elements[0] if elements else "",
                        "sentiment": "positive",
                    }
                ],
            },
        ],
    }


def create_stage4_skeleton(
    category: str, subcategory: str, element: str, nav: HierarchyNavigator
) -> dict:
    """Create Stage 4 skeleton for an element."""
    attributes = nav.get_attributes(category, subcategory, element)

    labels = []
    for attr in attributes:
        labels.append(
            {
                "name": attr,
                "description": f"[Add description for {attr}]",
            }
        )

    return {
        "ready": False,
        "prompt_metadata": {
            "stage": 4,
            "focus": f"{category} > {subcategory} > {element}",
            "task": f"Extract attribute feedback related to {element.upper()}",
            "version": "1.0",
        },
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": f"Extract attribute feedback related to {element.upper()}",
        "custom_instructions": "",
        "labels_title": "ATTRIBUTES TO IDENTIFY",
        "label_field": "attribute",
        "labels": labels,
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each attribute.",
            "A comment can have MULTIPLE attribute spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE attribute only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
        ],
        "examples": [
            {
                "comment": "[Add example comment here]",
                "classifications": [
                    {
                        "excerpt": "[Add excerpt here]",
                        "reasoning": "[Add reasoning here]",
                        "attribute": attributes[0] if attributes else "",
                        "sentiment": "positive",
                    }
                ],
            },
        ],
    }


def main():
    nav = HierarchyNavigator(HIERARCHY_PATH)
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    templates_dir = Path(PROMPT_TEMPLATES_DIR)

    print("=" * 60)
    print("GENERATING SKELETON YAML FILES")
    print("=" * 60)

    created_count = 0
    skipped_count = 0

    # Stage 2: Categories
    stage2_dir = templates_dir / "stage_2"
    stage2_dir.mkdir(parents=True, exist_ok=True)

    print("\nStage 2 (Categories):")
    for category in nav.get_categories():
        filename = label_to_filename(category)
        filepath = stage2_dir / filename

        if filepath.exists():
            print(f"  ⊘ {filename} (already exists)")
            skipped_count += 1
            continue

        data = create_stage2_skeleton(category, nav)
        with open(filepath, "w") as f:
            f.write(f"# Stage 2: {category}\n")
            f.write("# Status: NOT READY - Edit examples and rules, then set ready: true\n\n")
            yaml.dump(data, f)

        print(f"  ✓ {filename}")
        created_count += 1

    # Stage 3: Sub-categories
    stage3_dir = templates_dir / "stage_3"
    stage3_dir.mkdir(parents=True, exist_ok=True)

    print("\nStage 3 (Sub-categories):")
    processed = set()
    for category in nav.get_categories():
        for subcategory in nav.get_subcategories(category):
            if subcategory in processed:
                continue
            processed.add(subcategory)

            filename = label_to_filename(subcategory)
            filepath = stage3_dir / filename

            if filepath.exists():
                print(f"  ⊘ {filename} (already exists)")
                skipped_count += 1
                continue

            data = create_stage3_skeleton(category, subcategory, nav)
            with open(filepath, "w") as f:
                f.write(f"# Stage 3: {subcategory}\n")
                f.write(
                    "# Status: NOT READY - Edit examples and rules, then set ready: true\n\n"
                )
                yaml.dump(data, f)

            print(f"  ✓ {filename}")
            created_count += 1

    # Stage 4: Elements
    stage4_dir = templates_dir / "stage_4"
    stage4_dir.mkdir(parents=True, exist_ok=True)

    print("\nStage 4 (Elements):")
    processed = set()
    for category in nav.get_categories():
        for subcategory in nav.get_subcategories(category):
            for element in nav.get_elements(category, subcategory):
                if element in processed:
                    continue
                processed.add(element)

                filename = label_to_filename(element)
                filepath = stage4_dir / filename

                if filepath.exists():
                    print(f"  ⊘ {filename} (already exists)")
                    skipped_count += 1
                    continue

                data = create_stage4_skeleton(category, subcategory, element, nav)
                with open(filepath, "w") as f:
                    f.write(f"# Stage 4: {element}\n")
                    f.write(
                        "# Status: NOT READY - Edit examples and rules, then set ready: true\n\n"
                    )
                    yaml.dump(data, f)

                print(f"  ✓ {filename}")
                created_count += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Created: {created_count} files")
    print(f"Skipped: {skipped_count} files (already exist)")
    print("\n⚠️  All new files have ready: false")
    print("   Edit them and set ready: true when done!")


if __name__ == "__main__":
    main()
