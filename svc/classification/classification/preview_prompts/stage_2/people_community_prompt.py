"""Generated Prompt - Stage 2: People & Community Interactions"""

def people_community_prompt(comment: str, category: str) -> str:
    return f"""You are an expert conference feedback analyzer. Extract sub-category feedback related to PEOPLE & COMMUNITY INTERACTIONS.

FOCUS: People & Community Interactions

COMMENT TO ANALYZE:
{comment}

---

SUB-CATEGORIES TO IDENTIFY:

**Community Interactions**
Feedback about networking, community connections, and social aspects.
Elements include:
- Community: Sense of belonging, community spirit, feeling welcomed
- Networking: Meeting people, professional connections, peer discussions
- Social Events: Gala dinners, receptions, informal gatherings

**People**
Feedback about specific individuals or groups at the conference.
Elements include:
- Conference Staff: Organizers, volunteers, support staff, Explorance team
- Experts/Consultants: Industry experts, product specialists, Explorance experts
- Participants/Attendees: Fellow attendees, other conference-goers, customers
- Speakers/Presenters: Keynote speakers, session presenters, panelists
- Unspecified Person: References to people without clear role identification

---

CLASSIFICATION RULES:

1. Extract the EXACT excerpt from the comment that relates to each sub-category.
2. A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.
3. Each excerpt should be classified to ONE sub-category only.
4. Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).
5. "Community Interactions" = networking, connecting, community building activities.
6. "People" = feedback about specific individuals or groups of people.

---

EXAMPLES:

Comment: "Samer is an engaging presenter."
{"classifications": [{"excerpt": "Samer is an engaging presenter", "reasoning": "Praise for a specific speaker/presenter", "sub_category": "People", "sentiment": "positive"}]}

Comment: "eXplorance staff were not as friendly as UofL staff. It would be helpful if eXplorance staff interacted more with the customers."
{"classifications": [{"excerpt": "eXplorance staff were not as friendly as UofL staff. It would be helpful if eXplorance staff interacted more with the customers", "reasoning": "Criticism of conference staff friendliness and customer interaction", "sub_category": "People", "sentiment": "negative"}]}

Comment: "Again another epic Bluenotes conference despite joining remotely. The ability to talk not only to Explorance Experts but to network with community members and share experiences made this an extremely valuable conference."
{"classifications": [{"excerpt": "The ability to talk not only to Explorance Experts", "reasoning": "Value of access to product experts", "sub_category": "People", "sentiment": "positive"}, {"excerpt": "to network with community members and share experiences", "reasoning": "Networking opportunities and peer connections", "sub_category": "Community Interactions", "sentiment": "positive"}]}

Comment: "New ideas, networking, hearing others have the same issues. Tech Zone!"
{"classifications": [{"excerpt": "networking", "reasoning": "Networking opportunities and connections", "sub_category": "Community Interactions", "sentiment": "positive"}]}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""
