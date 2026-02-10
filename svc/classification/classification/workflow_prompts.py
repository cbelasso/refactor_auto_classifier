"""
Complete workflow: Export → Validate → Generate

Usage:
    python workflow_prompts.py
"""

from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from export_prompts_to_yaml import export_all_prompts
from test_generic_prompts import main as test_main


def main():
    templates_dir = Path("./prompt_templates")

    print("🔥" * 30)
    print("COMPLETE PROMPT WORKFLOW")
    print("🔥" * 30)

    # Step 1: Export
    print("\n")
    export_all_prompts(templates_dir)

    # Step 2: Validate & Generate
    print("\n")
    test_main()

    print("\n🔥" * 30)
    print("WORKFLOW COMPLETE!")
    print("🔥" * 30)


if __name__ == "__main__":
    main()
