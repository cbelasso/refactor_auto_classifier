"""
Shorthand Description Updater

Update hierarchy schemas with concise, LLM-optimized descriptions.
These are stored in 'shorthand_description' field and used in prompts.

Usage:
    updater = ShorthandUpdater("schema_v3.json")
    updater.view_category("Client Perceptions")
    updater.update_category("Client Perceptions", "Feedback about the organization's software, tools, or the value/outcomes gained from using them.")
    updater.save()
"""

import json
from pathlib import Path
from typing import Optional


class ShorthandUpdater:
    """Update shorthand descriptions in a hierarchy schema."""

    def __init__(self, schema_path: str | Path):
        self.schema_path = Path(schema_path)
        with open(self.schema_path, "r") as f:
            self.schema = json.load(f)
        self._build_index()

    def _build_index(self):
        """Build lookup index for fast node access."""
        self._categories = {}
        self._subcategories = {}
        self._elements = {}
        self._attributes = {}

        for cat_node in self.schema.get("children", []):
            cat_name = cat_node["name"]
            self._categories[cat_name] = cat_node

            for subcat_node in cat_node.get("children", []):
                subcat_name = subcat_node["name"]
                self._subcategories[(cat_name, subcat_name)] = subcat_node

                for elem_node in subcat_node.get("children", []):
                    elem_name = elem_node["name"]
                    self._elements[(cat_name, subcat_name, elem_name)] = elem_node

                    for attr_node in elem_node.get("children", []):
                        attr_name = attr_node["name"]
                        self._attributes[(cat_name, subcat_name, elem_name, attr_name)] = (
                            attr_node
                        )

    # ========== View Methods ==========

    def list_categories(self) -> list[str]:
        """List all category names."""
        return list(self._categories.keys())

    def list_subcategories(self, category: str) -> list[str]:
        """List subcategory names under a category."""
        cat_node = self._categories.get(category)
        if not cat_node:
            return []
        return [child["name"] for child in cat_node.get("children", [])]

    def view_category(self, category: str):
        """View a category's current definitions."""
        node = self._categories.get(category)
        if not node:
            print(f"Category '{category}' not found")
            return

        self._print_node(category, node)

    def view_subcategory(self, category: str, subcategory: str):
        """View a subcategory's current definitions."""
        node = self._subcategories.get((category, subcategory))
        if not node:
            print(f"Subcategory '{category} > {subcategory}' not found")
            return

        self._print_node(f"{category} > {subcategory}", node)

    def view_all_categories(self):
        """View all categories with their current shorthand descriptions."""
        print("=" * 70)
        print("ALL CATEGORIES - SHORTHAND DESCRIPTIONS")
        print("=" * 70)

        for cat_name in self.list_categories():
            node = self._categories[cat_name]
            shorthand = node.get("shorthand_description", "")
            status = "✓" if shorthand else "✗ (empty)"

            print(f"\n{cat_name}")
            print(f"  Shorthand: {shorthand if shorthand else '(not set)'}")
            print(f"  Status: {status}")

    def _print_node(self, label: str, node: dict):
        """Print a node's definitions for comparison."""
        print(f"\n{'=' * 70}")
        print(f"{label}")
        print(f"{'=' * 70}")
        print("\n[Original Description]")
        print(f"{node.get('description', '(empty)')}")
        print("\n[Original Definition]")
        print(f"{node.get('definition', '(empty)')}")
        print("\n[Shorthand Description] <- EDITABLE")
        print(f"{node.get('shorthand_description', '(not set)')}")
        print("\n[Subcategories]")
        children = [c["name"] for c in node.get("children", [])]
        print(f"{children if children else '(none)'}")

    # ========== Update Methods ==========

    def update_category(self, category: str, shorthand: str):
        """Update shorthand description for a category."""
        node = self._categories.get(category)
        if not node:
            raise ValueError(f"Category '{category}' not found")
        node["shorthand_description"] = shorthand.strip()
        print(f"✓ Updated: {category}")

    def update_subcategory(self, category: str, subcategory: str, shorthand: str):
        """Update shorthand description for a subcategory."""
        node = self._subcategories.get((category, subcategory))
        if not node:
            raise ValueError(f"Subcategory '{category} > {subcategory}' not found")
        node["shorthand_description"] = shorthand.strip()
        print(f"✓ Updated: {category} > {subcategory}")

    def update_element(self, category: str, subcategory: str, element: str, shorthand: str):
        """Update shorthand description for an element."""
        node = self._elements.get((category, subcategory, element))
        if not node:
            raise ValueError(f"Element '{category} > {subcategory} > {element}' not found")
        node["shorthand_description"] = shorthand.strip()
        print(f"✓ Updated: {category} > {subcategory} > {element}")

    def batch_update_categories(self, updates: dict[str, str]):
        """
        Batch update multiple category shorthand descriptions.

        Args:
            updates: Dict mapping category name to shorthand description
        """
        for category, shorthand in updates.items():
            self.update_category(category, shorthand)

    # ========== Save ==========

    def save(self, output_path: Optional[str | Path] = None):
        """Save the updated schema."""
        output_path = Path(output_path) if output_path else self.schema_path
        with open(output_path, "w") as f:
            json.dump(self.schema, f, indent=2)
        print(f"\n✓ Schema saved to: {output_path}")

    # ========== Export ==========

    def export_shorthand_report(self) -> str:
        """Export a report of all shorthand descriptions."""
        lines = ["SHORTHAND DESCRIPTIONS REPORT", "=" * 70, ""]

        for cat_name in self.list_categories():
            cat_node = self._categories[cat_name]
            cat_shorthand = cat_node.get("shorthand_description", "")

            lines.append(f"CATEGORY: {cat_name}")
            lines.append(f"  Shorthand: {cat_shorthand if cat_shorthand else '(not set)'}")

            for subcat_name in self.list_subcategories(cat_name):
                subcat_node = self._subcategories[(cat_name, subcat_name)]
                subcat_shorthand = subcat_node.get("shorthand_description", "")
                lines.append(f"  └── {subcat_name}")
                lines.append(
                    f"      Shorthand: {subcat_shorthand if subcat_shorthand else '(not set)'}"
                )

            lines.append("")

        return "\n".join(lines)
