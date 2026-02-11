"""
Hierarchy Navigation Utilities

Functions to extract and traverse hierarchical taxonomy structures.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class HierarchyNavigator:
    """Navigate and extract information from hierarchy JSON."""

    def __init__(self, hierarchy_or_path):
        """
        Initialize navigator with hierarchy dict or path to JSON file.

        Args:
            hierarchy_or_path: Either the hierarchy dict or path to JSON file (str or Path)
        """
        # Handle both dict and file path
        if isinstance(hierarchy_or_path, (str, Path)):
            from .data_io import load_json

            self.hierarchy = load_json(hierarchy_or_path)
        else:
            self.hierarchy = hierarchy_or_path

        self._category_cache: Dict[str, Dict[str, Any]] = {}
        self._build_cache()

    def _build_cache(self):
        """Build lookup cache for fast node access."""
        # Cache categories
        for cat_node in self.hierarchy.get("children", []):
            self._category_cache[cat_node["name"]] = cat_node

    def get_categories(self) -> List[str]:
        """Get list of all category names."""
        return [node["name"] for node in self.hierarchy.get("children", [])]

    def get_category_node(self, category: str) -> Optional[Dict[str, Any]]:
        """Get the full node for a category."""
        return self._category_cache.get(category)

    def get_subcategories(self, category: str) -> List[str]:
        """Get list of sub-category names under a category."""
        cat_node = self.get_category_node(category)
        if cat_node is None:
            return []
        return [child["name"] for child in cat_node.get("children", [])]

    def get_subcategory_node(self, category: str, subcategory: str) -> Optional[Dict[str, Any]]:
        """Get the full node for a sub-category."""
        cat_node = self.get_category_node(category)
        if cat_node is None:
            return None

        for child in cat_node.get("children", []):
            if child["name"] == subcategory:
                return child
        return None

    def get_elements(self, category: str, subcategory: Optional[str] = None) -> List[str]:
        """
        Get list of element names.

        If subcategory is None, gets elements directly under category (3-level hierarchy).
        If subcategory is provided, gets elements under that sub-category (4-level hierarchy).
        """
        if subcategory is None:
            # Elements directly under category
            cat_node = self.get_category_node(category)
            if cat_node is None:
                return []
            return [child["name"] for child in cat_node.get("children", [])]
        else:
            # Elements under sub-category
            subcat_node = self.get_subcategory_node(category, subcategory)
            if subcat_node is None:
                return []
            return [child["name"] for child in subcat_node.get("children", [])]

    def get_element_node(
        self, category: str, subcategory: Optional[str], element: str
    ) -> Optional[Dict[str, Any]]:
        """Get the full node for an element."""
        if subcategory is None:
            # Element directly under category
            cat_node = self.get_category_node(category)
            if cat_node is None:
                return None

            for child in cat_node.get("children", []):
                if child["name"] == element:
                    return child
            return None
        else:
            # Element under sub-category
            subcat_node = self.get_subcategory_node(category, subcategory)
            if subcat_node is None:
                return None

            for child in subcat_node.get("children", []):
                if child["name"] == element:
                    return child
            return None

    def get_attributes(
        self, category: str, subcategory: Optional[str], element: str
    ) -> List[str]:
        """Get list of attribute names under an element."""
        elem_node = self.get_element_node(category, subcategory, element)
        if elem_node is None:
            return []
        return [child["name"] for child in elem_node.get("children", [])]

    def get_node_definition(self, node: Dict[str, Any]) -> str:
        """Extract comprehensive definition from a node."""
        return node.get("comprehensive_definition", "")

    def print_categories_with_subcategories(self):
        """Print each category with its list of sub-categories."""
        for cat in self.get_categories():
            subcats = self.get_subcategories(cat)
            print(f"\nCategory: {cat}")
            if subcats:
                print(f"Sub-categories: {subcats}")
            else:
                print("Sub-categories: []")

    def print_category_summary(self, category: str):
        """Print a formatted summary of a category and its children."""
        cat_node = self.get_category_node(category)
        if cat_node is None:
            print(f"Category '{category}' not found")
            return

        print(f"\n{'=' * 60}")
        print(f"CATEGORY: {category}")
        print(f"{'=' * 60}")
        print(f"\nDefinition: {cat_node.get('definition', 'N/A')}")
        print(f"Description: {cat_node.get('description', 'N/A')}")
        print(f"Keywords: {', '.join(cat_node.get('keywords', []))}")

        if cat_node.get("inclusions"):
            print(f"Inclusions: {cat_node['inclusions']}")
        if cat_node.get("exclusions"):
            print(f"Exclusions: {cat_node['exclusions']}")
        if cat_node.get("decision_rule"):
            print(f"Decision Rule: {cat_node['decision_rule']}")

        # Print sub-categories or elements
        children = cat_node.get("children", [])
        if children:
            print(f"\nChildren ({len(children)}):")
            for child in children:
                print(f"  - {child['name']}")
        print()

    def export_level_definitions(self, level: int = 1) -> Dict[str, str]:
        """
        Export comprehensive definitions for all nodes at a given level.

        Args:
            level: 1=categories, 2=sub-categories, 3=elements, 4=attributes

        Returns:
            Dict mapping node names to their comprehensive definitions
        """
        definitions = {}

        if level == 1:
            # Categories
            for cat in self.get_categories():
                node = self.get_category_node(cat)
                if node:
                    definitions[cat] = self.get_node_definition(node)

        elif level == 2:
            # Sub-categories
            for cat in self.get_categories():
                for subcat in self.get_subcategories(cat):
                    node = self.get_subcategory_node(cat, subcat)
                    if node:
                        key = f"{cat} > {subcat}"
                        definitions[key] = self.get_node_definition(node)

        elif level == 3:
            # Elements
            for cat in self.get_categories():
                # Check for 3-level elements (directly under category)
                cat_node = self.get_category_node(cat)
                if cat_node:
                    for child in cat_node.get("children", []):
                        # Check if this is an element (has no elements/subcats as children)
                        # or if it's a subcategory
                        subcats = self.get_subcategories(cat)
                        if subcats:
                            # 4-level: iterate through subcategories
                            for subcat in subcats:
                                for elem in self.get_elements(cat, subcat):
                                    node = self.get_element_node(cat, subcat, elem)
                                    if node:
                                        key = f"{cat} > {subcat} > {elem}"
                                        definitions[key] = self.get_node_definition(node)
                        else:
                            # 3-level: elements directly under category
                            for elem in self.get_elements(cat):
                                node = self.get_element_node(cat, None, elem)
                                if node:
                                    key = f"{cat} > {elem}"
                                    definitions[key] = self.get_node_definition(node)

        return definitions

    def get_structure_summary(self) -> str:
        """Get a text summary of the entire hierarchy structure."""
        lines = [f"ROOT: {self.hierarchy['name']}", ""]

        for cat in self.get_categories():
            lines.append(f"└── {cat}")
            subcats = self.get_subcategories(cat)

            if subcats:
                # 4-level hierarchy
                for i, subcat in enumerate(subcats):
                    is_last_subcat = i == len(subcats) - 1
                    prefix_subcat = "    └──" if is_last_subcat else "    ├──"
                    lines.append(f"{prefix_subcat} {subcat}")

                    elements = self.get_elements(cat, subcat)
                    for j, elem in enumerate(elements):
                        is_last_elem = j == len(elements) - 1
                        prefix_elem = "        └──" if is_last_elem else "        ├──"
                        lines.append(f"{prefix_elem} {elem}")

                        # Check for attributes
                        attrs = self.get_attributes(cat, subcat, elem)
                        for k, attr in enumerate(attrs):
                            is_last_attr = k == len(attrs) - 1
                            prefix_attr = (
                                "            └──" if is_last_attr else "            ├──"
                            )
                            lines.append(f"{prefix_attr} {attr}")
            else:
                # 3-level hierarchy (elements directly under category)
                elements = self.get_elements(cat)
                for i, elem in enumerate(elements):
                    is_last_elem = i == len(elements) - 1
                    prefix_elem = "    └──" if is_last_elem else "    ├──"
                    lines.append(f"{prefix_elem} {elem}")

                    # Check for attributes
                    attrs = self.get_attributes(cat, None, elem)
                    for j, attr in enumerate(attrs):
                        is_last_attr = j == len(attrs) - 1
                        prefix_attr = "        └──" if is_last_attr else "        ├──"
                        lines.append(f"{prefix_attr} {attr}")

        return "\n".join(lines)
