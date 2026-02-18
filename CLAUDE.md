# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **hierarchical multi-stage classifier** for conference feedback analysis. It uses LLMs to progressively classify free-text comments into a 4-level taxonomy (Category → Sub-category → Element → Attribute), extracting sentiment at each stage.

The project is built as a **UV workspace monorepo** with:
- **lib/classifier**: Core classification library with reusable components
- **svc/classification**: Service for running classifications on conference comments
- **svc/preprocessing**: Service for converting Excel taxonomy definitions to JSON schemas

## Development Environment

### Setup
```bash
# Install dependencies (UV workspace-aware)
uv sync

# Activate virtual environment (direnv automatically activates if installed)
source .venv/bin/activate
```

### Running Services

**Run classification:**
```bash
cd svc/classification
python classification/run_classification.py
```

**Convert taxonomy Excel to JSON schema:**
```bash
cd svc/preprocessing
python preprocessing/format_definition_file_to_json_schema.py
```

**Generate skeleton YAML prompt templates:**
```bash
cd svc/classification
python classification/utils/generate_skeleton_yamls.py
```

**Preview prompts as Python code:**
```bash
cd svc/classification
python classification/utils/preview_prompts.py
```

## Architecture

### Multi-Stage Classification Pipeline

The classifier processes comments through up to 4 progressive stages:

1. **Stage 1 (Category)**: Extract top-level categories from comment (e.g., "Event Experience & Technology")
2. **Stage 2 (Sub-category)**: For each category span, extract sub-categories (e.g., "Event Technology")
3. **Stage 3 (Element)**: For each sub-category span, extract elements (e.g., "Conference Application/Software")
4. **Stage 4 (Attribute)**: For each element span, extract specific attributes (e.g., "Registration Process")

Each stage:
- Operates on **spans** (excerpts) from the comment
- Extracts **sentiment** (positive/negative/neutral/mixed)
- Provides **reasoning** for classification
- Uses a **dedicated YAML prompt template** with examples and rules

### Key Components

**HierarchicalClassifier** (`lib/classifier/src/classifier/draft_classifier/orchestrator.py`):
- Main orchestrator that runs the multi-stage pipeline
- Accepts `max_stage` parameter (1-4) to control depth
- Processes comments in batches using GPU-accelerated LLM inference
- Tracks YAML usage for reporting

**PromptLoader** (`lib/classifier/src/classifier/draft_classifier/prompt_loader.py`):
- Loads YAML prompt templates from `prompt_templates/stage_N/` directories
- Validates that templates are marked `ready: true` before use
- Builds runtime prompts by injecting examples, rules, and context

**DynamicSchemaGenerator** (`lib/classifier/src/classifier/draft_classifier/dynamic_schema.py`):
- Generates constrained Pydantic schemas for LLM structured outputs
- Dynamically filters valid options based on hierarchy path (e.g., only show sub-categories valid for the current category)

**HierarchyNavigator** (`lib/classifier/src/classifier/utils/hierarchy_navigator.py`):
- Traverse the 4-level taxonomy JSON hierarchy
- Query valid children at each level (e.g., "what sub-categories exist under this category?")
- Fast lookup via cached indices

**HierarchyBuilder** (`lib/classifier/src/classifier/utils/json_hierarchy_builder.py`):
- Convert Excel taxonomy definitions (with columns like Category, Sub-category, Element, Attribute) to JSON hierarchy
- Validates structure and logs warnings for issues

**ShorthandUpdater** (`lib/classifier/src/classifier/utils/shorthand_updater.py`):
- Add/update shorthand descriptions in the hierarchy JSON
- Used for generating concise labels in prompts

### Prompt Template Format

YAML templates in `svc/classification/classification/prompt_templates/stage_N/` follow this structure:

```yaml
ready: true  # Must be true to be used; false = skip
prompt_metadata:
  stage: 2
  focus: "Category > Sub-category"
  task: "Extract sub-category feedback"
  version: "1.0"
system_prompt: "You are an expert..."
task_description: "Extract sub-category feedback related to..."
labels_title: "SUB-CATEGORIES TO IDENTIFY"
label_field: "sub_category"  # Field name in Pydantic model
labels:
  - name: "Venue & Facilities"
    description: "Feedback about physical spaces..."
    context_items:  # Stage 2+ only
      - "Registration Area: Check-in process..."
      - "Venue Location: Accessibility..."
rules:
  - "Extract EXACT excerpts from comment"
  - "Each excerpt maps to ONE label only"
  - "Sentiment: positive/negative/neutral/mixed"
examples:
  - comment: "The venue was great but registration was slow"
    classifications:
      - excerpt: "venue was great"
        reasoning: "Praise for the venue"
        sub_category: "Venue & Facilities"
        sentiment: positive
      - excerpt: "registration was slow"
        reasoning: "Criticism of registration speed"
        sub_category: "Registration & Check-in"
        sentiment: negative
```

### Data Flow

1. **Input**: Excel file with comments + JSON hierarchy schema
2. **Stage 1**: Classify entire comment → extract category spans
3. **Stage 2**: For each category span → extract sub-category spans
4. **Stage 3**: For each sub-category span → extract element spans
5. **Stage 4**: For each element span → extract attribute spans
6. **Output**:
   - JSON with full structured results (`FinalClassificationOutput` objects)
   - Excel/CSV with flattened rows (one row per classification span)
   - YAML usage report showing which templates were used/skipped

### Versioned Runs

The classification service creates versioned output directories per run:
```
outputs/run_2025-01-15_14-30-00_stage2/
├── run_metadata.json           # Configuration snapshot
├── yaml_templates/             # Copy of YAML templates used
├── python_previews/            # Python code generated from YAMLs
└── results/
    ├── results.json            # Structured output
    ├── results.xlsx            # Flattened tabular format
    ├── results.csv
    └── yaml_usage_report.txt   # Which YAMLs were used
```

This ensures reproducibility: you can see exactly which prompts and config produced each run's results.

## Important Patterns

### Workspace Dependencies

The UV workspace uses `[tool.uv.sources]` to reference workspace members:
```toml
[tool.uv.sources]
classifier = { workspace = true }  # Reference lib/classifier
```

Always use `uv sync` (not `pip install`) to respect workspace dependencies.

### LLM Integration

The project depends on `llm-parallelization` (an internal library from Azure DevOps):
```python
from llm_parallelization.new_processor import NewProcessor, NEMO

processor = NewProcessor(
    gpu_list=[6, 7],
    llm=NEMO,  # Model identifier
    gpu_memory_utilization=0.85,
    max_model_len=8192
)
```

The processor handles batch inference with constrained generation (Pydantic schemas).

### Pydantic Models

All classification outputs use Pydantic models in `lib/classifier/src/classifier/draft_classifier/models.py`:
- `Stage1Output`, `Stage2Output`, `Stage3Output`, `Stage4Output` (per-stage outputs)
- `ClassificationSpan` (final merged classification with all stages)
- `FinalClassificationOutput` (per-comment results)

These models define the structured output schema for LLM generation.

### YAML Validation

Before running classification:
1. Generate skeleton YAMLs: `generate_skeleton_yamls.py`
2. Edit descriptions, examples, and rules
3. Set `ready: true` when complete
4. Validate with `check_required_yamls.py` or `validate_prompt_yaml()`

YAMLs marked `ready: false` are skipped at runtime.

## File Naming Conventions

YAML templates use snake_case filenames derived from labels:
- "Event Experience & Technology" → `event_experience_and_technology.yaml`
- "Wi-Fi" → `wi_fi.yaml`
- "Food/Beverages" → `food_beverages.yaml`

See `label_to_filename()` in `generate_skeleton_yamls.py`.

## Git Ignore Notes

The `.gitignore` excludes:
- `*.yaml`, `*.json`, `*.csv`, `*.xlsx` (data files)
- `prompt_templates/` directories (generated/user-specific)
- `.envrc` files (user-specific direnv config)

When working with prompt templates, they are NOT version-controlled. Each user maintains their own templates locally.

## External Dependencies

- **Python 3.13**: Project requires Python 3.13+
- **UV**: Package manager (install via `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Direnv**: Optional but recommended for auto-activating venv
- **GPU**: Classification requires CUDA-compatible GPUs for LLM inference
- **llm-parallelization**: Internal Azure DevOps library (credentials required)
