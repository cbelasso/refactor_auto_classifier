"""Generated Prompt - Stage 2: Content & Learning Delivery"""

def content_learning_prompt(comment: str, category: str) -> str:
    return f"""You are an expert conference feedback analyzer. Extract sub-category feedback related to CONTENT & LEARNING DELIVERY.

FOCUS: Content & Learning Delivery

COMMENT TO ANALYZE:
{comment}

---

SUB-CATEGORIES TO IDENTIFY:

**Knowledge & Engagement**
Feedback about learning, engagement, and knowledge sharing.
Elements include:
- Knowledge Sharing: Peer-to-peer learning, sharing experiences
- Open Discussion: Q&A, audience participation, interactive discussions
- Session/Workshop: Hands-on learning, workshop activities, breakout sessions
- Topics: Subject matter, themes, content relevance

**Session Formats & Materials**
Feedback about how content was delivered and session resources.
Elements include:
- Demonstration: Live demos, product showcases, hands-on examples
- Panel Discussions: Multi-speaker panels, panel quality
- Session/Workshop Presentations: Individual talks, presentation quality
- Resources/Materials: Handouts, slides, documentation, learning materials

---

CLASSIFICATION RULES:

1. Extract the EXACT excerpt from the comment that relates to each sub-category.
2. A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.
3. Each excerpt should be classified to ONE sub-category only.
4. Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).
5. "Knowledge & Engagement" = what was learned or discussed.
6. "Session Formats & Materials" = how it was delivered or what materials were provided.

---

EXAMPLES:

Comment: "Interactive and engaging"
{"classifications": [{"excerpt": "Interactive and engaging", "reasoning": "Positive feedback about session interactivity and engagement quality", "sub_category": "Knowledge & Engagement", "sentiment": "positive"}]}

Comment: "Well-presented and explained"
{"classifications": [{"excerpt": "Well-presented and explained", "reasoning": "Positive feedback about presentation delivery quality", "sub_category": "Session Formats & Materials", "sentiment": "positive"}]}

Comment: "Workshop activities did not seem prepared."
{"classifications": [{"excerpt": "Workshop activities did not seem prepared", "reasoning": "Criticism of workshop preparation and execution", "sub_category": "Session Formats & Materials", "sentiment": "negative"}]}

Comment: "New ideas, networking, hearing others have the same issues. Tech Zone!"
{"classifications": [{"excerpt": "New ideas", "reasoning": "Learning new concepts and takeaways", "sub_category": "Knowledge & Engagement", "sentiment": "positive"}, {"excerpt": "hearing others have the same issues", "reasoning": "Peer learning and knowledge sharing", "sub_category": "Knowledge & Engagement", "sentiment": "positive"}]}

Comment: "The content wasn't in the area of my role in my organization but it really resonated as I see it happening around me."
{"classifications": [{"excerpt": "The content wasn't in the area of my role in my organization but it really resonated as I see it happening around me", "reasoning": "Feedback about topic relevance and personal connection to content", "sub_category": "Knowledge & Engagement", "sentiment": "mixed"}]}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""
