"""
Pydantic models for hierarchical multi-stage classification.

Stages:
    1. Category extraction (with sentiment)
    2. Sub-category extraction (with sentiment, per category)
    3. Element extraction (with sentiment, per sub-category)
    4. Attribute extraction (with sentiment, per element)
"""

from typing import List, Literal, Optional

from pydantic import BaseModel, Field

# ============================================================
# Sentiment Type
# ============================================================

SentimentType = Literal["positive", "negative", "neutral", "mixed"]


# ============================================================
# STAGE 1: Category Extraction
# ============================================================


class CategorySpan(BaseModel):
    """Single category-level classification span."""

    excerpt: str = Field(description="Exact text excerpt from the comment")
    reasoning: str = Field(description="Why this excerpt belongs to this category")
    category: str = Field(description="Category name")
    sentiment: SentimentType = Field(description="Sentiment of the excerpt")


class Stage1Output(BaseModel):
    """Stage 1: Extract all category-level spans."""

    classifications: List[CategorySpan] = Field(
        description="List of category classifications found in the comment"
    )


# ============================================================
# STAGE 2: Sub-category Extraction (per category)
# ============================================================


class SubCategorySpan(BaseModel):
    """Single sub-category-level classification span."""

    excerpt: str = Field(description="Exact text excerpt from the comment")
    reasoning: str = Field(description="Why this excerpt belongs to this sub-category")
    sub_category: str = Field(description="Sub-category name")
    sentiment: SentimentType = Field(description="Sentiment of the excerpt")


class Stage2Output(BaseModel):
    """Stage 2: Extract all sub-category spans for a given category."""

    classifications: List[SubCategorySpan] = Field(
        description="List of sub-category classifications found"
    )


# ============================================================
# STAGE 3: Element Extraction (per sub-category)
# ============================================================


class ElementSpan(BaseModel):
    """Single element-level classification span."""

    excerpt: str = Field(description="Exact text excerpt from the comment")
    reasoning: str = Field(description="Why this excerpt belongs to this element")
    element: str = Field(description="Element name")
    sentiment: SentimentType = Field(description="Sentiment of the excerpt")


class Stage3Output(BaseModel):
    """Stage 3: Extract all element spans for a given sub-category."""

    classifications: List[ElementSpan] = Field(
        description="List of element classifications found"
    )


# ============================================================
# STAGE 4: Attribute Extraction (per element)
# ============================================================


class AttributeSpan(BaseModel):
    """Single attribute-level classification span."""

    excerpt: str = Field(description="Exact text excerpt from the comment")
    reasoning: str = Field(description="Why this excerpt belongs to this attribute")
    attribute: str = Field(description="Attribute name")
    sentiment: SentimentType = Field(description="Sentiment of the excerpt")


class Stage4Output(BaseModel):
    """Stage 4: Extract all attribute spans for a given element."""

    classifications: List[AttributeSpan] = Field(
        description="List of attribute classifications found"
    )


class ClassificationSpan(BaseModel):
    """Final classification span with full stage-by-stage traceability."""

    # Stage 1 - Category
    category: Optional[str] = None
    stage1_excerpt: Optional[str] = Field(None, description="Excerpt that identified category")
    stage1_reasoning: Optional[str] = Field(
        None, description="Reasoning for category classification"
    )
    stage1_sentiment: Optional[SentimentType] = Field(
        None, description="Sentiment at category level"
    )

    # Stage 2 - Sub-category
    sub_category: Optional[str] = None
    stage2_excerpt: Optional[str] = Field(
        None, description="Excerpt that identified sub-category"
    )
    stage2_reasoning: Optional[str] = Field(
        None, description="Reasoning for sub-category classification"
    )
    stage2_sentiment: Optional[SentimentType] = Field(
        None, description="Sentiment at sub-category level"
    )

    # Stage 3 - Element
    element: Optional[str] = None
    stage3_excerpt: Optional[str] = Field(None, description="Excerpt that identified element")
    stage3_reasoning: Optional[str] = Field(
        None, description="Reasoning for element classification"
    )
    stage3_sentiment: Optional[SentimentType] = Field(
        None, description="Sentiment at element level"
    )

    # Stage 4 - Attribute
    attribute: Optional[str] = None
    stage4_excerpt: Optional[str] = Field(None, description="Excerpt that identified attribute")
    stage4_reasoning: Optional[str] = Field(
        None, description="Reasoning for attribute classification"
    )
    stage4_sentiment: Optional[SentimentType] = Field(
        None, description="Sentiment at attribute level"
    )

    def to_dict(self) -> dict:
        """Convert to dictionary for DataFrame export."""
        return {
            "category": self.category,
            "stage1_excerpt": self.stage1_excerpt,
            "stage1_reasoning": self.stage1_reasoning,
            "stage1_sentiment": self.stage1_sentiment,
            "sub_category": self.sub_category,
            "stage2_excerpt": self.stage2_excerpt,
            "stage2_reasoning": self.stage2_reasoning,
            "stage2_sentiment": self.stage2_sentiment,
            "element": self.element,
            "stage3_excerpt": self.stage3_excerpt,
            "stage3_reasoning": self.stage3_reasoning,
            "stage3_sentiment": self.stage3_sentiment,
            "attribute": self.attribute,
            "stage4_excerpt": self.stage4_excerpt,
            "stage4_reasoning": self.stage4_reasoning,
            "stage4_sentiment": self.stage4_sentiment,
        }


class FinalClassificationOutput(BaseModel):
    """Final output with original comment and all classifications."""

    original_comment: str
    classifications: List[ClassificationSpan]

    def to_records(self) -> List[dict]:
        """
        Convert to list of records for DataFrame export.
        Each classification becomes one row.
        """

        if not self.classifications:
            return [
                {
                    "original_comment": self.original_comment,
                    "category": None,
                    "stage1_excerpt": None,
                    "stage1_reasoning": None,
                    "stage1_sentiment": None,
                    "sub_category": None,
                    "stage2_excerpt": None,
                    "stage2_reasoning": None,
                    "stage2_sentiment": None,
                    "element": None,
                    "stage3_excerpt": None,
                    "stage3_reasoning": None,
                    "stage3_sentiment": None,
                    "attribute": None,
                    "stage4_excerpt": None,
                    "stage4_reasoning": None,
                    "stage4_sentiment": None,
                }
            ]

        records = []
        for classification in self.classifications:
            record = {
                "original_comment": self.original_comment,
                "category": classification.category,
                "stage1_excerpt": classification.stage1_excerpt,
                "stage1_reasoning": classification.stage1_reasoning,
                "stage1_sentiment": classification.stage1_sentiment,
                "sub_category": classification.sub_category,
                "stage2_excerpt": classification.stage2_excerpt,
                "stage2_reasoning": classification.stage2_reasoning,
                "stage2_sentiment": classification.stage2_sentiment,
                "element": classification.element,
                "stage3_excerpt": classification.stage3_excerpt,
                "stage3_reasoning": classification.stage3_reasoning,
                "stage3_sentiment": classification.stage3_sentiment,
                "attribute": classification.attribute,
                "stage4_excerpt": classification.stage4_excerpt,
                "stage4_reasoning": classification.stage4_reasoning,
                "stage4_sentiment": classification.stage4_sentiment,
            }
            records.append(record)

        return records
