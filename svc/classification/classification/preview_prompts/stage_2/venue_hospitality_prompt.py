"""Generated Prompt - Stage 2: Venue & Hospitality"""

def venue_hospitality_prompt(comment: str, category: str) -> str:
    return f"""You are an expert conference feedback analyzer. Extract sub-category feedback related to VENUE & HOSPITALITY.

FOCUS: Venue & Hospitality

COMMENT TO ANALYZE:
{comment}

---

SUB-CATEGORIES TO IDENTIFY:

**Conference Venue**
Feedback about conference meeting spaces and facilities.
Elements include:
- Accessibility: Ease of access, disability accommodations
- Arrangement: Room setup, layout, space configuration
- Cleanliness: Facility cleanliness and maintenance
- Comfort Level: Temperature, seating comfort, lighting
- Safety & Security: Safety measures, security presence

**Food/Beverages**
Feedback about meals, snacks, and beverages provided.
Elements include:
- Accessibility: Ease of accessing food/beverages
- Availability: Food options available, timing of meals
- Cost: Pricing of food and beverages
- Variety: Range of options, dietary accommodations

**Hotel**
Feedback about accommodation and lodging.
Elements include:
- Accessibility: Ease of access to hotel
- Arrangement: Room setup and amenities
- Cleanliness: Room and hotel cleanliness
- Comfort Level: Bed quality, temperature, noise
- Cost: Room pricing and value
- Safety & Security: Hotel security and safety
- Value: Overall value for money

**Location (City)**
Feedback about the city or destination where the conference was held.

---

CLASSIFICATION RULES:

1. Extract the EXACT excerpt from the comment that relates to each sub-category.
2. A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.
3. Each excerpt should be classified to ONE sub-category only.
4. Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).
5. "Conference Venue" = meeting rooms and conference facilities.
6. "Food/Beverages" = meals, snacks, catering.
7. "Hotel" = accommodation and lodging.
8. "Location (City)" = the destination city itself.

---

EXAMPLES:

Comment: "The hotel was way too cold including the guest rooms as well."
{"classifications": [{"excerpt": "The hotel was way too cold including the guest rooms as well", "reasoning": "Complaint about hotel temperature and comfort", "sub_category": "Hotel", "sentiment": "negative"}]}

Comment: "Knowing in advance about full breakfast vs. continental. May sound trivial but yoghurt-fruit are insufficient fuel for my morning. Tuesday's breakfast was too light. Weds morning ate in restaurant, only to discover conference had full breakfast. So skipped restaurant Thurs, but by the time I discovered conference had continental breakfast again, too late to get more substantial food before first session started."
{"classifications": [{"excerpt": "Knowing in advance about full breakfast vs. continental. May sound trivial but yoghurt-fruit are insufficient fuel for my morning. Tuesday's breakfast was too light", "reasoning": "Complaint about breakfast variety and advance communication", "sub_category": "Food/Beverages", "sentiment": "negative"}, {"excerpt": "Weds morning ate in restaurant, only to discover conference had full breakfast. So skipped restaurant Thurs, but by the time I discovered conference had continental breakfast again, too late to get more substantial food before first session started", "reasoning": "Confusion about food availability and poor communication", "sub_category": "Food/Beverages", "sentiment": "negative"}]}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""
