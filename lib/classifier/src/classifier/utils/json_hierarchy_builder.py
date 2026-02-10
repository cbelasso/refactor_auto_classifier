"""
Hierarchical JSON Builder Utility

Converts flat tabular data (Excel, CSV, JSON) into a hierarchical JSON structure
suitable for classification taxonomies.

Hierarchy: Root → Group → Topic → Attribute
"""

import ast
from dataclasses import dataclass, field
import json
import math
from pathlib import Path
from typing import Any

from .data_io import read_tabular_file, save_json


@dataclass
class BuilderLog:
    """Container for warnings and errors during hierarchy building."""

    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def warn(self, message: str, row_idx: int | None = None):
        prefix = f"[Row {row_idx}] " if row_idx is not None else ""
        self.warnings.append(f"{prefix}{message}")

    def error(self, message: str, row_idx: int | None = None):
        prefix = f"[Row {row_idx}] " if row_idx is not None else ""
        self.errors.append(f"{prefix}{message}")

    def has_issues(self) -> bool:
        return bool(self.warnings or self.errors)

    def summary(self) -> str:
        lines = []
        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  ✗ {err}")
        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  ⚠ {warn}")
        if not lines:
            lines.append("No issues found.")
        return "\n".join(lines)

    def print_log(self):
        """Print the log summary."""
        print(self.summary())


class HierarchyBuilder:
    """
    Builds hierarchical JSON from flat tabular data.

    Expected columns:
        - category: Top-level category (level 1)
        - sub-category: Second-level category (level 2)
        - element: Third-level category (level 3)
        - attribute: Fourth-level category (level 4)
        - descriptions: Short description of the node
        - definitions: Detailed definition
        - inclusions: What this category includes
        - exclusions: What this category excludes
        - keywords: Keywords/tags (comma-separated string or list)
        - decision rule: Guidance for classification decisions

    Hierarchy determination:
        - If only category is present → metadata belongs to Category node
        - If category + sub-category → metadata belongs to Sub-Category node
        - If category + sub-category + element → metadata belongs to Element node
        - If category + sub-category + element + attribute → metadata belongs to Attribute node
    """

    COLUMN_ALIASES = {
        "category": ["category", "categories", "group", "groups"],
        "sub-category": ["sub-category", "sub_category", "subcategory", "sub category"],
        "element": ["element", "elements", "topic", "topics"],
        "attribute": ["attribute", "attributes", "sub_attribute"],
        "descriptions": ["descriptions", "description", "desc"],
        "definitions": ["definitions", "definition", "def"],
        "inclusions": ["inclusions", "inclusion", "includes", "include"],
        "exclusions": ["exclusions", "exclusion", "excludes", "exclude"],
        "keywords": ["keywords", "keyword", "tags", "tag"],
        "decision rule": ["decision rule", "decision_rule", "decision rules", "rule"],
    }

    def __init__(self, root_name: str = "World", sheet_name: str | int | None = None):
        self.root_name = root_name
        self.sheet_name = sheet_name
        self.log = BuilderLog()
        self._hierarchy: dict[str, Any] | None = None

    def _normalize_columns(self, df) -> dict[str, str]:
        """Map actual column names to standard names."""
        column_map = {}
        df_columns_lower = {col.lower().strip(): col for col in df.columns}

        for standard_name, aliases in self.COLUMN_ALIASES.items():
            for alias in aliases:
                if alias.lower() in df_columns_lower:
                    column_map[standard_name] = df_columns_lower[alias.lower()]
                    break

        return column_map

    def _parse_list_string(self, value: Any) -> list[str] | None:
        """
        Try to parse a string that looks like a Python/JSON list.
        Returns None if not a list-like string.
        """
        if not isinstance(value, str):
            return None

        value = value.strip()
        if not (value.startswith("[") and value.endswith("]")):
            return None

        # Try JSON first
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
        except json.JSONDecodeError:
            pass

        # Try Python literal
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if item]
        except (ValueError, SyntaxError):
            pass

        return None

    def _parse_keywords(self, value: Any) -> list[str]:
        """Convert keywords to a list, handling various input formats."""
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return []

        if isinstance(value, list):
            return [str(k).strip() for k in value if k and str(k).strip()]

        if isinstance(value, str):
            # Try parsing as list-like string first
            parsed = self._parse_list_string(value)
            if parsed is not None:
                return parsed

            # Fall back to comma-separated
            if not value.strip():
                return []
            keywords = [k.strip() for k in value.split(",")]
            return [k for k in keywords if k]

        return []

    def _parse_string_field(self, value: Any) -> str:
        """
        Parse a string field, joining list items if it's a list-like string.
        """
        if value is None:
            return ""
        if isinstance(value, float) and math.isnan(value):
            return ""

        value_str = str(value).strip()

        # Check if it's a list-like string
        parsed = self._parse_list_string(value_str)
        if parsed is not None:
            return "; ".join(parsed)

        return value_str

    def _safe_str(self, value: Any) -> str:
        """Safely convert value to string, handling NaN and None."""
        if value is None:
            return ""
        if isinstance(value, float) and math.isnan(value):
            return ""
        return str(value).strip()

    def _build_scope(self, inclusions: str, exclusions: str) -> str:
        """Combine inclusions and exclusions into a scope string."""
        parts = []
        if inclusions:
            parts.append(f"Includes {inclusions}")
        if exclusions:
            parts.append(f"Excludes {exclusions}")
        return ". ".join(parts) + "." if parts else ""

    def _build_comprehensive_definition(
        self,
        name: str,
        description: str,
        definition: str,
        inclusions: str,
        exclusions: str,
        decision_rule: str,
    ) -> str:
        """Build a comprehensive definition suitable for classification prompts."""
        lines = [f"**{name}**", ""]

        if description:
            lines.append(description)
            lines.append("")

        if definition:
            lines.append(f"**Definition:** {definition}")
            lines.append("")

        if inclusions:
            lines.append(f"**Includes:** {inclusions}")
            lines.append("")

        if exclusions:
            lines.append(f"**Excludes:** {exclusions}")
            lines.append("")

        if decision_rule:
            lines.append(f"**Decision Rule:** {decision_rule}")

        return "\n".join(lines).strip()

    def _create_node(
        self,
        name: str,
        description: str = "",
        definition: str = "",
        inclusions: str = "",
        exclusions: str = "",
        keywords: list[str] | None = None,
        decision_rule: str = "",
    ) -> dict[str, Any]:
        """Create a hierarchy node with all required fields."""
        keywords = keywords or []
        scope = self._build_scope(inclusions, exclusions)
        comprehensive_definition = self._build_comprehensive_definition(
            name, description, definition, inclusions, exclusions, decision_rule
        )

        return {
            "name": name,
            "keywords": keywords,
            "definition": definition,
            "description": description,
            "scope": scope,
            "inclusions": inclusions,
            "exclusions": exclusions,
            "decision_rule": decision_rule,
            "comprehensive_definition": comprehensive_definition,
            "children": [],
        }

    def _create_root_node(self) -> dict[str, Any]:
        """Create the root node with default empty values."""
        return self._create_node(self.root_name)

    def _update_node(
        self,
        node: dict[str, Any],
        description: str,
        definition: str,
        inclusions: str,
        exclusions: str,
        keywords: list[str],
        decision_rule: str,
    ):
        """Update an existing node with new metadata."""
        node["description"] = description
        node["definition"] = definition
        node["inclusions"] = inclusions
        node["exclusions"] = exclusions
        node["keywords"] = keywords
        node["decision_rule"] = decision_rule
        node["scope"] = self._build_scope(inclusions, exclusions)
        node["comprehensive_definition"] = self._build_comprehensive_definition(
            node["name"], description, definition, inclusions, exclusions, decision_rule
        )

    def build(self, filepath: str | Path) -> dict[str, Any]:
        """
        Build the hierarchy from a file.

        Args:
            filepath: Path to Excel, CSV, or JSON file

        Returns:
            Hierarchical dictionary structure
        """

        self.log = BuilderLog()

        df = read_tabular_file(filepath, sheet_name=self.sheet_name)
        col_map = self._normalize_columns(df)

        if "category" not in col_map:
            self.log.error("Missing required 'category' column")
            raise ValueError("Missing required 'category' column")

        root = self._create_root_node()

        categories: dict[str, dict[str, Any]] = {}
        sub_categories: dict[tuple[str, str], dict[str, Any]] = {}
        elements: dict[
            tuple, dict[str, Any]
        ] = {}  # Key can be (cat, elem) or (cat, subcat, elem)

        for idx, row in df.iterrows():
            row_num = idx + 2

            category_name = self._safe_str(row.get(col_map.get("category", ""), ""))
            sub_category_name = self._safe_str(row.get(col_map.get("sub-category", ""), ""))
            element_name = self._safe_str(row.get(col_map.get("element", ""), ""))
            attr_name = self._safe_str(row.get(col_map.get("attribute", ""), ""))

            description = self._safe_str(row.get(col_map.get("descriptions", ""), ""))
            definition = self._safe_str(row.get(col_map.get("definitions", ""), ""))
            inclusions = self._parse_string_field(row.get(col_map.get("inclusions", ""), ""))
            exclusions = self._parse_string_field(row.get(col_map.get("exclusions", ""), ""))
            decision_rule = self._safe_str(row.get(col_map.get("decision rule", ""), ""))
            keywords = self._parse_keywords(row.get(col_map.get("keywords", ""), ""))

            if not category_name:
                self.log.warn("Empty category name, skipping row", row_num)
                continue

            # Ensure category exists
            if category_name not in categories:
                category_node = self._create_node(category_name)
                categories[category_name] = category_node
                root["children"].append(category_node)

            # CASE 1: Category only
            if not sub_category_name and not element_name and not attr_name:
                node = categories[category_name]
                self._update_node(
                    node,
                    description,
                    definition,
                    inclusions,
                    exclusions,
                    keywords,
                    decision_rule,
                )

            # CASE 2: Category + Sub-category only
            elif sub_category_name and not element_name and not attr_name:
                sub_cat_key = (category_name, sub_category_name)
                if sub_cat_key in sub_categories:
                    self.log.warn(
                        f"Duplicate sub-category '{sub_category_name}' under '{category_name}', updating existing",
                        row_num,
                    )
                    node = sub_categories[sub_cat_key]
                else:
                    node = self._create_node(sub_category_name)
                    sub_categories[sub_cat_key] = node
                    categories[category_name]["children"].append(node)

                self._update_node(
                    node,
                    description,
                    definition,
                    inclusions,
                    exclusions,
                    keywords,
                    decision_rule,
                )

            # CASE 3: Category + Sub-category + Element (no attribute)
            elif sub_category_name and element_name and not attr_name:
                # Ensure sub-category exists
                sub_cat_key = (category_name, sub_category_name)
                if sub_cat_key not in sub_categories:
                    self.log.warn(
                        f"Sub-category '{sub_category_name}' under '{category_name}' not previously defined, auto-creating",
                        row_num,
                    )
                    sub_cat_node = self._create_node(sub_category_name)
                    sub_categories[sub_cat_key] = sub_cat_node
                    categories[category_name]["children"].append(sub_cat_node)

                element_key = (category_name, sub_category_name, element_name)
                if element_key in elements:
                    self.log.warn(
                        f"Duplicate element '{element_name}', updating existing", row_num
                    )
                    node = elements[element_key]
                else:
                    node = self._create_node(element_name)
                    elements[element_key] = node
                    sub_categories[sub_cat_key]["children"].append(node)

                self._update_node(
                    node,
                    description,
                    definition,
                    inclusions,
                    exclusions,
                    keywords,
                    decision_rule,
                )

            # CASE 4: Category + Element (no sub-category, no attribute) - 3-level hierarchy
            elif not sub_category_name and element_name and not attr_name:
                element_key = (category_name, element_name)
                if element_key in elements:
                    self.log.warn(
                        f"Duplicate element '{element_name}' under '{category_name}', updating existing",
                        row_num,
                    )
                    node = elements[element_key]
                else:
                    node = self._create_node(element_name)
                    elements[element_key] = node
                    categories[category_name]["children"].append(node)

                self._update_node(
                    node,
                    description,
                    definition,
                    inclusions,
                    exclusions,
                    keywords,
                    decision_rule,
                )

            # CASE 5: Category + Sub-category + Element + Attribute (4-level)
            elif sub_category_name and element_name and attr_name:
                # Ensure sub-category exists
                sub_cat_key = (category_name, sub_category_name)
                if sub_cat_key not in sub_categories:
                    self.log.warn(
                        f"Sub-category '{sub_category_name}' not previously defined, auto-creating",
                        row_num,
                    )
                    sub_cat_node = self._create_node(sub_category_name)
                    sub_categories[sub_cat_key] = sub_cat_node
                    categories[category_name]["children"].append(sub_cat_node)

                # Ensure element exists
                element_key = (category_name, sub_category_name, element_name)
                if element_key not in elements:
                    self.log.warn(
                        f"Element '{element_name}' not previously defined, auto-creating",
                        row_num,
                    )
                    element_node = self._create_node(element_name)
                    elements[element_key] = element_node
                    sub_categories[sub_cat_key]["children"].append(element_node)

                # Create attribute
                attr_node = self._create_node(
                    attr_name,
                    description,
                    definition,
                    inclusions,
                    exclusions,
                    keywords,
                    decision_rule,
                )
                elements[element_key]["children"].append(attr_node)

            # CASE 6: Category + Element + Attribute (no sub-category) - 3-level hierarchy
            elif not sub_category_name and element_name and attr_name:
                # Ensure element exists (attached to category)
                element_key = (category_name, element_name)
                if element_key not in elements:
                    self.log.warn(
                        f"Element '{element_name}' under '{category_name}' not previously defined, auto-creating",
                        row_num,
                    )
                    element_node = self._create_node(element_name)
                    elements[element_key] = element_node
                    categories[category_name]["children"].append(element_node)

                # Create attribute
                attr_node = self._create_node(
                    attr_name,
                    description,
                    definition,
                    inclusions,
                    exclusions,
                    keywords,
                    decision_rule,
                )
                elements[element_key]["children"].append(attr_node)

            # Invalid cases
            else:
                if sub_category_name and not element_name and attr_name:
                    self.log.warn(
                        f"Attribute '{attr_name}' has no parent element under '{category_name}/{sub_category_name}', skipping",
                        row_num,
                    )
                elif not sub_category_name and not element_name and attr_name:
                    self.log.warn(
                        f"Attribute '{attr_name}' has no parent element under '{category_name}', skipping",
                        row_num,
                    )
                else:
                    self.log.warn("Invalid row structure, skipping", row_num)

        self._hierarchy = root
        return root

    def save(self, filepath: str | Path, indent: int = 2) -> Path:
        """Save the hierarchy to a JSON file."""
        if self._hierarchy is None:
            raise ValueError("No hierarchy built yet. Call build() first.")
        return save_json(self._hierarchy, filepath, indent=indent)

    def to_dict(self) -> dict[str, Any]:
        """Return the hierarchy as a Python dictionary."""
        if self._hierarchy is None:
            raise ValueError("No hierarchy built yet. Call build() first.")
        return self._hierarchy

    def get_log(self) -> BuilderLog:
        """Return the build log with warnings and errors."""
        return self.log

    def get_column_mapping(self, filepath: str | Path) -> dict[str, str]:
        """
        Show how columns in the file map to standard column names.
        Useful for debugging.
        """
        df = read_tabular_file(filepath, sheet_name=self.sheet_name)
        return self._normalize_columns(df)

    def print_log(self):
        """Print the build log summary."""
        print(self.log.summary())


def build_hierarchy(
    input_file: str | Path,
    output_file: str | Path | None = None,
    root_name: str = "World",
    sheet_name: str | int | None = None,
    indent: int = 2,
) -> tuple[dict[str, Any], BuilderLog]:
    """
    Convenience function to build hierarchy from file.

    Args:
        input_file: Path to input Excel/CSV/JSON file
        output_file: Optional path to save JSON output
        root_name: Name for the root node
        sheet_name: For Excel files, the sheet name or index (0-based)
        indent: JSON indentation level

    Returns:
        Tuple of (hierarchy dict, build log)
    """
    builder = HierarchyBuilder(root_name=root_name, sheet_name=sheet_name)
    hierarchy = builder.build(input_file)

    if output_file:
        builder.save(output_file, indent=indent)

    return hierarchy, builder.get_log()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python hierarchy_builder.py <input_file> [output_file]")
        print("Supported formats: .xlsx, .xls, .csv, .json")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    if output_path is None:
        input_p = Path(input_path)
        output_path = input_p.parent / f"{input_p.stem}_hierarchy.json"

    hierarchy, log = build_hierarchy(input_path, output_path)

    print("\nHierarchy built successfully!")
    print(f"Output saved to: {output_path}")
    print(f"\n{log.summary()}")
