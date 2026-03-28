import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

ROLE_BASED_PREFIXES = {
    "info", "support", "hello", "contact", "admin", "team", "help",
    "sales", "marketing", "billing", "noreply", "no-reply", "mail",
    "office", "enquiries", "enquiry", "hr", "jobs", "careers",
    "press", "media", "pr", "webmaster", "hostmaster", "postmaster",
}


def check_syntax(email: str) -> bool:
    """Return True if email has valid syntax."""
    return bool(EMAIL_REGEX.match(email.strip().lower()))


def is_role_based(email: str) -> bool:
    """Return True if the local part matches a known role-based prefix."""
    local = email.split("@")[0].lower().strip()
    return local in ROLE_BASED_PREFIXES
