"""
Check which YAML files are required vs which exist.

Usage:
    python check_required_yamls.py
"""

from pathlib import Path

from classifier.draft_classifier import PromptLoader

# Configuration
PROMPT_TEMPLATES_DIR = "/data-fast/data3/clyde/projects/world/outputs/run_2026-02-10_10-23-34_stage2/yaml_templates"
HIERARCHY_PATH = "/data-fast/data3/clyde/projects/world/documents/schemas/schema_v2.json"


def main():
    loader = PromptLoader(templates_dir=PROMPT_TEMPLATES_DIR, hierarchy_path=HIERARCHY_PATH)

    required = loader.list_required_yamls()

    print("=" * 60)
    print("REQUIRED YAML FILES")
    print("=" * 60)

    total_required = 0
    total_existing = 0

    for stage, files in sorted(required.items()):
        print(f"\n{stage}/ ({len(files)} files required):")
        stage_existing = 0

        for filename in sorted(files):
            filepath = Path(PROMPT_TEMPLATES_DIR) / stage / filename
            exists = filepath.exists()
            status = "✓" if exists else "✗"
            print(f"  {status} {filename}")

            if exists:
                stage_existing += 1

        total_required += len(files)
        total_existing += stage_existing

        print(f"  ({stage_existing}/{len(files)} exist)")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total files required: {total_required}")
    print(f"Total files existing: {total_existing}")
    print(f"Missing: {total_required - total_existing}")

    if total_existing == total_required:
        print("\n✓ All required YAML files exist!")
    else:
        print(f"\n⚠️  {total_required - total_existing} YAML files need to be created")


if __name__ == "__main__":
    main()
