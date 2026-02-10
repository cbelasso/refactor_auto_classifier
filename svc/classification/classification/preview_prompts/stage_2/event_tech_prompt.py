"""Generated Prompt - Stage 2: Event Experience & Technology"""

def event_tech_prompt(comment: str, category: str) -> str:
    return f"""You are an expert conference feedback analyzer. Extract sub-category feedback related to EVENT EXPERIENCE & TECHNOLOGY.

FOCUS: Event Experience & Technology

COMMENT TO ANALYZE:
{comment}

---

SUB-CATEGORIES TO IDENTIFY:

**Event Technology**
Feedback about conference technology infrastructure and tools.
Elements include:
- Conference Application/Software: Mobile apps, event platforms, digital tools
- Technological Tools: A/V equipment, microphones, projectors, tech setup
- Wi-Fi: Internet connectivity, network access

**Event Experience**
Feedback about overall conference organization and management.
Elements include:
- TechZone: Hands-on technology demonstration area
- Conference: General event organization, overall quality, event management
- Conference Registration: Sign-up process, check-in, badge pickup
- Conference Scheduling: Session timing, agenda, time management
- Messaging & Awareness: Communication, announcements, information clarity

---

CLASSIFICATION RULES:

1. Extract the EXACT excerpt from the comment that relates to each sub-category.
2. A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.
3. Each excerpt should be classified to ONE sub-category only.
4. Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).
5. "Event Technology" = technical infrastructure (WiFi, apps, A/V).
6. "Event Experience" = organizational aspects (scheduling, registration, communication).

---

EXAMPLES:

Comment: "Great job. It must be very tough planning a large scale event like this during the pandemic."
{"classifications": [{"excerpt": "Great job. It must be very tough planning a large scale event like this during the pandemic", "reasoning": "Praise for conference organization under challenging circumstances", "sub_category": "Event Experience", "sentiment": "positive"}]}

Comment: "New ideas, networking, hearing others have the same issues. Tech Zone!"
{"classifications": [{"excerpt": "Tech Zone!", "reasoning": "Positive feedback about the TechZone area", "sub_category": "Event Experience", "sentiment": "positive"}]}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""
