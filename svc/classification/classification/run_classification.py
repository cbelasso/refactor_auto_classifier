"""
Run hierarchical classification on conference comments with versioned outputs.

Usage:
    python run_classification.py
"""

from datetime import datetime
import json
from pathlib import Path
import shutil

# Import classifier components
from classifier.draft_classifier import HierarchicalClassifier
from classifier.draft_classifier.prompt_manager_generic import batch_generate_all_stages
from classifier.utils import save_dataframe, save_json

# Import your processor
from llm_parallelization.new_processor import NEMO, NewProcessor
import pandas as pd


def main():
    # ============================================================
    # Configuration
    # ============================================================

    INPUT_FILE = "/data-fast/data3/clyde/projects/world/documents/annotator_files/conference_comments_annotated.xlsx"
    COMMENT_COLUMN = "comment"
    HIERARCHY_PATH = "/data-fast/data3/clyde/projects/world/documents/schemas/schema_v2.json"
    PROMPT_TEMPLATES_DIR = "./prompt_templates"

    # Processor configuration
    GPU_LIST = [6, 7]
    LLM_MODEL = NEMO
    BATCH_SIZE = 25

    # Classification configuration
    MAX_STAGE = 2

    # Create versioned output directory
    TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    RUN_NAME = f"run_{TIMESTAMP}_stage{MAX_STAGE}"
    BASE_OUTPUT_DIR = Path(f"/data-fast/data3/clyde/projects/world/outputs/{RUN_NAME}")
    BASE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Output subdirectories
    YAML_OUTPUT_DIR = BASE_OUTPUT_DIR / "yaml_templates"
    PYTHON_OUTPUT_DIR = BASE_OUTPUT_DIR / "python_previews"
    RESULTS_DIR = BASE_OUTPUT_DIR / "results"
    RESULTS_DIR.mkdir(exist_ok=True)

    # ============================================================
    # Save Run Metadata
    # ============================================================

    print("=" * 60)
    print(f"HIERARCHICAL CLASSIFICATION - {RUN_NAME}")
    print("=" * 60)

    metadata = {
        "timestamp": TIMESTAMP,
        "run_name": RUN_NAME,
        "configuration": {
            "gpu_list": GPU_LIST,
            "llm_model": LLM_MODEL,
            "max_stage": MAX_STAGE,
            "batch_size": BATCH_SIZE,
        },
        "paths": {
            "input_file": str(INPUT_FILE),
            "hierarchy_path": str(HIERARCHY_PATH),
            "prompt_templates_dir": str(PROMPT_TEMPLATES_DIR),
        },
        "output_structure": {
            "yaml_templates": str(YAML_OUTPUT_DIR),
            "python_previews": str(PYTHON_OUTPUT_DIR),
            "results": str(RESULTS_DIR),
        },
    }

    metadata_file = BASE_OUTPUT_DIR / "run_metadata.json"
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Saved run metadata to: {metadata_file}")

    # ============================================================
    # Version Control: Copy YAML Templates
    # ============================================================

    print("\n" + "=" * 60)
    print("COPYING YAML TEMPLATES")
    print("=" * 60)

    shutil.copytree(PROMPT_TEMPLATES_DIR, YAML_OUTPUT_DIR, dirs_exist_ok=True)
    yaml_count = len(list(YAML_OUTPUT_DIR.rglob("*.yaml")))
    print(f"✓ Copied {yaml_count} YAML files to: {YAML_OUTPUT_DIR}")

    # ============================================================
    # Version Control: Generate Python Previews
    # ============================================================

    print("\n" + "=" * 60)
    print("GENERATING PYTHON PREVIEWS")
    print("=" * 60)

    results_map = batch_generate_all_stages(YAML_OUTPUT_DIR, PYTHON_OUTPUT_DIR)
    total_py_files = sum(len(files) for files in results_map.values())
    print(f"✓ Generated {total_py_files} Python preview files")
    for stage_name, files in sorted(results_map.items()):
        print(f"  {stage_name}: {len(files)} files")

    # ============================================================
    # Load Data
    # ============================================================

    print("\n" + "=" * 60)
    print("LOADING DATA")
    print("=" * 60)

    df = pd.read_excel(INPUT_FILE).iloc[:10]  # Test on first 10
    print(f"Loaded {len(df)} rows from {INPUT_FILE}")

    if COMMENT_COLUMN not in df.columns:
        raise ValueError(f"Column '{COMMENT_COLUMN}' not found in Excel file")

    comments = df[COMMENT_COLUMN].fillna("").astype(str).tolist()
    print(f"Extracted {len(comments)} comments")

    # ============================================================
    # Initialize Processor
    # ============================================================

    print("\n" + "=" * 60)
    print("INITIALIZING PROCESSOR")
    print("=" * 60)

    processor = NewProcessor(
        gpu_list=GPU_LIST, llm=LLM_MODEL, gpu_memory_utilization=0.85, max_model_len=2048 * 4
    )
    print(f"✓ Processor initialized with model: {LLM_MODEL}")
    print(f"✓ Using GPUs: {GPU_LIST}")

    # ============================================================
    # Run Classification
    # ============================================================

    print("\n" + "=" * 60)
    print(f"RUNNING CLASSIFICATION (MAX_STAGE={MAX_STAGE})")
    print("=" * 60)

    classifier = HierarchicalClassifier(
        processor=processor,
        prompt_templates_dir=str(YAML_OUTPUT_DIR),  # Use versioned YAMLs!
        hierarchy_path=HIERARCHY_PATH,
    )

    results = classifier.classify_comments(
        comments=comments,
        max_stage=MAX_STAGE,
        batch_size=BATCH_SIZE,
    )

    print(f"\nClassification complete! Processed {len(results)} comments")

    # ============================================================
    # Save Results
    # ============================================================

    print("\n" + "=" * 60)
    print("SAVING RESULTS")
    print("=" * 60)

    # Save as JSON (full structured output)
    json_output = RESULTS_DIR / "results.json"
    json_data = [result.model_dump() for result in results]
    save_json(json_data, json_output)
    print(f"✓ Saved JSON to: {json_output}")

    # Save as DataFrame (exploded format for analysis)
    df_results = classifier.results_to_dataframe(results)

    excel_output = RESULTS_DIR / "results.xlsx"
    save_dataframe(df_results, excel_output)
    print(f"✓ Saved Excel to: {excel_output}")

    csv_output = RESULTS_DIR / "results.csv"
    save_dataframe(df_results, csv_output)
    print(f"✓ Saved CSV to: {csv_output}")

    # Generate and save YAML usage report
    yaml_report = classifier.generate_yaml_usage_report(max_stage=MAX_STAGE)  # Pass max_stage
    report_file = RESULTS_DIR / "yaml_usage_report.txt"

    with open(report_file, "w") as f:
        f.write(yaml_report)
    print(f"✓ Saved YAML usage report to: {report_file}")

    # Also print to console
    print("\n" + yaml_report)

    # ============================================================
    # Summary Statistics
    # ============================================================

    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)

    print(f"\nTotal comments processed: {len(comments)}")
    print(f"Comments with classifications: {len([r for r in results if r.classifications])}")
    print(f"Empty classifications: {len([r for r in results if not r.classifications])}")
    print(f"Total classification spans: {len(df_results)}")

    print("\nCategory distribution:")
    category_counts = df_results["category"].value_counts()
    for category, count in category_counts.items():
        print(f"  {category}: {count}")

    # Sentiment distribution per stage
    print("\nSentiment distribution:")

    # Count sentiments from the most granular stage available per row
    sentiment_cols = [
        "stage4_sentiment",
        "stage3_sentiment",
        "stage2_sentiment",
        "stage1_sentiment",
    ]
    sentiments = []

    for _, row in df_results.iterrows():
        # Use the most specific sentiment available
        for col in sentiment_cols:
            if pd.notna(row[col]):
                sentiments.append(row[col])
                break

    if sentiments:
        sentiment_counts = pd.Series(sentiments).value_counts()
        for sentiment, count in sentiment_counts.items():
            print(f"  {sentiment}: {count}")
    else:
        print("  No sentiments found")

    # Sentiment by stage
    print("\nSentiment by stage:")
    for i in range(1, MAX_STAGE + 1):
        col = f"stage{i}_sentiment"
        if col in df_results.columns:
            stage_sentiments = df_results[col].dropna()
            if not stage_sentiments.empty:
                print(f"  Stage {i}:")
                for sentiment, count in stage_sentiments.value_counts().items():
                    print(f"    {sentiment}: {count}")

    # ============================================================
    # Final Summary
    # ============================================================

    print("\n" + "=" * 60)
    print("RUN COMPLETE!")
    print("=" * 60)
    print(f"\n📁 All outputs saved to: {BASE_OUTPUT_DIR}")
    print("\nDirectory structure:")
    print(" ├── run_metadata.json        (run configuration)")
    print(f" ├── yaml_templates/          ({yaml_count} YAML files)")
    print(f" ├── python_previews/         ({total_py_files} Python files)")
    print(" └── results/")
    print("      ├── results.json")
    print("      ├── results.xlsx")
    print("      └── results.csv")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
