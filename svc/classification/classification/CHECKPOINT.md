# Classification Project Checkpoint
**Date:** 2026-02-18
**Status:** Stage 1 Classification Complete & Evaluated

---

## 📊 Current Status

### ✅ Completed
1. **Multi-model testing infrastructure** - Test 6 AWQ models with timeout protection
2. **3-model consensus annotation** - Created 325 high-quality golden annotations
3. **Expanded golden dataset** - 345 total annotations (17x larger than original 20)
4. **Model evaluation** - All 6 models tested against expanded golden dataset
5. **File organization** - Cleaned and reorganized into folders

### 🎯 Best Performing Model
**Qwen-2.5-14B-AWQ** (tied with Llama-3.3-70B)
- **F1 Score:** 90.1%
- **Precision:** 84.2%
- **Recall:** 97.0%
- **Efficiency:** 5x smaller than Llama-70B, same performance
- **Recommended for production use**

---

## 📁 File Structure

```
classification/
├── CHECKPOINT.md                    # This file - project state snapshot
├── run_classification.py            # Main classification runner
├── scripts/                         # Utility scripts
│   ├── test_multi_model.py         # Test all models on test set
│   ├── validate_models.py          # Pre-validate models load correctly
│   ├── evaluate_metrics.py         # Calculate P/R/F1 metrics
│   ├── consensus_annotation.py     # Run 3-model consensus annotation
│   ├── combine_datasets.py         # Combine Excel files for annotation
│   ├── merge_golden_annotations.py # Merge consensus with original golden set
│   ├── annotate_batch.py           # Batch annotate with single model
│   ├── export_results_to_excel.py  # Convert JSON results to Excel
│   └── create_annotation_sample.py # Create stratified samples for annotation
├── data/                           # Data files
│   ├── golden_annotations.json     # ⭐ ACTIVE: 345 merged golden annotations
│   ├── golden_annotations_original.json  # Original 20 test cases (backup)
│   ├── consensus_golden_annotations.json # 325 consensus annotations
│   ├── combined_dataframe_400_comments.xlsx  # Combined dataset (200 fused + 200 conference)
│   └── annotation_template.json    # Template for annotations
├── docs/                           # Documentation
│   ├── ANNOTATION_GUIDE.md         # How to annotate comments
│   ├── ANNOTATION_PROCEDURE.md     # Annotation workflow
│   ├── EXCEL_EXPORT_GUIDE.md       # Excel export format
│   ├── IMPROVED_EXAMPLES.md        # Example classifications
│   └── TEST_CASES.md               # Test case definitions
├── runs/                           # Test run outputs
│   ├── multi_model_comparison_2026-02-18_12-13-28/  # ⭐ LATEST: 6 models on 345 golden set
│   │   ├── model_comparison_report.txt      # Summary results
│   │   ├── model_comparison_report.xlsx     # Detailed comparison
│   │   ├── results_qwen14b.json            # Qwen-14B results (best model)
│   │   ├── metrics_summary_qwen14b.json    # Qwen-14B metrics
│   │   └── ... (other model results)
│   ├── multi_model_comparison_2026-02-18_11-05-34/  # Earlier: 6 models on 20 golden set
│   └── run_2026-02-10_15-24-34_stage2/      # Stage 1 & 2 prompts (current)
│       └── python_previews/stage_1/
│           └── category_prompt_v3.py        # ⭐ Current Stage 1 prompt
├── utils/                          # Utility modules
│   ├── generate_shorthand_descriptions.py
│   ├── generate_skeleton_yamls.py
│   ├── preview_prompts.py
│   └── ... (other utilities)
└── prompt_templates/               # YAML prompt templates (if using)
```

---

## 🏆 Model Performance Summary

**Test Date:** 2026-02-18
**Golden Dataset:** 345 annotations (20 original + 325 consensus)
**Test Set:** 20 comments (5 real + 15 synthetic test cases)

| Rank | Model | F1 | Precision | Recall | Size | Notes |
|------|-------|------|-----------|--------|------|-------|
| **1** | **Qwen-14B** | **90.1%** | 84.2% | 97.0% | 14B | ⭐ **RECOMMENDED** |
| **1** | Llama-70B | **90.1%** | 84.2% | 97.0% | 70B | Same as Qwen-14B but 5x larger |
| 3 | Qwen-32B | 88.6% | 83.8% | 93.9% | 32B | Close third |
| 4 | Qwen-7B | 82.2% | 75.0% | 90.9% | 7B | Good small model |
| 5 | Llama-8B | 73.7% | 65.1% | 84.8% | 8B | - |
| 6 | Mistral-Nemo-12B | 71.1% | 62.8% | 81.8% | 12B | - |

**Category Performance (Average F1 across all models):**
- ✅ Venue & Hospitality: 97.6% (excellent)
- ✅ People & Community Interactions: 93.3% (excellent)
- ⚠️ Client Perceptions: 86.7% (good)
- ⚠️ Content & Learning Delivery: 78.2% (moderate)
- ❌ Event Experience & Technology: 69.6% (needs work)

---

## 🔑 Key Configuration

**GPU Setup:**
- GPUs: 6, 7
- Memory utilization: 0.95
- Tensor parallel size: 1 (all models)
- Max model length: 8192 tokens

**Model Details:**
```python
BEST_MODEL = {
    "name": "Qwen-2.5-14B-AWQ",
    "model_id": "Qwen/Qwen2.5-14B-Instruct-AWQ",
    "short_name": "qwen14b"
}
```

**Consensus Annotation:**
- Models used: Qwen-14B, Llama-70B, Qwen-32B
- Consensus rate: 81.2% (325/400 comments)
- Strategy: Keep excerpts/reasoning from Qwen-14B where all 3 agree

---

## 📝 Important Notes

### Golden Annotations
- **Current active file:** `data/golden_annotations.json` (345 annotations)
- Contains 20 original test cases + 325 consensus annotations
- Consensus annotations have `source: "consensus_3model"`
- Original annotations have `source: "real"` or `source: "synthetic"`

### Model Testing
- Test scripts use hardcoded test comments (20 total)
- Evaluation uses `data/golden_annotations.json` by default
- All models use V1 engine (no XFORMERS) for best performance
- Proper cleanup with `processor.terminate()` to avoid GPU memory leaks

### Stage 1 Classification
- Current prompt: `category_prompt_v3.py`
- Categories: 5 main categories
  1. Client Perceptions
  2. Content & Learning Delivery
  3. Event Experience & Technology
  4. People & Community Interactions
  5. Venue & Hospitality
- Output: Category + Sentiment + Reasoning + Excerpt

---

## 🚀 Next Steps

### Immediate (Not Started)
1. **Stage 2 Classification** - Sub-category level
   - Use hierarchical classifier with Stage 2 prompts
   - Test on subset first
   - Evaluate performance

2. **Production Classification** - Run on full datasets
   - Use Qwen-14B (best model)
   - Options:
     - All 1,289 comments from `fused_comments_output.xlsx`
     - All 498 comments from `conference_comments_annotated.xlsx`
     - Both datasets
   - Stage 1 only for now

### Future (Multi-Stage)
3. **Stage 3 Classification** - Element level
4. **Stage 4 Classification** - Attribute level
5. **Full Pipeline** - All 4 stages end-to-end

---

## 🔧 Common Commands

### Run Multi-Model Test
```bash
cd svc/classification/classification
python scripts/test_multi_model.py --models all
```

### Validate Models Before Testing
```bash
python scripts/validate_models.py --models all --gpu 6,7
```

### Run Consensus Annotation
```bash
python scripts/consensus_annotation.py \
  --excel data/combined_dataframe_400_comments.xlsx \
  --batch-size 10
```

### Merge Golden Annotations
```bash
python scripts/merge_golden_annotations.py \
  --existing data/golden_annotations_original.json \
  --consensus data/consensus_golden_annotations.json \
  --output data/golden_annotations_merged.json
```

### Evaluate Single Model
```bash
python scripts/evaluate_metrics.py runs/path/to/results_qwen14b.json
```

---

## 📚 External Data Sources

**Original Datasets:**
- `/data-fast/data3/clyde/projects/world/documents/annotator_files/fused_comments_output.xlsx`
  - 1,289 total comments
  - Column: `fused_comment`

- `/data-fast/data3/clyde/projects/world/documents/annotator_files/conference_comments_annotated.xlsx`
  - 498 total comments
  - Column: `comment`

**Combined Dataset (for annotation):**
- `data/combined_dataframe_400_comments.xlsx`
  - 200 from fused + 200 from conference
  - Used for creating consensus golden set

---

## ⚠️ Important Warnings

1. **Never commit large data files** - Excel/JSON files are in .gitignore
2. **Always use proper cleanup** - `processor.terminate()` before deletion
3. **Don't force push to main** - Use normal workflow
4. **Check golden annotations file** - Ensure using correct version
5. **Stage references** - Current prompts are in `run_2026-02-10_15-24-34_stage2`

---

## 🎓 What We Learned

1. **Consensus annotation works well** - 81.2% agreement across 3 models
2. **Qwen-14B is the sweet spot** - Best performance at reasonable size
3. **Larger datasets reveal true performance** - 90% vs 100% on small test set
4. **Event Experience & Technology is hardest** - May need better examples/rules
5. **3-model consensus is efficient** - Better than 5+ models with diminishing returns

---

## 📊 Performance Evolution

| Dataset | Annotations | Best Model | F1 Score | Date |
|---------|-------------|------------|----------|------|
| Original Test | 20 | Qwen-14B | 100% | 2026-02-18 (early) |
| Expanded Golden | 345 | Qwen-14B | 90.1% | 2026-02-18 (final) |

The drop from 100% to 90.1% is expected and healthy - it shows the larger dataset captures more realistic complexity.

---

## 📞 Contact & Resources

- **Project:** Hierarchical Multi-Stage Classifier for Conference Feedback
- **Library:** `lib/classifier` (UV workspace)
- **Service:** `svc/classification`
- **Python:** 3.13+
- **Package Manager:** UV
- **GPU:** CUDA required for inference

---

**Last Updated:** 2026-02-18
**Next Session:** Start with Stage 2 classification testing
