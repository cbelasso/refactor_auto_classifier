"""Generated Prompt - Stage 2: Client Perceptions"""

def client_perceptions_prompt(comment: str, category: str) -> str:
    return f"""You are an expert conference feedback analyzer. Extract sub-category feedback related to CLIENT PERCEPTIONS.

FOCUS: Client Perceptions

COMMENT TO ANALYZE:
{comment}

---

SUB-CATEGORIES TO IDENTIFY:

**Products & Services**
Feedback about Explorance products, tools, features, and services.
Elements include:
- Customer Experience: Overall experience using Explorance products
- Complaints: Issues, bugs, problems with products or services
- Intent to Buy: Interest in purchasing or upgrading products
- Intent to Leave: Dissatisfaction leading to consideration of alternatives
- Praise: Positive feedback about product quality and capabilities

**Personal Impact & Outcomes**
Feedback about personal benefits, growth, and institutional outcomes.
Elements include:
- Gained Knowledge: What was learned about using products or solving problems
- Mindset Shift: Changes in thinking or approach
- Emotional Impact: How the experience or product made them feel

---

CLASSIFICATION RULES:

1. Extract the EXACT excerpt from the comment that relates to each sub-category.
2. A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.
3. Each excerpt should be classified to ONE sub-category only.
4. Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).
5. "Products & Services" = feedback about the tools/features themselves.
6. "Personal Impact & Outcomes" = how it affected the person or their institution.

---

EXAMPLES:

Comment: "I have experimented with MLY and I think you're on the right track with the features."
{"classifications": [{"excerpt": "I have experimented with MLY and I think you're on the right track with the features", "reasoning": "Positive feedback about MLY product features and direction", "sub_category": "Products & Services", "sentiment": "positive"}]}

Comment: "Don't mind the low scores because I was being honest and it had nothing to do with my work role. My role has nothing to do with training people, but I was curious to see if I could apply some of the theory to my job of holding surveys and reporting the results. And I got some nice gems out of it."
{"classifications": [{"excerpt": "I got some nice gems out of it", "reasoning": "Personal takeaways and knowledge gained applicable to their work", "sub_category": "Personal Impact & Outcomes", "sentiment": "positive"}]}

Comment: "As a Microsoft Certified Trainer, the MTM platform provides valuable insights, but there are a few areas where enhancements could significantly improve both trainer and learner experience. We consistently encounter challenges when explaining the MTM surveys to students. Several students mistakenly assign low scores, unaware that 5 represents the highest rating. The lack of federated login complicates access. Some MCTs have experienced data loss after merging accounts."
{"classifications": [{"excerpt": "the MTM platform provides valuable insights", "reasoning": "Praise for product value and capabilities", "sub_category": "Products & Services", "sentiment": "positive"}, {"excerpt": "there are a few areas where enhancements could significantly improve both trainer and learner experience. We consistently encounter challenges when explaining the MTM surveys to students. Several students mistakenly assign low scores, unaware that 5 represents the highest rating. The lack of federated login complicates access. Some MCTs have experienced data loss after merging accounts", "reasoning": "Multiple complaints about usability issues, survey confusion, authentication, and data loss", "sub_category": "Products & Services", "sentiment": "negative"}]}

Comment: "We are inside our upgrade window for Blue 9. As to our goals being met, I marked Somewhat Agree because of the resistance to Blue Evaluations we still have at our institution. When we fully implemented a few years ago, a new group of faculty put up resistance. Because evaluations are voluntary, students feel their opinion does not matter."
{"classifications": [{"excerpt": "We are inside our upgrade window for Blue 9", "reasoning": "Reference to product upgrade intent", "sub_category": "Products & Services", "sentiment": "neutral"}, {"excerpt": "As to our goals being met, I marked Somewhat Agree because of the resistance to Blue Evaluations we still have at our institution. When we fully implemented a few years ago, a new group of faculty put up resistance. Because evaluations are voluntary, students feel their opinion does not matter", "reasoning": "Institutional challenges and mixed outcomes with product implementation", "sub_category": "Personal Impact & Outcomes", "sentiment": "mixed"}]}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""
