"""
Preview Prompts - QA Tool

Generate Python files from YAML to preview what prompts will look like.
Output goes to /preview_prompts/ folder (not used in production).
"""

from pathlib import Path

from classifier.draft_classifier.prompt_manager_generic import (
    batch_generate_all_stages,
    validate_prompt_yaml,
)


def preview_all_prompts(templates_dir: str | Path, preview_dir: str | Path):
    """
    Generate Python preview files from all YAML templates.

    Args:
        templates_dir: Directory with stage_1/, stage_2/, etc.
        preview_dir: Where to save preview Python files
    """
    templates_dir = Path(templates_dir)
    preview_dir = Path(preview_dir)

    print("=" * 60)
    print("PREVIEW PROMPTS - QA WORKFLOW")
    print("=" * 60)

    # Step 1: Validate
    print("\n📋 Step 1: Validating YAML files...")
    yaml_files = list(templates_dir.rglob("*.yaml"))

    all_valid = True
    for yaml_file in yaml_files:
        errors = validate_prompt_yaml(yaml_file)
        if errors:
            print(f"\n❌ {yaml_file.relative_to(templates_dir)}:")
            for error in errors:
                print(f"  - {error}")
            all_valid = False

    if not all_valid:
        print("\n❌ Fix YAML errors before previewing")
        return

    print("✓ All YAML files valid")

    # Step 2: Generate preview files
    print("\n📝 Step 2: Generating preview Python files...")
    results = batch_generate_all_stages(templates_dir, preview_dir)

    total_files = sum(len(files) for files in results.values())

    print(f"\n✓ Generated {total_files} preview files")

    # Step 3: Show summary
    print("\n" + "=" * 60)
    print("PREVIEW FILES CREATED")
    print("=" * 60)

    for stage_name, files in sorted(results.items()):
        print(f"\n{stage_name}:")
        for f in files:
            print(f"  📄 {f.relative_to(preview_dir)}")

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"\n1. Review preview files in: {preview_dir}")
    print("2. If satisfied → Run classification (uses YAML directly)")
    print(f"3. If changes needed → Edit YAML in {templates_dir}")
    print("4. Re-run preview to see changes")
    print("\n⚠️  These preview files are for QA only - not used in production!")


if __name__ == "__main__":
    import sys

    templates_dir = Path("./prompt_templates")
    preview_dir = Path("./preview_prompts")

    preview_all_prompts(templates_dir, preview_dir)
