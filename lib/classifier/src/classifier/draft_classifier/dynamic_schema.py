"""
Dynamic Schema Generator

Generates Pydantic models with correct Literal types from JSON hierarchy.
"""

from pathlib import Path
from typing import List, Literal, Type, get_args

from pydantic import BaseModel, Field, create_model

from classifier.utils import HierarchyNavigator, load_json


class DynamicSchemaGenerator:
    """Generate Pydantic models dynamically from hierarchy JSON."""

    def __init__(self, hierarchy_path: str | Path):
        """
        Initialize with hierarchy JSON.

        Args:
            hierarchy_path: Path to hierarchy JSON file
        """
        self.hierarchy = load_json(hierarchy_path)
        self.nav = HierarchyNavigator(self.hierarchy)

    def get_stage1_schema(self) -> Type[BaseModel]:
        """Generate Stage 1 (Category) output schema."""
        categories = self.nav.get_categories()
        CategoryType = Literal[tuple(categories)]  # Dynamic Literal

        class CategorySpan(BaseModel):
            excerpt: str = Field(description="Exact text excerpt")
            reasoning: str = Field(description="Classification reasoning")
            category: CategoryType = Field(description="Category name")
            sentiment: Literal["positive", "negative", "neutral", "mixed"]

        class Stage1Output(BaseModel):
            classifications: List[CategorySpan]

        return Stage1Output

    def get_stage2_schema(self, category: str) -> Type[BaseModel]:
        """Generate Stage 2 (Sub-category) output schema for a category."""
        subcategories = self.nav.get_subcategories(category)

        if not subcategories:
            # No sub-categories for this category
            SubCategoryType = Literal[""]
        else:
            SubCategoryType = Literal[tuple(subcategories)]

        class SubCategorySpan(BaseModel):
            excerpt: str = Field(description="Exact text excerpt")
            reasoning: str = Field(description="Classification reasoning")
            sub_category: SubCategoryType = Field(description="Sub-category name")
            sentiment: Literal["positive", "negative", "neutral", "mixed"]

        class Stage2Output(BaseModel):
            classifications: List[SubCategorySpan]

        return Stage2Output

    def get_stage3_schema(self, category: str, sub_category: str) -> Type[BaseModel]:
        """Generate Stage 3 (Element) output schema."""
        elements = self.nav.get_elements(category, sub_category)

        if not elements:
            ElementType = Literal[""]
        else:
            ElementType = Literal[tuple(elements)]

        class ElementSpan(BaseModel):
            excerpt: str = Field(description="Exact text excerpt")
            reasoning: str = Field(description="Classification reasoning")
            element: ElementType = Field(description="Element name")
            sentiment: Literal["positive", "negative", "neutral", "mixed"]

        class Stage3Output(BaseModel):
            classifications: List[ElementSpan]

        return Stage3Output

    def get_stage4_schema(
        self, category: str, sub_category: str, element: str
    ) -> Type[BaseModel]:
        """Generate Stage 4 (Attribute) output schema."""
        attributes = self.nav.get_attributes(category, sub_category, element)

        if not attributes:
            AttributeType = Literal[""]
        else:
            AttributeType = Literal[tuple(attributes)]

        class AttributeSpan(BaseModel):
            excerpt: str = Field(description="Exact text excerpt")
            reasoning: str = Field(description="Classification reasoning")
            attribute: AttributeType = Field(description="Attribute name")
            sentiment: Literal["positive", "negative", "neutral", "mixed"]

        class Stage4Output(BaseModel):
            classifications: List[AttributeSpan]

        return Stage4Output

    def validate_prediction(
        self, stage: int, predicted_label: str, context: dict = None
    ) -> bool:
        """
        Validate a predicted label against the hierarchy.

        Args:
            stage: 1-4
            predicted_label: The label to validate
            context: For stage 2+, {'category': '...', 'sub_category': '...', etc.}
        """
        if stage == 1:
            return predicted_label in self.nav.get_categories()
        elif stage == 2:
            category = context.get("category")
            return predicted_label in self.nav.get_subcategories(category)
        elif stage == 3:
            category = context.get("category")
            sub_category = context.get("sub_category")
            return predicted_label in self.nav.get_elements(category, sub_category)
        elif stage == 4:
            category = context.get("category")
            sub_category = context.get("sub_category")
            element = context.get("element")
            return predicted_label in self.nav.get_attributes(category, sub_category, element)

        return False
