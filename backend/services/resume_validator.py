import re

SECTION_CATEGORIES = {
    "experience": [
        "experience",
        "work experience",
        "employment history",
        "professional experience",
        "work history",
        "professional background",
    ],

    "education": [
        "education",
        "educational background",
        "academic background",
        "academic qualifications",
        "b.tech",
        "btech",
        "bachelor of technology",
        "bachelor of engineering",
        "bachelor's degree",
        "master of technology",
        "master of engineering",
        "university",
        "college",
        "degree",
        "cgpa",
        "gpa",
    ],

    "skills": [
        "skills",
        "technical skills",
        "technical expertise",
        "core competencies",
        "key skills",
        "programming skills",
        "technologies",
        "tools and technologies",
        "technical proficiencies",
    ],

    "projects": [
        "projects",
        "project experience",
        "academic projects",
        "personal projects",
        "key projects",
    ],

    "summary": [
        "summary",
        "professional summary",
        "career summary",
        "objective",
        "career objective",
        "profile",
        "professional profile",
    ],

    "certifications": [
        "certifications",
        "certification",
        "licenses and certifications",
    ],

    "achievements": [
        "achievements",
        "accomplishments",
        "awards",
        "honors",
    ],

    "internship": [
        "internship",
        "internships",
        "intern experience",
        "internship experience",
    ],

    "leadership": [
        "leadership",
        "leadership experience",
        "positions of responsibility",
    ],
}



RESUME_KEYWORDS = [
    # Job / career
    "developer",
    "engineer",
    "software engineer",
    "software developer",
    "data analyst",
    "data scientist",
    "machine learning",
    "artificial intelligence",
    "frontend",
    "backend",
    "full stack",
    "intern",
    "internship",

    # Technical
    "python",
    "java",
    "javascript",
    "typescript",
    "c++",
    "c#",
    "sql",
    "html",
    "css",
    "react",
    "node.js",
    "nodejs",
    "fastapi",
    "django",
    "flask",
    "mongodb",
    "mysql",
    "postgresql",
    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",

    # Resume language
    "responsibilities",
    "achieved",
    "developed",
    "implemented",
    "designed",
    "created",
    "built",
    "managed",
    "optimized",
    "deployed",
]




OFF_TOPIC_KEYWORDS = [
    # Academic documents
    "table of contents",
    "chapter one",
    "chapter 1",
    "abstract",
    "literature review",
    "references",
    "bibliography",
    "isbn",


    "invoice",
    "invoice number",
    "purchase order",
    "purchase order number",
    "amount payable",
    "grand total",
    "subtotal",
    "tax invoice",
    "billing address",
    "shipping address",
    "transaction id",
    "order id",


    "pnr",
    "irctc",
    "boarding pass",
    "boarding at",
    "passenger details",
    "ticket fare",
    "booking status",
    "e-ticket",
    "reservation slip",
    "flight no",
    "flight number",
    "seat no",
    "seat number",
    "departure",
    "arrival",


    "certificate of completion",
    "certificate of participation",
    "certificate of achievement",
    "certificate of virtual internship",
    "certificate id",
    "digital badge",
    "training badge",
    "credly.com",
    "course hours completed",
    "this is to certify that",
    "has successfully completed",
    "has successfully participated",
    "issued to",
    "certificate number",


    "offer letter",
    "internship offer letter",
    "appointment letter",
    "joining letter",
    "employment offer",
    "terms and conditions",
    "acceptance of offer",

    "attendance sheet",
    "attendance record",
    "student list",
    "student roster",
    "roll number",
    "registration number",
    "allocation list",
    "candidate list",
    "participant list",


    "recipe",
    "ingredients",
    "screenplay",
    "lorem ipsum",
    "medical report",
    "prescription",
]



EMAIL_RE = re.compile(
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"
)

PHONE_RE = re.compile(
    r"(?<!\d)"
    r"(?:\+?\d{1,3}[\s.-]?)?"
    r"(?:\(?\d{3,4}\)?[\s.-]?)"
    r"\d{3,4}[\s.-]?\d{3,4}"
    r"(?!\d)"
)

URL_RE = re.compile(
    r"(https?://|www\.)[^\s]+",
    re.IGNORECASE
)

LINKEDIN_RE = re.compile(
    r"(linkedin\.com|linkedin)",
    re.IGNORECASE
)

GITHUB_RE = re.compile(
    r"(github\.com|github)",
    re.IGNORECASE
)

YEAR_RE = re.compile(
    r"\b(?:19|20)\d{2}\b"
)

BULLET_RE = re.compile(
    r"(^|\n)\s*(?:[-•●▪◦*]|[0-9]+\.)\s+"
)



MIN_WORD_COUNT = 80
MAX_WORD_COUNT = 5000

MAX_DISTINCT_EMAILS = 2
MAX_DISTINCT_PHONES = 2

MIN_SECTIONS = 3

MIN_RESUME_SCORE = 8

def _normalize(text: str) -> str:
    """Normalize whitespace while preserving line structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _count_keyword_hits(text: str, keywords: list[str]) -> int:
    """Count unique keyword occurrences."""
    lower = text.lower()

    return sum(
        1
        for keyword in keywords
        if keyword.lower() in lower
    )


def _find_sections(text: str) -> list[str]:
    """Find recognized resume sections."""
    lower = text.lower()

    matched = []

    for category, keywords in SECTION_CATEGORIES.items():
        if any(keyword.lower() in lower for keyword in keywords):
            matched.append(category)

    return matched


def _distinct_emails(text: str) -> set[str]:
    return {
        email.lower()
        for email in EMAIL_RE.findall(text)
    }


def _distinct_phones(text: str) -> set[str]:
    phones = set()

    for phone in PHONE_RE.findall(text):
        normalized = re.sub(r"\D", "", phone)

        # Ignore obviously invalid short numbers
        if 7 <= len(normalized) <= 15:
            phones.add(normalized)

    return phones


def _has_contact_information(text: str) -> bool:
    return bool(
        EMAIL_RE.search(text)
        or PHONE_RE.search(text)
    )


def _has_professional_links(text: str) -> bool:
    return bool(
        LINKEDIN_RE.search(text)
        or GITHUB_RE.search(text)
        or URL_RE.search(text)
    )


def _has_resume_structure(text: str) -> bool:
    """
    Resume text normally contains multiple lines and/or bullets.
    """

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

    if len(lines) >= 12:
        return True

    if len(BULLET_RE.findall(text)) >= 2:
        return True

    return False


def _has_years(text: str) -> bool:
    return bool(YEAR_RE.search(text))


# ============================================================
# MAIN VALIDATOR
# ============================================================

def is_valid_resume(text: str):
    """
    Validate whether extracted PDF/DOCX text is likely to be
    a genuine individual resume.

    Returns:
        (True, "")
        OR
        (False, user-facing reason)
    """

    # --------------------------------------------------------
    # 1. Empty / unreadable document
    # --------------------------------------------------------

    if not text or not text.strip():
        return (
            False,
            "We couldn't read any text from this file. "
            "Please upload a valid PDF or DOCX resume."
        )

    cleaned = _normalize(text)
    lower = cleaned.lower()

    # --------------------------------------------------------
    # 2. Basic document size
    # --------------------------------------------------------

    words = cleaned.split()
    word_count = len(words)

    if word_count < MIN_WORD_COUNT:
        return (
            False,
            "This file is too short to be a complete resume. "
            "Please upload your full resume."
        )

    if word_count > MAX_WORD_COUNT:
        return (
            False,
            "This document is unusually long and does not appear "
            "to be a standard resume. Please upload your resume."
        )

    # --------------------------------------------------------
    # 3. Multiple-person detection
    # --------------------------------------------------------

    emails = _distinct_emails(cleaned)
    phones = _distinct_phones(cleaned)

    if len(emails) > MAX_DISTINCT_EMAILS:
        return (
            False,
            "This document appears to contain information for "
            "multiple people. Please upload an individual resume."
        )

    if len(phones) > MAX_DISTINCT_PHONES:
        return (
            False,
            "This document appears to contain records for multiple "
            "people rather than a single resume."
        )

    # --------------------------------------------------------
    # 4. Strong rejection for clearly unrelated documents
    # --------------------------------------------------------

    off_topic_hits = _count_keyword_hits(
        cleaned,
        OFF_TOPIC_KEYWORDS
    )

    # A single very strong document identifier should reject.
    strong_rejection_terms = [
        "invoice number",
        "purchase order number",
        "boarding pass",
        "certificate of completion",
        "certificate of participation",
        "this is to certify that",
        "attendance sheet",
        "student roster",
        "offer letter",
        "appointment letter",
        "table of contents",
    ]

    if any(term in lower for term in strong_rejection_terms):
        return (
            False,
            "The uploaded document does not appear to be a resume. "
            "Please upload your resume in PDF or DOCX format."
        )

    if off_topic_hits >= 2:
        return (
            False,
            "The uploaded document appears to be another type of "
            "document rather than a resume. Please upload your resume."
        )


    sections = _find_sections(cleaned)


    score = 0

    # ---- Sections ----

    score += min(len(sections), 5)

    # ---- Contact information ----

    if emails:
        score += 2

    if phones:
        score += 2

    # ---- Professional links ----

    if _has_professional_links(cleaned):
        score += 1

    # ---- Resume structure ----

    if _has_resume_structure(cleaned):
        score += 2

    # ---- Dates / years ----

    if _has_years(cleaned):
        score += 1



    resume_keyword_hits = _count_keyword_hits(
        cleaned,
        RESUME_KEYWORDS
    )

    if resume_keyword_hits >= 3:
        score += 2

    if resume_keyword_hits >= 7:
        score += 2

    if resume_keyword_hits >= 12:
        score += 1



    # A genuine resume should normally have at least 3 sections.
    if len(sections) < MIN_SECTIONS:
        return (
            False,
            "We couldn't recognize this document as a resume. "
            "A resume should normally contain sections such as "
            "Education, Skills, Experience, Projects, or Summary."
        )



    has_email = bool(emails)
    has_phone = bool(phones)
    has_link = _has_professional_links(cleaned)

    if not (has_email or has_phone or has_link):
        return (
            False,
            "This document does not contain recognizable professional "
            "contact information. Please upload a complete resume."
        )


    # At least one of these should normally exist.
    professional_identity = (
        has_email
        or has_phone
        or has_link
        or resume_keyword_hits >= 3
    )

    if not professional_identity:
        return (
            False,
            "The uploaded document does not contain enough "
            "professional resume information."
        )


    if score < MIN_RESUME_SCORE:
        return (
            False,
            "This document does not appear to be a complete resume. "
            "Please upload an individual resume containing sections "
            "such as Education, Skills, Experience, or Projects."
        )



    return True, ""