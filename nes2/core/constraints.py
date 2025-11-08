"""Model constraints and validation constants for nes2."""

# Length constraints
MAX_ID_LENGTH = 32
MAX_TYPE_LENGTH = 16
MAX_SUBTYPE_LENGTH = 25
MAX_SLUG_LENGTH = 100
MIN_SLUG_LENGTH = 3
MAX_SHORT_DESCRIPTION_LENGTH = 300
MAX_DESCRIPTION_LENGTH = 5000

# Regex patterns
SLUG_PATTERN = r"^[a-z0-9-]+$"
