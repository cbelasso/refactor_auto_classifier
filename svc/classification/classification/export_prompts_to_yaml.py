"""
Export current prompts to generic YAML format.
Run this once to create all YAML template files.
"""

from pathlib import Path

from ruamel.yaml import YAML


def export_stage1_yaml(output_dir: Path):
    """Export Stage 1 category prompt."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    data = {
        "prompt_metadata": {
            "stage": 1,
            "task": "Extract all category-level feedback from this comment",
            "version": "1.0",
        },
        "labels_title": "CATEGORIES TO IDENTIFY",
        "label_field": "category",
        "labels": [
            {
                "name": "Client Perceptions",
                "description": "Feedback about Explorance products, services, and the personal impact or outcomes experienced by attendees.",
                "context_items": [
                    "Products & Services: Explorance software, tools, features, platform capabilities, product quality",
                    "Personal Impact & Outcomes: Personal benefits gained, career growth, institutional improvements, ROI, value received",
                ],
            },
            {
                "name": "Content & Learning Delivery",
                "description": "Feedback about educational content, sessions, and knowledge gained at the conference.",
                "context_items": [
                    "Knowledge & Engagement: What attendees learned, key takeaways, actionable insights, knowledge sharing, peer learning",
                    "Session Formats & Materials: Presentations, workshops, panels, demos, session structure, handouts, resources, topics covered",
                ],
            },
            {
                "name": "Event Experience & Technology",
                "description": "Feedback about the overall conference experience and technology infrastructure.",
                "context_items": [
                    "Event Technology: Conference apps, WiFi, A/V equipment, digital tools, technological setup",
                    "Event Experience: Overall event quality, organization, scheduling, registration, communication, general conference management",
                ],
            },
            {
                "name": "People & Community Interactions",
                "description": "Feedback about people at the conference and community aspects.",
                "context_items": [
                    "Community Interactions: Networking, sense of community, connecting with peers, social events, knowledge exchange among attendees",
                    "People: Conference staff, speakers, presenters, experts, consultants, attendees, participants (the individuals themselves)",
                ],
            },
            {
                "name": "Venue & Hospitality",
                "description": "Feedback about physical location, facilities, and hospitality services.",
                "context_items": [
                    "Conference Venue: Meeting rooms, facilities, accessibility, seating, temperature, physical space",
                    "Food/Beverages: Meals, snacks, drinks, catering quality, dietary options",
                    "Hotel: Accommodation, lodging arrangements, hotel quality",
                    "Location (City): City location, travel to/from city, local area, destination appeal",
                ],
            },
        ],
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each category.",
            "A comment can have MULTIPLE category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
            '"People" category = feedback about the INDIVIDUALS themselves; separate from what they presented or organized.',
            '"Content & Learning Delivery" = what was taught/learned; "People" = who taught it.',
            'General praise like "great conference" without specifics → Event Experience & Technology.',
            "If a comment mentions both content AND the person delivering it, create separate spans for each category.",
        ],
        "examples": [
            {
                "comment": "It was engaging and brought up many new ideas that I had not considered.",
                "classifications": [
                    {
                        "excerpt": "It was engaging and brought up many new ideas that I had not considered",
                        "reasoning": "Feedback about learning outcomes and new knowledge gained",
                        "category": "Content & Learning Delivery",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "MTM is a great tool that has improved our collection methods and ability to judge the results.",
                "classifications": [
                    {
                        "excerpt": "MTM is a great tool that has improved our collection methods and ability to judge the results",
                        "reasoning": "Praise for Explorance product and its institutional impact on processes and outcomes",
                        "category": "Client Perceptions",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "WiFi access during the conference. Or clearer directions on how to access it, since I wasn't able to find directions for connecting to the WiFi in the public areas of the hotel, and thus only had WiFi in my room, not during conference sessions.",
                "classifications": [
                    {
                        "excerpt": "WiFi access during the conference. Or clearer directions on how to access it, since I wasn't able to find directions for connecting to the WiFi in the public areas of the hotel, and thus only had WiFi in my room, not during conference sessions",
                        "reasoning": "Issues with WiFi infrastructure and communication about accessing it",
                        "category": "Event Experience & Technology",
                        "sentiment": "negative",
                    }
                ],
            },
            {
                "comment": "I hate conference apps.",
                "classifications": [
                    {
                        "excerpt": "I hate conference apps",
                        "reasoning": "Strong negative sentiment about conference technology",
                        "category": "Event Experience & Technology",
                        "sentiment": "negative",
                    }
                ],
            },
            {
                "comment": "Making new friends, and seeing old friends again - it's like a family reunion at Bluenotes. All the impromptu conversations and connections that we make while hanging out in the lobby, or sitting at lunch, or getting lost trying to find the next session room is the main reason I attend conferences in person.",
                "classifications": [
                    {
                        "excerpt": "Making new friends, and seeing old friends again - it's like a family reunion at Bluenotes. All the impromptu conversations and connections that we make while hanging out in the lobby, or sitting at lunch, or getting lost trying to find the next session room is the main reason I attend conferences in person",
                        "reasoning": "Emphasizes networking, community connections, and peer interactions",
                        "category": "People & Community Interactions",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "Bethany Remely and Alan Kully, wonderful resources.",
                "classifications": [
                    {
                        "excerpt": "Bethany Remely and Alan Kully, wonderful resources",
                        "reasoning": "Praise for specific individuals and their expertise",
                        "category": "People & Community Interactions",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "Getting to know the community and discovering that we are really facing many of the same problems. Hopefully we can solve some of these problems together.",
                "classifications": [
                    {
                        "excerpt": "Getting to know the community and discovering that we are really facing many of the same problems. Hopefully we can solve some of these problems together",
                        "reasoning": "Feedback about community connection and collaborative problem-solving among peers",
                        "category": "People & Community Interactions",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "The hotel that was recommended. I should have done some research prior and possibly booked elsewhere. The rooms were very small, the food not great and the service very slow.",
                "classifications": [
                    {
                        "excerpt": "The hotel that was recommended. I should have done some research prior and possibly booked elsewhere. The rooms were very small",
                        "reasoning": "Negative feedback about hotel room size and quality",
                        "category": "Venue & Hospitality",
                        "sentiment": "negative",
                    },
                    {
                        "excerpt": "the food not great and the service very slow",
                        "reasoning": "Criticism of food quality and service",
                        "category": "Venue & Hospitality",
                        "sentiment": "negative",
                    },
                ],
            },
            {
                "comment": "Feeling valued as a conf presenter; seeing how Blue really works and how it can be expanded to serve the institution.",
                "classifications": [
                    {
                        "excerpt": "Feeling valued as a conf presenter",
                        "reasoning": "Personal experience as a conference presenter",
                        "category": "Event Experience & Technology",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "seeing how Blue really works and how it can be expanded to serve the institution",
                        "reasoning": "Learning about Explorance product capabilities and institutional applications",
                        "category": "Client Perceptions",
                        "sentiment": "positive",
                    },
                ],
            },
            {
                "comment": "Surandranath Gopinath is a customer service superstar! Some of the functionality and setup options, especially around Blue Connector and BPI, feel outdated and harder to navigate than necessary. I have raised a bug regarding data review after import which was fixed really quickly which is great.",
                "classifications": [
                    {
                        "excerpt": "Surandranath Gopinath is a customer service superstar",
                        "reasoning": "Praise for a specific Explorance staff member",
                        "category": "People & Community Interactions",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "Some of the functionality and setup options, especially around Blue Connector and BPI, feel outdated and harder to navigate than necessary",
                        "reasoning": "Criticism of Explorance product features and usability",
                        "category": "Client Perceptions",
                        "sentiment": "negative",
                    },
                    {
                        "excerpt": "I have raised a bug regarding data review after import which was fixed really quickly which is great",
                        "reasoning": "Positive feedback about Explorance product support and bug resolution",
                        "category": "Client Perceptions",
                        "sentiment": "positive",
                    },
                ],
            },
            {
                "comment": "Scheduling was a big thing this year. Weekend workshops and then having Ex. World ending on a Wednesday are not ideal. The Westin was great as usual, clients were open and approachable, keynote sessions were engaging and informative.",
                "classifications": [
                    {
                        "excerpt": "Scheduling was a big thing this year. Weekend workshops and then having Ex. World ending on a Wednesday are not ideal",
                        "reasoning": "Criticism of conference scheduling and timing",
                        "category": "Event Experience & Technology",
                        "sentiment": "negative",
                    },
                    {
                        "excerpt": "The Westin was great as usual",
                        "reasoning": "Positive feedback about venue quality",
                        "category": "Venue & Hospitality",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "clients were open and approachable",
                        "reasoning": "Praise for attendee interactions and accessibility",
                        "category": "People & Community Interactions",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "keynote sessions were engaging and informative",
                        "reasoning": "Positive feedback about session content and delivery",
                        "category": "Content & Learning Delivery",
                        "sentiment": "positive",
                    },
                ],
            },
            {
                "comment": "Diagrams of",
                "classifications": [],
            },
        ],
    }

    output_file = output_dir / "category_prompt.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w") as f:
        f.write("# Stage 1: Category Classification\n")
        f.write("# Edit categories, rules, and examples as needed\n\n")
        yaml.dump(data, f)

    print(f"✓ Exported Stage 1: {output_file}")
    return output_file


def export_stage2_client_perceptions_yaml(output_dir: Path):
    """Export Stage 2 - Client Perceptions."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    data = {
        "prompt_metadata": {
            "stage": 2,
            "focus": "Client Perceptions",
            "task": "Extract sub-category feedback related to CLIENT PERCEPTIONS",
            "version": "1.0",
        },
        # NEW: Customizable fields
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": "Extract sub-category feedback related to CLIENT PERCEPTIONS",
        "custom_instructions": "",  # Optional additional instructions
        "labels_title": "SUB-CATEGORIES TO IDENTIFY",
        "label_field": "sub_category",
        "labels": [
            {
                "name": "Products & Services",
                "description": "Feedback about Explorance products, tools, features, and services.",
                "context_items": [
                    "Customer Experience: Overall experience using Explorance products",
                    "Complaints: Issues, bugs, problems with products or services",
                    "Intent to Buy: Interest in purchasing or upgrading products",
                    "Intent to Leave: Dissatisfaction leading to consideration of alternatives",
                    "Praise: Positive feedback about product quality and capabilities",
                ],
            },
            {
                "name": "Personal Impact & Outcomes",
                "description": "Feedback about personal benefits, growth, and institutional outcomes.",
                "context_items": [
                    "Gained Knowledge: What was learned about using products or solving problems",
                    "Mindset Shift: Changes in thinking or approach",
                    "Emotional Impact: How the experience or product made them feel",
                ],
            },
        ],
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each sub-category.",
            "A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE sub-category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
            '"Products & Services" = feedback about the tools/features themselves.',
            '"Personal Impact & Outcomes" = how it affected the person or their institution.',
        ],
        "examples": [
            {
                "comment": "I have experimented with MLY and I think you're on the right track with the features.",
                "classifications": [
                    {
                        "excerpt": "I have experimented with MLY and I think you're on the right track with the features",
                        "reasoning": "Positive feedback about MLY product features and direction",
                        "sub_category": "Products & Services",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "Don't mind the low scores because I was being honest and it had nothing to do with my work role. My role has nothing to do with training people, but I was curious to see if I could apply some of the theory to my job of holding surveys and reporting the results. And I got some nice gems out of it.",
                "classifications": [
                    {
                        "excerpt": "I got some nice gems out of it",
                        "reasoning": "Personal takeaways and knowledge gained applicable to their work",
                        "sub_category": "Personal Impact & Outcomes",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "As a Microsoft Certified Trainer, the MTM platform provides valuable insights, but there are a few areas where enhancements could significantly improve both trainer and learner experience. We consistently encounter challenges when explaining the MTM surveys to students. Several students mistakenly assign low scores, unaware that 5 represents the highest rating. The lack of federated login complicates access. Some MCTs have experienced data loss after merging accounts.",
                "classifications": [
                    {
                        "excerpt": "the MTM platform provides valuable insights",
                        "reasoning": "Praise for product value and capabilities",
                        "sub_category": "Products & Services",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "there are a few areas where enhancements could significantly improve both trainer and learner experience. We consistently encounter challenges when explaining the MTM surveys to students. Several students mistakenly assign low scores, unaware that 5 represents the highest rating. The lack of federated login complicates access. Some MCTs have experienced data loss after merging accounts",
                        "reasoning": "Multiple complaints about usability issues, survey confusion, authentication, and data loss",
                        "sub_category": "Products & Services",
                        "sentiment": "negative",
                    },
                ],
            },
            {
                "comment": "We are inside our upgrade window for Blue 9. As to our goals being met, I marked Somewhat Agree because of the resistance to Blue Evaluations we still have at our institution. When we fully implemented a few years ago, a new group of faculty put up resistance. Because evaluations are voluntary, students feel their opinion does not matter.",
                "classifications": [
                    {
                        "excerpt": "We are inside our upgrade window for Blue 9",
                        "reasoning": "Reference to product upgrade intent",
                        "sub_category": "Products & Services",
                        "sentiment": "neutral",
                    },
                    {
                        "excerpt": "As to our goals being met, I marked Somewhat Agree because of the resistance to Blue Evaluations we still have at our institution. When we fully implemented a few years ago, a new group of faculty put up resistance. Because evaluations are voluntary, students feel their opinion does not matter",
                        "reasoning": "Institutional challenges and mixed outcomes with product implementation",
                        "sub_category": "Personal Impact & Outcomes",
                        "sentiment": "mixed",
                    },
                ],
            },
        ],
    }

    output_file = output_dir / "client_perceptions.yaml"
    output_file.parent.mkdir(parents=True, exist_ok=True)  # ADD THIS LINE

    with open(output_file, "w") as f:
        f.write("# Stage 2: Client Perceptions Sub-categories\n\n")
        yaml.dump(data, f)

    print(f"✓ Exported Stage 2 - Client Perceptions: {output_file}")
    return output_file


def export_stage2_content_learning_yaml(output_dir: Path):
    """Export Stage 2 - Content & Learning Delivery."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    data = {
        "prompt_metadata": {
            "stage": 2,
            "focus": "Content & Learning Delivery",
            "task": "Extract sub-category feedback related to CONTENT & LEARNING DELIVERY",
            "version": "1.0",
        },
        # NEW: Customizable fields
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": "Extract sub-category feedback related to CONTENT & LEARNING DELIVERY",
        "custom_instructions": "",  # Optional additional instructions
        "labels_title": "SUB-CATEGORIES TO IDENTIFY",
        "label_field": "sub_category",
        "labels": [
            {
                "name": "Knowledge & Engagement",
                "description": "Feedback about learning, engagement, and knowledge sharing.",
                "context_items": [
                    "Knowledge Sharing: Peer-to-peer learning, sharing experiences",
                    "Open Discussion: Q&A, audience participation, interactive discussions",
                    "Session/Workshop: Hands-on learning, workshop activities, breakout sessions",
                    "Topics: Subject matter, themes, content relevance",
                ],
            },
            {
                "name": "Session Formats & Materials",
                "description": "Feedback about how content was delivered and session resources.",
                "context_items": [
                    "Demonstration: Live demos, product showcases, hands-on examples",
                    "Panel Discussions: Multi-speaker panels, panel quality",
                    "Session/Workshop Presentations: Individual talks, presentation quality",
                    "Resources/Materials: Handouts, slides, documentation, learning materials",
                ],
            },
        ],
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each sub-category.",
            "A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE sub-category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
            '"Knowledge & Engagement" = what was learned or discussed.',
            '"Session Formats & Materials" = how it was delivered or what materials were provided.',
        ],
        "examples": [
            {
                "comment": "Interactive and engaging",
                "classifications": [
                    {
                        "excerpt": "Interactive and engaging",
                        "reasoning": "Positive feedback about session interactivity and engagement quality",
                        "sub_category": "Knowledge & Engagement",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "Well-presented and explained",
                "classifications": [
                    {
                        "excerpt": "Well-presented and explained",
                        "reasoning": "Positive feedback about presentation delivery quality",
                        "sub_category": "Session Formats & Materials",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "Workshop activities did not seem prepared.",
                "classifications": [
                    {
                        "excerpt": "Workshop activities did not seem prepared",
                        "reasoning": "Criticism of workshop preparation and execution",
                        "sub_category": "Session Formats & Materials",
                        "sentiment": "negative",
                    }
                ],
            },
            {
                "comment": "New ideas, networking, hearing others have the same issues. Tech Zone!",
                "classifications": [
                    {
                        "excerpt": "New ideas",
                        "reasoning": "Learning new concepts and takeaways",
                        "sub_category": "Knowledge & Engagement",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "hearing others have the same issues",
                        "reasoning": "Peer learning and knowledge sharing",
                        "sub_category": "Knowledge & Engagement",
                        "sentiment": "positive",
                    },
                ],
            },
            {
                "comment": "The content wasn't in the area of my role in my organization but it really resonated as I see it happening around me.",
                "classifications": [
                    {
                        "excerpt": "The content wasn't in the area of my role in my organization but it really resonated as I see it happening around me",
                        "reasoning": "Feedback about topic relevance and personal connection to content",
                        "sub_category": "Knowledge & Engagement",
                        "sentiment": "mixed",
                    }
                ],
            },
        ],
    }

    output_file = output_dir / "content_learning.yaml"
    with open(output_file, "w") as f:
        f.write("# Stage 2: Content & Learning Delivery Sub-categories\n\n")
        yaml.dump(data, f)

    print(f"✓ Exported Stage 2 - Content & Learning: {output_file}")
    return output_file


def export_stage2_event_tech_yaml(output_dir: Path):
    """Export Stage 2 - Event Experience & Technology."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    data = {
        "prompt_metadata": {
            "stage": 2,
            "focus": "Event Experience & Technology",
            "task": "Extract sub-category feedback related to EVENT EXPERIENCE & TECHNOLOGY",
            "version": "1.0",
        },
        # NEW: Customizable fields
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": "Extract sub-category feedback related to EVENT EXPERIENCE & TECHNOLOGY",
        "custom_instructions": "",  # Optional additional instructions
        "labels_title": "SUB-CATEGORIES TO IDENTIFY",
        "label_field": "sub_category",
        "labels": [
            {
                "name": "Event Technology",
                "description": "Feedback about conference technology infrastructure and tools.",
                "context_items": [
                    "Conference Application/Software: Mobile apps, event platforms, digital tools",
                    "Technological Tools: A/V equipment, microphones, projectors, tech setup",
                    "Wi-Fi: Internet connectivity, network access",
                ],
            },
            {
                "name": "Event Experience",
                "description": "Feedback about overall conference organization and management.",
                "context_items": [
                    "TechZone: Hands-on technology demonstration area",
                    "Conference: General event organization, overall quality, event management",
                    "Conference Registration: Sign-up process, check-in, badge pickup",
                    "Conference Scheduling: Session timing, agenda, time management",
                    "Messaging & Awareness: Communication, announcements, information clarity",
                ],
            },
        ],
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each sub-category.",
            "A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE sub-category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
            '"Event Technology" = technical infrastructure (WiFi, apps, A/V).',
            '"Event Experience" = organizational aspects (scheduling, registration, communication).',
        ],
        "examples": [
            {
                "comment": "Great job. It must be very tough planning a large scale event like this during the pandemic.",
                "classifications": [
                    {
                        "excerpt": "Great job. It must be very tough planning a large scale event like this during the pandemic",
                        "reasoning": "Praise for conference organization under challenging circumstances",
                        "sub_category": "Event Experience",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "New ideas, networking, hearing others have the same issues. Tech Zone!",
                "classifications": [
                    {
                        "excerpt": "Tech Zone!",
                        "reasoning": "Positive feedback about the TechZone area",
                        "sub_category": "Event Experience",
                        "sentiment": "positive",
                    }
                ],
            },
        ],
    }

    output_file = output_dir / "event_tech.yaml"
    with open(output_file, "w") as f:
        f.write("# Stage 2: Event Experience & Technology Sub-categories\n\n")
        yaml.dump(data, f)

    print(f"✓ Exported Stage 2 - Event Tech: {output_file}")
    return output_file


def export_stage2_people_community_yaml(output_dir: Path):
    """Export Stage 2 - People & Community Interactions."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    data = {
        "prompt_metadata": {
            "stage": 2,
            "focus": "People & Community Interactions",
            "task": "Extract sub-category feedback related to PEOPLE & COMMUNITY INTERACTIONS",
            "version": "1.0",
        },
        # NEW: Customizable fields
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": "Extract sub-category feedback related to PEOPLE & COMMUNITY INTERACTIONS",
        "custom_instructions": "",  # Optional additional instructions
        "labels_title": "SUB-CATEGORIES TO IDENTIFY",
        "label_field": "sub_category",
        "labels": [
            {
                "name": "Community Interactions",
                "description": "Feedback about networking, community connections, and social aspects.",
                "context_items": [
                    "Community: Sense of belonging, community spirit, feeling welcomed",
                    "Networking: Meeting people, professional connections, peer discussions",
                    "Social Events: Gala dinners, receptions, informal gatherings",
                ],
            },
            {
                "name": "People",
                "description": "Feedback about specific individuals or groups at the conference.",
                "context_items": [
                    "Conference Staff: Organizers, volunteers, support staff, Explorance team",
                    "Experts/Consultants: Industry experts, product specialists, Explorance experts",
                    "Participants/Attendees: Fellow attendees, other conference-goers, customers",
                    "Speakers/Presenters: Keynote speakers, session presenters, panelists",
                    "Unspecified Person: References to people without clear role identification",
                ],
            },
        ],
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each sub-category.",
            "A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE sub-category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
            '"Community Interactions" = networking, connecting, community building activities.',
            '"People" = feedback about specific individuals or groups of people.',
        ],
        "examples": [
            {
                "comment": "Samer is an engaging presenter.",
                "classifications": [
                    {
                        "excerpt": "Samer is an engaging presenter",
                        "reasoning": "Praise for a specific speaker/presenter",
                        "sub_category": "People",
                        "sentiment": "positive",
                    }
                ],
            },
            {
                "comment": "eXplorance staff were not as friendly as UofL staff. It would be helpful if eXplorance staff interacted more with the customers.",
                "classifications": [
                    {
                        "excerpt": "eXplorance staff were not as friendly as UofL staff. It would be helpful if eXplorance staff interacted more with the customers",
                        "reasoning": "Criticism of conference staff friendliness and customer interaction",
                        "sub_category": "People",
                        "sentiment": "negative",
                    }
                ],
            },
            {
                "comment": "Again another epic Bluenotes conference despite joining remotely. The ability to talk not only to Explorance Experts but to network with community members and share experiences made this an extremely valuable conference.",
                "classifications": [
                    {
                        "excerpt": "The ability to talk not only to Explorance Experts",
                        "reasoning": "Value of access to product experts",
                        "sub_category": "People",
                        "sentiment": "positive",
                    },
                    {
                        "excerpt": "to network with community members and share experiences",
                        "reasoning": "Networking opportunities and peer connections",
                        "sub_category": "Community Interactions",
                        "sentiment": "positive",
                    },
                ],
            },
            {
                "comment": "New ideas, networking, hearing others have the same issues. Tech Zone!",
                "classifications": [
                    {
                        "excerpt": "networking",
                        "reasoning": "Networking opportunities and connections",
                        "sub_category": "Community Interactions",
                        "sentiment": "positive",
                    }
                ],
            },
        ],
    }

    output_file = output_dir / "people_community.yaml"
    with open(output_file, "w") as f:
        f.write("# Stage 2: People & Community Interactions Sub-categories\n\n")
        yaml.dump(data, f)

    print(f"✓ Exported Stage 2 - People & Community: {output_file}")
    return output_file


def export_stage2_venue_hospitality_yaml(output_dir: Path):
    """Export Stage 2 - Venue & Hospitality."""
    yaml = YAML()
    yaml.default_flow_style = False
    yaml.width = 4096

    data = {
        "prompt_metadata": {
            "stage": 2,
            "focus": "Venue & Hospitality",
            "task": "Extract sub-category feedback related to VENUE & HOSPITALITY",
            "version": "1.0",
        },
        # NEW: Customizable fields
        "system_prompt": "You are an expert conference feedback analyzer.",
        "task_description": "Extract sub-category feedback related to VENUE & HOSPITALITY",
        "custom_instructions": "",  # Optional additional instructions
        "labels_title": "SUB-CATEGORIES TO IDENTIFY",
        "label_field": "sub_category",
        "labels": [
            {
                "name": "Conference Venue",
                "description": "Feedback about conference meeting spaces and facilities.",
                "context_items": [
                    "Accessibility: Ease of access, disability accommodations",
                    "Arrangement: Room setup, layout, space configuration",
                    "Cleanliness: Facility cleanliness and maintenance",
                    "Comfort Level: Temperature, seating comfort, lighting",
                    "Safety & Security: Safety measures, security presence",
                ],
            },
            {
                "name": "Food/Beverages",
                "description": "Feedback about meals, snacks, and beverages provided.",
                "context_items": [
                    "Accessibility: Ease of accessing food/beverages",
                    "Availability: Food options available, timing of meals",
                    "Cost: Pricing of food and beverages",
                    "Variety: Range of options, dietary accommodations",
                ],
            },
            {
                "name": "Hotel",
                "description": "Feedback about accommodation and lodging.",
                "context_items": [
                    "Accessibility: Ease of access to hotel",
                    "Arrangement: Room setup and amenities",
                    "Cleanliness: Room and hotel cleanliness",
                    "Comfort Level: Bed quality, temperature, noise",
                    "Cost: Room pricing and value",
                    "Safety & Security: Hotel security and safety",
                    "Value: Overall value for money",
                ],
            },
            {
                "name": "Location (City)",
                "description": "Feedback about the city or destination where the conference was held.",
            },
        ],
        "rules": [
            "Extract the EXACT excerpt from the comment that relates to each sub-category.",
            "A comment can have MULTIPLE sub-category spans if it discusses multiple aspects.",
            "Each excerpt should be classified to ONE sub-category only.",
            "Sentiment: positive (praise), negative (criticism), neutral (observation), mixed (both positive and negative).",
            '"Conference Venue" = meeting rooms and conference facilities.',
            '"Food/Beverages" = meals, snacks, catering.',
            '"Hotel" = accommodation and lodging.',
            '"Location (City)" = the destination city itself.',
        ],
        "examples": [
            {
                "comment": "The hotel was way too cold including the guest rooms as well.",
                "classifications": [
                    {
                        "excerpt": "The hotel was way too cold including the guest rooms as well",
                        "reasoning": "Complaint about hotel temperature and comfort",
                        "sub_category": "Hotel",
                        "sentiment": "negative",
                    }
                ],
            },
            {
                "comment": "Knowing in advance about full breakfast vs. continental. May sound trivial but yoghurt-fruit are insufficient fuel for my morning. Tuesday's breakfast was too light. Weds morning ate in restaurant, only to discover conference had full breakfast. So skipped restaurant Thurs, but by the time I discovered conference had continental breakfast again, too late to get more substantial food before first session started.",
                "classifications": [
                    {
                        "excerpt": "Knowing in advance about full breakfast vs. continental. May sound trivial but yoghurt-fruit are insufficient fuel for my morning. Tuesday's breakfast was too light",
                        "reasoning": "Complaint about breakfast variety and advance communication",
                        "sub_category": "Food/Beverages",
                        "sentiment": "negative",
                    },
                    {
                        "excerpt": "Weds morning ate in restaurant, only to discover conference had full breakfast. So skipped restaurant Thurs, but by the time I discovered conference had continental breakfast again, too late to get more substantial food before first session started",
                        "reasoning": "Confusion about food availability and poor communication",
                        "sub_category": "Food/Beverages",
                        "sentiment": "negative",
                    },
                ],
            },
        ],
    }

    output_file = output_dir / "venue_hospitality.yaml"
    with open(output_file, "w") as f:
        f.write("# Stage 2: Venue & Hospitality Sub-categories\n\n")
        yaml.dump(data, f)

    print(f"✓ Exported Stage 2 - Venue & Hospitality: {output_file}")
    return output_file


def export_all_prompts(base_dir: Path):
    """Export all prompt YAML files."""
    print("=" * 60)
    print("EXPORTING ALL PROMPT YAMLS")
    print("=" * 60)

    # Stage 1
    stage1_dir = base_dir / "stage_1"
    export_stage1_yaml(stage1_dir)

    # Stage 2
    stage2_dir = base_dir / "stage_2"
    export_stage2_client_perceptions_yaml(stage2_dir)
    export_stage2_content_learning_yaml(stage2_dir)
    export_stage2_event_tech_yaml(stage2_dir)
    export_stage2_people_community_yaml(stage2_dir)
    export_stage2_venue_hospitality_yaml(stage2_dir)

    print("\n" + "=" * 60)
    print("✓ ALL PROMPTS EXPORTED")
    print("=" * 60)
    print(f"\nYAML files created in: {base_dir}")
    print(f"  Stage 1: {stage1_dir}")
    print(f"  Stage 2: {stage2_dir}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        output_dir = Path("./prompt_templates")

    export_all_prompts(output_dir)
