"""
Hierarchical Classifier Orchestrator

Multi-stage progressive classification system.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel

from .dynamic_schema import DynamicSchemaGenerator
from .models import (
    ClassificationSpan,
    FinalClassificationOutput,
)
from .prompt_loader import PromptLoader


class HierarchicalClassifier:
    """
    Multi-stage hierarchical classifier for conference comments.

    Usage:
        from classifier.draft_classifier import HierarchicalClassifier
        from new_processor import NewProcessor

        processor = NewProcessor(gpu_list=[0, 1], llm="mistralai/Mistral-Nemo-Instruct-2407")
        classifier = HierarchicalClassifier(
            processor=processor,
            prompt_templates_dir="./prompt_templates",
            hierarchy_path="./schema_v2.json"
        )

        # Run only categories + sub-categories
        results = classifier.classify_comments(comments, max_stage=2)

        # Run full 4-stage classification
        results = classifier.classify_comments(comments, max_stage=4)
    """

    def __init__(
        self,
        processor,
        prompt_templates_dir: str | Path,
        hierarchy_path: str | Path,
        guided_config: Optional[Dict] = None,
    ):
        """
        Initialize the hierarchical classifier.

        Args:
            processor: NewProcessor instance
            prompt_templates_dir: Path to YAML prompt templates
            hierarchy_path: Path to JSON hierarchy schema
            guided_config: Optional sampling params override
        """
        self.processor = processor
        self.prompt_loader = PromptLoader(prompt_templates_dir)
        self.schema_gen = DynamicSchemaGenerator(hierarchy_path)
        self.guided_config = guided_config or {
            "temperature": 0.1,
            "top_k": 50,
            "top_p": 0.95,
            "max_tokens": 1500,
        }

    def classify_comments(
        self,
        comments: List[str],
        max_stage: int = 4,
        batch_size: int = 25,
    ) -> List[FinalClassificationOutput]:
        """
        Run multi-stage hierarchical classification.

        Args:
            comments: List of comment strings to classify
            max_stage: Maximum stage depth (1-4)
            batch_size: Batch size for processing

        Returns:
            List of FinalClassificationOutput objects
        """
        if not 1 <= max_stage <= 4:
            raise ValueError(f"max_stage must be 1-4, got {max_stage}")

        num_comments = len(comments)

        # Stage 1: Category extraction
        print("=" * 60)
        print(f"STAGE 1: Category Extraction ({num_comments} comments)")
        print("=" * 60)

        stage1_results = self._run_stage1(comments, batch_size)

        if max_stage == 1:
            return self._build_final_output(comments, stage1_results)

        # Stage 2: Sub-category extraction
        print("=" * 60)
        print("STAGE 2: Sub-category Extraction")
        print("=" * 60)

        stage2_results = self._run_stage2(comments, stage1_results, batch_size)

        if max_stage == 2:
            return self._build_final_output(comments, stage1_results, stage2_results)

        # Stage 3: Element extraction
        print("=" * 60)
        print("STAGE 3: Element Extraction")
        print("=" * 60)

        stage3_results = self._run_stage3(comments, stage1_results, stage2_results, batch_size)

        if max_stage == 3:
            return self._build_final_output(
                comments, stage1_results, stage2_results, stage3_results
            )

        # Stage 4: Attribute extraction
        print("=" * 60)
        print("STAGE 4: Attribute Extraction")
        print("=" * 60)

        stage4_results = self._run_stage4(
            comments, stage1_results, stage2_results, stage3_results, batch_size
        )

        return self._build_final_output(
            comments, stage1_results, stage2_results, stage3_results, stage4_results
        )

    def _run_stage1(self, comments: List[str], batch_size: int) -> Dict[int, BaseModel]:
        """Run stage 1: category extraction."""
        prompts = [self.prompt_loader.load_stage1_prompt(c) for c in comments]

        # Generate dynamic schema
        Stage1Schema = self.schema_gen.get_stage1_schema()

        responses = self.processor.process_with_schema(
            prompts=prompts,
            schema=Stage1Schema,
            batch_size=batch_size,
            guided_config=self.guided_config,
        )

        parsed = self.processor.parse_results_with_schema(
            schema=Stage1Schema,
            responses=responses,
            validate=True,
        )

        # Map comment_idx -> Stage1Output
        return {i: result for i, result in enumerate(parsed) if result is not None}

    def _run_stage2(
        self,
        comments: List[str],
        stage1_results: Dict[int, BaseModel],
        batch_size: int,
    ) -> Dict[Tuple[int, str], BaseModel]:
        """Run stage 2: sub-category extraction per category."""
        # Group tasks by category (so we can use category-specific schemas)
        tasks_by_category = {}  # category -> [(comment_idx, comment, prompt)]

        for comment_idx, stage1_result in stage1_results.items():
            comment = comments[comment_idx]
            for cat_span in stage1_result.classifications:
                category = cat_span.category
                prompt = self.prompt_loader.load_stage2_prompt(comment, category)

                if category not in tasks_by_category:
                    tasks_by_category[category] = []
                tasks_by_category[category].append((comment_idx, comment, prompt))

        if not tasks_by_category:
            print("  No categories found, skipping stage 2")
            return {}

        total_tasks = sum(len(tasks) for tasks in tasks_by_category.values())
        print(
            f"  Processing {total_tasks} category contexts across {len(tasks_by_category)} categories"
        )

        # Process each category separately with its own schema
        all_results = {}

        for category, category_tasks in tasks_by_category.items():
            print(f"    → {category}: {len(category_tasks)} tasks")

            # Generate category-specific schema
            Stage2Schema = self.schema_gen.get_stage2_schema(category)

            task_indices = [(t[0], category) for t in category_tasks]
            task_prompts = [t[2] for t in category_tasks]

            responses = self.processor.process_with_schema(
                prompts=task_prompts,
                schema=Stage2Schema,  # Category-specific schema!
                batch_size=batch_size,
                guided_config=self.guided_config,
            )

            parsed = self.processor.parse_results_with_schema(
                schema=Stage2Schema,  # Category-specific schema!
                responses=responses,
                validate=True,
            )

            # Collect results for this category
            for (comment_idx, cat), result in zip(task_indices, parsed):
                if result is not None:
                    all_results[(comment_idx, cat)] = result

        return all_results

    def _run_stage3(
        self,
        comments: List[str],
        stage1_results: Dict[int, BaseModel],
        stage2_results: Dict[Tuple[int, str], BaseModel],
        batch_size: int,
    ) -> Dict[Tuple[int, str, str], BaseModel]:
        """Run stage 3: element extraction per sub-category."""
        # Group tasks by (category, sub_category)
        tasks_by_subcat = {}  # (category, sub_category) -> [(comment_idx, comment, prompt)]

        for (comment_idx, category), stage2_result in stage2_results.items():
            comment = comments[comment_idx]
            for subcat_span in stage2_result.classifications:
                sub_category = subcat_span.sub_category
                prompt = self.prompt_loader.load_stage3_prompt(comment, category, sub_category)

                key = (category, sub_category)
                if key not in tasks_by_subcat:
                    tasks_by_subcat[key] = []
                tasks_by_subcat[key].append((comment_idx, comment, prompt))

        if not tasks_by_subcat:
            print("  No sub-categories found, skipping stage 3")
            return {}

        total_tasks = sum(len(tasks) for tasks in tasks_by_subcat.values())
        print(
            f"  Processing {total_tasks} sub-category contexts across {len(tasks_by_subcat)} sub-categories"
        )

        # Process each sub-category separately with its own schema
        all_results = {}

        for (category, sub_category), subcat_tasks in tasks_by_subcat.items():
            print(f"    → {category} / {sub_category}: {len(subcat_tasks)} tasks")

            # Generate sub-category-specific schema
            Stage3Schema = self.schema_gen.get_stage3_schema(category, sub_category)

            task_indices = [(t[0], category, sub_category) for t in subcat_tasks]
            task_prompts = [t[2] for t in subcat_tasks]

            responses = self.processor.process_with_schema(
                prompts=task_prompts,
                schema=Stage3Schema,
                batch_size=batch_size,
                guided_config=self.guided_config,
            )

            parsed = self.processor.parse_results_with_schema(
                schema=Stage3Schema,
                responses=responses,
                validate=True,
            )

            # Collect results
            for (comment_idx, cat, subcat), result in zip(task_indices, parsed):
                if result is not None:
                    all_results[(comment_idx, cat, subcat)] = result

        return all_results

    def _run_stage4(
        self,
        comments: List[str],
        stage1_results: Dict[int, BaseModel],
        stage2_results: Dict[Tuple[int, str], BaseModel],
        stage3_results: Dict[Tuple[int, str, str], BaseModel],
        batch_size: int,
    ) -> Dict[Tuple[int, str, str, str], BaseModel]:
        """Run stage 4: attribute extraction per element."""
        # Group tasks by (category, sub_category, element)
        tasks_by_element = {}  # (category, sub_category, element) -> [(comment_idx, comment, prompt)]

        for (comment_idx, category, sub_category), stage3_result in stage3_results.items():
            comment = comments[comment_idx]
            for elem_span in stage3_result.classifications:
                element = elem_span.element
                prompt = self.prompt_loader.load_stage4_prompt(
                    comment, category, sub_category, element
                )

                key = (category, sub_category, element)
                if key not in tasks_by_element:
                    tasks_by_element[key] = []
                tasks_by_element[key].append((comment_idx, comment, prompt))

        if not tasks_by_element:
            print("  No elements found, skipping stage 4")
            return {}

        total_tasks = sum(len(tasks) for tasks in tasks_by_element.values())
        print(
            f"  Processing {total_tasks} element contexts across {len(tasks_by_element)} elements"
        )

        # Process each element separately with its own schema
        all_results = {}

        for (category, sub_category, element), element_tasks in tasks_by_element.items():
            print(f"    → {category} / {sub_category} / {element}: {len(element_tasks)} tasks")

            # Generate element-specific schema
            Stage4Schema = self.schema_gen.get_stage4_schema(category, sub_category, element)

            task_indices = [(t[0], category, sub_category, element) for t in element_tasks]
            task_prompts = [t[2] for t in element_tasks]

            responses = self.processor.process_with_schema(
                prompts=task_prompts,
                schema=Stage4Schema,
                batch_size=batch_size,
                guided_config=self.guided_config,
            )

            parsed = self.processor.parse_results_with_schema(
                schema=Stage4Schema,
                responses=responses,
                validate=True,
            )

            # Collect results
            for (comment_idx, cat, subcat, elem), result in zip(task_indices, parsed):
                if result is not None:
                    all_results[(comment_idx, cat, subcat, elem)] = result

        return all_results

    def _build_final_output(
        self,
        comments: List[str],
        stage1_results: Dict[int, BaseModel],
        stage2_results: Optional[Dict[Tuple[int, str], BaseModel]] = None,
        stage3_results: Optional[Dict[Tuple[int, str, str], BaseModel]] = None,
        stage4_results: Optional[Dict[Tuple[int, str, str, str], BaseModel]] = None,
    ) -> List[FinalClassificationOutput]:
        """Combine all stage results into final output with full traceability."""

        final_outputs = []

        for comment_idx, comment in enumerate(comments):
            classifications = []

            # Get stage 1 results
            stage1_result = stage1_results.get(comment_idx)
            if stage1_result is None:
                # No classifications for this comment
                final_outputs.append(
                    FinalClassificationOutput(
                        original_comment=comment,
                        classifications=[],
                    )
                )
                continue

            # If only stage 1 was run
            if stage2_results is None:
                for cat_span in stage1_result.classifications:
                    classifications.append(
                        ClassificationSpan(
                            category=cat_span.category,
                            stage1_excerpt=cat_span.excerpt,
                            stage1_reasoning=cat_span.reasoning,
                            stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                        )
                    )

            # If stage 2 was run
            elif stage3_results is None:
                for cat_span in stage1_result.classifications:
                    category = cat_span.category
                    stage2_result = stage2_results.get((comment_idx, category))

                    if stage2_result is None or not stage2_result.classifications:
                        # Category detected but no sub-categories
                        classifications.append(
                            ClassificationSpan(
                                category=category,
                                stage1_excerpt=cat_span.excerpt,
                                stage1_reasoning=cat_span.reasoning,
                                stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                            )
                        )
                    else:
                        for subcat_span in stage2_result.classifications:
                            classifications.append(
                                ClassificationSpan(
                                    category=category,
                                    stage1_excerpt=cat_span.excerpt,
                                    stage1_reasoning=cat_span.reasoning,
                                    stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                                    sub_category=subcat_span.sub_category,
                                    stage2_excerpt=subcat_span.excerpt,
                                    stage2_reasoning=subcat_span.reasoning,
                                    stage2_sentiment=subcat_span.sentiment,  # Read from .sentiment
                                )
                            )

            # If stage 3 was run
            elif stage4_results is None:
                for cat_span in stage1_result.classifications:
                    category = cat_span.category
                    stage2_result = stage2_results.get((comment_idx, category))

                    if stage2_result is None:
                        continue

                    for subcat_span in stage2_result.classifications:
                        sub_category = subcat_span.sub_category
                        stage3_result = stage3_results.get(
                            (comment_idx, category, sub_category)
                        )

                        if stage3_result is None or not stage3_result.classifications:
                            classifications.append(
                                ClassificationSpan(
                                    category=category,
                                    stage1_excerpt=cat_span.excerpt,
                                    stage1_reasoning=cat_span.reasoning,
                                    stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                                    sub_category=sub_category,
                                    stage2_excerpt=subcat_span.excerpt,
                                    stage2_reasoning=subcat_span.reasoning,
                                    stage2_sentiment=subcat_span.sentiment,  # Read from .sentiment
                                )
                            )
                        else:
                            for elem_span in stage3_result.classifications:
                                classifications.append(
                                    ClassificationSpan(
                                        category=category,
                                        stage1_excerpt=cat_span.excerpt,
                                        stage1_reasoning=cat_span.reasoning,
                                        stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                                        sub_category=sub_category,
                                        stage2_excerpt=subcat_span.excerpt,
                                        stage2_reasoning=subcat_span.reasoning,
                                        stage2_sentiment=subcat_span.sentiment,  # Read from .sentiment
                                        element=elem_span.element,
                                        stage3_excerpt=elem_span.excerpt,
                                        stage3_reasoning=elem_span.reasoning,
                                        stage3_sentiment=elem_span.sentiment,  # Read from .sentiment
                                    )
                                )

            # If stage 4 was run (full hierarchy)
            else:
                for cat_span in stage1_result.classifications:
                    category = cat_span.category
                    stage2_result = stage2_results.get((comment_idx, category))

                    if stage2_result is None:
                        continue

                    for subcat_span in stage2_result.classifications:
                        sub_category = subcat_span.sub_category
                        stage3_result = stage3_results.get(
                            (comment_idx, category, sub_category)
                        )

                        if stage3_result is None:
                            continue

                        for elem_span in stage3_result.classifications:
                            element = elem_span.element
                            stage4_result = stage4_results.get(
                                (comment_idx, category, sub_category, element)
                            )

                            if stage4_result is None or not stage4_result.classifications:
                                classifications.append(
                                    ClassificationSpan(
                                        category=category,
                                        stage1_excerpt=cat_span.excerpt,
                                        stage1_reasoning=cat_span.reasoning,
                                        stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                                        sub_category=sub_category,
                                        stage2_excerpt=subcat_span.excerpt,
                                        stage2_reasoning=subcat_span.reasoning,
                                        stage2_sentiment=subcat_span.sentiment,  # Read from .sentiment
                                        element=element,
                                        stage3_excerpt=elem_span.excerpt,
                                        stage3_reasoning=elem_span.reasoning,
                                        stage3_sentiment=elem_span.sentiment,  # Read from .sentiment
                                    )
                                )
                            else:
                                for attr_span in stage4_result.classifications:
                                    classifications.append(
                                        ClassificationSpan(
                                            category=category,
                                            stage1_excerpt=cat_span.excerpt,
                                            stage1_reasoning=cat_span.reasoning,
                                            stage1_sentiment=cat_span.sentiment,  # Read from .sentiment
                                            sub_category=sub_category,
                                            stage2_excerpt=subcat_span.excerpt,
                                            stage2_reasoning=subcat_span.reasoning,
                                            stage2_sentiment=subcat_span.sentiment,  # Read from .sentiment
                                            element=element,
                                            stage3_excerpt=elem_span.excerpt,
                                            stage3_reasoning=elem_span.reasoning,
                                            stage3_sentiment=elem_span.sentiment,  # Read from .sentiment
                                            attribute=attr_span.attribute,
                                            stage4_excerpt=attr_span.excerpt,
                                            stage4_reasoning=attr_span.reasoning,
                                            stage4_sentiment=attr_span.sentiment,  # Read from .sentiment
                                        )
                                    )

            final_outputs.append(
                FinalClassificationOutput(
                    original_comment=comment,
                    classifications=classifications,
                )
            )

        return final_outputs

    def results_to_dataframe(self, results: List[FinalClassificationOutput]):
        """Convert results to pandas DataFrame (exploded format)."""
        import pandas as pd

        all_records = []
        for result in results:
            all_records.extend(result.to_records())

        return pd.DataFrame(all_records)
