import re

# Configurable aliases mapping (lowercase input -> normalized name)
ALIASES = {
    "py": "Python",
    "python programming": "Python",
    "beginner python": "Python",
    "learn python": "Python",
    "guitar lessons": "Guitar",
    "learn guitar": "Guitar",
    "beginner guitar": "Guitar",
    "beginner guitar lessons": "Guitar",
    "ml": "Machine Learning",
    "ai": "Artificial Intelligence",
    "cooking basics": "Cooking",
    "learn photography": "Photography",
    "beginner photography": "Photography",
    "i want to learn photography": "Photography",
    "i want to learn python": "Python",
}

# Configurable skill-to-domain mapping (normalized name -> domain/category)
SKILL_DOMAINS = {
    # Technology
    "Python": "Technology",
    "Java": "Technology",
    "JavaScript": "Technology",
    "Rust": "Technology",
    "Go": "Technology",
    "C++": "Technology",
    "FastAPI": "Technology",
    "React": "Technology",
    "Kubernetes": "Technology",
    "Machine Learning": "Technology",
    "Git": "Technology",
    "Artificial Intelligence": "Technology",
    "HTML": "Technology",
    "CSS": "Technology",
    "Databases": "Technology",
    "SQL": "Technology",
    "Web Development": "Technology",
    # Music
    "Guitar": "Music",
    "Singing": "Music",
    "Piano": "Music",
    "Violin": "Music",
    "Drums": "Music",
    "Music": "Music",
    "Music Theory": "Music",
    "Flute": "Music",
    # Sports
    "Cricket": "Sports",
    "Football": "Sports",
    "Soccer": "Sports",
    "Basketball": "Sports",
    "Tennis": "Sports",
    "Badminton": "Sports",
    "Baseball": "Sports",
    "Golf": "Sports",
    # Dance
    "Dance": "Dance",
    "Ballet": "Dance",
    "Salsa": "Dance",
    "Hip Hop": "Dance",
    "Contemporary": "Dance",
    # Art
    "Drawing": "Art",
    "Painting": "Art",
    "Sketching": "Art",
    "Art": "Art",
    "Sculpture": "Art",
    "Design": "Art",
    # Photography
    "Photography": "Photography",
    "Videography": "Photography",
    # Cooking
    "Cooking": "Cooking",
    "Baking": "Cooking",
    "Culinary": "Cooking",
    "Kitchen": "Cooking",
    # Communication
    "Public Speaking": "Communication",
    "Communication": "Communication",
    "Writing": "Communication",
    "Debate": "Communication",
    # Academics
    "Mathematics": "Academics",
    "Physics": "Academics",
    "Chemistry": "Academics",
    "Biology": "Academics",
    "History": "Academics",
    "Geography": "Academics",
    "Economics": "Academics",
    # Languages
    "Spanish": "Languages",
    "French": "Languages",
    "German": "Languages",
    "Mandarin": "Languages",
    "English": "Languages",
    "Japanese": "Languages",
    "Korean": "Languages",
}

# Stopwords and common phrasing prefixes/suffixes to strip
PHRASES_TO_REMOVE = [
    r"^i want to learn\s+",
    r"^how to learn\s+",
    r"^learn\s+",
    r"^learning\s+",
    r"^beginner\s+",
    r"^advanced\s+",
    r"^basics of\s+",
    r"\s+programming$",
    r"\s+lessons$",
    r"\s+lesson$",
    r"\s+tutorial$",
    r"\s+tutorials$",
    r"\s+course$",
    r"\s+courses$",
    r"\s+guide$",
    r"\s+guides$",
    r"\s+training$",
]

def normalize_skill(skill_input: str) -> str:
    """
    Deterministic skill normalization.
    """
    if not skill_input:
        return ""
    
    val = skill_input.lower().strip()
    
    # 1. Check direct aliases first
    if val in ALIASES:
        return ALIASES[val]
        
    # 2. Iteratively strip phrases
    changed = True
    while changed:
        before = val
        for pattern in PHRASES_TO_REMOVE:
            val = re.sub(pattern, "", val, flags=re.IGNORECASE).strip()
        if val == before:
            changed = False
            
    if not val:
        return skill_input.strip()

    # Check aliases again after stripping
    if val in ALIASES:
        return ALIASES[val]

    # Try mapping to matching key in domain case-insensitively
    for k in SKILL_DOMAINS.keys():
        if k.lower() == val:
            return k

    # Fallback to title casing or original case capitalized
    return val.title()

def get_skill_category(normalized_skill: str) -> str:
    """
    Gets the skill's category, defaulting to "Other".
    """
    return SKILL_DOMAINS.get(normalized_skill, "Other")
