"""Draft hierarchical classifier for conference feedback."""

from .dynamic_schema import DynamicSchemaGenerator
from .models import (
    AttributeSpan,
    CategorySpan,
    ClassificationSpan,
    ElementSpan,
    FinalClassificationOutput,
    SentimentType,
    Stage1Output,
    Stage2Output,
    Stage3Output,
    Stage4Output,
    SubCategorySpan,
)
from .orchestrator import HierarchicalClassifier
from .prompt_loader import PromptLoader
from .prompt_manager_generic import (
    batch_generate_all_stages,
    batch_generate_stage,
    build_prompt_from_yaml,
    generate_python_function,
    validate_prompt_yaml,
)

__all__ = [
    # Models
    "SentimentType",
    "CategorySpan",
    "SubCategorySpan",
    "ElementSpan",
    "AttributeSpan",
    "Stage1Output",
    "Stage2Output",
    "Stage3Output",
    "Stage4Output",
    "ClassificationSpan",
    "FinalClassificationOutput",
    # Orchestrator
    "HierarchicalClassifier",
    # Runtime Components
    "PromptLoader",
    "DynamicSchemaGenerator",
    # Prompt Management - Generic (Multi-Stage)
    "build_prompt_from_yaml",
    "generate_python_function",
    "batch_generate_stage",
    "batch_generate_all_stages",
    "validate_prompt_yaml",
]
