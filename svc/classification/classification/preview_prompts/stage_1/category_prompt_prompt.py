"""Generated Prompt - Stage 1"""

def category_prompt_prompt(comment: str) -> str:
    return f"""You are an expert conference feedback analyzer. Extract all category-level feedback from this comment.

COMMENT TO ANALYZE:
{comment}

---

CATEGORIES TO IDENTIFY:

**Client Perceptions**
Feedback about Explorance products, services, and the personal impact or outcomes experienced by attendees.
Elements include:
- Products & Services: Explorance software, tools, features, platform capabilities, product quality
- Personal Impact & Outcomes: Personal benefits gained, career growth, institutional improvements, ROI, value received

**Content & Learning Delivery**
Feedback about educational content, sessions, and knowledge gained at the conference.
Elements include:
- Knowledge & Engagement: What attendees learned, key takeaways, actionable insights, knowledge sharing, peer learning
- Session Formats & Materials: Presentations, workshops, panels, demos, session structure, handouts, resources, topics covered

**Event Experience & Technology**
Feedback about the overall conference experience and technology infrastructure.
Elements include:
- Event Technology: Conference apps, WiFi, A/V equipment, digital tools, technological setup
- Event Experience: Overall event quality, organization, scheduling, registration, communication, general conference management

**People & Community Interactions**
Feedback about people at the conference and community aspects.
Elements include:
- Community Interactions: Networking, sense of community, connecting with peers, social events, knowledge exchange among attendees
- People: Conference staff, speakers, presenters, experts, consultants, attendees, participants (the individuals themselves)

**Venue & Hospitality**
Feedback about physical location, facilities, and hospitality services.
Elements include:
- Conference Venue: Meeting rooms, facilities, accessibility, seating, temperature, physical space
- Food/Beverages: Meals, snacks, drinks, catering quality, dietary options
- Hotel: Accommodation, lodging arrangements, hotel quality
- Location (City): City location, travel to/from city, local area, destination appeal

---

CLASSIFICATION RULES:

1. Extract the EXACT excerpt from the comment that relates to each category.
2. A comment can have MULTIPLE category spans if it discusses multiple aspects.
3. Each excerpt should be classified to ONE category only.
4. Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).
5. "People" category = feedback about the INDIVIDUALS themselves; separate from what they presented or organized.
6. "Content & Learning Delivery" = what was taught/learned; "People" = who taught it.
7. General praise like "great conference" without specifics → Event Experience & Technology.
8. If a comment mentions both content AND the person delivering it, create separate spans for each category.

---

EXAMPLES:

Comment: "It was engaging and brought up many new ideas that I had not considered."
{"classifications": [{"excerpt": "It was engaging and brought up many new ideas that I had not considered", "reasoning": "Feedback about learning outcomes and new knowledge gained", "category": "Content & Learning Delivery", "sentiment": "positive"}]}

Comment: "MTM is a great tool that has improved our collection methods and ability to judge the results."
{"classifications": [{"excerpt": "MTM is a great tool that has improved our collection methods and ability to judge the results", "reasoning": "Praise for Explorance product and its institutional impact on processes and outcomes", "category": "Client Perceptions", "sentiment": "positive"}]}

Comment: "WiFi access during the conference. Or clearer directions on how to access it, since I wasn't able to find directions for connecting to the WiFi in the public areas of the hotel, and thus only had WiFi in my room, not during conference sessions."
{"classifications": [{"excerpt": "WiFi access during the conference. Or clearer directions on how to access it, since I wasn't able to find directions for connecting to the WiFi in the public areas of the hotel, and thus only had WiFi in my room, not during conference sessions", "reasoning": "Issues with WiFi infrastructure and communication about accessing it", "category": "Event Experience & Technology", "sentiment": "negative"}]}

Comment: "I hate conference apps."
{"classifications": [{"excerpt": "I hate conference apps", "reasoning": "Strong negative sentiment about conference technology", "category": "Event Experience & Technology", "sentiment": "negative"}]}

Comment: "Making new friends, and seeing old friends again - it's like a family reunion at Bluenotes. All the impromptu conversations and connections that we make while hanging out in the lobby, or sitting at lunch, or getting lost trying to find the next session room is the main reason I attend conferences in person."
{"classifications": [{"excerpt": "Making new friends, and seeing old friends again - it's like a family reunion at Bluenotes. All the impromptu conversations and connections that we make while hanging out in the lobby, or sitting at lunch, or getting lost trying to find the next session room is the main reason I attend conferences in person", "reasoning": "Emphasizes networking, community connections, and peer interactions", "category": "People & Community Interactions", "sentiment": "positive"}]}

Comment: "Bethany Remely and Alan Kully, wonderful resources."
{"classifications": [{"excerpt": "Bethany Remely and Alan Kully, wonderful resources", "reasoning": "Praise for specific individuals and their expertise", "category": "People & Community Interactions", "sentiment": "positive"}]}

Comment: "Getting to know the community and discovering that we are really facing many of the same problems. Hopefully we can solve some of these problems together."
{"classifications": [{"excerpt": "Getting to know the community and discovering that we are really facing many of the same problems. Hopefully we can solve some of these problems together", "reasoning": "Feedback about community connection and collaborative problem-solving among peers", "category": "People & Community Interactions", "sentiment": "positive"}]}

Comment: "The hotel that was recommended. I should have done some research prior and possibly booked elsewhere. The rooms were very small, the food not great and the service very slow."
{"classifications": [{"excerpt": "The hotel that was recommended. I should have done some research prior and possibly booked elsewhere. The rooms were very small", "reasoning": "Negative feedback about hotel room size and quality", "category": "Venue & Hospitality", "sentiment": "negative"}, {"excerpt": "the food not great and the service very slow", "reasoning": "Criticism of food quality and service", "category": "Venue & Hospitality", "sentiment": "negative"}]}

Comment: "Feeling valued as a conf presenter; seeing how Blue really works and how it can be expanded to serve the institution."
{"classifications": [{"excerpt": "Feeling valued as a conf presenter", "reasoning": "Personal experience as a conference presenter", "category": "Event Experience & Technology", "sentiment": "positive"}, {"excerpt": "seeing how Blue really works and how it can be expanded to serve the institution", "reasoning": "Learning about Explorance product capabilities and institutional applications", "category": "Client Perceptions", "sentiment": "positive"}]}

Comment: "Surandranath Gopinath is a customer service superstar! Some of the functionality and setup options, especially around Blue Connector and BPI, feel outdated and harder to navigate than necessary. I have raised a bug regarding data review after import which was fixed really quickly which is great."
{"classifications": [{"excerpt": "Surandranath Gopinath is a customer service superstar", "reasoning": "Praise for a specific Explorance staff member", "category": "People & Community Interactions", "sentiment": "positive"}, {"excerpt": "Some of the functionality and setup options, especially around Blue Connector and BPI, feel outdated and harder to navigate than necessary", "reasoning": "Criticism of Explorance product features and usability", "category": "Client Perceptions", "sentiment": "negative"}, {"excerpt": "I have raised a bug regarding data review after import which was fixed really quickly which is great", "reasoning": "Positive feedback about Explorance product support and bug resolution", "category": "Client Perceptions", "sentiment": "positive"}]}

Comment: "Scheduling was a big thing this year. Weekend workshops and then having Ex. World ending on a Wednesday are not ideal. The Westin was great as usual, clients were open and approachable, keynote sessions were engaging and informative."
{"classifications": [{"excerpt": "Scheduling was a big thing this year. Weekend workshops and then having Ex. World ending on a Wednesday are not ideal", "reasoning": "Criticism of conference scheduling and timing", "category": "Event Experience & Technology", "sentiment": "negative"}, {"excerpt": "The Westin was great as usual", "reasoning": "Positive feedback about venue quality", "category": "Venue & Hospitality", "sentiment": "positive"}, {"excerpt": "clients were open and approachable", "reasoning": "Praise for attendee interactions and accessibility", "category": "People & Community Interactions", "sentiment": "positive"}, {"excerpt": "keynote sessions were engaging and informative", "reasoning": "Positive feedback about session content and delivery", "category": "Content & Learning Delivery", "sentiment": "positive"}]}

Comment: "Diagrams of"
{"classifications": []}

---

Extract all relevant spans and return ONLY valid JSON matching the schema."""
