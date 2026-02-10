from pathlib import Path

from classifier.draft_classifier import PromptLoader

loader = PromptLoader("./prompt_templates")

# Test Stage 1
test_comment = "The WiFi was terrible and the keynote speaker was amazing."
prompt = loader.load_stage1_prompt(test_comment)

print("STAGE 1 PROMPT:")
print("=" * 60)
print(prompt[:500])
print("...")

# Test Stage 2
prompt2 = loader.load_stage2_prompt(test_comment, "Event Experience & Technology")

print("\n\nSTAGE 2 PROMPT:")
print("=" * 60)
print(prompt2[:500])
print("...")
